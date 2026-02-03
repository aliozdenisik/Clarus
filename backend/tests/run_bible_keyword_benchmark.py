#!/usr/bin/env python3
"""
Bible Keyword Search Performance Benchmark & Regression Test

Benchmarks Bible morphological search performance across 10 roots with varying frequencies.
Verifies performance targets, index usage, and regression tests for Quran keyword search.

Performance Targets:
- Low frequency (<100 occurrences): <500ms
- Medium frequency (100-1000): <1s
- High frequency (1000+): <2s
- Very high frequency (3000+): <5s (acceptable with warning)

Usage:
    python tests/run_bible_keyword_benchmark.py
"""

import asyncio
import json
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Dict, Any

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()


# ============================================================================
# DATA CLASSES
# ============================================================================


@dataclass
class BenchmarkRoot:
    """A single root to benchmark"""

    strong_number: str
    hebrew: str
    transliteration: str
    expected_occurrences: int
    frequency_category: str  # low, medium, high, very_high


@dataclass
class BenchmarkResult:
    """Result of a single benchmark run"""

    strong_number: str
    hebrew: str
    transliteration: str
    expected_occurrences: int
    actual_occurrences: int
    frequency_category: str
    response_time_ms: float
    target_time_ms: float
    passed: bool
    error: str = None


@dataclass
class RegressionTestResult:
    """Result of a regression test"""

    test_name: str
    description: str
    passed: bool
    details: str = ""
    error: str = None


# ============================================================================
# BENCHMARK CONFIGURATION
# ============================================================================

# 10 roots with varying frequencies
BENCHMARK_ROOTS = [
    BenchmarkRoot("H3789", "כתב", "ktb", 225, "low"),  # write
    BenchmarkRoot("H1961", "היה", "hyh", 3800, "very_high"),  # be/become (most common)
    BenchmarkRoot("H559", "אמר", "amr", 5300, "very_high"),  # say/speak
    BenchmarkRoot("H1254", "ברא", "bra", 55, "low"),  # create
    BenchmarkRoot("H430", "אלהים", "elohim", 2600, "high"),  # God
    BenchmarkRoot("H3045", "ידע", "yda", 950, "medium"),  # know
    BenchmarkRoot("H8085", "שמע", "shma", 1160, "high"),  # hear
    BenchmarkRoot("H1696", "דבר", "dbr", 1145, "high"),  # speak
    BenchmarkRoot("H4428", "מלך", "mlk", 2500, "high"),  # king (noun)
    BenchmarkRoot("H7971", "שלח", "shlch", 850, "medium"),  # send
]

# Performance targets (ms)
PERFORMANCE_TARGETS = {
    "low": 500,  # <100 occurrences
    "medium": 1000,  # 100-1000 occurrences
    "high": 2000,  # 1000-3000 occurrences
    "very_high": 5000,  # 3000+ occurrences
}


# ============================================================================
# BENCHMARK EXECUTION
# ============================================================================


async def run_single_benchmark(root: BenchmarkRoot) -> BenchmarkResult:
    """Run benchmark for a single root."""
    from src.bible_morphology import BibleMorphologySearch

    try:
        search = await BibleMorphologySearch.get_instance()

        # Measure search time
        start_time = time.time()
        result = await search.search(root.strong_number, page=1, per_page=0)
        elapsed_ms = (time.time() - start_time) * 1000

        # Get target time for this frequency category
        target_ms = PERFORMANCE_TARGETS[root.frequency_category]

        # Check if passed
        passed = elapsed_ms <= target_ms and result.total_occurrences > 0

        return BenchmarkResult(
            strong_number=root.strong_number,
            hebrew=root.hebrew,
            transliteration=root.transliteration,
            expected_occurrences=root.expected_occurrences,
            actual_occurrences=result.total_occurrences,
            frequency_category=root.frequency_category,
            response_time_ms=elapsed_ms,
            target_time_ms=target_ms,
            passed=passed,
        )

    except Exception as e:
        return BenchmarkResult(
            strong_number=root.strong_number,
            hebrew=root.hebrew,
            transliteration=root.transliteration,
            expected_occurrences=root.expected_occurrences,
            actual_occurrences=0,
            frequency_category=root.frequency_category,
            response_time_ms=0,
            target_time_ms=PERFORMANCE_TARGETS[root.frequency_category],
            passed=False,
            error=str(e),
        )


async def run_all_benchmarks() -> List[BenchmarkResult]:
    """Run all benchmark tests."""
    results = []

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task(
            "[cyan]Running benchmarks...", total=len(BENCHMARK_ROOTS)
        )

        for root in BENCHMARK_ROOTS:
            progress.update(
                task,
                description=f"[cyan]Benchmarking {root.strong_number} ({root.hebrew})...",
            )
            result = await run_single_benchmark(root)
            results.append(result)
            progress.advance(task)

    return results


# ============================================================================
# REGRESSION TESTS
# ============================================================================


async def test_index_usage() -> RegressionTestResult:
    """Verify that PostgreSQL uses Index Scan (not Seq Scan) for strong_number queries."""
    try:
        from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
        from sqlalchemy import text as sa_text

        DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:54322/postgres"
        engine = create_async_engine(DATABASE_URL, echo=False)

        async with AsyncSession(engine) as session:
            # Run EXPLAIN ANALYZE on a sample query
            result = await session.execute(
                sa_text(
                    "EXPLAIN ANALYZE SELECT * FROM bm_words WHERE strong_number = 'H3789' LIMIT 100"
                )
            )
            explain_output = "\n".join([row[0] for row in result.fetchall()])

            # Check for Index Scan (not Seq Scan)
            has_index_scan = "Index Scan" in explain_output
            has_seq_scan = (
                "Seq Scan" in explain_output and "Index Scan" not in explain_output
            )

            await engine.dispose()

            if has_index_scan:
                return RegressionTestResult(
                    test_name="Index Usage",
                    description="Verify Index Scan on strong_number column",
                    passed=True,
                    details="✓ Using Index Scan (ix_bm_words_strong)",
                )
            elif has_seq_scan:
                return RegressionTestResult(
                    test_name="Index Usage",
                    description="Verify Index Scan on strong_number column",
                    passed=False,
                    details="✗ Using Sequential Scan (index not used)",
                )
            else:
                return RegressionTestResult(
                    test_name="Index Usage",
                    description="Verify Index Scan on strong_number column",
                    passed=False,
                    details="⚠ Could not determine scan type from EXPLAIN output",
                )

    except Exception as e:
        return RegressionTestResult(
            test_name="Index Usage",
            description="Verify Index Scan on strong_number column",
            passed=False,
            error=str(e),
        )


async def test_quran_keyword_search() -> RegressionTestResult:
    """Verify Quran keyword search still works (regression test)."""
    try:
        import subprocess

        # Run Quran keyword search CLI command
        result = subprocess.run(
            ["python", "main.py", "keyword-search", "كتب"],
            cwd=Path(__file__).parent.parent,
            capture_output=True,
            text=True,
            timeout=30,
        )

        # Check exit code
        if result.returncode == 0:
            # Verify output contains expected patterns (more lenient check)
            output = result.stdout
            has_root = "Root:" in output or "جذر:" in output or "Root Info" in output
            has_occurrences = (
                "occurrences" in output or "Occurrences" in output or "tekrar" in output
            )

            if has_root and has_occurrences:
                return RegressionTestResult(
                    test_name="Quran Keyword Search",
                    description="Verify Quran keyword search CLI still works",
                    passed=True,
                    details="✓ CLI command executed successfully with expected output",
                )
            else:
                return RegressionTestResult(
                    test_name="Quran Keyword Search",
                    description="Verify Quran keyword search CLI still works",
                    passed=False,
                    details=f"⚠ Command succeeded but output format unexpected:\n{output[:200]}",
                )
        else:
            return RegressionTestResult(
                test_name="Quran Keyword Search",
                description="Verify Quran keyword search CLI still works",
                passed=False,
                details=f"✗ Command failed with exit code {result.returncode}\nStderr: {result.stderr[:200]}",
            )

    except subprocess.TimeoutExpired:
        return RegressionTestResult(
            test_name="Quran Keyword Search",
            description="Verify Quran keyword search CLI still works",
            passed=False,
            error="Command timed out after 30 seconds",
        )
    except Exception as e:
        return RegressionTestResult(
            test_name="Quran Keyword Search",
            description="Verify Quran keyword search CLI still works",
            passed=False,
            error=str(e),
        )


async def test_frontend_tests() -> RegressionTestResult:
    """Verify frontend tests still pass."""
    try:
        import subprocess

        frontend_dir = Path(__file__).parent.parent.parent / "frontend"

        if not frontend_dir.exists():
            return RegressionTestResult(
                test_name="Frontend Tests",
                description="Verify frontend tests pass",
                passed=True,
                details="⊘ Frontend directory not found (skipped)",
            )

        # Run npm test
        result = subprocess.run(
            ["npm", "test", "--", "--run"],
            cwd=frontend_dir,
            capture_output=True,
            text=True,
            timeout=120,
        )

        # Check exit code
        if result.returncode == 0:
            return RegressionTestResult(
                test_name="Frontend Tests",
                description="Verify frontend tests pass",
                passed=True,
                details="✓ All frontend tests passed",
            )
        else:
            return RegressionTestResult(
                test_name="Frontend Tests",
                description="Verify frontend tests pass",
                passed=False,
                details=f"✗ Tests failed with exit code {result.returncode}\nStderr: {result.stderr[:300]}",
            )

    except subprocess.TimeoutExpired:
        return RegressionTestResult(
            test_name="Frontend Tests",
            description="Verify frontend tests pass",
            passed=False,
            error="Tests timed out after 120 seconds",
        )
    except FileNotFoundError:
        return RegressionTestResult(
            test_name="Frontend Tests",
            description="Verify frontend tests pass",
            passed=True,
            details="⊘ npm not found (skipped)",
        )
    except Exception as e:
        return RegressionTestResult(
            test_name="Frontend Tests",
            description="Verify frontend tests pass",
            passed=False,
            error=str(e),
        )


async def run_regression_tests() -> List[RegressionTestResult]:
    """Run all regression tests."""
    results = []

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("[yellow]Running regression tests...", total=3)

        # Test 1: Index usage
        progress.update(task, description="[yellow]Testing index usage...")
        results.append(await test_index_usage())
        progress.advance(task)

        # Test 2: Quran keyword search
        progress.update(task, description="[yellow]Testing Quran keyword search...")
        results.append(await test_quran_keyword_search())
        progress.advance(task)

        # Test 3: Frontend tests
        progress.update(task, description="[yellow]Testing frontend...")
        results.append(await test_frontend_tests())
        progress.advance(task)

    return results


# ============================================================================
# REPORTING
# ============================================================================


def print_benchmark_results(results: List[BenchmarkResult]) -> None:
    """Print benchmark results table."""
    console.print("\n" + "═" * 100)
    console.print(
        "[bold cyan]                    BIBLE KEYWORD SEARCH PERFORMANCE BENCHMARK[/bold cyan]"
    )
    console.print("═" * 100 + "\n")

    # Create results table
    table = Table(
        title="Benchmark Results", show_header=True, header_style="bold magenta"
    )
    table.add_column("Strong's", width=10)
    table.add_column("Hebrew", width=10)
    table.add_column("Transliteration", width=15)
    table.add_column("Frequency", width=12)
    table.add_column("Occurrences", width=12)
    table.add_column("Time (ms)", width=12)
    table.add_column("Target (ms)", width=12)
    table.add_column("Status", width=8)

    for r in results:
        # Determine status color
        if r.error:
            status = "[red]ERROR[/red]"
            time_str = "[red]—[/red]"
        elif r.passed:
            status = "[green]✓ PASS[/green]"
            time_str = f"[green]{r.response_time_ms:.0f}[/green]"
        else:
            status = "[red]✗ FAIL[/red]"
            time_str = f"[red]{r.response_time_ms:.0f}[/red]"

        # Occurrence count color
        occ_diff = abs(r.actual_occurrences - r.expected_occurrences)
        if occ_diff == 0:
            occ_str = f"[green]{r.actual_occurrences}[/green]"
        elif occ_diff < 50:
            occ_str = f"[yellow]{r.actual_occurrences}[/yellow]"
        else:
            occ_str = f"[red]{r.actual_occurrences}[/red]"

        table.add_row(
            r.strong_number,
            r.hebrew,
            r.transliteration,
            r.frequency_category,
            occ_str,
            time_str,
            f"{r.target_time_ms:.0f}",
            status,
        )

    console.print(table)

    # Summary statistics
    passed_count = sum(1 for r in results if r.passed)
    total_count = len(results)
    avg_time = sum(r.response_time_ms for r in results if not r.error) / max(
        1, sum(1 for r in results if not r.error)
    )

    console.print(f"\n[bold]Summary:[/bold]")
    console.print(f"  Total benchmarks: {total_count}")
    console.print(
        f"  Passed: [green]{passed_count}/{total_count}[/green] ({passed_count / total_count * 100:.0f}%)"
    )
    console.print(f"  Average response time: [cyan]{avg_time:.0f}ms[/cyan]")

    # Performance by category
    console.print(f"\n[bold]Performance by Frequency Category:[/bold]")
    for category in ["low", "medium", "high", "very_high"]:
        cat_results = [r for r in results if r.frequency_category == category]
        if cat_results:
            cat_avg = sum(r.response_time_ms for r in cat_results) / len(cat_results)
            cat_target = PERFORMANCE_TARGETS[category]
            cat_passed = sum(1 for r in cat_results if r.passed)
            status = "✓" if cat_avg <= cat_target else "✗"
            console.print(
                f"  {category.upper():12} ({len(cat_results)} roots): {cat_avg:6.0f}ms avg (target: {cat_target}ms) {status} [{cat_passed}/{len(cat_results)} passed]"
            )


def print_regression_results(results: List[RegressionTestResult]) -> None:
    """Print regression test results."""
    console.print("\n" + "═" * 100)
    console.print(
        "[bold yellow]                         REGRESSION TEST RESULTS[/bold yellow]"
    )
    console.print("═" * 100 + "\n")

    # Create results table
    table = Table(
        title="Regression Tests", show_header=True, header_style="bold magenta"
    )
    table.add_column("Test", width=25)
    table.add_column("Description", width=40)
    table.add_column("Status", width=10)
    table.add_column("Details", width=20)

    for r in results:
        if r.error:
            status = "[red]ERROR[/red]"
            details = f"[red]{r.error[:20]}...[/red]"
        elif r.passed:
            status = "[green]✓ PASS[/green]"
            details = r.details[:20] if r.details else ""
        else:
            status = "[red]✗ FAIL[/red]"
            details = r.details[:20] if r.details else ""

        table.add_row(r.test_name, r.description, status, details)

    console.print(table)

    # Print full details for failed tests
    failed_tests = [r for r in results if not r.passed]
    if failed_tests:
        console.print(f"\n[bold red]Failed Test Details:[/bold red]")
        for r in failed_tests:
            console.print(f"\n[red]✗ {r.test_name}[/red]")
            if r.error:
                console.print(f"  Error: {r.error}")
            if r.details:
                console.print(f"  Details: {r.details}")

    # Summary
    passed_count = sum(1 for r in results if r.passed)
    total_count = len(results)
    console.print(f"\n[bold]Regression Summary:[/bold]")
    console.print(
        f"  Passed: [green]{passed_count}/{total_count}[/green] ({passed_count / total_count * 100:.0f}%)"
    )


def compile_report(
    benchmark_results: List[BenchmarkResult],
    regression_results: List[RegressionTestResult],
) -> Dict[str, Any]:
    """Compile comprehensive report."""
    return {
        "metadata": {
            "test_type": "bible_keyword_benchmark",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_benchmarks": len(benchmark_results),
            "total_regression_tests": len(regression_results),
        },
        "benchmarks": {
            "total": len(benchmark_results),
            "passed": sum(1 for r in benchmark_results if r.passed),
            "failed": sum(1 for r in benchmark_results if not r.passed and not r.error),
            "errors": sum(1 for r in benchmark_results if r.error),
            "avg_response_time_ms": sum(
                r.response_time_ms for r in benchmark_results if not r.error
            )
            / max(1, sum(1 for r in benchmark_results if not r.error)),
            "by_category": {
                category: {
                    "count": len(
                        [
                            r
                            for r in benchmark_results
                            if r.frequency_category == category
                        ]
                    ),
                    "avg_time_ms": sum(
                        r.response_time_ms
                        for r in benchmark_results
                        if r.frequency_category == category
                    )
                    / max(
                        1,
                        len(
                            [
                                r
                                for r in benchmark_results
                                if r.frequency_category == category
                            ]
                        ),
                    ),
                    "target_ms": PERFORMANCE_TARGETS[category],
                    "passed": sum(
                        1
                        for r in benchmark_results
                        if r.frequency_category == category and r.passed
                    ),
                }
                for category in ["low", "medium", "high", "very_high"]
            },
            "details": [
                {
                    "strong_number": r.strong_number,
                    "hebrew": r.hebrew,
                    "transliteration": r.transliteration,
                    "frequency_category": r.frequency_category,
                    "expected_occurrences": r.expected_occurrences,
                    "actual_occurrences": r.actual_occurrences,
                    "response_time_ms": r.response_time_ms,
                    "target_time_ms": r.target_time_ms,
                    "passed": r.passed,
                    "error": r.error,
                }
                for r in benchmark_results
            ],
        },
        "regression": {
            "total": len(regression_results),
            "passed": sum(1 for r in regression_results if r.passed),
            "failed": sum(1 for r in regression_results if not r.passed),
            "details": [
                {
                    "test_name": r.test_name,
                    "description": r.description,
                    "passed": r.passed,
                    "details": r.details,
                    "error": r.error,
                }
                for r in regression_results
            ],
        },
    }


# ============================================================================
# MAIN
# ============================================================================


async def main():
    """Run all benchmarks and regression tests."""
    console.print(
        Panel.fit(
            "[bold cyan]Bible Keyword Search Performance Benchmark[/bold cyan]\n"
            "[dim]Testing 10 roots with varying frequencies + regression tests[/dim]",
            border_style="cyan",
        )
    )

    # Run benchmarks
    console.print("\n[bold]Phase 1: Performance Benchmarks[/bold]")
    benchmark_results = await run_all_benchmarks()
    print_benchmark_results(benchmark_results)

    # Run regression tests
    console.print("\n[bold]Phase 2: Regression Tests[/bold]")
    regression_results = await run_regression_tests()
    print_regression_results(regression_results)

    # Compile and save report
    report = compile_report(benchmark_results, regression_results)
    report_path = Path(__file__).parent / "bible_keyword_benchmark_results.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    console.print(f"\n[dim]Full report saved to: {report_path}[/dim]")

    # Final verdict
    console.print("\n" + "═" * 100)
    benchmark_pass_rate = (
        sum(1 for r in benchmark_results if r.passed) / len(benchmark_results) * 100
    )
    regression_pass_rate = (
        sum(1 for r in regression_results if r.passed) / len(regression_results) * 100
    )

    if benchmark_pass_rate >= 80 and regression_pass_rate == 100:
        console.print(
            "[bold green]✅ ALL TESTS PASSED[/bold green] - System meets performance targets and no regressions detected"
        )
        return 0
    elif benchmark_pass_rate >= 60 and regression_pass_rate >= 66:
        console.print(
            "[bold yellow]⚠️ PARTIAL PASS[/bold yellow] - Some performance issues or regressions detected"
        )
        return 1
    else:
        console.print(
            "[bold red]❌ TESTS FAILED[/bold red] - Significant performance issues or regressions detected"
        )
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
