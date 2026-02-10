#!/usr/bin/env python3
# ruff: noqa: E402
# Archive test script mutates sys.path before local imports.
"""
Test the Ultimate RAG Pipeline on the Gospels (İnciller) only.
Gospels: Matthew, Mark, Luke, John
"""

import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, str(Path(__file__).parent))

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from qdrant_client import QdrantClient

console = Console()

# Gospel book names
GOSPELS = ["Matthew", "Mark", "Luke", "John"]
GOSPEL_NAMES_TR = {
    "Matthew": "Matta",
    "Mark": "Markos",
    "Luke": "Luka",
    "John": "Yuhanna",
}

# Test queries for Gospels
TEST_QUERIES = [
    # Basic Gospel events
    "İsa'nın doğumu",
    "Müjdecilerin İsa'yı ziyareti",
    "İsa'nın vaftiz edilmesi",
    "İsa'nın çölde denenmesi",
    # İsa'nın mucizeleri
    "Su üzerinde yürüme mucizesi",
    "Körlerin gözlerinin açılması",
    "Ölülerin diriltilmesi",
    "Beş ekmek iki balık mucizesi",
    "Kana düğünündeki mucize",
    "Lazar'ın diriltilmesi",
    # İsa'nın öğretileri
    "Dağdaki vaaz",
    "İyi Samariyeli hikayesi",
    "Müsrif oğul hikayesi",
    "Kayıp koyun benzetmesi",
    "Tanrının Egemenliği",
    # Çarmıh ve diriliş
    "İsa'nın çarmıha gerilmesi",
    "İsa'nın ölümü",
    "İsa'nın dirilişi",
    "İsa'nın göğe yükselişi",
    # Önemli kişiler
    "Petrus'un imanı",
    "Yahuda'nın ihaneti",
    "Meryem Magdalena",
    "Yuhanna vaftizci",
    # Anahtar kavramlar
    "Sevgi emri",
    "Günahların bağışlanması",
    "Sonsuz yaşam",
]


def search_gospels_only(query: str, translation: str = "turhadi", top_k: int = 5):
    """
    Search the Bible using Ultimate RAG and filter results to Gospels only.
    """
    from src.ultimate_rag import UltimateRAG

    rag = UltimateRAG(
        qdrant_url="http://localhost:6333",
        enable_multi_query=True,
        search_mode="semantic",
        final_top_k=top_k * 4,  # Get more results for filtering
        verbose=False,
    )

    # Get results
    results = rag.search_bible(query, translation=translation, top_k=top_k * 4)

    # Filter to Gospels only
    filtered_results = [r for r in results if r.book_name in GOSPELS]

    return filtered_results[:top_k]


def display_results(query: str, results, method: str = "Ultimate RAG"):
    """Display search results in a formatted table."""
    console.print(f"\n[bold cyan]Query:[/bold cyan] {query}")
    console.print(f"[dim]Method: {method}[/dim]")

    if not results:
        console.print("[yellow]No results found in Gospels.[/yellow]")
        return

    table = Table(show_lines=True, expand=False)
    table.add_column("#", style="dim", width=3)
    table.add_column("İncil", style="cyan", width=15)
    table.add_column("Ref", style="green", width=10)
    table.add_column("Score", style="yellow", width=8)
    table.add_column("Text", style="white", max_width=60)

    for i, r in enumerate(results, 1):
        gospel_tr = GOSPEL_NAMES_TR.get(r.book_name, r.book_name)
        ref = f"{r.chapter}:{r.verse}"
        score = f"{r.score:.3f}"
        text = r.text[:80] + "..." if len(r.text) > 80 else r.text
        table.add_row(str(i), gospel_tr, ref, score, text)

    console.print(table)


def run_test_suite():
    """Run full test suite on Gospels."""
    console.print(
        Panel.fit(
            "[bold magenta]🔍 İnciller (Gospels) RAG Test Suite[/bold magenta]\n"
            "[dim]Testing Ultimate RAG Pipeline on Matthew, Mark, Luke, John[/dim]",
            border_style="magenta",
        )
    )

    # Check if Bible collection exists
    try:
        client = QdrantClient(url="http://localhost:6333")
        collections = [c.name for c in client.get_collections().collections]
        if "bible_turhadi" not in collections:
            console.print("[red][ERROR] bible_turhadi collection not found![/red]")
            console.print(
                "[yellow]Please run: python main.py index-bible --translation turhadi[/yellow]"
            )
            return 1
    except Exception as e:
        console.print(f"[red][ERROR] Cannot connect to Qdrant: {e}[/red]")
        return 1

    # Count verses in Gospels
    console.print("\n[bold blue]📊 Gospel Statistics[/bold blue]")

    import json

    data = json.load(open("data/bible_turhadi.json", "r", encoding="utf-8"))
    books = data.get("books", [])

    gospel_stats = {}
    total_verses = 0
    for book in books:
        if book.get("name") in GOSPELS:
            verse_count = sum(
                len(ch.get("verses", [])) for ch in book.get("chapters", [])
            )
            gospel_stats[book.get("name")] = {
                "chapters": len(book.get("chapters", [])),
                "verses": verse_count,
            }
            total_verses += verse_count

    stats_table = Table(title="Gospel Statistics")
    stats_table.add_column("İncil", style="cyan")
    stats_table.add_column("Chapters", style="green", justify="right")
    stats_table.add_column("Verses", style="yellow", justify="right")

    for name in GOSPELS:
        tr_name = GOSPEL_NAMES_TR.get(name, name)
        stats = gospel_stats.get(name, {})
        stats_table.add_row(
            f"{tr_name} ({name})",
            str(stats.get("chapters", 0)),
            str(stats.get("verses", 0)),
        )

    stats_table.add_row("[bold]TOTAL[/bold]", "", f"[bold]{total_verses}[/bold]")
    console.print(stats_table)

    # Run test queries
    console.print(
        f"\n[bold blue]🧪 Running {len(TEST_QUERIES)} Test Queries[/bold blue]"
    )

    successful = 0
    failed = 0

    for i, query in enumerate(TEST_QUERIES, 1):
        console.print(f"\n[dim]Test {i}/{len(TEST_QUERIES)}[/dim]")
        try:
            results = search_gospels_only(query, top_k=3)
            display_results(query, results, method="Ultimate RAG + Gospel Filter")

            if results:
                successful += 1
            else:
                failed += 1
                console.print(f"[yellow]⚠️ No results for: {query}[/yellow]")

        except Exception as e:
            failed += 1
            console.print(f"[red]❌ Error for '{query}': {e}[/red]")
            import traceback

            traceback.print_exc()

    # Summary
    console.print(
        Panel.fit(
            f"[bold green]✅ Successful: {successful}/{len(TEST_QUERIES)}[/bold green]\n"
            f"[bold red]❌ Failed: {failed}/{len(TEST_QUERIES)}[/bold red]\n"
            f"[bold]Success Rate: {successful / len(TEST_QUERIES) * 100:.1f}%[/bold]",
            title="Test Summary",
            border_style="blue",
        )
    )

    return 0 if failed == 0 else 1


def interactive_search():
    """Interactive search mode for Gospels."""
    console.print(
        Panel.fit(
            "[bold magenta]🔍 İnciller Interactive Search[/bold magenta]\n"
            "[dim]Type your query to search in Matthew, Mark, Luke, John[/dim]\n"
            "[dim]Type 'exit' or 'q' to quit[/dim]",
            border_style="magenta",
        )
    )

    while True:
        try:
            query = console.input("\n[bold cyan]Query:[/bold cyan] ").strip()

            if query.lower() in ("exit", "q", "quit"):
                console.print("[dim]Goodbye![/dim]")
                break

            if not query:
                continue

            results = search_gospels_only(query, top_k=5)
            display_results(query, results, method="Ultimate RAG + Gospel Filter")

        except KeyboardInterrupt:
            console.print("\n[dim]Goodbye![/dim]")
            break
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Test RAG on Gospels (İnciller)")
    parser.add_argument(
        "--interactive", "-i", action="store_true", help="Interactive search mode"
    )
    parser.add_argument("--query", "-q", type=str, help="Single query to test")
    parser.add_argument("--limit", "-l", type=int, default=5, help="Number of results")

    args = parser.parse_args()

    if args.query:
        results = search_gospels_only(args.query, top_k=args.limit)
        display_results(args.query, results, method="Ultimate RAG + Gospel Filter")
    elif args.interactive:
        interactive_search()
    else:
        sys.exit(run_test_suite())
