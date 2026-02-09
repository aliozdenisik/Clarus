#!/usr/bin/env python3
"""
Clarus CLI

Command-line interface for indexing and searching Quran and Bible translations
using Qdrant vector database with hybrid (semantic + BM25) search.

Usage:
    python main.py search "query"                        # Search Quran
    python main.py search-bible "query"                  # Search Bible
    python main.py info

    # For indexing, use the unified script:
    python scripts/setup_all_collections.py
"""

import argparse
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from src.data_loader import QuranDataLoader
from src.indexer import QuranIndexer, SemanticChunkIndexer, TurkishBibleIndexer
from src.search import (
    SemanticChunkSearcher,
)
from src.semantic_chunker import SemanticVerseChunker, analyze_surah_chunks

console = Console()


def format_confidence_display(confidence: float, breakdown=None) -> str:
    """Format confidence with optional breakdown for Rich display.

    Args:
        confidence: Overall confidence score (0.0-1.0)
        breakdown: Optional dict with two-phase breakdown:
                   Phase 1 (Retrieval): score_quality, score_separation, result_coverage
                   Phase 2 (Answer): citation_density, top_k_citation_rate, answer_substance
                   Composites: retrieval_confidence, answer_quality, source_breadth_bonus

    Returns:
        Formatted string for Rich console display with color coding
    """
    # Color based on thresholds
    if confidence >= 0.8:
        color = "green"
    elif confidence >= 0.6:
        color = "yellow"
    else:
        color = "red"

    conf_str = f"[{color}]Güven: {confidence:.0%}[/{color}]"

    if breakdown:
        retrieval = breakdown.get("retrieval_confidence", 0)
        answer = breakdown.get("answer_quality", 0)
        details = (
            f"Retrieval: {retrieval:.0%} "
            f"[dim](Q:{breakdown.get('score_quality', 0):.0%} "
            f"S:{breakdown.get('score_separation', 0):.0%} "
            f"C:{breakdown.get('result_coverage', 0):.0%})[/dim] | "
            f"Answer: {answer:.0%} "
            f"[dim](D:{breakdown.get('citation_density', 0):.0%} "
            f"T:{breakdown.get('top_k_citation_rate', 0):.0%} "
            f"W:{breakdown.get('answer_substance', 0):.0%})[/dim]"
        )
        conf_str += f"\n  {details}"

    return conf_str


def cmd_index(args):
    """Index Quran data into Qdrant"""
    import asyncio

    console.print("\n[bold blue]Quran Hybrid Search Indexer[/bold blue]\n")

    # Check for async mode
    use_async = getattr(args, "use_async", True)  # Default to async
    if use_async:
        console.print("[dim]Mode: Async (parallel embeddings)[/dim]")

    # Load data
    console.print("[yellow]Loading Quran data...[/yellow]")
    loader = QuranDataLoader(data_dir=Path("data"))
    loader.download_data()

    # Show stats
    stats = loader.get_stats()
    console.print(
        f"[green][OK][/green] Loaded {stats['total_surahs']} surahs, {stats['total_verses']} verses"
    )

    # Create chunks
    console.print("\n[yellow]Creating chunks...[/yellow]")
    chunks = loader.create_chunks(show_progress=True)
    console.print(f"[green][OK][/green] Created {len(chunks)} chunks")

    # Initialize indexer
    console.print("\n[yellow]Initializing Qdrant...[/yellow]")
    try:
        indexer = QuranIndexer(qdrant_url=args.qdrant_url)
        indexer.create_collection(recreate=args.recreate)
    except Exception as e:
        console.print(f"[red][ERROR] Error connecting to Qdrant: {e}[/red]")
        console.print("\n[yellow]Make sure Qdrant is running:[/yellow]")
        console.print("  docker run -p 6333:6333 qdrant/qdrant")
        return 1

    # Index chunks (use async for faster embedding)
    console.print("\n[yellow]Indexing chunks...[/yellow]")
    if use_async:
        console.print("[dim]Using async parallel embedding (2-3x faster)[/dim]")
        count = asyncio.run(
            indexer.index_chunks_async(chunks, batch_size=args.batch_size)
        )
    else:
        count = indexer.index_chunks(chunks, batch_size=args.batch_size)

    # Show info
    info = indexer.get_collection_info()
    console.print(f"\n[green][OK][/green] Successfully indexed {count} verses!")
    console.print(f"  Collection: {info['name']}")
    console.print(f"  Points: {info['points_count']}")
    console.print(f"  Status: {info['status']}")

    return 0


def display_quran_results(args, results, query):
    """Display Quran search results in a formatted table."""
    if not results:
        console.print("[yellow]No results found.[/yellow]")
        return 0

    # Create results table
    table = Table(title=f"Search Results ({len(results)} found)", show_lines=True)
    table.add_column("#", style="dim", width=3)
    table.add_column("Reference", style="cyan", width=15)
    table.add_column("Score", style="green", width=8)
    table.add_column("Translation", style="white")

    for i, result in enumerate(results, 1):
        # Handle both regular SearchResult and SemanticChunkSearchResult
        if hasattr(result, "verse_id"):
            # Regular single-verse result
            ref = f"{result.surah_id}:{result.verse_id}\n{result.surah_name}"
            translation = result.translation
        else:
            # SemanticChunkSearchResult (multi-verse)
            verse_range = (
                f"{result.start_verse}-{result.end_verse}"
                if result.start_verse != result.end_verse
                else str(result.start_verse)
            )
            ref = f"{result.surah_id}:{verse_range}\n{result.surah_name} ({result.verse_count}v)"
            translation = result.combined_translation

        score = f"{result.score:.3f}"
        translation_display = translation[:150] + (
            "..." if len(translation) > 150 else ""
        )
        table.add_row(str(i), ref, score, translation_display)

    console.print(table)

    # Show detailed first result
    if results and getattr(args, "verbose", False):
        first = results[0]
        if hasattr(first, "verse_id"):
            # Regular result
            console.print(
                Panel(
                    f"[bold]{first.surah_name}[/bold] ({first.surah_transliteration})\n"
                    f"Ayet {first.verse_id} | {first.surah_type.capitalize()}\n\n"
                    f"[dim]Arabic:[/dim]\n{first.arabic_text}\n\n"
                    f"[dim]Translation:[/dim]\n{first.translation}",
                    title="[green]Top Result[/green]",
                    expand=False,
                )
            )
        else:
            # Semantic chunk result
            console.print(
                Panel(
                    f"[bold]{first.surah_name}[/bold] ({first.surah_transliteration})\n"
                    f"Ayetler {first.start_verse}-{first.end_verse} ({first.verse_count} ayet) | {first.surah_type.capitalize()}\n\n"
                    f"[dim]Arabic:[/dim]\n{first.combined_arabic}\n\n"
                    f"[dim]Translation:[/dim]\n{first.combined_translation}",
                    title="[green]Top Result (Semantic Chunk)[/green]",
                    expand=False,
                )
            )

    return 0


def cmd_search(args):
    """Search Quran data using Ultimate RAG Pipeline"""
    import asyncio

    query = args.query
    limit = args.limit
    translator = getattr(args, "translator", "diyanet")

    console.print(
        f"\n[bold magenta]🚀 Ultimate RAG Pipeline ({translator})[/bold magenta]"
    )
    console.print(
        "[dim]Combining: Enhance + Multi-Query + Semantic + RRF Fusion[/dim]\n"
    )

    try:
        from src.ultimate_rag import UltimateRAG

        rag = UltimateRAG(
            qdrant_url=args.qdrant_url,
            enable_multi_query=True,
            search_mode="semantic",
            final_top_k=limit,
            verbose=True,
        )
        results = asyncio.run(
            rag.search_quran(query, translator=translator, top_k=limit)
        )
        return display_quran_results(args, results, query)
    except Exception as e:
        console.print(f"[red][ERROR] Ultimate RAG failed: {e}[/red]")
        import traceback

        traceback.print_exc()
        return 1


def cmd_info(args):
    """Show collection info for all or specific collections"""
    from qdrant_client import QdrantClient

    console.print("\n[bold blue]Collection Info[/bold blue]\n")

    try:
        client = QdrantClient(url=args.qdrant_url)
        collections = client.get_collections().collections

        if not collections:
            console.print("[yellow]No collections found.[/yellow]")
            return 0

        # Filter collections based on flags
        show_quran = args.quran if hasattr(args, "quran") else False
        show_bible = args.bible if hasattr(args, "bible") else False
        show_all = not show_quran and not show_bible

        # Create main table
        table = Table(title="Available Collections", show_lines=True)
        table.add_column("Collection", style="cyan", width=20)
        table.add_column("Type", style="magenta", width=12)
        table.add_column("Points", style="green", justify="right", width=10)
        table.add_column("Vectors", style="yellow", justify="right", width=10)
        table.add_column("Status", style="white", width=10)

        found_any = False
        for collection in collections:
            name = collection.name

            # Determine collection type
            if name.startswith("quran_tr_"):
                translator = name.replace("quran_tr_", "")
                col_type = f"Quran ({translator})"
                if not show_all and not show_quran:
                    continue
            elif name.startswith("bible_"):
                translation = name.replace("bible_", "")
                col_type = f"Bible ({translation})"
                if not show_all and not show_bible:
                    continue
            else:
                col_type = "Other"
                if not show_all:
                    continue

            # Get detailed info
            info = client.get_collection(name)
            points = info.points_count
            vectors = getattr(info, "vectors_count", points)
            status = str(info.status).replace("CollectionStatus.", "")

            table.add_row(name, col_type, str(points), str(vectors), status)
            found_any = True

        if found_any:
            console.print(table)

            # Show summary
            console.print(
                "\n[dim]Tip: Use --quran or --bible to filter collections[/dim]"
            )
        else:
            console.print("[yellow]No matching collections found.[/yellow]")

    except Exception as e:
        console.print(f"[red][ERROR] Error: {e}[/red]")
        console.print(
            "[dim]Make sure Qdrant is running: docker run -p 6333:6333 qdrant/qdrant[/dim]"
        )
        return 1

    return 0


def cmd_index_quran(args):
    """Index Quran translation(s) from Tanzil XML"""
    translator = args.translator

    if translator == "all" or translator is None:
        console.print("\n[bold blue]Indexing All Quran Translators[/bold blue]\n")
        QuranIndexer.index_all_translators(qdrant_url=args.qdrant_url, recreate=True)
    else:
        console.print(f"\n[bold blue]Indexing Quran ({translator})[/bold blue]\n")
        indexer = QuranIndexer(translator=translator, qdrant_url=args.qdrant_url)
        indexer.create_collection(recreate=True)
        count = indexer.index()
        console.print(f"[green]✓[/green] Indexed {count} verses for {translator}")

    return 0


def cmd_index_bible_tr(args):
    """Index Turkish Bible from OSIS XML"""
    console.print("\n[bold blue]Indexing Turkish Bible[/bold blue]\n")

    indexer = TurkishBibleIndexer(qdrant_url=args.qdrant_url)
    counts = indexer.index_all(recreate=True)

    console.print("\n[green]✓[/green] Indexed Turkish Bible:")
    console.print(f"  OT: {counts['ot']} verses")
    console.print(f"  NT: {counts['nt']} verses")

    return 0


def cmd_delete_collection(args):
    """Delete a Qdrant collection"""
    from qdrant_client import QdrantClient

    name = args.name
    force = args.force

    console.print(f"\n[bold red]Delete Collection: {name}[/bold red]\n")

    if not force:
        response = input(f"Are you sure you want to delete '{name}'? [yes/N]: ")
        if response.lower() != "yes":
            console.print("[yellow]Cancelled.[/yellow]")
            return 0

    try:
        client = QdrantClient(url=args.qdrant_url)
        client.delete_collection(name)
        console.print(f"[green]✓[/green] Deleted collection: {name}")
        return 0
    except Exception as e:
        console.print(f"[red][ERROR] {e}[/red]")
        return 1


def cmd_search_bible(args):
    """Search Bible data using Ultimate RAG Pipeline"""
    import asyncio

    query = args.query
    translation = args.translation
    limit = args.limit
    language = getattr(args, "language", "en")

    console.print("\n[bold magenta]🚀 Ultimate RAG Pipeline (Bible)[/bold magenta]")
    console.print(
        "[dim]Combining: Enhance + Multi-Query + Semantic + RRF Fusion[/dim]\n"
    )

    if language == "tr":
        console.print("[dim]Language: Turkish Bible[/dim]")

    try:
        from src.ultimate_rag import UltimateRAG

        rag = UltimateRAG(
            qdrant_url=args.qdrant_url,
            enable_multi_query=True,
            search_mode="semantic",
            final_top_k=limit,
            verbose=True,
        )
        results = asyncio.run(
            rag.search_bible(
                query, translation=translation, top_k=limit, language=language
            )
        )

        if not results:
            console.print("[yellow]No results found.[/yellow]")
            return 0

        # Create results table
        table = Table(title=f"Search Results ({len(results)} found)", show_lines=True)
        table.add_column("#", style="dim", width=3)
        table.add_column("Reference", style="cyan", width=20)
        table.add_column("Score", style="green", width=8)
        table.add_column("Text", style="white")

        # Testament display mapping for Turkish
        testament_names = {"OT": "Eski Ahit", "NT": "Yeni Ahit", "Apocrypha": "Apokrif"}

        for i, result in enumerate(results, 1):
            testament_display = testament_names.get(result.testament, result.testament)

            # Handle both single verses and semantic chunks
            if hasattr(result, "verse"):
                # Single verse result
                ref = f"{result.book_name} {result.chapter}:{result.verse}\n({testament_display})"
            else:
                # Semantic chunk result
                verse_range = (
                    f"{result.start_verse}-{result.end_verse}"
                    if result.start_verse != result.end_verse
                    else str(result.start_verse)
                )
                ref = f"{result.book_name} {result.chapter}:{verse_range}\n({testament_display})"

            score = f"{result.score:.3f}"
            text = result.text[:150] + ("..." if len(result.text) > 150 else "")
            table.add_row(str(i), ref, score, text)

        console.print(table)

        # Show detailed first result
        if results and args.verbose:
            first = results[0]
            testament_display = testament_names.get(first.testament, first.testament)

            if hasattr(first, "verse"):
                ref_text = f"{first.book_name} {first.chapter}:{first.verse}"
            else:
                verse_range = (
                    f"{first.start_verse}-{first.end_verse}"
                    if first.start_verse != first.end_verse
                    else str(first.start_verse)
                )
                ref_text = f"{first.book_name} {first.chapter}:{verse_range}"

            console.print(
                Panel(
                    f"[bold]{ref_text}[/bold]\n"
                    f"{testament_display} | {getattr(first, 'translation', getattr(first, 'verse_count', 'N/A') + ' verses')}\n\n"
                    f"[dim]Text:[/dim]\n{first.text}",
                    title="[green]Top Result[/green]",
                    expand=False,
                )
            )

        return 0
    except Exception as e:
        console.print(f"[red][ERROR] Ultimate RAG failed: {e}[/red]")
        import traceback

        traceback.print_exc()
        return 1


def cmd_ask(args):
    """Ask a question about Quran - Full RAG Q&A with citations"""
    import asyncio

    query = args.query
    limit = args.limit
    translator = getattr(args, "translator", "diyanet")

    console.print(
        f"\n[bold magenta]🧠 Ultimate RAG Q&A Pipeline (Kuran - {translator})[/bold magenta]"
    )
    console.print("[dim]Search + Answer Generation with Citations[/dim]\n")

    try:
        from src.ultimate_rag import UltimateRAG

        rag = UltimateRAG(
            qdrant_url=args.qdrant_url,
            enable_multi_query=True,
            search_mode="semantic",
            final_top_k=limit,
            verbose=True,
        )

        answer = asyncio.run(rag.ask_quran(query, translator=translator, top_k=limit))

        # Display answer
        console.print(
            Panel(
                f"[bold white]{answer.text}[/bold white]",
                title=f"Cevap ({format_confidence_display(answer.confidence, getattr(answer, 'confidence_breakdown', None))})",
                subtitle=f"[dim]{len(answer.citations)} kaynak kullanıldı[/dim]",
                expand=False,
            )
        )

        # Show citations
        if answer.citations:
            console.print("\n[cyan]📖 Kaynaklar:[/cyan]")
            for i, ref in enumerate(answer.citations, 1):
                console.print(f"  {i}. {ref}")

        return 0
    except Exception as e:
        console.print(f"[red][ERROR] Q&A failed: {e}[/red]")
        import traceback

        traceback.print_exc()
        return 1


def cmd_ask_bible(args):
    """Ask a question about Bible - Full RAG Q&A with citations"""
    import asyncio

    query = args.query
    translation = args.translation
    limit = args.limit

    console.print(
        f"\n[bold magenta]🧠 Ultimate RAG Q&A Pipeline (Bible - {translation})[/bold magenta]"
    )
    console.print("[dim]Search + Answer Generation with Citations[/dim]\n")

    try:
        from src.ultimate_rag import UltimateRAG

        rag = UltimateRAG(
            qdrant_url=args.qdrant_url,
            enable_multi_query=True,
            search_mode="semantic",
            final_top_k=limit,
            verbose=True,
        )

        answer = asyncio.run(rag.ask_bible(query, translation=translation, top_k=limit))

        # Display answer
        console.print(
            Panel(
                f"[bold white]{answer.text}[/bold white]",
                title=f"Cevap ({format_confidence_display(answer.confidence, getattr(answer, 'confidence_breakdown', None))})",
                subtitle=f"[dim]{len(answer.citations)} kaynak kullanıldı[/dim]",
                expand=False,
            )
        )

        # Show citations
        if answer.citations:
            console.print("\n[cyan]📖 Kaynaklar:[/cyan]")
            for i, ref in enumerate(answer.citations, 1):
                console.print(f"  {i}. {ref}")

        return 0
    except Exception as e:
        console.print(f"[red][ERROR] Q&A failed: {e}[/red]")
        import traceback

        traceback.print_exc()
        return 1


def cmd_compare(args):
    """Comparative scripture analysis - Search Quran and Bible, generate theological essay"""
    query = args.query
    verses = args.verses
    translation = args.translation
    multi_agent = args.multi_agent
    translator = getattr(args, "translator", "diyanet")

    if multi_agent:
        console.print(
            "\n[bold magenta]📚 Multi-Agent Comparative Scripture Analysis[/bold magenta]"
        )
        console.print(
            f"[dim]4 Specialist Agents (OT, NT, Apocrypha, Quran-{translator}) + Synthesis Agent[/dim]\n"
        )
    else:
        console.print(
            "\n[bold magenta]📚 Comparative Scripture Analysis[/bold magenta]"
        )
        console.print(
            f"[dim]Searching Quran ({translator}) + Bible → Comparative Theological Essay[/dim]\n"
        )

    try:
        from src.comparative_rag import ComparativeRAG

        rag = ComparativeRAG(
            qdrant_url=args.qdrant_url,
            bible_translation=translation,
            verses_per_search=verses,
            verbose=True,
        )

        if multi_agent:
            result = rag.compare_multi_agent(query, translator=translator)
            essay_text = result.to_essay()
            confidence = result.confidence
            confidence_breakdown = getattr(result, "confidence_breakdown", None)
            citations = result.citations
            # Flatten citations for display
            all_refs = []
            for source, refs in citations.items():
                all_refs.extend([f"({source}) {ref}" for ref in refs])
        else:
            result = rag.compare(query, translator=translator)
            essay_text = result.essay
            confidence = result.confidence
            confidence_breakdown = getattr(result, "confidence_breakdown", None)
            all_refs = result.all_references

        # Display essay
        console.print(
            Panel(
                f"[white]{essay_text}[/white]",
                title=f"Karşılaştırmalı Analiz ({format_confidence_display(confidence, confidence_breakdown)})",
                expand=False,
                padding=(1, 2),
            )
        )

        # Show references
        if all_refs:
            console.print("\n[bold cyan]📖 Kullanılan Kaynaklar:[/bold cyan]")
            for i, ref in enumerate(all_refs, 1):
                console.print(f"  {i}. {ref}")

        return 0
    except Exception as e:
        console.print(f"[red][ERROR] Comparative analysis failed: {e}[/red]")
        import traceback

        traceback.print_exc()
        return 1


def cmd_build_bible_semantic_chunks(args):
    """Build semantic chunks for Bible"""
    import asyncio

    translation = args.translation
    console.print(
        f"\n[bold blue]Building Semantic Chunks for Bible ({translation})[/bold blue]\n"
    )

    from src.bible_semantic_chunker import BibleSemanticVerseChunker

    # Initialize chunker
    chunker = BibleSemanticVerseChunker(
        translation=translation,
        similarity_threshold=args.threshold,
        max_chunk_size=args.max_size,
    )

    # Create chunks
    console.print("[yellow]Creating semantic chunks...[/yellow]")
    console.print(f"  Threshold: {args.threshold} ({args.threshold_type})")
    console.print(f"  Max Size: {args.max_size}")

    chunks = chunker.create_semantic_chunks(
        show_progress=True, threshold_type=args.threshold_type
    )

    if args.analyze_only:
        console.print("[yellow]Analysis mode: Skipping indexing[/yellow]")
        return 0

    # Save to file
    chunker.save_chunks(chunks)

    # Index using async for speed
    console.print("\n[yellow]Indexing semantic chunks (async mode)...[/yellow]")
    from src.indexer import BibleSemanticChunkIndexer

    indexer = BibleSemanticChunkIndexer(
        translation=translation, qdrant_url=args.qdrant_url
    )
    indexer.create_collection(recreate=args.recreate)

    # Use async indexer for 2-3x speed improvement
    asyncio.run(indexer.index_chunks_async(chunks))

    info = indexer.get_collection_info()
    console.print(
        f"\n[green][OK][/green] Successfully indexed {info['points_count']} semantic chunks!"
    )

    return 0


def cmd_search_bible_semantic(args):
    """Search Bible semantic chunks"""
    query = args.query
    limit = args.limit
    translation = args.translation

    console.print(f"\n[bold blue]Bible Semantic Search ({translation})[/bold blue]\n")
    console.print(f"[dim]Query: {query}[/dim]")

    from src.search import BibleSemanticChunkSearcher

    searcher = BibleSemanticChunkSearcher(
        translation=translation, qdrant_url=args.qdrant_url
    )

    if not searcher.collection_exists():
        console.print(f"[red]Collection not found: {searcher.collection_name}[/red]")
        console.print(
            f"[yellow]Run 'python main.py build-bible-semantic-chunks --translation {translation}' first.[/yellow]"
        )
        return 1

    results = searcher.search(query, limit=limit)

    if not results:
        console.print("[yellow]No results found.[/yellow]")
        return 0

    # Create results table
    table = Table(
        title=f"Semantic Chunk Results ({len(results)} found)", show_lines=True
    )
    table.add_column("#", style="dim", width=3)
    table.add_column("Reference", style="cyan", width=20)
    table.add_column("Score", style="green", width=8)
    table.add_column("Text", style="white")

    for i, result in enumerate(results, 1):
        verse_range = (
            f"{result.start_verse}-{result.end_verse}"
            if result.start_verse != result.end_verse
            else str(result.start_verse)
        )
        ref = f"{result.book_name} {result.chapter}:{verse_range}\n({result.testament})"
        score = f"{result.score:.3f}"
        text = result.text[:150] + ("..." if len(result.text) > 150 else "")
        table.add_row(str(i), ref, score, text)

    console.print(table)

    if results and args.verbose:
        first = results[0]
        verse_range = f"{first.start_verse}-{first.end_verse}"
        console.print(
            Panel(
                f"[bold]{first.book_name} {first.chapter}:{verse_range}[/bold]\n"
                f"{first.testament} | {first.verse_count} verses\n\n"
                f"[dim]Text:[/dim]\n{first.text}",
                title="[green]Top Semantic Result[/green]",
                expand=False,
            )
        )

    return 0


def main():
    parser = argparse.ArgumentParser(
        description="Clarus - Semantic + BM25 search for Quran and Bible"
    )
    parser.add_argument(
        "--qdrant-url", default="http://localhost:6333", help="Qdrant server URL"
    )

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Setup command (Runs everything)
    setup_parser = subparsers.add_parser(
        "setup", help="Full setup: Index Quran, Semantic Chunks, and Bible"
    )
    setup_parser.add_argument(
        "--recreate",
        action="store_true",
        help="Recreate all collections (delete existing)",
    )
    setup_parser.add_argument(
        "--batch-size",
        type=int,
        default=100,
        help="Batch size for indexing (default: 100)",
    )
    # Bible args
    setup_parser.add_argument(
        "--translation",
        default="kjva",
        choices=["kjva", "kjv"],
        help="Bible translation to index (default: kjva)",
    )
    setup_parser.add_argument(
        "--parallel",
        type=int,
        default=20,
        help="Max concurrent API calls for Bible (default: 20)",
    )
    # Semantic args
    setup_parser.add_argument(
        "--semantic-threshold",
        type=float,
        default=10,
        help="Semantic chunking threshold (default: 10)",
    )
    setup_parser.add_argument(
        "--threshold-type",
        type=str,
        default="percentile",
        choices=["percentile", "gradient", "interquartile", "std", "fixed"],
        help="Threshold strategy (default: percentile)",
    )
    setup_parser.add_argument(
        "--semantic-max-size",
        type=int,
        default=10,
        help="Maximum verses per chunk (default: 10)",
    )

    # Index Quran command
    index_parser = subparsers.add_parser("index", help="Index Quran data")
    index_parser.add_argument(
        "--recreate", action="store_true", help="Recreate collection (delete existing)"
    )
    index_parser.add_argument(
        "--batch-size", type=int, default=100, help="Batch size for indexing"
    )

    # Search Quran command (uses Ultimate RAG Pipeline)
    search_parser = subparsers.add_parser("search", help="Search Quran (Ultimate RAG)")
    search_parser.add_argument("query", help="Search query")
    search_parser.add_argument(
        "--limit", type=int, default=10, help="Number of results"
    )
    search_parser.add_argument(
        "-v", "--verbose", action="store_true", help="Show detailed first result"
    )
    search_parser.add_argument(
        "--translator",
        type=str,
        default="diyanet",
        choices=[
            "diyanet",
            "yazir",
            "ates",
            "bulac",
            "ozturk",
            "vakfi",
            "yildirim",
            "yuksel",
        ],
        help="Quran translator (default: diyanet)",
    )

    # Search Bible command (uses Ultimate RAG Pipeline)
    search_bible_parser = subparsers.add_parser(
        "search-bible", help="Search Bible (Ultimate RAG)"
    )
    search_bible_parser.add_argument("query", help="Search query")
    search_bible_parser.add_argument(
        "--translation",
        default="kjva",
        help="Bible translation to search (default: kjva)",
    )
    search_bible_parser.add_argument(
        "--limit", type=int, default=10, help="Number of results"
    )
    search_bible_parser.add_argument(
        "-v", "--verbose", action="store_true", help="Show detailed first result"
    )
    search_bible_parser.add_argument(
        "--language",
        default="en",
        choices=["en", "tr"],
        help="Bible language: en (English KJVA) or tr (Turkish) (default: en)",
    )

    # Ask Quran command (Full RAG Q&A with citations)
    ask_parser = subparsers.add_parser(
        "ask", help="Ask a question about Quran (RAG Q&A)"
    )
    ask_parser.add_argument("query", help="Question to ask")
    ask_parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="Number of search results to use as context",
    )
    ask_parser.add_argument(
        "--translator",
        type=str,
        default="diyanet",
        choices=[
            "diyanet",
            "yazir",
            "ates",
            "bulac",
            "ozturk",
            "vakfi",
            "yildirim",
            "yuksel",
        ],
        help="Quran translator (default: diyanet)",
    )

    # Ask Bible command (Full RAG Q&A with citations)
    ask_bible_parser = subparsers.add_parser(
        "ask-bible", help="Ask a question about Bible (RAG Q&A)"
    )
    ask_bible_parser.add_argument("query", help="Question to ask")
    ask_bible_parser.add_argument(
        "--translation", default="kjva", help="Bible translation to use (default: kjva)"
    )
    ask_bible_parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="Number of search results to use as context",
    )

    # Comparative Scripture Analysis command
    compare_parser = subparsers.add_parser(
        "compare", help="Comparative scripture analysis (Quran + Bible)"
    )
    compare_parser.add_argument("query", help="Religious/philosophical question")
    compare_parser.add_argument(
        "--verses",
        type=int,
        default=20,
        help="Verses per search type (default: 20, total: 80)",
    )
    compare_parser.add_argument(
        "--translation", default="kjva", help="Bible translation to use (default: kjva)"
    )
    compare_parser.add_argument(
        "--multi-agent",
        action="store_true",
        help="Use multi-agent system (5 paragraphs: OT, NT, Apocrypha, Quran, Synthesis)",
    )
    compare_parser.add_argument(
        "--translator",
        type=str,
        default="diyanet",
        choices=[
            "diyanet",
            "yazir",
            "ates",
            "bulac",
            "ozturk",
            "vakfi",
            "yildirim",
            "yuksel",
        ],
        help="Quran translator (default: diyanet)",
    )

    # Info command
    info_parser = subparsers.add_parser("info", help="Show collection info")
    info_parser.add_argument(
        "--quran", action="store_true", help="Show only Quran collection"
    )
    info_parser.add_argument(
        "--bible", action="store_true", help="Show only Bible collections"
    )

    # Index Quran command
    index_quran_parser = subparsers.add_parser(
        "index-quran", help="Index Quran translations from Tanzil XML"
    )
    index_quran_parser.add_argument(
        "--translator",
        type=str,
        default=None,
        choices=[
            "diyanet",
            "yazir",
            "ates",
            "bulac",
            "ozturk",
            "vakfi",
            "yildirim",
            "yuksel",
            "all",
        ],
        help="Translator to index (default: all)",
    )

    # Index Turkish Bible command
    subparsers.add_parser("index-bible-tr", help="Index Turkish Bible from OSIS XML")

    # Delete collection command
    delete_col_parser = subparsers.add_parser(
        "delete-collection", help="Delete a Qdrant collection"
    )
    delete_col_parser.add_argument("name", type=str, help="Collection name to delete")
    delete_col_parser.add_argument(
        "--force", action="store_true", help="Skip confirmation prompt"
    )

    # GraphRAG commands
    build_graph_parser = subparsers.add_parser(
        "build-graph", help="Build knowledge graph from indexed data"
    )
    build_graph_parser.add_argument(
        "--collection",
        type=str,
        default="quran_tr_diyanet",
        help="Qdrant collection to process (default: quran_tr_diyanet)",
    )
    build_graph_parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Limit documents to process (default: all)",
    )
    build_graph_parser.add_argument(
        "--clear", action="store_true", help="Clear existing graph before building"
    )
    build_graph_parser.add_argument(
        "--resume", action="store_true", help="Resume from last checkpoint"
    )
    build_graph_parser.add_argument(
        "--workers",
        type=int,
        default=4,
        help="Number of concurrent workers (default: 4)",
    )
    build_graph_parser.add_argument(
        "--batch-size",
        type=int,
        default=50,
        help="Batch size for fetching from Qdrant (default: 50)",
    )
    build_graph_parser.add_argument(
        "--checkpoint-interval",
        type=int,
        default=100,
        help="Save checkpoint every N documents (default: 100)",
    )

    subparsers.add_parser("graph-info", help="Show knowledge graph statistics")

    # Add --graph flag to search parsers
    search_parser.add_argument(
        "--graph",
        action="store_true",
        help="Enable graph-enhanced search (requires Neo4j)",
    )
    search_bible_parser.add_argument(
        "--graph",
        action="store_true",
        help="Enable graph-enhanced search (requires Neo4j)",
    )

    # Semantic Chunking commands
    build_chunks_parser = subparsers.add_parser(
        "build-semantic-chunks", help="Build semantic chunks from Quran verses"
    )
    build_chunks_parser.add_argument(
        "--threshold",
        type=float,
        default=10,
        help="Threshold value (meaning depends on --threshold-type, default: 10 for percentile)",
    )
    build_chunks_parser.add_argument(
        "--threshold-type",
        type=str,
        default="percentile",
        choices=["percentile", "gradient", "interquartile", "std", "fixed"],
        help="Threshold strategy: percentile (default), gradient, interquartile, std, or fixed",
    )
    build_chunks_parser.add_argument(
        "--max-size",
        type=int,
        default=10,
        help="Maximum verses per chunk (default: 10)",
    )
    build_chunks_parser.add_argument(
        "--recreate", action="store_true", help="Recreate collection (delete existing)"
    )
    build_chunks_parser.add_argument(
        "--analyze-only", action="store_true", help="Only analyze chunks, don't index"
    )

    search_semantic_parser = subparsers.add_parser(
        "search-semantic", help="Search using semantic chunks"
    )
    search_semantic_parser.add_argument("query", help="Search query")
    search_semantic_parser.add_argument(
        "--limit", type=int, default=5, help="Number of results (default: 5)"
    )
    search_semantic_parser.add_argument(
        "-v", "--verbose", action="store_true", help="Show detailed results"
    )

    analyze_chunks_parser = subparsers.add_parser(
        "analyze-chunks", help="Analyze semantic chunks for a surah"
    )
    analyze_chunks_parser.add_argument(
        "--surah", type=int, default=1, help="Surah number to analyze (default: 1)"
    )

    # Bible Semantic Chunking commands
    build_bible_chunks_parser = subparsers.add_parser(
        "build-bible-semantic-chunks", help="Build semantic chunks from Bible verses"
    )
    build_bible_chunks_parser.add_argument(
        "--translation",
        default="kjva",
        choices=["kjva", "kjv"],
        help="Bible translation (default: kjva)",
    )
    build_bible_chunks_parser.add_argument(
        "--threshold",
        type=float,
        default=0.75,
        help="Similarity threshold (default: 0.75)",
    )
    build_bible_chunks_parser.add_argument(
        "--threshold-type",
        type=str,
        default="percentile",
        choices=["percentile", "gradient", "interquartile", "std", "fixed"],
        help="Threshold strategy (default: percentile)",
    )
    build_bible_chunks_parser.add_argument(
        "--max-size",
        type=int,
        default=10,
        help="Maximum verses per chunk (default: 10)",
    )
    build_bible_chunks_parser.add_argument(
        "--recreate", action="store_true", help="Recreate collection (delete existing)"
    )
    build_bible_chunks_parser.add_argument(
        "--analyze-only", action="store_true", help="Only analyze chunks, don't index"
    )

    search_bible_semantic_parser = subparsers.add_parser(
        "search-bible-semantic", help="Search Bible semantic chunks"
    )
    search_bible_semantic_parser.add_argument("query", help="Search query")
    search_bible_semantic_parser.add_argument(
        "--translation",
        default="kjva",
        help="Bible translation to search (default: kjva)",
    )
    search_bible_semantic_parser.add_argument(
        "--limit", type=int, default=5, help="Number of results (default: 5)"
    )
    search_bible_semantic_parser.add_argument(
        "-v", "--verbose", action="store_true", help="Show detailed results"
    )

    # Cache management commands
    subparsers.add_parser("cache-info", help="Show semantic cache statistics")

    cache_clear_parser = subparsers.add_parser(
        "cache-clear", help="Clear semantic cache"
    )
    cache_clear_parser.add_argument(
        "--older-than",
        type=int,
        default=None,
        help="Only clear entries older than N hours (default: clear all)",
    )

    # Keyword Search command (morphological root-based)
    keyword_search_parser = subparsers.add_parser(
        "keyword-search",
        help="Search Quran by morphological root (Arabic or Buckwalter)",
    )
    keyword_search_parser.add_argument(
        "query", help="Arabic word or Buckwalter root (e.g., كتب or ktb)"
    )
    keyword_search_parser.add_argument(
        "--limit",
        type=int,
        default=50,
        help="Number of verse results per page (default: 50)",
    )
    keyword_search_parser.add_argument(
        "--page", type=int, default=1, help="Page number (default: 1)"
    )
    keyword_search_parser.add_argument(
        "--format",
        choices=["table", "json"],
        default="table",
        help="Output format (default: table)",
    )

    # Bible Keyword Search command
    bible_keyword_search_parser = subparsers.add_parser(
        "bible-keyword-search",
        help="Search Bible by morphological root (Hebrew, Aramaic, or Strong's number)",
    )
    bible_keyword_search_parser.add_argument(
        "query",
        help="Hebrew word, Strong's number, or Latin transliteration (e.g., כתב, H3789, ktb)",
    )
    bible_keyword_search_parser.add_argument(
        "--limit",
        type=int,
        default=50,
        help="Number of verse results per page (default: 50)",
    )
    bible_keyword_search_parser.add_argument(
        "--page", type=int, default=1, help="Page number (default: 1)"
    )
    bible_keyword_search_parser.add_argument(
        "--format",
        choices=["table", "json"],
        default="table",
        help="Output format (default: table)",
    )
    bible_keyword_search_parser.add_argument(
        "--language",
        choices=["hebrew", "aramaic", "all"],
        default="all",
        help="Filter by language (default: all)",
    )

    # Verse lookup command
    verse_lookup_parser = subparsers.add_parser(
        "verse-lookup", help="Look up verse by reference"
    )
    verse_lookup_parser.add_argument(
        "reference",
        help="Verse reference (e.g., 'Bakara 183', '2:183', 'Genesis 1:1')",
    )

    args = parser.parse_args()

    if args.command == "index":
        return cmd_index(args)
    elif args.command == "search":
        return cmd_search(args)

    elif args.command == "search-bible":
        return cmd_search_bible(args)
    elif args.command == "info":
        return cmd_info(args)
    elif args.command == "index-quran":
        return cmd_index_quran(args)
    elif args.command == "index-bible-tr":
        return cmd_index_bible_tr(args)
    elif args.command == "delete-collection":
        return cmd_delete_collection(args)
    elif args.command == "build-graph":
        return cmd_build_graph(args)
    elif args.command == "graph-info":
        return cmd_graph_info(args)
    elif args.command == "cache-info":
        return cmd_cache_info(args)
    elif args.command == "cache-clear":
        return cmd_cache_clear(args)
    elif args.command == "build-semantic-chunks":
        return cmd_build_semantic_chunks(args)
    elif args.command == "search-semantic":
        return cmd_search_semantic(args)
    elif args.command == "analyze-chunks":
        return cmd_analyze_chunks(args)
    elif args.command == "build-bible-semantic-chunks":
        return cmd_build_bible_semantic_chunks(args)
    elif args.command == "search-bible-semantic":
        return cmd_search_bible_semantic(args)
    elif args.command == "setup":
        return cmd_setup(args)
    elif args.command == "ask":
        return cmd_ask(args)
    elif args.command == "ask-bible":
        return cmd_ask_bible(args)
    elif args.command == "compare":
        return cmd_compare(args)
    elif args.command == "keyword-search":
        return cmd_keyword_search(args)
    elif args.command == "bible-keyword-search":
        return cmd_bible_keyword_search(args)
    elif args.command == "verse-lookup":
        return cmd_verse_lookup(args)
    else:
        parser.print_help()
        return 0


def cmd_cache_info(args):
    """Show semantic cache statistics"""
    console.print("\n[bold blue]Semantic Cache Info[/bold blue]\n")

    try:
        from src.semantic_cache import SemanticCache

        cache = SemanticCache(qdrant_url=args.qdrant_url)
        stats = cache.get_stats()

        table = Table(title="Cache Statistics")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green", justify="right")

        table.add_row("Total Entries", str(stats.total_entries))
        table.add_row("Session Hits", str(stats.hits))
        table.add_row("Session Misses", str(stats.misses))
        table.add_row("Hit Rate", f"{stats.hit_rate:.1%}")
        table.add_row("Avg Similarity", f"{stats.avg_similarity:.3f}")
        table.add_row("Oldest Entry", f"{stats.oldest_entry_hours:.1f} hours")

        console.print(table)

        return 0

    except Exception as e:
        console.print(f"[red][ERROR] {e}[/red]")
        return 1


def cmd_cache_clear(args):
    """Clear semantic cache"""
    console.print("\n[bold blue]Clear Semantic Cache[/bold blue]\n")

    try:
        from src.semantic_cache import SemanticCache

        cache = SemanticCache(qdrant_url=args.qdrant_url)
        older_than = getattr(args, "older_than", None)

        if older_than:
            console.print(
                f"[yellow]Clearing entries older than {older_than} hours...[/yellow]"
            )
        else:
            console.print("[yellow]Clearing all cache entries...[/yellow]")

        deleted = cache.clear(older_than_hours=older_than)
        console.print(f"[green][OK][/green] Cleared {deleted} cache entries")

        return 0

    except Exception as e:
        console.print(f"[red][ERROR] {e}[/red]")
        return 1


def cmd_keyword_search(args):
    """Search Quran by morphological root."""
    import asyncio
    import json as json_module
    from src.quran_morphology import QuranMorphologySearch

    console.print(f"\n[bold blue]Keyword Search[/bold blue]: {args.query}\n")

    async def run_search():
        search = QuranMorphologySearch(
            "postgresql+asyncpg://postgres:postgres@localhost:54322/postgres"
        )
        try:
            return await search.search_by_root(
                args.query, page=args.page, per_page=args.limit
            )
        finally:
            await search.close()

    result = asyncio.run(run_search())

    if result.root is None:
        console.print("[yellow]No results found.[/yellow]")
        return 0

    if args.format == "json":
        print(json_module.dumps(result.to_dict(), ensure_ascii=False, indent=2))
        return 0

    # Rich table format
    # 1. Header panel
    console.print(
        Panel(
            f"Root: [bold green]{result.root}[/bold green]  |  "
            f"Source: [cyan]{result.root_source}[/cyan]  |  "
            f"Total Occurrences: [bold]{result.total_occurrences}[/bold]  |  "
            f"Unique Words: [bold]{len(result.unique_words)}[/bold]  |  "
            f"Verses: [bold]{result.total_verses}[/bold]",
            title="Root Info",
        )
    )

    # 2. Derived words
    if result.unique_words:
        words_text = "  ".join(result.unique_words[:30])  # Show max 30
        if len(result.unique_words) > 30:
            words_text += f"  ... (+{len(result.unique_words) - 30} more)"
        console.print(Panel(words_text, title="Derived Words"))

    # 3. Surah distribution table
    if result.surah_distribution:
        dist_table = Table(title="Surah Distribution")
        dist_table.add_column("#", style="dim")
        dist_table.add_column("Surah", style="green")
        dist_table.add_column("Count", style="bold", justify="right")
        for i, sd in enumerate(result.surah_distribution[:20], 1):  # Top 20
            dist_table.add_row(
                str(i), f"[{sd.surah_id}] {sd.surah_name}", str(sd.count)
            )
        if len(result.surah_distribution) > 20:
            dist_table.add_row(
                "...", f"(+{len(result.surah_distribution) - 20} more surahs)", ""
            )
        console.print(dist_table)

    # 4. Verses table
    if result.verses:
        verse_table = Table(title=f"Verses (Page {result.page})")
        verse_table.add_column("#", style="dim", width=4)
        verse_table.add_column("Reference", style="cyan", width=15)
        verse_table.add_column("Arabic Text (Uthmani)", min_width=40)
        verse_table.add_column("Matched Words", style="yellow", width=20)
        for i, v in enumerate(result.verses, 1):
            ref = f"{v.surah_id}:{v.ayah_number}"
            text = v.text_uthmani[:100] + ("..." if len(v.text_uthmani) > 100 else "")
            matched = ", ".join(v.matched_words[:5])
            verse_table.add_row(str(i), ref, text, matched)
        console.print(verse_table)

        # Pagination info
        total_pages = (result.total_verses + result.per_page - 1) // result.per_page
        console.print(
            f"\n[dim]Page {result.page}/{total_pages} ({result.total_verses} total verses)[/dim]"
        )

    return 0


def cmd_bible_keyword_search(args):
    """Search Bible by morphological root."""
    import asyncio
    import json as json_module
    from src.bible_morphology import BibleMorphologySearch

    console.print(f"\n[bold blue]Bible Keyword Search[/bold blue]: {args.query}\n")

    language_filter = None if args.language == "all" else args.language

    async def run_search():
        search = await BibleMorphologySearch.get_instance()
        try:
            return await search.search(
                args.query,
                page=args.page,
                per_page=args.limit,
                language_filter=language_filter,
            )
        finally:
            await search.close()

    result = asyncio.run(run_search())

    if result is None or result.total_occurrences == 0:
        console.print("[yellow]No results found.[/yellow]")
        return 0

    if args.format == "json":
        # Convert dataclass to dict for JSON output
        output = {
            "query": result.query,
            "root": result.root,
            "root_source": result.root_source,
            "strong_number": result.strong_number,
            "total_occurrences": result.total_occurrences,
            "unique_words": result.unique_words,
            "total_verses": result.total_verses,
            "transliteration": result.transliteration,
            "book_distribution": [
                {"book_id": b.book_id, "book_name": b.book_name, "count": b.count}
                for b in result.book_distribution
            ],
            "verses": [
                {
                    "book_name": v.book_name,
                    "chapter": v.chapter,
                    "verse": v.verse,
                    "reference": v.reference,
                    "text_original": v.text_original,
                    "text_english": v.text_english,
                    "matched_words": v.matched_words,
                }
                for v in result.verses
            ],
        }
        print(json_module.dumps(output, ensure_ascii=False, indent=2))
        return 0

    # Rich table format
    # 1. Header panel
    strong_info = (
        f"  |  Strong's: [magenta]{result.strong_number}[/magenta]"
        if result.strong_number
        else ""
    )
    translit_info = (
        f"  |  Transliteration: [italic]{result.transliteration}[/italic]"
        if result.transliteration
        else ""
    )
    console.print(
        Panel(
            f"Root: [bold green]{result.root}[/bold green]  |  "
            f"Source: [cyan]{result.root_source}[/cyan]  |  "
            f"Total Occurrences: [bold]{result.total_occurrences}[/bold]  |  "
            f"Unique Words: [bold]{len(result.unique_words)}[/bold]  |  "
            f"Verses: [bold]{result.total_verses}[/bold]"
            f"{strong_info}{translit_info}",
            title="Root Info",
        )
    )

    # 2. Derived words (Hebrew text, right-aligned)
    if result.unique_words:
        words_text = "  ".join(result.unique_words[:30])
        if len(result.unique_words) > 30:
            words_text += f"  ... (+{len(result.unique_words) - 30} more)"
        console.print(Panel(words_text, title="Derived Words"))

    # 3. Book distribution table
    if result.book_distribution:
        dist_table = Table(title="Book Distribution")
        dist_table.add_column("#", style="dim")
        dist_table.add_column("Book", style="green")
        dist_table.add_column("Count", style="bold", justify="right")
        for i, bd in enumerate(result.book_distribution[:20], 1):
            dist_table.add_row(str(i), bd.book_name, str(bd.count))
        if len(result.book_distribution) > 20:
            dist_table.add_row(
                "...", f"(+{len(result.book_distribution) - 20} more books)", ""
            )
        console.print(dist_table)

    # 4. Verses table
    if result.verses:
        verse_table = Table(title=f"Verses (Page {result.page})")
        verse_table.add_column("#", style="dim", width=4)
        verse_table.add_column("Reference", style="cyan", width=15)
        verse_table.add_column("Hebrew Text", min_width=30)
        verse_table.add_column("English Text", min_width=30)
        verse_table.add_column("Matched", style="yellow", width=15)
        for i, v in enumerate(result.verses, 1):
            hebrew = (v.text_original or "")[:80] + (
                "..." if v.text_original and len(v.text_original) > 80 else ""
            )
            english = (v.text_english or "")[:80] + (
                "..." if v.text_english and len(v.text_english) > 80 else ""
            )
            matched = ", ".join(v.matched_words[:3])
            verse_table.add_row(str(i), v.reference, hebrew, english, matched)
        console.print(verse_table)

        # Pagination info
        if result.per_page > 0:
            total_pages = (result.total_verses + result.per_page - 1) // result.per_page
            console.print(
                f"\n[dim]Page {result.page}/{total_pages} ({result.total_verses} total verses)[/dim]"
            )

    return 0


def cmd_build_graph(args):
    """Build knowledge graph from indexed data"""
    console.print("\n[bold blue]Building Knowledge Graph[/bold blue]\n")

    try:
        from src.graph_rag import GraphRAGBuilder

        builder = GraphRAGBuilder(qdrant_url=args.qdrant_url)

        if args.clear:
            console.print("[yellow]Clearing existing graph...[/yellow]")
            builder.clear_graph()

        console.print(f"[yellow]Building graph from '{args.collection}'...[/yellow]")

        # Get batch_size from args (argparse uses hyphen, we need to use getattr)
        batch_size = getattr(args, "batch_size", 50)
        checkpoint_interval = getattr(args, "checkpoint_interval", 100)

        entities, relationships = builder.build_from_collection(
            collection_name=args.collection,
            limit=args.limit,
            batch_size=batch_size,
            show_progress=True,
            workers=args.workers,
            resume=args.resume,
            checkpoint_interval=checkpoint_interval,
        )

        # Show stats
        stats = builder.get_graph_stats()
        console.print("\n[green][OK][/green] Knowledge graph built!")
        console.print(f"  Nodes: {stats['total_nodes']}")
        console.print(f"  Relationships: {stats['total_relationships']}")

        if stats.get("entity_types"):
            console.print("\n  Entity types:")
            for etype, count in stats["entity_types"].items():
                console.print(f"    - {etype}: {count}")

        return 0

    except ImportError as e:
        console.print(f"[red][ERROR] Neo4j not available: {e}[/red]")
        console.print("[dim]Install with: pip install neo4j[/dim]")
        return 1
    except Exception as e:
        console.print(f"[red][ERROR] {e}[/red]")
        console.print("[dim]Make sure Neo4j is running and NEO4J_PASSWORD is set[/dim]")
        return 1


def cmd_graph_info(args):
    """Show knowledge graph statistics"""
    console.print("\n[bold blue]Knowledge Graph Info[/bold blue]\n")

    try:
        from src.graph_rag import GraphRAGBuilder

        builder = GraphRAGBuilder(qdrant_url=args.qdrant_url)
        stats = builder.get_graph_stats()

        table = Table(title="Graph Statistics")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green", justify="right")

        table.add_row("Total Nodes", str(stats["total_nodes"]))
        table.add_row("Total Relationships", str(stats["total_relationships"]))

        console.print(table)

        if stats.get("entity_types"):
            type_table = Table(title="Entity Types")
            type_table.add_column("Type", style="cyan")
            type_table.add_column("Count", style="green", justify="right")

            for etype, count in stats["entity_types"].items():
                type_table.add_row(etype, str(count))

            console.print(type_table)

        return 0

    except ImportError as e:
        console.print(f"[red][ERROR] Neo4j not available: {e}[/red]")
        return 1
    except Exception as e:
        console.print(f"[red][ERROR] {e}[/red]")
        return 1


def cmd_build_semantic_chunks(args):
    """Build semantic chunks from Quran verses"""
    console.print("\n[bold blue]Building Semantic Chunks[/bold blue]\n")

    threshold_type = getattr(args, "threshold_type", "percentile")

    try:
        # Initialize chunker
        console.print(
            f"[yellow]Initializing chunker (threshold={args.threshold}, type={threshold_type}, max_size={args.max_size})...[/yellow]"
        )
        chunker = SemanticVerseChunker(
            similarity_threshold=args.threshold,
            max_chunk_size=args.max_size,
            respect_surah_boundary=True,
        )

        # Create chunks with specified threshold type
        console.print(
            "[yellow]Creating semantic chunks (this may take a while)...[/yellow]"
        )
        chunks = chunker.create_semantic_chunks(
            show_progress=True, threshold_type=threshold_type
        )

        # Show statistics
        stats = chunker.get_statistics()
        console.print(f"\n[green][OK][/green] Created {len(chunks)} semantic chunks")
        console.print(f"  Total verses: {stats['num_verses']}")
        console.print(
            f"  Avg chunk size: {stats['num_verses'] / len(chunks):.2f} verses"
        )
        console.print(f"  Similarity mean: {stats['similarity_mean']:.4f}")
        console.print(f"  Similarity std: {stats['similarity_std']:.4f}")

        if args.analyze_only:
            # Just save and analyze
            chunker.save_chunks(chunks)
            console.print("\n[yellow]Analyzing first 3 surahs...[/yellow]")
            for surah_id in [1, 2, 3]:
                analyze_surah_chunks(chunks, surah_id)
            return 0

        # Index chunks
        console.print("\n[yellow]Indexing semantic chunks to Qdrant...[/yellow]")
        indexer = SemanticChunkIndexer(qdrant_url=args.qdrant_url)
        indexer.create_collection(recreate=args.recreate)
        count = indexer.index_chunks(chunks, batch_size=50)

        # Save chunks for later use
        chunker.save_chunks(chunks)

        # Show info
        info = indexer.get_collection_info()
        console.print(
            f"\n[green][OK][/green] Successfully indexed {count} semantic chunks!"
        )
        console.print(f"  Collection: {info['name']}")
        console.print(f"  Points: {info['points_count']}")
        console.print(f"  Status: {info['status']}")

        return 0

    except Exception as e:
        console.print(f"[red][ERROR] {e}[/red]")
        import traceback

        traceback.print_exc()
        return 1


def cmd_search_semantic(args):
    """Search using semantic chunks"""
    query = args.query
    limit = args.limit

    console.print("\n[bold magenta]🔍 Semantic Chunk Search[/bold magenta]")
    console.print(f"[dim]Query: {query}[/dim]\n")

    try:
        searcher = SemanticChunkSearcher(qdrant_url=args.qdrant_url)

        if not searcher.collection_exists():
            console.print("[yellow]Semantic chunks collection not found.[/yellow]")
            console.print(
                "[dim]Run 'python main.py build-semantic-chunks' first.[/dim]"
            )
            return 1

        results = searcher.hybrid_search(query, limit=limit)

        if not results:
            console.print("[yellow]No results found.[/yellow]")
            return 0

        # Create results table
        table = Table(
            title=f"Semantic Chunk Results ({len(results)} found)", show_lines=True
        )
        table.add_column("#", style="dim", width=3)
        table.add_column("Reference", style="cyan", width=18)
        table.add_column("Score", style="green", width=8)
        table.add_column("Verses", style="yellow", width=6)
        table.add_column("Combined Translation", style="white")

        for i, result in enumerate(results, 1):
            verse_range = (
                f"{result.start_verse}-{result.end_verse}"
                if result.start_verse != result.end_verse
                else str(result.start_verse)
            )
            ref = f"{result.surah_id}:{verse_range}\n{result.surah_name}"
            score = f"{result.score:.3f}"
            verses = str(result.verse_count)
            translation = result.combined_translation[:180] + (
                "..." if len(result.combined_translation) > 180 else ""
            )
            table.add_row(str(i), ref, score, verses, translation)

        console.print(table)

        # Show detailed first result
        if args.verbose and results:
            first = results[0]
            console.print(
                Panel(
                    f"[bold]{first.surah_name}[/bold] ({first.surah_transliteration})\n"
                    f"Verses {first.start_verse}-{first.end_verse} | {first.surah_type.capitalize()}\n"
                    f"Verse IDs: {', '.join(first.verse_ids)}\n\n"
                    f"[dim]Arabic:[/dim]\n{first.combined_arabic}\n\n"
                    f"[dim]Translation:[/dim]\n{first.combined_translation}",
                    title=f"[green]Top Result ({first.verse_count} verses)[/green]",
                    expand=False,
                )
            )

        return 0

    except Exception as e:
        console.print(f"[red][ERROR] {e}[/red]")
        import traceback

        traceback.print_exc()
        return 1


def cmd_analyze_chunks(args):
    """Analyze semantic chunks for a specific surah"""
    console.print(
        f"\n[bold blue]Analyzing Semantic Chunks - Surah {args.surah}[/bold blue]\n"
    )

    try:
        from pathlib import Path

        chunks_path = Path("data/semantic_chunks.json")

        if not chunks_path.exists():
            console.print("[yellow]Semantic chunks file not found.[/yellow]")
            console.print(
                "[dim]Run 'python main.py build-semantic-chunks' first.[/dim]"
            )
            return 1

        # Load chunks
        chunker = SemanticVerseChunker()
        chunks = chunker.load_chunks(chunks_path)

        # Analyze specified surah
        analyze_surah_chunks(chunks, args.surah)

        return 0

    except Exception as e:
        console.print(f"[red][ERROR] {e}[/red]")
        return 1


def cmd_verse_lookup(args):
    """Look up a specific verse by reference."""
    import asyncio
    from src.verse_parser import parse_verse_reference, ParseError
    from qdrant_client import AsyncQdrantClient
    from qdrant_client.http.models import Filter, FieldCondition, MatchValue

    reference = args.reference
    console.print(f"\n[bold blue]Verse Lookup[/bold blue]: {reference}\n")

    # Parse reference
    result = parse_verse_reference(reference)
    if isinstance(result, ParseError):
        console.print(f"[red]Error: {result.message}[/red]")
        return 1

    # Query Qdrant
    async def fetch_verses():
        client = AsyncQdrantClient(host="localhost", port=6333)
        verses = []

        try:
            if result.source == "quran":
                # Get surah name from SURAH_NAME_MAP
                from src.verse_parser import SURAH_NAME_MAP

                surah_name = None
                for name, info in SURAH_NAME_MAP.items():
                    if info["id"] == result.surah_id:
                        surah_name = name
                        break

                # Fetch each verse
                for verse_id in result.verses:
                    filter_condition = Filter(
                        must=[
                            FieldCondition(
                                key="surah_id", match=MatchValue(value=result.surah_id)
                            ),
                            FieldCondition(
                                key="verse_id", match=MatchValue(value=verse_id)
                            ),
                        ]
                    )

                    points = await client.scroll(
                        collection_name="quran_tr_diyanet",  # Default Diyanet translation
                        scroll_filter=filter_condition,
                        limit=1,
                        with_payload=True,
                        with_vectors=False,
                    )

                    if points[0]:
                        for point in points[0]:
                            payload = point.payload
                            if payload is not None:
                                verses.append(
                                    {
                                        "reference": f"{result.surah_id}:{verse_id}",
                                        "surah_name": surah_name,
                                        "verse_id": verse_id,
                                        "arabic_text": payload.get("arabic_text", ""),
                                        "translation": payload.get("translation", ""),
                                        "source": "quran",
                                    }
                                )

            else:  # Bible
                # Determine collection from testament
                testament_to_collection = {
                    "OT": "bible_ot",
                    "NT": "bible_nt",
                    "Apocrypha": "bible_apocrypha",
                }
                collection_name = testament_to_collection[result.testament]

                # Fetch each verse
                for verse_num in result.verses:
                    filter_condition = Filter(
                        must=[
                            FieldCondition(
                                key="book_id", match=MatchValue(value=result.book_id)
                            ),
                            FieldCondition(
                                key="chapter", match=MatchValue(value=result.chapter)
                            ),
                            FieldCondition(
                                key="verse", match=MatchValue(value=verse_num)
                            ),
                        ]
                    )

                    points = await client.scroll(
                        collection_name=collection_name,
                        scroll_filter=filter_condition,
                        limit=1,
                        with_payload=True,
                        with_vectors=False,
                    )

                    if points[0]:
                        for point in points[0]:
                            payload = point.payload
                            if payload is not None:
                                verses.append(
                                    {
                                        "reference": f"{result.book_name} {result.chapter}:{verse_num}",
                                        "book_name": result.book_name,
                                        "chapter": result.chapter,
                                        "verse": verse_num,
                                        "text": payload.get("text", ""),
                                        "source": result.testament,
                                    }
                                )

        finally:
            await client.close()

        return verses

    try:
        verses = asyncio.run(fetch_verses())

        if not verses:
            console.print("[yellow]No verses found.[/yellow]")
            return 1

        # Display verses
        for verse in verses:
            if verse["source"] == "quran":
                # Quran format: Arabic + Turkish
                console.print(
                    Panel(
                        f"[bold cyan]{verse['surah_name']} ({verse['surah_name']}) {verse['reference']}[/bold cyan]\n\n"
                        f"[dim]Arabic:[/dim]\n{verse['arabic_text']}\n\n"
                        f"[dim]Turkish:[/dim]\n{verse['translation']}",
                        title="[green]Quran[/green]",
                        expand=False,
                    )
                )
            else:
                # Bible format: English text
                testament_names = {
                    "OT": "Old Testament",
                    "NT": "New Testament",
                    "Apocrypha": "Apocrypha",
                }
                testament_display = testament_names.get(
                    verse["source"], verse["source"]
                )
                console.print(
                    Panel(
                        f"[bold cyan]{verse['reference']}[/bold cyan]\n"
                        f"[dim]{testament_display}[/dim]\n\n"
                        f"{verse['text']}",
                        title="[green]Bible[/green]",
                        expand=False,
                    )
                )

        return 0

    except Exception as e:
        console.print(f"[red][ERROR] Failed to fetch verses: {e}[/red]")
        import traceback

        traceback.print_exc()
        return 1


def cmd_setup(args):
    """Redirect to unified setup script"""
    console.print(
        "\n[bold yellow]⚠️  Deprecated: Use unified script instead[/bold yellow]\n"
    )
    console.print("Run the following command for complete setup:")
    console.print("  [cyan]python scripts/setup_all_collections.py[/cyan]\n")
    console.print(
        "This creates all collections (quran_tr, bible_ot, bible_nt, bible_apocrypha)"
    )
    console.print("with testament-split Bible indexing for better search accuracy.\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
