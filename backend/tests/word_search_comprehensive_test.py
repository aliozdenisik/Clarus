#!/usr/bin/env python3
"""Comprehensive Word Search API Tests

Tests:
- 20 Hebrew (Hebrew script)
- 20 Greek (Greek script)
- 20 Latin (transliteration)
- 4 Edge cases

Run: python tests/word_search_comprehensive_test.py
"""

import asyncio
import httpx
from dataclasses import dataclass
from typing import Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()
API_BASE = "http://localhost:8000"


@dataclass
class TestCase:
    id: str
    category: str
    query: str
    description: str
    expected_min_occurrences: int = 1
    expected_root_source: Optional[str] = None
    language_filter: Optional[str] = None


# =============================================================================
# TEST DATA
# =============================================================================

HEBREW_TESTS = [
    TestCase("HEB-01", "hebrew", "אלהים", "Elohim (God)", 2600),
    TestCase("HEB-02", "hebrew", "יהוה", "YHWH (LORD)", 1),  # May not be indexed
    TestCase("HEB-03", "hebrew", "דבר", "Dabar (word/speak)", 100),
    TestCase("HEB-04", "hebrew", "שלום", "Shalom (peace)", 50),
    TestCase("HEB-05", "hebrew", "אהבה", "Ahavah (love)", 10),
    TestCase("HEB-06", "hebrew", "צדק", "Tsedeq (righteousness)", 50),
    TestCase("HEB-07", "hebrew", "חכמה", "Chokmah (wisdom)", 50),
    TestCase("HEB-08", "hebrew", "רחם", "Racham (compassion)", 10),
    TestCase("HEB-09", "hebrew", "ברך", "Barak (bless)", 100),
    TestCase("HEB-10", "hebrew", "קדש", "Qadash (holy)", 100),
    TestCase("HEB-11", "hebrew", "משיח", "Mashiach (messiah/anointed)", 10),
    TestCase("HEB-12", "hebrew", "תורה", "Torah (law/instruction)", 100),
    TestCase("HEB-13", "hebrew", "נביא", "Navi (prophet)", 50),
    TestCase("HEB-14", "hebrew", "מלאך", "Malak (angel/messenger)", 50),
    TestCase("HEB-15", "hebrew", "כהן", "Kohen (priest)", 100),
    TestCase("HEB-16", "hebrew", "עולם", "Olam (eternity/world)", 100),
    TestCase("HEB-17", "hebrew", "חסד", "Chesed (lovingkindness)", 100),
    TestCase("HEB-18", "hebrew", "אמת", "Emet (truth)", 50),
    TestCase("HEB-19", "hebrew", "גאל", "Gaal (redeem)", 50),
    TestCase("HEB-20", "hebrew", "ישע", "Yasha (save)", 50),
]

GREEK_TESTS = [
    TestCase("GRK-01", "greek", "λόγος", "Logos (word)", 100),
    TestCase("GRK-02", "greek", "θεός", "Theos (God)", 500),
    TestCase("GRK-03", "greek", "ἀγάπη", "Agape (love)", 50),
    TestCase("GRK-04", "greek", "πίστις", "Pistis (faith)", 100),
    TestCase("GRK-05", "greek", "χάρις", "Charis (grace)", 100),
    TestCase("GRK-06", "greek", "ζωή", "Zoe (life)", 50),
    TestCase("GRK-07", "greek", "εἰρήνη", "Eirene (peace)", 50),
    TestCase("GRK-08", "greek", "ἀλήθεια", "Aletheia (truth)", 50),
    TestCase("GRK-09", "greek", "δόξα", "Doxa (glory)", 50),
    TestCase("GRK-10", "greek", "κύριος", "Kyrios (Lord)", 300),
    TestCase("GRK-11", "greek", "Χριστός", "Christos (Christ)", 200),
    TestCase("GRK-12", "greek", "πνεῦμα", "Pneuma (spirit)", 200),
    TestCase("GRK-13", "greek", "σάρξ", "Sarx (flesh)", 50),
    TestCase("GRK-14", "greek", "ἁμαρτία", "Hamartia (sin)", 50),
    TestCase("GRK-15", "greek", "δικαιοσύνη", "Dikaiosyne (righteousness)", 50),
    TestCase("GRK-16", "greek", "βασιλεία", "Basileia (kingdom)", 100),
    TestCase("GRK-17", "greek", "ἐκκλησία", "Ekklesia (church)", 50),
    TestCase("GRK-18", "greek", "ἀπόστολος", "Apostolos (apostle)", 30),
    TestCase("GRK-19", "greek", "εὐαγγέλιον", "Euangelion (gospel)", 30),
    TestCase("GRK-20", "greek", "σωτηρία", "Soteria (salvation)", 20),
]

LATIN_TESTS = [
    # Hebrew transliterations
    TestCase(
        "LAT-01",
        "latin",
        "elohim",
        "Elohim (Hebrew Latin)",
        100,
        language_filter="hebrew",
    ),
    TestCase(
        "LAT-02",
        "latin",
        "shalom",
        "Shalom (Hebrew Latin)",
        10,
        language_filter="hebrew",
    ),
    TestCase(
        "LAT-03",
        "latin",
        "chesed",
        "Chesed (Hebrew Latin)",
        50,
        language_filter="hebrew",
    ),
    TestCase(
        "LAT-04", "latin", "dabar", "Dabar (Hebrew Latin)", 50, language_filter="hebrew"
    ),
    TestCase(
        "LAT-05", "latin", "torah", "Torah (Hebrew Latin)", 10, language_filter="hebrew"
    ),
    TestCase(
        "LAT-06", "latin", "amen", "Amen (Hebrew Latin)", 1, language_filter="hebrew"
    ),
    TestCase(
        "LAT-07",
        "latin",
        "hallelujah",
        "Hallelujah (Hebrew Latin)",
        1,
        language_filter="hebrew",
    ),
    TestCase(
        "LAT-08",
        "latin",
        "messiah",
        "Messiah (Hebrew Latin)",
        1,
        language_filter="hebrew",
    ),
    TestCase(
        "LAT-09",
        "latin",
        "kohen",
        "Kohen/priest (Hebrew Latin)",
        50,
        language_filter="hebrew",
    ),
    TestCase(
        "LAT-10",
        "latin",
        "navi",
        "Navi/prophet (Hebrew Latin)",
        10,
        language_filter="hebrew",
    ),
    # Greek transliterations
    TestCase("LAT-11", "latin", "logos", "Logos (Greek Latin)", 50),
    TestCase("LAT-12", "latin", "theos", "Theos (Greek Latin)", 100),
    TestCase("LAT-13", "latin", "agape", "Agape (Greek Latin)", 30),
    TestCase("LAT-14", "latin", "pistis", "Pistis (Greek Latin)", 50),
    TestCase("LAT-15", "latin", "charis", "Charis (Greek Latin)", 50),
    TestCase("LAT-16", "latin", "zoe", "Zoe (Greek Latin)", 30),
    TestCase("LAT-17", "latin", "eirene", "Eirene (Greek Latin)", 30),
    TestCase("LAT-18", "latin", "christos", "Christos (Greek Latin)", 100),
    TestCase("LAT-19", "latin", "pneuma", "Pneuma (Greek Latin)", 100),
    TestCase("LAT-20", "latin", "kyrios", "Kyrios (Greek Latin)", 100),
]

EDGE_CASE_TESTS = [
    TestCase("EDGE-01", "edge", "", "Empty query", 0),
    TestCase("EDGE-02", "edge", "H430", "Strong's number direct", 2000),
    TestCase("EDGE-03", "edge", "G2316", "Greek Strong's number", 500),
    TestCase("EDGE-04", "edge", "nonexistentword12345", "Non-existent word", 0),
]

# =============================================================================
# TEST RUNNER
# =============================================================================


async def run_single_test(client: httpx.AsyncClient, test: TestCase) -> dict:
    """Run a single test case and return results."""
    try:
        payload = {"query": test.query, "page": 1, "per_page": 5}
        if test.language_filter:
            payload["language_filter"] = test.language_filter

        response = await client.post(
            f"{API_BASE}/api/keyword-search/bible/", json=payload, timeout=30.0
        )

        if response.status_code != 200:
            return {
                "id": test.id,
                "query": test.query,
                "description": test.description,
                "status": "ERROR",
                "message": f"HTTP {response.status_code}",
                "occurrences": 0,
                "root": None,
                "root_source": None,
            }

        data = response.json()
        occurrences = data.get("total_occurrences", 0)
        root = data.get("root")
        root_source = data.get("root_source", "")

        # Determine pass/fail
        if test.expected_min_occurrences == 0:
            # For edge cases expecting 0, pass if we get 0 or "not_found"
            passed = occurrences == 0 or root_source == "not_found"
        else:
            passed = occurrences >= test.expected_min_occurrences

        return {
            "id": test.id,
            "query": test.query,
            "description": test.description,
            "status": "PASS" if passed else "FAIL",
            "occurrences": occurrences,
            "expected_min": test.expected_min_occurrences,
            "root": root,
            "root_source": root_source,
        }

    except Exception as e:
        return {
            "id": test.id,
            "query": test.query,
            "description": test.description,
            "status": "ERROR",
            "message": str(e),
            "occurrences": 0,
            "root": None,
            "root_source": None,
        }


async def run_test_category(
    client: httpx.AsyncClient, tests: list[TestCase], category_name: str
) -> list[dict]:
    """Run all tests in a category."""
    console.print(f"\n[bold cyan]Running {category_name} tests...[/bold cyan]")
    results = []
    for test in tests:
        result = await run_single_test(client, test)
        results.append(result)

        # Print progress
        status_color = (
            "green"
            if result["status"] == "PASS"
            else "red"
            if result["status"] == "FAIL"
            else "yellow"
        )
        console.print(
            f"  [{status_color}]{result['status']}[/{status_color}] {test.id}: {test.query} → {result.get('occurrences', 0)} occurrences ({result.get('root_source', 'N/A')})"
        )

    return results


def print_summary_table(results: list[dict], title: str):
    """Print a summary table for a category."""
    table = Table(title=title)
    table.add_column("ID", style="cyan")
    table.add_column("Query", style="white")
    table.add_column("Description", style="dim")
    table.add_column("Occurrences", justify="right")
    table.add_column("Expected Min", justify="right")
    table.add_column("Root Source", style="magenta")
    table.add_column("Status", style="bold")

    for r in results:
        status_style = (
            "green"
            if r["status"] == "PASS"
            else "red"
            if r["status"] == "FAIL"
            else "yellow"
        )
        root_source = r.get("root_source") or "N/A"
        table.add_row(
            r["id"],
            r["query"],
            r["description"][:25] + "..."
            if len(r["description"]) > 25
            else r["description"],
            str(r.get("occurrences", "N/A")),
            str(r.get("expected_min", "N/A")),
            root_source[:15] if root_source else "N/A",
            f"[{status_style}]{r['status']}[/{status_style}]",
        )
        table.add_row(
            r["id"],
            r["query"],
            r["description"][:25] + "..."
            if len(r["description"]) > 25
            else r["description"],
            str(r.get("occurrences", "N/A")),
            str(r.get("expected_min", "N/A")),
            r.get("root_source", "N/A")[:15],
            f"[{status_style}]{r['status']}[/{status_style}]",
        )

    console.print(table)


async def main():
    console.print(
        Panel.fit(
            "[bold]Bible Word Search Comprehensive Test Suite[/bold]\n"
            "Testing Hebrew, Greek, Latin transliterations, and Edge Cases",
            border_style="blue",
        )
    )

    async with httpx.AsyncClient() as client:
        # Check API health
        try:
            health = await client.get(f"{API_BASE}/api/health", timeout=5.0)
            if health.status_code != 200:
                console.print("[red]API not healthy![/red]")
                return
            console.print("[green]✓ API is healthy[/green]\n")
        except Exception as e:
            console.print(f"[red]Cannot connect to API: {e}[/red]")
            return

        all_results = []

        # Run Hebrew tests
        hebrew_results = await run_test_category(client, HEBREW_TESTS, "Hebrew (עברית)")
        all_results.extend(hebrew_results)
        print_summary_table(hebrew_results, "Hebrew Test Results")

        # Run Greek tests
        greek_results = await run_test_category(client, GREEK_TESTS, "Greek (Ελληνικά)")
        all_results.extend(greek_results)
        print_summary_table(greek_results, "Greek Test Results")

        # Run Latin tests
        latin_results = await run_test_category(
            client, LATIN_TESTS, "Latin Transliteration"
        )
        all_results.extend(latin_results)
        print_summary_table(latin_results, "Latin Transliteration Test Results")

        # Run Edge Case tests
        edge_results = await run_test_category(client, EDGE_CASE_TESTS, "Edge Cases")
        all_results.extend(edge_results)
        print_summary_table(edge_results, "Edge Case Test Results")

        # Final Summary
        total = len(all_results)
        passed = sum(1 for r in all_results if r["status"] == "PASS")
        failed = sum(1 for r in all_results if r["status"] == "FAIL")
        errors = sum(1 for r in all_results if r["status"] == "ERROR")

        console.print("\n")
        console.print(
            Panel.fit(
                f"[bold]FINAL SUMMARY[/bold]\n\n"
                f"Total Tests: {total}\n"
                f"[green]Passed: {passed}[/green]\n"
                f"[red]Failed: {failed}[/red]\n"
                f"[yellow]Errors: {errors}[/yellow]\n\n"
                f"Pass Rate: [bold]{passed / total * 100:.1f}%[/bold]",
                border_style="green" if failed == 0 and errors == 0 else "red",
            )
        )

        # Print failures for debugging
        failures = [r for r in all_results if r["status"] in ("FAIL", "ERROR")]
        if failures:
            console.print("\n[bold red]Failed/Error Tests:[/bold red]")
            for f in failures:
                expected = f.get("expected_min", 0)
                actual = f.get("occurrences", 0)
                msg = f.get("message", f"Expected >={expected}, got {actual}")
                console.print(f"  • {f['id']}: {f['query']} - {msg}")


if __name__ == "__main__":
    asyncio.run(main())
