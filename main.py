#!/usr/bin/env python3
"""
Sacred Texts Hybrid Search CLI

Command-line interface for indexing and searching Quran and Bible translations
using Qdrant vector database with hybrid (semantic + BM25) search.

Usage:
    python main.py index [--recreate]                    # Index Quran
    python main.py search "query"                        # Search Quran
    python main.py index-bible --translation turhadi     # Index Bible
    python main.py search-bible "query"                  # Search Bible
    python main.py info
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
from rich import print as rprint

from src.data_loader import QuranDataLoader
from src.indexer import QuranIndexer, BibleIndexer
from src.search import QuranSearcher, BibleSearcher, print_results
from src.bible_loader import BibleDataLoader

console = Console()


def cmd_index(args):
    """Index Quran data into Qdrant"""
    console.print("\n[bold blue]Quran Hybrid Search Indexer[/bold blue]\n")
    
    # Load data
    console.print("[yellow]Loading Quran data...[/yellow]")
    loader = QuranDataLoader(data_dir=Path("data"))
    loader.download_data()
    
    # Show stats
    stats = loader.get_stats()
    console.print(f"[green][OK][/green] Loaded {stats['total_surahs']} surahs, {stats['total_verses']} verses")
    
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
    
    # Index chunks
    console.print("\n[yellow]Indexing chunks (this may take a while)...[/yellow]")
    count = indexer.index_chunks(chunks, batch_size=args.batch_size)
    
    # Show info
    info = indexer.get_collection_info()
    console.print(f"\n[green][OK][/green] Successfully indexed {count} verses!")
    console.print(f"  Collection: {info['name']}")
    console.print(f"  Points: {info['points_count']}")
    console.print(f"  Status: {info['status']}")
    
    return 0


def cmd_search(args):
    """Search Quran data"""
    query = args.query
    mode = args.mode
    limit = args.limit
    
    # Query enhancement
    if args.enhance:
        console.print("[yellow]Enhancing query with LLM...[/yellow]")
        try:
            from src.query_enhancer import QueryEnhancer
            enhancer = QueryEnhancer()
            enhanced_query = enhancer.expand_query(query)
            console.print(f"[green]Enhanced:[/green] {enhanced_query}")
            query = enhanced_query
        except Exception as e:
            console.print(f"[yellow]Warning: Could not enhance query: {e}[/yellow]")
    
    console.print(f"\n[bold blue]Quran Hybrid Search[/bold blue]")
    console.print(f"[dim]Query: \"{query}\" | Mode: {mode} | Limit: {limit}[/dim]\n")
    
    try:
        searcher = QuranSearcher(qdrant_url=args.qdrant_url)
        # Get more results if reranking
        search_limit = limit * 3 if args.rerank else limit
        results = searcher.search(query, mode=mode, limit=search_limit)
    except Exception as e:
        console.print(f"[red][ERROR] Search error: {e}[/red]")
        return 1
    
    # Reranking
    if args.rerank and results:
        console.print("[yellow]Reranking with Qwen3-Reranker...[/yellow]")
        try:
            from src.reranker import Reranker
            reranker = Reranker()
            results = reranker.rerank(query, results, top_k=limit)
            console.print("[green][OK][/green] Reranking complete\n")
        except Exception as e:
            console.print(f"[yellow]Warning: Reranking failed: {e}[/yellow]")
    
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
        ref = f"{result.surah_id}:{result.verse_id}\n{result.surah_name}"
        score = f"{result.score:.3f}"
        translation = result.translation[:150] + ("..." if len(result.translation) > 150 else "")
        table.add_row(str(i), ref, score, translation)
    
    console.print(table)
    
    # Show detailed first result
    if results and args.verbose:
        first = results[0]
        console.print(Panel(
            f"[bold]{first.surah_name}[/bold] ({first.surah_transliteration})\n"
            f"Ayet {first.verse_id} | {first.surah_type.capitalize()}\n\n"
            f"[dim]Arabic:[/dim]\n{first.arabic_text}\n\n"
            f"[dim]Translation:[/dim]\n{first.translation}",
            title=f"[green]Top Result[/green]",
            expand=False
        ))
    
    return 0


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
        show_quran = args.quran if hasattr(args, 'quran') else False
        show_bible = args.bible if hasattr(args, 'bible') else False
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
            if name == "quran_tr":
                col_type = "Quran"
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
            vectors = getattr(info, 'vectors_count', points)
            status = str(info.status).replace("CollectionStatus.", "")
            
            table.add_row(name, col_type, str(points), str(vectors), status)
            found_any = True
        
        if found_any:
            console.print(table)
            
            # Show summary
            console.print("\n[dim]Tip: Use --quran or --bible to filter collections[/dim]")
        else:
            console.print("[yellow]No matching collections found.[/yellow]")
            
    except Exception as e:
        console.print(f"[red][ERROR] Error: {e}[/red]")
        console.print("[dim]Make sure Qdrant is running: docker run -p 6333:6333 qdrant/qdrant[/dim]")
        return 1
    
    return 0


def cmd_index_bible(args):
    """Index Bible data into Qdrant"""
    translation = args.translation
    console.print(f"\n[bold blue]Bible Hybrid Search Indexer ({translation})[/bold blue]\n")
    
    # Load data
    console.print(f"[yellow]Loading Bible data ({translation})...[/yellow]")
    try:
        loader = BibleDataLoader(translation=translation, data_dir=Path("data"))
        loader.download_data()
    except Exception as e:
        console.print(f"[red][ERROR] Error loading Bible data: {e}[/red]")
        return 1
    
    # Show stats
    stats = loader.get_stats()
    console.print(f"[green][OK][/green] Loaded {stats['total_books']} books, {stats['total_verses']} verses")
    console.print(f"  Translation: {stats['translation_name']}")
    console.print(f"  Old Testament: {stats['old_testament_books']} books")
    console.print(f"  New Testament: {stats['new_testament_books']} books")
    if stats.get('has_apocrypha'):
        console.print(f"  [dim]Includes Apocrypha[/dim]")
    
    # Create chunks
    console.print("\n[yellow]Creating chunks...[/yellow]")
    chunks = loader.create_chunks(show_progress=True)
    console.print(f"[green][OK][/green] Created {len(chunks)} chunks")
    
    # Initialize indexer
    console.print("\n[yellow]Initializing Qdrant...[/yellow]")
    try:
        indexer = BibleIndexer(translation=translation, qdrant_url=args.qdrant_url)
        indexer.create_collection(recreate=args.recreate)
    except Exception as e:
        console.print(f"[red][ERROR] Error connecting to Qdrant: {e}[/red]")
        console.print("\n[yellow]Make sure Qdrant is running:[/yellow]")
        console.print("  docker run -p 6333:6333 qdrant/qdrant")
        return 1
    
    # Index chunks
    console.print("\n[yellow]Indexing chunks (this may take a while)...[/yellow]")
    count = indexer.index_chunks(chunks, batch_size=args.batch_size)
    
    # Show info
    info = indexer.get_collection_info()
    console.print(f"\n[green][OK][/green] Successfully indexed {count} verses!")
    console.print(f"  Collection: {info['name']}")
    console.print(f"  Points: {info['points_count']}")
    console.print(f"  Status: {info['status']}")
    
    return 0


def cmd_search_bible(args):
    """Search Bible data"""
    query = args.query
    translation = args.translation
    mode = args.mode
    limit = args.limit
    
    # Query enhancement
    if args.enhance:
        console.print("[yellow]Enhancing query with LLM...[/yellow]")
        try:
            from src.query_enhancer import QueryEnhancer
            enhancer = QueryEnhancer()
            enhanced_query = enhancer.expand_query(query)
            console.print(f"[green]Enhanced:[/green] {enhanced_query}")
            query = enhanced_query
        except Exception as e:
            console.print(f"[yellow]Warning: Could not enhance query: {e}[/yellow]")
    
    console.print(f"\n[bold blue]Bible Hybrid Search ({translation})[/bold blue]")
    console.print(f"[dim]Query: \"{query}\" | Mode: {mode} | Limit: {limit}[/dim]\n")
    
    try:
        searcher = BibleSearcher(translation=translation, qdrant_url=args.qdrant_url)
        search_limit = limit * 3 if args.rerank else limit
        results = searcher.search(query, mode=mode, limit=search_limit)
    except Exception as e:
        console.print(f"[red][ERROR] Search error: {e}[/red]")
        return 1
    
    # Reranking
    if args.rerank and results:
        console.print("[yellow]Reranking with Qwen3-Reranker...[/yellow]")
        try:
            from src.reranker import Reranker
            reranker = Reranker()
            results = reranker.rerank(query, results, top_k=limit)
            console.print("[green][OK][/green] Reranking complete\n")
        except Exception as e:
            console.print(f"[yellow]Warning: Reranking failed: {e}[/yellow]")
    
    if not results:
        console.print("[yellow]No results found.[/yellow]")
        return 0
    
    # Create results table
    table = Table(title=f"Search Results ({len(results)} found)", show_lines=True)
    table.add_column("#", style="dim", width=3)
    table.add_column("Reference", style="cyan", width=20)
    table.add_column("Score", style="green", width=8)
    table.add_column("Text", style="white")
    
    for i, result in enumerate(results, 1):
        ref = f"{result.book_name} {result.chapter}:{result.verse}\n({result.testament})"
        score = f"{result.score:.3f}"
        text = result.text[:150] + ("..." if len(result.text) > 150 else "")
        table.add_row(str(i), ref, score, text)
    
    console.print(table)
    
    # Show detailed first result
    if results and args.verbose:
        first = results[0]
        console.print(Panel(
            f"[bold]{first.book_name} {first.chapter}:{first.verse}[/bold]\n"
            f"{first.testament} | {first.translation}\n\n"
            f"[dim]Text:[/dim]\n{first.text}",
            title=f"[green]Top Result[/green]",
            expand=False
        ))
    
    return 0


def main():
    parser = argparse.ArgumentParser(
        description="Sacred Texts Hybrid Search - Semantic + BM25 search for Quran and Bible"
    )
    parser.add_argument(
        "--qdrant-url", 
        default="http://localhost:6333",
        help="Qdrant server URL"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Index Quran command
    index_parser = subparsers.add_parser("index", help="Index Quran data")
    index_parser.add_argument(
        "--recreate", 
        action="store_true",
        help="Recreate collection (delete existing)"
    )
    index_parser.add_argument(
        "--batch-size",
        type=int,
        default=100,
        help="Batch size for indexing"
    )
    
    # Search Quran command
    search_parser = subparsers.add_parser("search", help="Search Quran")
    search_parser.add_argument("query", help="Search query")
    search_parser.add_argument(
        "--mode",
        choices=["hybrid", "semantic", "keyword"],
        default="hybrid",
        help="Search mode"
    )
    search_parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="Number of results"
    )
    search_parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Show detailed first result"
    )
    search_parser.add_argument(
        "--rerank",
        action="store_true",
        help="Rerank results with Qwen3-Reranker"
    )
    search_parser.add_argument(
        "--enhance",
        action="store_true",
        help="Enhance query with LLM expansion"
    )
    
    # Index Bible command
    index_bible_parser = subparsers.add_parser("index-bible", help="Index Bible data")
    index_bible_parser.add_argument(
        "--translation",
        default="turhadi",
        choices=["turhadi", "kjva", "kjv"],
        help="Bible translation to index (default: turhadi)"
    )
    index_bible_parser.add_argument(
        "--recreate", 
        action="store_true",
        help="Recreate collection (delete existing)"
    )
    index_bible_parser.add_argument(
        "--batch-size",
        type=int,
        default=100,
        help="Batch size for indexing"
    )
    
    # Search Bible command
    search_bible_parser = subparsers.add_parser("search-bible", help="Search Bible")
    search_bible_parser.add_argument("query", help="Search query")
    search_bible_parser.add_argument(
        "--translation",
        default="turhadi",
        help="Bible translation to search (default: turhadi)"
    )
    search_bible_parser.add_argument(
        "--mode",
        choices=["hybrid", "semantic", "keyword"],
        default="hybrid",
        help="Search mode"
    )
    search_bible_parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="Number of results"
    )
    search_bible_parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Show detailed first result"
    )
    search_bible_parser.add_argument(
        "--rerank",
        action="store_true",
        help="Rerank results with Qwen3-Reranker"
    )
    search_bible_parser.add_argument(
        "--enhance",
        action="store_true",
        help="Enhance query with LLM expansion"
    )
    
    # Info command
    info_parser = subparsers.add_parser("info", help="Show collection info")
    info_parser.add_argument(
        "--quran",
        action="store_true",
        help="Show only Quran collection"
    )
    info_parser.add_argument(
        "--bible",
        action="store_true",
        help="Show only Bible collections"
    )
    
    args = parser.parse_args()
    
    if args.command == "index":
        return cmd_index(args)
    elif args.command == "search":
        return cmd_search(args)
    elif args.command == "index-bible":
        return cmd_index_bible(args)
    elif args.command == "search-bible":
        return cmd_search_bible(args)
    elif args.command == "info":
        return cmd_info(args)
    else:
        parser.print_help()
        return 0


if __name__ == "__main__":
    sys.exit(main())
