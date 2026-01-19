#!/usr/bin/env python3
"""
RAG Retrieval Accuracy Test Suite

Tests the Ultimate RAG Pipeline against test_data.json with 35 comprehensive queries.
Measures precision, recall, and hallucination detection.

Usage:
    python tests/run_retrieval_accuracy_test.py
"""

import json
import sys
import time
import re
from pathlib import Path
from dataclasses import dataclass
from typing import List, Dict, Set, Tuple, Any
from dotenv import load_dotenv

# Load environment variables first
load_dotenv()

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel

console = Console()


@dataclass
class TestCase:
    """Single test case from test_data.json"""
    id: str
    source: str
    difficulty: str
    question: str
    expected_verses: List[str]


@dataclass
class TestResult:
    """Result of a single test execution"""
    test_id: str
    source: str
    difficulty: str
    question: str
    expected_verses: List[str]
    retrieved_verses: List[str]
    precision: float
    recall: float
    f1_score: float
    is_hallucination_test: bool
    hallucination_passed: bool
    elapsed_time: float
    error: str = None


def parse_verse_reference(ref: str, source: str) -> Set[str]:
    """
    Parse a verse reference into a set of individual verse identifiers.
    
    Examples:
        - "2:255" -> {"2:255"}
        - "1:1-7" -> {"1:1", "1:2", "1:3", "1:4", "1:5", "1:6", "1:7"}
        - "John 3:16" -> {"john 3:16"}
        - "Luke 15:11-32" -> {"luke 15:11", "luke 15:12", ..., "luke 15:32"}
    """
    verses = set()
    ref = ref.strip()
    
    if source == "quran":
        # Format: surah:verse or surah:start-end
        match = re.match(r'(\d+):(\d+)(?:-(\d+))?', ref)
        if match:
            surah = match.group(1)
            start_verse = int(match.group(2))
            end_verse = int(match.group(3)) if match.group(3) else start_verse
            for v in range(start_verse, end_verse + 1):
                verses.add(f"{surah}:{v}")
    else:
        # Bible format: "Book Chapter:Verse" or "Book Chapter:Start-End"
        match = re.match(r'(.+?)\s+(\d+):(\d+)(?:-(\d+))?', ref)
        if match:
            book = match.group(1).lower()
            chapter = match.group(2)
            start_verse = int(match.group(3))
            end_verse = int(match.group(4)) if match.group(4) else start_verse
            for v in range(start_verse, end_verse + 1):
                verses.add(f"{book} {chapter}:{v}")
    
    return verses


def expand_expected_verses(expected: List[str], source: str) -> Set[str]:
    """Expand expected verse references to individual verses."""
    all_verses = set()
    for ref in expected:
        all_verses.update(parse_verse_reference(ref, source))
    return all_verses


def extract_verse_from_result(result, source: str) -> str:
    """Extract verse reference from a search result."""
    if source == "quran":
        surah_id = getattr(result, 'surah_id', None)
        verse_id = getattr(result, 'verse_id', None)
        
        # Handle semantic chunks
        if verse_id is None:
            start_verse = getattr(result, 'start_verse', None)
            if start_verse:
                verse_id = start_verse
        
        # Fallback to payload
        if surah_id is None and hasattr(result, 'payload'):
            payload = result.payload or {}
            surah_id = payload.get('surah_id')
            verse_id = payload.get('verse_id') or payload.get('start_verse')
        
        if surah_id and verse_id:
            return f"{surah_id}:{verse_id}"
    else:
        book_name = getattr(result, 'book_name', None)
        chapter = getattr(result, 'chapter', None) or getattr(result, 'chapter_number', None)
        verse = getattr(result, 'verse', None) or getattr(result, 'verse_number', None)
        
        # Handle semantic chunks
        if verse is None:
            verse = getattr(result, 'start_verse', None)
        
        # Fallback to payload
        if book_name is None and hasattr(result, 'payload'):
            payload = result.payload or {}
            book_name = payload.get('book_name')
            chapter = payload.get('chapter') or payload.get('chapter_number')
            verse = payload.get('verse') or payload.get('verse_number') or payload.get('start_verse')
        
        if book_name and chapter and verse:
            return f"{book_name.lower()} {chapter}:{verse}"
    
    return None


def calculate_metrics(expected: Set[str], retrieved: Set[str]) -> Tuple[float, float, float]:
    """Calculate precision, recall, and F1 score."""
    if not retrieved:
        return (1.0, 0.0, 0.0) if expected else (1.0, 1.0, 1.0)
    
    if not expected:
        # Hallucination test
        return (1.0, 1.0, 1.0) if not retrieved else (0.0, 1.0, 0.0)
    
    # Find matches (partial matching for verse ranges)
    matches = set()
    for exp in expected:
        for ret in retrieved:
            # Check if retrieved verse is within expected range
            if exp == ret:
                matches.add(exp)
                break
            # Check surah/book match for partial credit
            exp_parts = exp.split(':')[0] if ':' in exp else exp.split()[0]
            ret_parts = ret.split(':')[0] if ':' in ret else ret.split()[0]
            if exp_parts == ret_parts:
                matches.add(exp)
                break
    
    precision = len(matches) / len(retrieved) if retrieved else 0.0
    recall = len(matches) / len(expected) if expected else 1.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
    
    return precision, recall, f1


def run_single_test(rag, test: TestCase) -> TestResult:
    """Execute a single test case."""
    start_time = time.time()
    retrieved_verses = []
    error = None
    
    try:
        # Run search based on source
        if test.source == "quran":
            results = rag.search_quran(test.question, top_k=10)
        else:
            results = rag.search_bible(test.question, translation="kjva", top_k=10)
        
        # Extract verse references from results
        for res in results:
            verse_ref = extract_verse_from_result(res, test.source)
            if verse_ref:
                retrieved_verses.append(verse_ref)
    
    except Exception as e:
        error = str(e)
    
    elapsed = time.time() - start_time
    
    # Expand expected verses for comparison
    expected_expanded = expand_expected_verses(test.expected_verses, test.source)
    retrieved_set = set(retrieved_verses)
    
    # Calculate metrics
    precision, recall, f1 = calculate_metrics(expected_expanded, retrieved_set)
    
    # Hallucination test check
    is_hallucination = len(test.expected_verses) == 0
    hallucination_passed = is_hallucination and len(retrieved_verses) == 0
    
    # For hallucination tests, if system returns results, precision should be 0
    if is_hallucination and retrieved_verses:
        precision = 0.0
        f1 = 0.0
    
    return TestResult(
        test_id=test.id,
        source=test.source,
        difficulty=test.difficulty,
        question=test.question,
        expected_verses=test.expected_verses,
        retrieved_verses=retrieved_verses[:5],  # Top 5 only
        precision=precision,
        recall=recall,
        f1_score=f1,
        is_hallucination_test=is_hallucination,
        hallucination_passed=hallucination_passed if is_hallucination else True,
        elapsed_time=elapsed,
        error=error
    )


def run_all_tests(test_data_path: str) -> Dict[str, Any]:
    """Run all tests and return comprehensive results."""
    from src.ultimate_rag import UltimateRAG
    
    console.print(Panel.fit(
        "[bold cyan]RAG Retrieval Accuracy Test Suite[/bold cyan]\n"
        "[dim]Testing complete pipeline with 35 questions[/dim]",
        border_style="cyan"
    ))
    
    # Load test data
    with open(test_data_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    tests = [
        TestCase(
            id=t['id'],
            source=t['source'],
            difficulty=t['difficulty'],
            question=t['question'],
            expected_verses=t['expected_verses']
        )
        for t in data['tests']
    ]
    
    console.print(f"\n[dim]Loaded {len(tests)} test cases[/dim]")
    console.print("[dim]Initializing Ultimate RAG Pipeline...[/dim]\n")
    
    # Initialize RAG
    rag = UltimateRAG(verbose=False)
    
    results: List[TestResult] = []
    
    console.print("=" * 70)
    console.print("[bold]STEP-BY-STEP TEST EXECUTION[/bold]")
    console.print("=" * 70 + "\n")
    
    for i, test in enumerate(tests, 1):
        # Print test header
        console.print(f"[bold cyan]━━━ {test.id} ({i}/{len(tests)}) ━━━[/bold cyan]")
        console.print(f"[dim]Source:[/dim] {test.source.upper()} | [dim]Difficulty:[/dim] {test.difficulty}")
        console.print(f"[dim]Question:[/dim] {test.question[:80]}...")
        console.print(f"[dim]Expected:[/dim] {test.expected_verses if test.expected_verses else '[HALLUCINATION TEST]'}")
        
        # Run test
        result = run_single_test(rag, test)
        results.append(result)
        
        # Print result
        if result.error:
            console.print(f"[red]❌ ERROR: {result.error}[/red]")
        elif result.is_hallucination_test:
            if result.hallucination_passed:
                console.print(f"[green]✅ PASSED[/green] - System correctly returned no results")
            else:
                console.print(f"[red]❌ FAILED[/red] - System hallucinated: {result.retrieved_verses[:3]}")
        else:
            status = "✅" if result.recall > 0.5 else "⚠️" if result.recall > 0 else "❌"
            console.print(f"[dim]Retrieved:[/dim] {result.retrieved_verses[:5]}")
            console.print(f"{status} P={result.precision*100:.0f}% R={result.recall*100:.0f}% F1={result.f1_score*100:.0f}% ({result.elapsed_time:.2f}s)")
        
        console.print()
    
    return compile_report(results, data['metadata'])


def compile_report(results: List[TestResult], metadata: Dict) -> Dict[str, Any]:
    """Compile comprehensive test report."""
    
    # Separate by source
    quran_results = [r for r in results if r.source == "quran"]
    bible_results = [r for r in results if r.source == "bible"]
    hallucination_results = [r for r in results if r.is_hallucination_test]
    normal_results = [r for r in results if not r.is_hallucination_test]
    
    # Calculate aggregate metrics
    def avg(values):
        return sum(values) / len(values) if values else 0.0
    
    def calc_stats(res_list):
        if not res_list:
            return {"precision": 0, "recall": 0, "f1": 0, "count": 0}
        return {
            "precision": avg([r.precision for r in res_list]),
            "recall": avg([r.recall for r in res_list]),
            "f1": avg([r.f1_score for r in res_list]),
            "count": len(res_list)
        }
    
    report = {
        "metadata": metadata,
        "summary": {
            "total_tests": len(results),
            "total_time": sum(r.elapsed_time for r in results),
            "avg_time_per_query": avg([r.elapsed_time for r in results]),
            "errors": sum(1 for r in results if r.error)
        },
        "overall": calc_stats(normal_results),
        "by_source": {
            "quran": calc_stats([r for r in quran_results if not r.is_hallucination_test]),
            "bible": calc_stats([r for r in bible_results if not r.is_hallucination_test])
        },
        "by_difficulty": {
            "easy": calc_stats([r for r in normal_results if r.difficulty == "easy"]),
            "medium": calc_stats([r for r in normal_results if r.difficulty == "medium"]),
            "hard": calc_stats([r for r in normal_results if r.difficulty == "hard"])
        },
        "hallucination": {
            "total": len(hallucination_results),
            "passed": sum(1 for r in hallucination_results if r.hallucination_passed),
            "pass_rate": avg([1.0 if r.hallucination_passed else 0.0 for r in hallucination_results])
        },
        "details": [
            {
                "id": r.test_id,
                "source": r.source,
                "difficulty": r.difficulty,
                "question": r.question[:50] + "...",
                "expected": r.expected_verses,
                "retrieved": r.retrieved_verses,
                "precision": r.precision,
                "recall": r.recall,
                "f1": r.f1_score,
                "time": r.elapsed_time,
                "hallucination_test": r.is_hallucination_test,
                "hallucination_passed": r.hallucination_passed,
                "error": r.error
            }
            for r in results
        ]
    }
    
    # Print report
    print_report(report)
    
    return report


def print_report(report: Dict):
    """Print formatted report to console."""
    
    console.print("\n" + "═" * 70)
    console.print("[bold cyan]                    TEST RESULTS SUMMARY[/bold cyan]")
    console.print("═" * 70 + "\n")
    
    # Overall metrics
    overall = report["overall"]
    console.print(f"[bold]Overall Metrics (Normal Tests):[/bold]")
    console.print(f"  Precision: [green]{overall['precision']*100:.1f}%[/green]")
    console.print(f"  Recall:    [green]{overall['recall']*100:.1f}%[/green]")
    console.print(f"  F1 Score:  [green]{overall['f1']*100:.1f}%[/green]")
    console.print()
    
    # By source table
    source_table = Table(title="Performance by Source", show_header=True, header_style="bold magenta")
    source_table.add_column("Source", width=10)
    source_table.add_column("Count", width=8)
    source_table.add_column("Precision", width=12)
    source_table.add_column("Recall", width=12)
    source_table.add_column("F1", width=12)
    
    for source, stats in report["by_source"].items():
        source_table.add_row(
            source.upper(),
            str(stats["count"]),
            f"{stats['precision']*100:.1f}%",
            f"{stats['recall']*100:.1f}%",
            f"{stats['f1']*100:.1f}%"
        )
    console.print(source_table)
    console.print()
    
    # By difficulty table
    diff_table = Table(title="Performance by Difficulty", show_header=True, header_style="bold magenta")
    diff_table.add_column("Difficulty", width=10)
    diff_table.add_column("Count", width=8)
    diff_table.add_column("Precision", width=12)
    diff_table.add_column("Recall", width=12)
    diff_table.add_column("F1", width=12)
    
    for diff, stats in report["by_difficulty"].items():
        diff_table.add_row(
            diff.upper(),
            str(stats["count"]),
            f"{stats['precision']*100:.1f}%",
            f"{stats['recall']*100:.1f}%",
            f"{stats['f1']*100:.1f}%"
        )
    console.print(diff_table)
    console.print()
    
    # Hallucination tests
    hall = report["hallucination"]
    console.print(f"[bold]Hallucination Detection:[/bold]")
    console.print(f"  Tests: {hall['total']}")
    console.print(f"  Passed: [green]{hall['passed']}/{hall['total']}[/green] ({hall['pass_rate']*100:.0f}%)")
    console.print()
    
    # Detailed results table
    detail_table = Table(title="Detailed Results", show_header=True, header_style="bold magenta")
    detail_table.add_column("#", width=5)
    detail_table.add_column("Source", width=6)
    detail_table.add_column("Diff", width=6)
    detail_table.add_column("Question", width=25)
    detail_table.add_column("Expected", width=15)
    detail_table.add_column("Retrieved", width=15)
    detail_table.add_column("P/R/F1", width=12)
    
    for d in report["details"]:
        status = "✅" if d["recall"] > 0.5 else "❌"
        if d["hallucination_test"]:
            status = "✅" if d["hallucination_passed"] else "⚠️"
        
        detail_table.add_row(
            d["id"],
            d["source"][:5].upper(),
            d["difficulty"][:4],
            d["question"][:24],
            ", ".join(d["expected"][:2])[:14] or "[NONE]",
            ", ".join(d["retrieved"][:2])[:14] or "[empty]",
            f"{status} {d['precision']*100:.0f}/{d['recall']*100:.0f}/{d['f1']*100:.0f}"
        )
    
    console.print(detail_table)
    
    # Summary stats
    summary = report["summary"]
    console.print("\n" + "═" * 70)
    console.print(f"[bold]Total Tests:[/bold] {summary['total_tests']}")
    console.print(f"[bold]Total Time:[/bold] {summary['total_time']:.1f}s")
    console.print(f"[bold]Avg Time/Query:[/bold] {summary['avg_time_per_query']:.2f}s")
    console.print(f"[bold]Errors:[/bold] {summary['errors']}")
    
    # Final verdict
    overall_f1 = report["overall"]["f1"]
    if overall_f1 >= 0.8:
        console.print("\n[bold green]✅ EXCELLENT: System performs very well![/bold green]")
    elif overall_f1 >= 0.6:
        console.print("\n[bold yellow]⚠️ GOOD: System performs reasonably well[/bold yellow]")
    elif overall_f1 >= 0.4:
        console.print("\n[bold orange3]⚠️ FAIR: System needs improvement[/bold orange3]")
    else:
        console.print("\n[bold red]❌ POOR: System needs significant improvement[/bold red]")


if __name__ == "__main__":
    test_data_path = Path(__file__).parent / "test_data.json"
    
    if not test_data_path.exists():
        console.print(f"[red]Error: {test_data_path} not found[/red]")
        sys.exit(1)
    
    report = run_all_tests(str(test_data_path))
    
    # Save report to JSON
    report_path = Path(__file__).parent / "test_results.json"
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    console.print(f"\n[dim]Report saved to: {report_path}[/dim]")
