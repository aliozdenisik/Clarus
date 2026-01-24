#!/usr/bin/env python3
"""
RAG Retrieval Accuracy Test Suite - End-to-End with Stage Logging

Tests the Ultimate RAG Pipeline with comprehensive stage-by-stage logging.
Each question goes through all pipeline stages with timing:
1. Query Enhancement (LLM expansion)
2. Multi-Query Generation
3. Search (RRF merge from multiple queries)
4. Reranking (Cross-encoder)

Measures precision, recall, hallucination detection, and per-stage timing.

Usage:
    python tests/run_retrieval_accuracy_test.py
"""

import json
import sys
import time
import re
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Dict, Set, Tuple, Any, Optional
from dotenv import load_dotenv

# Load environment variables first
load_dotenv()

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()


# ============================================================================
# DATA CLASSES
# ============================================================================

@dataclass
class StageLog:
    """Log for a single pipeline stage"""
    stage_name: str
    stage_number: int
    input_data: Any
    output_data: Any
    duration_ms: float
    metadata: Dict[str, Any] = field(default_factory=dict)


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
    """Result of a single test execution with stage logs"""
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
    # Stage logs
    stages: List[StageLog] = field(default_factory=list)
    # Error tracking
    error: str = None


# ============================================================================
# VERSE PARSING UTILITIES
# ============================================================================

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
        # Also handle chapter-only (e.g., "1 Samuel 17" means entire chapter)
        match = re.match(r'(.+?)\s+(\d+)(?::(\d+))?(?:-(\d+))?', ref)
        if match:
            book = match.group(1).lower()
            chapter = match.group(2)
            start_verse = int(match.group(3)) if match.group(3) else 1
            end_verse = int(match.group(4)) if match.group(4) else start_verse
            
            # If no verse specified, treat as chapter reference
            if match.group(3) is None:
                # Chapter reference - add chapter marker
                verses.add(f"{book} {chapter}:chapter")
            else:
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


# ============================================================================
# RAG PIPELINE WITH STAGE LOGGING
# ============================================================================

class RAGWithStageLogging:
    """Wrapper around UltimateRAG that captures stage details"""
    
    def __init__(self):
        from src.ultimate_rag import UltimateRAG
        self.rag = UltimateRAG(verbose=False)
        
    def run_with_logging(self, question: str, source: str) -> Tuple[List, List[StageLog]]:
        """
        Run RAG pipeline and capture each stage.
        
        Returns:
            Tuple of (final_results, stage_logs)
        """
        stages = []
        
        # Determine corpus for enhancer
        corpus = "quran" if source == "quran" else "bible"
        rag_source = "quran_tr" if source == "quran" else "bible_kjva"
        
        # =================================================================
        # STAGE 1: Query Enhancement
        # =================================================================
        stage1_start = time.time()
        try:
            enhanced_query = self.rag.enhancer.expand_query(question, corpus=corpus)
        except Exception as e:
            enhanced_query = question
            
        stage1_duration = (time.time() - stage1_start) * 1000
        
        stages.append(StageLog(
            stage_name="Query Enhancement",
            stage_number=1,
            input_data=question,
            output_data=enhanced_query,
            duration_ms=stage1_duration,
            metadata={"corpus": corpus}
        ))
        
        # =================================================================
        # STAGE 2: Multi-Query Generation
        # =================================================================
        stage2_start = time.time()
        queries = [question, enhanced_query]
        
        try:
            multi_queries = self.rag.enhancer.generate_multi_query(
                enhanced_query, n=3, corpus=corpus
            )
            queries.extend(multi_queries)
        except Exception as e:
            pass
        
        # Deduplicate
        seen = set()
        unique_queries = []
        for q in queries:
            q_lower = q.lower().strip()
            if q_lower not in seen:
                seen.add(q_lower)
                unique_queries.append(q)
        
        stage2_duration = (time.time() - stage2_start) * 1000
        
        stages.append(StageLog(
            stage_name="Multi-Query Generation",
            stage_number=2,
            input_data=enhanced_query,
            output_data=unique_queries,
            duration_ms=stage2_duration,
            metadata={"query_count": len(unique_queries)}
        ))
        
        # =================================================================
        # STAGE 3: Search (with RRF Fusion)
        # =================================================================
        stage3_start = time.time()
        
        # Get pre-rerank results
        search_results = self.rag._search_all_queries(unique_queries, rag_source)
        
        stage3_duration = (time.time() - stage3_start) * 1000
        
        # Extract metadata from results
        pre_rerank_refs = []
        for res in search_results[:20]:
            ref = extract_verse_from_result(res, source)
            if ref:
                pre_rerank_refs.append(ref)
        
        stages.append(StageLog(
            stage_name="Search (RRF Fusion)",
            stage_number=3,
            input_data=unique_queries,
            output_data=pre_rerank_refs[:10],  # Top 10 for logging
            duration_ms=stage3_duration,
            metadata={
                "total_results": len(search_results),
                "queries_used": len(unique_queries)
            }
        ))
        
        # =================================================================
        # STAGE 4: Reranking
        # =================================================================
        stage4_start = time.time()
        
        try:
            final_results = self.rag._rerank_results(question, search_results, top_k=10)
        except Exception as e:
            final_results = search_results[:10]
        
        stage4_duration = (time.time() - stage4_start) * 1000
        
        # Extract final references
        final_refs = []
        for res in final_results:
            ref = extract_verse_from_result(res, source)
            if ref:
                final_refs.append(ref)
        
        stages.append(StageLog(
            stage_name="Reranking (Cross-Encoder)",
            stage_number=4,
            input_data=f"{len(search_results)} candidates",
            output_data=final_refs,
            duration_ms=stage4_duration,
            metadata={"final_count": len(final_results)}
        ))
        
        return final_results, stages


# ============================================================================
# TEST EXECUTION
# ============================================================================

def run_single_test(rag_wrapper: RAGWithStageLogging, test: TestCase) -> TestResult:
    """Execute a single test case with stage logging."""
    start_time = time.time()
    retrieved_verses = []
    stages = []
    error = None
    
    try:
        # Run pipeline with logging
        results, stages = rag_wrapper.run_with_logging(test.question, test.source)
        
        # Extract verse references from final results
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
        stages=stages,
        error=error
    )


def print_stage_log(stage: StageLog, indent: str = "   "):
    """Print a single stage log with formatting."""
    console.print(f"{indent}[bold]Stage {stage.stage_number}: {stage.stage_name}[/bold] [dim]({stage.duration_ms:.0f}ms)[/dim]")
    
    # Print input (truncated)
    input_str = str(stage.input_data)
    if len(input_str) > 100:
        input_str = input_str[:100] + "..."
    console.print(f"{indent}  [dim]Input:[/dim] {input_str}")
    
    # Print output based on type
    if isinstance(stage.output_data, list):
        if len(stage.output_data) > 5:
            console.print(f"{indent}  [dim]Output:[/dim] {stage.output_data[:5]} ... (+{len(stage.output_data)-5} more)")
        else:
            console.print(f"{indent}  [dim]Output:[/dim] {stage.output_data}")
    else:
        output_str = str(stage.output_data)
        if len(output_str) > 100:
            output_str = output_str[:100] + "..."
        console.print(f"{indent}  [dim]Output:[/dim] {output_str}")


def run_all_tests(test_data_path: str) -> Dict[str, Any]:
    """Run all tests and return comprehensive results."""
    
    console.print(Panel.fit(
        "[bold cyan]RAG End-to-End Accuracy Test Suite[/bold cyan]\n"
        "[dim]Testing complete pipeline with stage-by-stage logging[/dim]",
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
    
    console.print(f"\n[dim]Loaded {len(tests)} test cases from {test_data_path}[/dim]")
    console.print("[dim]Initializing RAG Pipeline with Stage Logging...[/dim]\n")
    
    # Initialize RAG wrapper
    rag_wrapper = RAGWithStageLogging()
    
    results: List[TestResult] = []
    
    console.print("=" * 80)
    console.print("[bold]STAGE-BY-STAGE TEST EXECUTION[/bold]")
    console.print("=" * 80 + "\n")
    
    for i, test in enumerate(tests, 1):
        # Print test header
        console.print(f"[bold cyan]{'━' * 80}[/bold cyan]")
        console.print(f"[bold cyan]TEST {test.id} ({i}/{len(tests)})[/bold cyan]")
        console.print(f"[bold cyan]{'━' * 80}[/bold cyan]")
        console.print(f"[dim]Source:[/dim] {test.source.upper()} | [dim]Difficulty:[/dim] {test.difficulty}")
        console.print(f"[dim]Question:[/dim] {test.question}")
        console.print(f"[dim]Expected:[/dim] {test.expected_verses if test.expected_verses else '[HALLUCINATION TEST]'}")
        console.print()
        
        # Run test with stage logging
        result = run_single_test(rag_wrapper, test)
        results.append(result)
        
        # Print all stages
        console.print("[bold yellow]Pipeline Stages:[/bold yellow]")
        for stage in result.stages:
            print_stage_log(stage)
        
        console.print()
        
        # Print final result
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
            console.print(f"{status} [bold]P={result.precision*100:.0f}% R={result.recall*100:.0f}% F1={result.f1_score*100:.0f}%[/bold] | Total: {result.elapsed_time*1000:.0f}ms")
        
        # Stage timing summary
        stage_times = [f"{s.stage_name}: {s.duration_ms:.0f}ms" for s in result.stages]
        console.print(f"[dim]Stage Timing: {' → '.join(stage_times)}[/dim]")
        console.print()
    
    return compile_report(results, data['metadata'])


def compile_report(results: List[TestResult], metadata: Dict) -> Dict[str, Any]:
    """Compile comprehensive test report with stage details."""
    
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
    
    # Calculate stage timing averages
    stage_timing = {
        "query_enhancement_avg_ms": 0,
        "multi_query_avg_ms": 0,
        "search_avg_ms": 0,
        "rerank_avg_ms": 0
    }
    
    stage_times = {1: [], 2: [], 3: [], 4: []}
    for r in results:
        for s in r.stages:
            if s.stage_number in stage_times:
                stage_times[s.stage_number].append(s.duration_ms)
    
    stage_timing["query_enhancement_avg_ms"] = avg(stage_times.get(1, []))
    stage_timing["multi_query_avg_ms"] = avg(stage_times.get(2, []))
    stage_timing["search_avg_ms"] = avg(stage_times.get(3, []))
    stage_timing["rerank_avg_ms"] = avg(stage_times.get(4, []))
    
    report = {
        "metadata": metadata,
        "summary": {
            "total_tests": len(results),
            "total_time": sum(r.elapsed_time for r in results),
            "avg_time_per_query": avg([r.elapsed_time for r in results]),
            "errors": sum(1 for r in results if r.error)
        },
        "stage_timing": stage_timing,
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
                "question": r.question,
                "expected": r.expected_verses,
                "retrieved": r.retrieved_verses,
                "precision": r.precision,
                "recall": r.recall,
                "f1": r.f1_score,
                "time_ms": r.elapsed_time * 1000,
                "hallucination_test": r.is_hallucination_test,
                "hallucination_passed": r.hallucination_passed,
                "error": r.error,
                "stages": [
                    {
                        "stage_number": s.stage_number,
                        "stage_name": s.stage_name,
                        "input": str(s.input_data)[:200] if s.input_data else None,
                        "output": s.output_data if isinstance(s.output_data, list) else str(s.output_data)[:200],
                        "duration_ms": s.duration_ms,
                        "metadata": s.metadata
                    }
                    for s in r.stages
                ]
            }
            for r in results
        ]
    }
    
    # Print report
    print_report(report)
    
    return report


def print_report(report: Dict):
    """Print formatted report to console."""
    
    console.print("\n" + "═" * 80)
    console.print("[bold cyan]                         TEST RESULTS SUMMARY[/bold cyan]")
    console.print("═" * 80 + "\n")
    
    # Overall metrics
    overall = report["overall"]
    console.print(f"[bold]Overall Metrics (Normal Tests):[/bold]")
    console.print(f"  Precision: [green]{overall['precision']*100:.1f}%[/green]")
    console.print(f"  Recall:    [green]{overall['recall']*100:.1f}%[/green]")
    console.print(f"  F1 Score:  [green]{overall['f1']*100:.1f}%[/green]")
    console.print()
    
    # Stage timing summary
    st = report["stage_timing"]
    console.print(f"[bold]Average Stage Timing:[/bold]")
    console.print(f"  1. Query Enhancement: [cyan]{st['query_enhancement_avg_ms']:.0f}ms[/cyan]")
    console.print(f"  2. Multi-Query Gen:   [cyan]{st['multi_query_avg_ms']:.0f}ms[/cyan]")
    console.print(f"  3. Search (RRF):      [cyan]{st['search_avg_ms']:.0f}ms[/cyan]")
    console.print(f"  4. Reranking:         [cyan]{st['rerank_avg_ms']:.0f}ms[/cyan]")
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
    if hall["total"] > 0:
        console.print(f"[bold]Hallucination Detection:[/bold]")
        console.print(f"  Tests: {hall['total']}")
        console.print(f"  Passed: [green]{hall['passed']}/{hall['total']}[/green] ({hall['pass_rate']*100:.0f}%)")
        console.print()
    
    # Detailed results table
    detail_table = Table(title="Detailed Results", show_header=True, header_style="bold magenta")
    detail_table.add_column("#", width=5)
    detail_table.add_column("Source", width=6)
    detail_table.add_column("Diff", width=6)
    detail_table.add_column("Question", width=30)
    detail_table.add_column("Expected", width=15)
    detail_table.add_column("Retrieved", width=15)
    detail_table.add_column("P/R/F1", width=12)
    detail_table.add_column("Time", width=8)
    
    for d in report["details"]:
        status = "✅" if d["recall"] > 0.5 else "❌"
        if d["hallucination_test"]:
            status = "✅" if d["hallucination_passed"] else "⚠️"
        
        detail_table.add_row(
            d["id"],
            d["source"][:5].upper(),
            d["difficulty"][:4],
            d["question"][:29],
            ", ".join(d["expected"][:2])[:14] or "[NONE]",
            ", ".join(d["retrieved"][:2])[:14] or "[empty]",
            f"{status} {d['precision']*100:.0f}/{d['recall']*100:.0f}/{d['f1']*100:.0f}",
            f"{d['time_ms']:.0f}ms"
        )
    
    console.print(detail_table)
    
    # Summary stats
    summary = report["summary"]
    console.print("\n" + "═" * 80)
    console.print(f"[bold]Total Tests:[/bold] {summary['total_tests']}")
    console.print(f"[bold]Total Time:[/bold] {summary['total_time']:.1f}s")
    console.print(f"[bold]Avg Time/Query:[/bold] {summary['avg_time_per_query']*1000:.0f}ms")
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
    
    console.print(f"\n[dim]Full report saved to: {report_path}[/dim]")
