#!/usr/bin/env python3
# ruff: noqa: E402
# Archive test script mutates sys.path before local imports.
"""
Complete Bible Test Suite - İncil ve Eski Ahit Kompleks Arama Testi

Tests the Ultimate RAG Pipeline on the complete Bible including:
- Old Testament (Eski Ahit): Genesis, Exodus, Psalms, Prophets, etc.
- New Testament (Yeni Ahit): Acts, Epistles, Revelation, Gospels

30 complex search phrases with expected book references.
"""

import sys
from pathlib import Path
from typing import List, Dict
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, str(Path(__file__).parent))

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from qdrant_client import QdrantClient

console = Console()


@dataclass
class TestQuery:
    """Represents a test query with expected results"""

    query: str
    expected_books: List[str]  # Expected book names
    testament: str  # "OT" or "NT"
    reference_hint: str  # Human-readable reference hint


# ============================================================================
# ESKİ AHİT (OLD TESTAMENT) - 15 QUERIES
# ============================================================================
OLD_TESTAMENT_QUERIES = [
    TestQuery(
        query="Başlangıçta Tanrı gökleri ve yeri yarattı",
        expected_books=["Genesis"],
        testament="OT",
        reference_hint="Yaratılış 1:1",
    ),
    TestQuery(
        query="Nuh tufanı ve gemi inşası",
        expected_books=["Genesis"],
        testament="OT",
        reference_hint="Yaratılış 6-8",
    ),
    TestQuery(
        query="İbrahim'in imtihanı İshak kurban",
        expected_books=["Genesis"],
        testament="OT",
        reference_hint="Yaratılış 22",
    ),
    TestQuery(
        query="Yakup'un rüyasında merdiven gök",
        expected_books=["Genesis"],
        testament="OT",
        reference_hint="Yaratılış 28:12",
    ),
    TestQuery(
        query="Yusuf kardeşleri tarafından satıldı",
        expected_books=["Genesis"],
        testament="OT",
        reference_hint="Yaratılış 37",
    ),
    TestQuery(
        query="Musa yanan çalı Tanrı konuştu",
        expected_books=["Exodus"],
        testament="OT",
        reference_hint="Çıkış 3",
    ),
    TestQuery(
        query="Mısır'a gönderilen on bela",
        expected_books=["Exodus"],
        testament="OT",
        reference_hint="Çıkış 7-12",
    ),
    TestQuery(
        query="Kızıldeniz'in yarılması",
        expected_books=["Exodus"],
        testament="OT",
        reference_hint="Çıkış 14",
    ),
    TestQuery(
        query="On Emir Sina Dağı",
        expected_books=["Exodus", "Deuteronomy"],
        testament="OT",
        reference_hint="Çıkış 20, Yasa'nın Tekrarı 5",
    ),
    TestQuery(
        query="Rab benim çobanımdır eksiğim olmaz",
        expected_books=["Psalms"],
        testament="OT",
        reference_hint="Mezmur 23:1",
    ),
    TestQuery(
        query="Davut ve Golyat savaşı",
        expected_books=["1 Samuel"],
        testament="OT",
        reference_hint="1 Samuel 17",
    ),
    TestQuery(
        query="Süleyman'ın bilgeliği iki kadın bebek",
        expected_books=["1 Kings"],
        testament="OT",
        reference_hint="1 Krallar 3",
    ),
    TestQuery(
        query="Mesih gelecek bakire gebe kalacak",
        expected_books=["Isaiah"],
        testament="OT",
        reference_hint="Yeşaya 7:14",
    ),
    TestQuery(
        query="Eyüp'ün acıları sabır imtihan",
        expected_books=["Job"],
        testament="OT",
        reference_hint="Eyüp",
    ),
    TestQuery(
        query="Daniel aslan çukurunda",
        expected_books=["Daniel"],
        testament="OT",
        reference_hint="Daniel 6",
    ),
]

# ============================================================================
# YENİ AHİT (NEW TESTAMENT) - 15 QUERIES
# ============================================================================
NEW_TESTAMENT_QUERIES = [
    TestQuery(
        query="Pentikost günü Kutsal Ruh indi",
        expected_books=["Acts"],
        testament="NT",
        reference_hint="Elçilerin İşleri 2",
    ),
    TestQuery(
        query="İstefan ilk şehit taşlandı",
        expected_books=["Acts"],
        testament="NT",
        reference_hint="Elçilerin İşleri 7",
    ),
    TestQuery(
        query="Pavlus Şam yolunda ışık görüntü",
        expected_books=["Acts"],
        testament="NT",
        reference_hint="Elçilerin İşleri 9",
    ),
    TestQuery(
        query="Sevgi sabırlıdır iyilik eder",
        expected_books=["1 Corinthians"],
        testament="NT",
        reference_hint="1 Korintliler 13:4",
    ),
    TestQuery(
        query="Kutsal Ruh'un meyvesi sevgi sevinç",
        expected_books=["Galatians"],
        testament="NT",
        reference_hint="Galatyalılar 5:22",
    ),
    TestQuery(
        query="Tanrı'nın tüm silahlarını kuşanın",
        expected_books=["Ephesians"],
        testament="NT",
        reference_hint="Efesliler 6:11",
    ),
    TestQuery(
        query="Ne ekersen onu biçersin",
        expected_books=["Galatians"],
        testament="NT",
        reference_hint="Galatyalılar 6:7",
    ),
    TestQuery(
        query="Her şeyi yapabilirim Mesih'te güç",
        expected_books=["Philippians"],
        testament="NT",
        reference_hint="Filipililer 4:13",
    ),
    TestQuery(
        query="Mesih'te ne Yahudi ne Grek",
        expected_books=["Galatians"],
        testament="NT",
        reference_hint="Galatyalılar 3:28",
    ),
    TestQuery(
        query="imanla aklanırız kurtuluş lütuf",
        expected_books=["Romans"],
        testament="NT",
        reference_hint="Romalılar 1:17, 3:28",
    ),
    TestQuery(
        query="Bedenimiz Kutsal Ruh'un tapınağı",
        expected_books=["1 Corinthians"],
        testament="NT",
        reference_hint="1 Korintliler 6:19",
    ),
    TestQuery(
        query="Vahiy yedi kiliseye mektup",
        expected_books=["Revelation"],
        testament="NT",
        reference_hint="Vahiy 2-3",
    ),
    TestQuery(
        query="Yeni Yeruşalim gökten inen",
        expected_books=["Revelation"],
        testament="NT",
        reference_hint="Vahiy 21",
    ),
    TestQuery(
        query="Alfa ve Omega başlangıç son",
        expected_books=["Revelation"],
        testament="NT",
        reference_hint="Vahiy 22:13",
    ),
    TestQuery(
        query="İsa yol gerçek yaşam baba",
        expected_books=["John"],
        testament="NT",
        reference_hint="Yuhanna 14:6",
    ),
]

# Combine all queries
ALL_QUERIES = OLD_TESTAMENT_QUERIES + NEW_TESTAMENT_QUERIES


def search_bible(query: str, translation: str = "kjva", top_k: int = 5):
    """
    Search the Bible using Ultimate RAG Pipeline.
    """
    from src.ultimate_rag import UltimateRAG

    rag = UltimateRAG(
        qdrant_url="http://localhost:6333",
        enable_multi_query=True,
        search_mode="semantic",
        final_top_k=top_k,
        verbose=False,
    )

    results = rag.search_bible(query, translation=translation, top_k=top_k)
    return results


def evaluate_query(test_query: TestQuery, results, top_k: int = 5) -> Dict:
    """
    Evaluate a single query result against expected books.
    """
    if not results:
        return {
            "success": False,
            "book_match": False,
            "matched_books": [],
            "result_count": 0,
        }

    result_books = [r.book_name for r in results[:top_k]]
    matched_books = [b for b in result_books if b in test_query.expected_books]

    return {
        "success": len(results) > 0,
        "book_match": len(matched_books) > 0,
        "matched_books": matched_books,
        "result_count": len(results),
        "result_books": result_books,
    }


def display_results(test_query: TestQuery, results, evaluation: Dict):
    """Display search results in a formatted table."""
    # Status indicator
    if evaluation["book_match"]:
        status = "[bold green]✅ PASS[/bold green]"
    elif evaluation["success"]:
        status = "[bold yellow]⚠️ PARTIAL[/bold yellow]"
    else:
        status = "[bold red]❌ FAIL[/bold red]"

    console.print(f"\n{status} [cyan]Query:[/cyan] {test_query.query}")
    console.print(
        f"[dim]Expected: {', '.join(test_query.expected_books)} ({test_query.reference_hint})[/dim]"
    )

    if not results:
        console.print("[yellow]No results found.[/yellow]")
        return

    table = Table(show_lines=True, expand=False)
    table.add_column("#", style="dim", width=3)
    table.add_column("Book", style="cyan", width=15)
    table.add_column("Ref", style="green", width=10)
    table.add_column("Testament", style="magenta", width=8)
    table.add_column("Score", style="yellow", width=8)
    table.add_column("Text", style="white", max_width=50)

    for i, r in enumerate(results[:5], 1):
        ref = f"{r.chapter}:{r.verse}"
        score = f"{r.score:.3f}"
        text = r.text[:60] + "..." if len(r.text) > 60 else r.text
        book_style = (
            "green bold" if r.book_name in test_query.expected_books else "white"
        )
        table.add_row(
            str(i),
            f"[{book_style}]{r.book_name}[/{book_style}]",
            ref,
            r.testament,
            score,
            text,
        )

    console.print(table)


def run_test_suite(translation: str = "turhadi", verbose: bool = True):
    """Run the complete test suite."""
    console.print(
        Panel.fit(
            "[bold magenta]📖 Complete Bible Test Suite[/bold magenta]\n"
            "[dim]Testing Ultimate RAG Pipeline on Old & New Testament[/dim]\n"
            f"[dim]Translation: {translation} | Queries: {len(ALL_QUERIES)}[/dim]",
            border_style="magenta",
        )
    )

    # Check if collection exists
    try:
        client = QdrantClient(url="http://localhost:6333")
        collections = [c.name for c in client.get_collections().collections]
        collection_name = f"bible_{translation}"
        if collection_name not in collections:
            console.print(f"[red][ERROR] {collection_name} collection not found![/red]")
            console.print(
                "[yellow]Please run: python main.py index-bible --translation kjva[/yellow]"
            )
            return 1
    except Exception as e:
        console.print(f"[red][ERROR] Cannot connect to Qdrant: {e}[/red]")
        return 1

    # Run tests
    results_summary = {
        "total": len(ALL_QUERIES),
        "success": 0,
        "book_match": 0,
        "ot_success": 0,
        "nt_success": 0,
        "failed": [],
    }

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Running tests...", total=len(ALL_QUERIES))

        for i, test_query in enumerate(ALL_QUERIES, 1):
            progress.update(
                task,
                description=f"Test {i}/{len(ALL_QUERIES)}: {test_query.query[:30]}...",
            )

            try:
                results = search_bible(
                    test_query.query, translation=translation, top_k=5
                )
                evaluation = evaluate_query(test_query, results)

                if verbose:
                    display_results(test_query, results, evaluation)

                if evaluation["success"]:
                    results_summary["success"] += 1
                    if test_query.testament == "OT":
                        results_summary["ot_success"] += 1
                    else:
                        results_summary["nt_success"] += 1

                if evaluation["book_match"]:
                    results_summary["book_match"] += 1
                else:
                    results_summary["failed"].append(
                        {
                            "query": test_query.query,
                            "expected": test_query.expected_books,
                            "got": evaluation.get("result_books", []),
                        }
                    )

            except Exception as e:
                console.print(f"[red]Error testing '{test_query.query}': {e}[/red]")
                results_summary["failed"].append(
                    {"query": test_query.query, "error": str(e)}
                )

            progress.advance(task)

    # Summary
    console.print("\n")
    summary_table = Table(
        title="📊 Test Results Summary", show_header=True, header_style="bold cyan"
    )
    summary_table.add_column("Metric", style="white")
    summary_table.add_column("Value", style="green", justify="right")
    summary_table.add_column("Percentage", style="yellow", justify="right")

    total = results_summary["total"]
    summary_table.add_row("Total Queries", str(total), "100%")
    summary_table.add_row(
        "Queries with Results",
        str(results_summary["success"]),
        f"{results_summary['success'] / total * 100:.1f}%",
    )
    summary_table.add_row(
        "Book Match (Accuracy)",
        str(results_summary["book_match"]),
        f"{results_summary['book_match'] / total * 100:.1f}%",
    )
    summary_table.add_row(
        "Old Testament Success",
        str(results_summary["ot_success"]),
        f"{results_summary['ot_success'] / 15 * 100:.1f}%",
    )
    summary_table.add_row(
        "New Testament Success",
        str(results_summary["nt_success"]),
        f"{results_summary['nt_success'] / 15 * 100:.1f}%",
    )

    console.print(summary_table)

    # Failed queries
    if results_summary["failed"] and verbose:
        console.print("\n[bold red]Failed/Partial Matches:[/bold red]")
        for fail in results_summary["failed"][:5]:
            if "error" in fail:
                console.print(f"  • {fail['query']}: [red]{fail['error']}[/red]")
            else:
                console.print(f"  • {fail['query']}")
                console.print(
                    f"    Expected: {fail['expected']}, Got: {fail['got'][:3]}"
                )

    return 0 if results_summary["book_match"] >= total * 0.7 else 1


def interactive_search():
    """Interactive search mode."""
    console.print(
        Panel.fit(
            "[bold magenta]📖 Bible Interactive Search[/bold magenta]\n"
            "[dim]Type your query to search in the complete Bible[/dim]\n"
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

            results = search_bible(query, top_k=5)

            if not results:
                console.print("[yellow]No results found.[/yellow]")
                continue

            table = Table(show_lines=True, expand=False)
            table.add_column("#", style="dim", width=3)
            table.add_column("Book", style="cyan", width=15)
            table.add_column("Ref", style="green", width=10)
            table.add_column("Testament", style="magenta", width=8)
            table.add_column("Score", style="yellow", width=8)
            table.add_column("Text", style="white", max_width=50)

            for i, r in enumerate(results, 1):
                ref = f"{r.chapter}:{r.verse}"
                score = f"{r.score:.3f}"
                text = r.text[:60] + "..." if len(r.text) > 60 else r.text
                table.add_row(str(i), r.book_name, ref, r.testament, score, text)

            console.print(table)

        except KeyboardInterrupt:
            console.print("\n[dim]Goodbye![/dim]")
            break
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Complete Bible Test Suite")
    parser.add_argument(
        "--interactive", "-i", action="store_true", help="Interactive search mode"
    )
    parser.add_argument("--query", "-q", type=str, help="Single query to test")
    parser.add_argument("--limit", "-l", type=int, default=5, help="Number of results")
    parser.add_argument(
        "--translation", "-t", type=str, default="turhadi", help="Bible translation"
    )
    parser.add_argument("--quiet", action="store_true", help="Only show summary")

    args = parser.parse_args()

    if args.query:
        results = search_bible(
            args.query, translation=args.translation, top_k=args.limit
        )
        if results:
            for i, r in enumerate(results, 1):
                console.print(
                    f"[cyan]{i}.[/cyan] [{r.testament}] {r.book_name} {r.chapter}:{r.verse} - {r.text[:80]}..."
                )
        else:
            console.print("[yellow]No results found.[/yellow]")
    elif args.interactive:
        interactive_search()
    else:
        sys.exit(run_test_suite(translation=args.translation, verbose=not args.quiet))
