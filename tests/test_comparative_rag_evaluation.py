"""
Comparative RAG Pipeline Evaluation

Comprehensive test suite for evaluating the Comparative RAG system.
Tests retrieval quality, latency, essay synthesis, and cost estimation.

Usage:
    python tests/test_comparative_rag_evaluation.py
    
Or with pytest:
    python -m pytest tests/test_comparative_rag_evaluation.py -v
"""
import os
import sys
import json
import time
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()


# ============== DATA CLASSES ==============

@dataclass
class LatencyBreakdown:
    """Per-step latency measurements"""
    query_enhancement_ms: float = 0.0
    multi_query_gen_ms: float = 0.0
    parallel_searches_ms: float = 0.0
    rrf_fusion_ms: float = 0.0
    reranking_ms: float = 0.0
    essay_generation_ms: float = 0.0
    total_ms: float = 0.0
    
    def to_dict(self) -> dict:
        return {
            "query_enhancement_ms": self.query_enhancement_ms,
            "multi_query_gen_ms": self.multi_query_gen_ms,
            "parallel_searches_ms": self.parallel_searches_ms,
            "rrf_fusion_ms": self.rrf_fusion_ms,
            "reranking_ms": self.reranking_ms,
            "essay_generation_ms": self.essay_generation_ms,
            "total_ms": self.total_ms
        }


@dataclass
class RetrievalMetrics:
    """Retrieval quality metrics"""
    quran_count: int = 0
    bible_count: int = 0
    balance_ratio: float = 0.0  # 1.0 = perfect balance
    ground_truth_quran_found: List[str] = field(default_factory=list)
    ground_truth_bible_found: List[str] = field(default_factory=list)
    keyword_coverage: List[str] = field(default_factory=list)
    gt_quran_recall: float = 0.0
    gt_bible_recall: float = 0.0


@dataclass
class EssayMetrics:
    """Essay synthesis quality metrics"""
    quran_citations: int = 0
    bible_citations: int = 0
    total_citations: int = 0
    citation_balance: float = 0.0  # 1.0 = perfect balance
    confidence_score: float = 0.0
    essay_length: int = 0
    has_intro: bool = False
    has_conclusion: bool = False


@dataclass 
class CostEstimate:
    """Cost estimation breakdown"""
    query_enhancer_calls: int = 2
    embedding_calls: int = 200  # 4 × 50
    reranker_calls: int = 4
    essay_gen_calls: int = 1
    
    # Approximate costs (USD)
    query_enhancer_cost: float = 0.001
    embedding_cost: float = 0.0001
    reranker_cost: float = 0.002
    essay_gen_cost: float = 0.01
    
    @property
    def total_cost(self) -> float:
        return (
            self.query_enhancer_cost + 
            self.embedding_cost + 
            self.reranker_cost + 
            self.essay_gen_cost
        )


@dataclass
class EvaluationResult:
    """Complete evaluation result for one query"""
    query_id: int
    query: str
    category: str
    mode: str  # "single-query" or "multi-query"
    latency: LatencyBreakdown
    retrieval: RetrievalMetrics
    essay: EssayMetrics
    cost: CostEstimate
    raw_answer: Any = None


# ============== TEST DATA ==============

def load_test_data() -> List[Dict]:
    """Load test data from JSON file"""
    test_file = os.path.join(
        os.path.dirname(__file__), 
        "test_data.json"
    )
    with open(test_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data["data"]


def get_selected_samples(data: List[Dict], ids: List[int] = None) -> List[Dict]:
    """Get specific test samples by ID. If ids is None, return ALL samples."""
    if ids is None:
        return data  # Return all 50 queries
    return [d for d in data if d["id"] in ids]


# ============== EVALUATION FUNCTIONS ==============

def evaluate_retrieval(
    search_result,
    ground_truth: Dict
) -> RetrievalMetrics:
    """Evaluate retrieval quality against ground truth"""
    metrics = RetrievalMetrics()
    
    # Count verses per scripture
    metrics.quran_count = (
        len(search_result.quran_semantic) + 
        len(search_result.quran_chunks)
    )
    metrics.bible_count = (
        len(search_result.bible_semantic) + 
        len(search_result.bible_chunks)
    )
    
    total = metrics.quran_count + metrics.bible_count
    if total > 0:
        min_ratio = min(metrics.quran_count, metrics.bible_count) / (total / 2)
        metrics.balance_ratio = min_ratio
    
    # Extract all retrieved references
    retrieved_quran = set()
    retrieved_bible = set()
    
    for result in search_result.quran_semantic + search_result.quran_chunks:
        surah = getattr(result, 'surah_name', None) or getattr(result, 'surah_id', '')
        verse = getattr(result, 'verse_id', '') or getattr(result, 'verse_ids', '')
        if surah and verse:
            retrieved_quran.add(f"{surah} {verse}".lower())
    
    for result in search_result.bible_semantic + search_result.bible_chunks:
        book = getattr(result, 'book_name', '')
        chapter = getattr(result, 'chapter_number', '') or getattr(result, 'chapter', '')
        verse = getattr(result, 'verse_number', '') or getattr(result, 'verse', '')
        if book and chapter and verse:
            retrieved_bible.add(f"{book} {chapter}:{verse}".lower())
    
    # Check ground truth overlap
    gt_quran = ground_truth.get("quran_refs", [])
    gt_bible = ground_truth.get("bible_refs", [])
    gt_keywords = ground_truth.get("keywords", [])
    
    for ref in gt_quran:
        ref_lower = ref.lower()
        for retrieved in retrieved_quran:
            if ref_lower in retrieved or retrieved in ref_lower:
                metrics.ground_truth_quran_found.append(ref)
                break
    
    for ref in gt_bible:
        ref_lower = ref.lower()
        for retrieved in retrieved_bible:
            if ref_lower in retrieved or retrieved in ref_lower:
                metrics.ground_truth_bible_found.append(ref)
                break
    
    # Calculate recall
    if gt_quran:
        metrics.gt_quran_recall = len(metrics.ground_truth_quran_found) / len(gt_quran)
    if gt_bible:
        metrics.gt_bible_recall = len(metrics.ground_truth_bible_found) / len(gt_bible)
    
    # Keyword coverage in retrieved text
    all_text = ""
    for r in (search_result.quran_semantic + search_result.quran_chunks + 
              search_result.bible_semantic + search_result.bible_chunks):
        text = getattr(r, 'translation', '') or getattr(r, 'text', '') or ''
        all_text += text.lower() + " "
    
    for kw in gt_keywords:
        if kw.lower() in all_text:
            metrics.keyword_coverage.append(kw)
    
    return metrics


def evaluate_essay(answer) -> EssayMetrics:
    """Evaluate essay synthesis quality"""
    metrics = EssayMetrics()
    
    metrics.quran_citations = len(answer.quran_references)
    metrics.bible_citations = len(answer.bible_references)
    metrics.total_citations = len(answer.all_references)
    
    total = metrics.quran_citations + metrics.bible_citations
    if total > 0:
        min_cit = min(metrics.quran_citations, metrics.bible_citations)
        metrics.citation_balance = min_cit / (total / 2)
    
    metrics.confidence_score = answer.confidence
    metrics.essay_length = len(answer.essay)
    
    # Check essay structure (Turkish keywords)
    essay_lower = answer.essay.lower()
    intro_markers = ["giriş", "konu", "inceleme", "ele alın", "açıdan"]
    conclusion_markers = ["sonuç", "özet", "netice", "sonuç olarak", "özetle"]
    
    metrics.has_intro = any(m in essay_lower for m in intro_markers)
    metrics.has_conclusion = any(m in essay_lower for m in conclusion_markers)
    
    return metrics


def run_single_evaluation(
    query_item: Dict,
    enable_multi_query: bool = False,
    rag_instance = None
) -> EvaluationResult:
    """Run evaluation for a single query. Reuses rag_instance if provided."""
    from src.comparative_rag import ComparativeRAG
    
    query_id = query_item["id"]
    query = query_item["query"]
    category = query_item["category"]
    ground_truth = query_item["ground_truth"]
    mode = "multi-query" if enable_multi_query else "single-query"
    
    console.print(f"\n[bold cyan]Query {query_id}[/bold cyan]: {query[:80]}...")
    console.print(f"[dim]Category: {category}, Mode: {mode}[/dim]")
    
    # Use provided RAG instance or create new one
    if rag_instance is not None:
        rag = rag_instance
    else:
        rag = ComparativeRAG(
            enable_multi_query=enable_multi_query,
            verbose=False
        )
    
    latency = LatencyBreakdown()
    
    # ===== STEP 1: Query Enhancement =====
    start = time.time()
    if enable_multi_query:
        from concurrent.futures import ThreadPoolExecutor
        
        def gen_quran():
            return rag._generate_multi_queries(query, corpus="quran", n=3)
        def gen_bible():
            return rag._generate_multi_queries(query, corpus="bible", n=3)
        
        with ThreadPoolExecutor(max_workers=2) as executor:
            quran_future = executor.submit(gen_quran)
            bible_future = executor.submit(gen_bible)
            quran_queries = quran_future.result()
            bible_queries = bible_future.result()
        
        latency.multi_query_gen_ms = (time.time() - start) * 1000
    else:
        quran_query, bible_query = rag._enhance_query_parallel(query)
        latency.query_enhancement_ms = (time.time() - start) * 1000
    
    # ===== STEP 2: Parallel Searches =====
    start = time.time()
    if enable_multi_query:
        quran_sem, quran_chunks, bible_sem, bible_chunks = rag._search_all_multi_query(
            quran_queries, bible_queries, pool_size=50
        )
        quran_query, bible_query = query, query
    else:
        quran_sem, quran_chunks, bible_sem, bible_chunks = rag._search_all_parallel(
            quran_query, bible_query, pool_size=50
        )
    latency.parallel_searches_ms = (time.time() - start) * 1000
    
    # ===== STEP 3: Reranking =====
    start = time.time()
    quran_sem, quran_chunks, bible_sem, bible_chunks = rag._rerank_each(
        quran_query, bible_query,
        quran_sem, quran_chunks, bible_sem, bible_chunks
    )
    latency.reranking_ms = (time.time() - start) * 1000
    
    # Create search result for metrics
    from src.comparative_rag import ComparativeScriptureResult
    search_result = ComparativeScriptureResult(
        quran_semantic=quran_sem,
        quran_chunks=quran_chunks,
        bible_semantic=bible_sem,
        bible_chunks=bible_chunks
    )
    
    # ===== STEP 4: Essay Generation =====
    start = time.time()
    answer = rag.answer_generator.generate_comparative_answer(
        query=query,
        quran_semantic=quran_sem,
        quran_chunks=quran_chunks,
        bible_semantic=bible_sem,
        bible_chunks=bible_chunks
    )
    latency.essay_generation_ms = (time.time() - start) * 1000
    
    # Calculate total
    latency.total_ms = (
        latency.query_enhancement_ms +
        latency.multi_query_gen_ms +
        latency.parallel_searches_ms +
        latency.reranking_ms +
        latency.essay_generation_ms
    )
    
    # Evaluate retrieval and essay
    retrieval_metrics = evaluate_retrieval(search_result, ground_truth)
    essay_metrics = evaluate_essay(answer)
    
    console.print(f"  [green]✓[/green] Total: {latency.total_ms:.0f}ms, "
                  f"Verses: {search_result.total_verses}, "
                  f"Citations: {essay_metrics.total_citations}")
    
    return EvaluationResult(
        query_id=query_id,
        query=query,
        category=category,
        mode=mode,
        latency=latency,
        retrieval=retrieval_metrics,
        essay=essay_metrics,
        cost=CostEstimate(),
        raw_answer=answer
    )


# ============== REPORTING ==============

def print_aggregate_summary(results: List[EvaluationResult], title: str):
    """Print aggregate summary statistics for all results"""
    n = len(results)
    if n == 0:
        return
    
    mode = results[0].mode
    
    # Calculate averages
    avg_latency = sum(r.latency.total_ms for r in results) / n
    avg_enhancement = sum(r.latency.query_enhancement_ms + r.latency.multi_query_gen_ms for r in results) / n
    avg_search = sum(r.latency.parallel_searches_ms for r in results) / n
    avg_rerank = sum(r.latency.reranking_ms for r in results) / n
    avg_essay = sum(r.latency.essay_generation_ms for r in results) / n
    
    avg_quran = sum(r.retrieval.quran_count for r in results) / n
    avg_bible = sum(r.retrieval.bible_count for r in results) / n
    avg_balance = sum(r.retrieval.balance_ratio for r in results) / n
    avg_gt_recall = sum((r.retrieval.gt_quran_recall + r.retrieval.gt_bible_recall) / 2 for r in results) / n
    
    avg_citations = sum(r.essay.total_citations for r in results) / n
    avg_quran_cit = sum(r.essay.quran_citations for r in results) / n
    avg_bible_cit = sum(r.essay.bible_citations for r in results) / n
    avg_citation_balance = sum(r.essay.citation_balance for r in results) / n
    avg_confidence = sum(r.essay.confidence_score for r in results) / n
    avg_length = sum(r.essay.essay_length for r in results) / n
    
    min_latency = min(r.latency.total_ms for r in results)
    max_latency = max(r.latency.total_ms for r in results)
    
    console.print(f"\n[bold cyan]{title}[/bold cyan]")
    console.print(f"[dim]Mode: {mode} | Queries: {n}[/dim]\n")
    
    # Latency Table
    table = Table(title="⏱️ Latency (ms)")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", justify="right")
    
    table.add_row("Query Enhancement", f"{avg_enhancement:.0f}")
    table.add_row("Parallel Searches", f"{avg_search:.0f}")
    table.add_row("Reranking", f"{avg_rerank:.0f}")
    table.add_row("Essay Generation", f"{avg_essay:.0f}")
    table.add_row("[bold]TOTAL (avg)[/bold]", f"[bold]{avg_latency:.0f}[/bold]")
    table.add_row("Min / Max", f"{min_latency:.0f} / {max_latency:.0f}")
    
    console.print(table)
    
    # Retrieval Table
    table2 = Table(title="📊 Retrieval Quality")
    table2.add_column("Metric", style="cyan")
    table2.add_column("Value", justify="right")
    
    table2.add_row("Avg Quran Verses", f"{avg_quran:.1f}")
    table2.add_row("Avg Bible Verses", f"{avg_bible:.1f}")
    table2.add_row("Balance Ratio", f"{avg_balance:.0%}")
    table2.add_row("GT Recall (avg)", f"{avg_gt_recall:.0%}")
    
    console.print(table2)
    
    # Essay Table
    table3 = Table(title="📝 Essay Synthesis")
    table3.add_column("Metric", style="cyan")
    table3.add_column("Value", justify="right")
    
    table3.add_row("Avg Total Citations", f"{avg_citations:.1f}")
    table3.add_row("Avg Quran Citations", f"{avg_quran_cit:.1f}")
    table3.add_row("Avg Bible Citations", f"{avg_bible_cit:.1f}")
    table3.add_row("Citation Balance", f"{avg_citation_balance:.0%}")
    table3.add_row("Avg Confidence", f"{avg_confidence:.0%}")
    table3.add_row("Avg Essay Length", f"{avg_length:,.0f} chars")
    
    console.print(table3)


def print_cost_summary(results: List[EvaluationResult]):
    """Print cost estimation summary"""
    n = len(results)
    total_cost = sum(r.cost.total_cost for r in results)
    
    table = Table(title="💰 Cost Estimation")
    
    table.add_column("Component", style="cyan")
    table.add_column("Per Query", justify="right")
    table.add_column(f"Total ({n} queries)", justify="right")
    
    if results:
        c = results[0].cost
        table.add_row("Query Enhancer", f"${c.query_enhancer_cost:.4f}", f"${c.query_enhancer_cost * n:.4f}")
        table.add_row("Embeddings", f"${c.embedding_cost:.4f}", f"${c.embedding_cost * n:.4f}")
        table.add_row("Reranker", f"${c.reranker_cost:.4f}", f"${c.reranker_cost * n:.4f}")
        table.add_row("Essay Gen", f"${c.essay_gen_cost:.4f}", f"${c.essay_gen_cost * n:.4f}")
        table.add_row("[bold]TOTAL[/bold]", f"[bold]${c.total_cost:.4f}[/bold]", f"[bold]${total_cost:.4f}[/bold]")
    
    console.print("\n")
    console.print(table)


def print_summary_comparison(single_results: List[EvaluationResult], multi_results: List[EvaluationResult]):
    """Print comparison summary between single and multi-query modes"""
    
    def avg(lst, key):
        vals = [key(r) for r in lst]
        return sum(vals) / len(vals) if vals else 0
    
    table = Table(title="⚖️ Single-Query vs Multi-Query Comparison")
    
    table.add_column("Metric", style="cyan")
    table.add_column("Single-Query", justify="right")
    table.add_column("Multi-Query", justify="right")
    table.add_column("Difference", justify="right")
    
    # Latency
    single_latency = avg(single_results, lambda r: r.latency.total_ms)
    multi_latency = avg(multi_results, lambda r: r.latency.total_ms)
    diff_latency = multi_latency - single_latency
    
    table.add_row(
        "Avg Latency (ms)",
        f"{single_latency:.0f}",
        f"{multi_latency:.0f}",
        f"+{diff_latency:.0f}" if diff_latency > 0 else f"{diff_latency:.0f}"
    )
    
    # Retrieval balance
    single_balance = avg(single_results, lambda r: r.retrieval.balance_ratio)
    multi_balance = avg(multi_results, lambda r: r.retrieval.balance_ratio)
    
    table.add_row(
        "Avg Retrieval Balance",
        f"{single_balance:.0%}",
        f"{multi_balance:.0%}",
        f"{(multi_balance - single_balance):.0%}"
    )
    
    # GT Recall
    single_recall = avg(single_results, lambda r: (r.retrieval.gt_quran_recall + r.retrieval.gt_bible_recall) / 2)
    multi_recall = avg(multi_results, lambda r: (r.retrieval.gt_quran_recall + r.retrieval.gt_bible_recall) / 2)
    
    table.add_row(
        "Avg GT Recall",
        f"{single_recall:.0%}",
        f"{multi_recall:.0%}",
        f"{(multi_recall - single_recall):.0%}"
    )
    
    # Citations
    single_cit = avg(single_results, lambda r: r.essay.total_citations)
    multi_cit = avg(multi_results, lambda r: r.essay.total_citations)
    
    table.add_row(
        "Avg Citations",
        f"{single_cit:.1f}",
        f"{multi_cit:.1f}",
        f"{(multi_cit - single_cit):+.1f}"
    )
    
    # Confidence
    single_conf = avg(single_results, lambda r: r.essay.confidence_score)
    multi_conf = avg(multi_results, lambda r: r.essay.confidence_score)
    
    table.add_row(
        "Avg Confidence",
        f"{single_conf:.0%}",
        f"{multi_conf:.0%}",
        f"{(multi_conf - single_conf):.0%}"
    )
    
    console.print("\n")
    console.print(table)


# ============== MAIN ==============

def run_evaluation(sample_ids: List[int] = None, test_multi_query: bool = True):
    """Run full evaluation on all 50 queries"""
    from src.comparative_rag import ComparativeRAG
    
    console.print(Panel.fit(
        "[bold]Comparative RAG Pipeline Evaluation[/bold]\n"
        "Testing retrieval quality, latency, and essay synthesis\n"
        "[dim]Running ALL 50 queries × 2 modes[/dim]",
        title="🔬 Evaluation Start"
    ))
    
    # Load test data
    test_data = load_test_data()
    samples = get_selected_samples(test_data, sample_ids)
    
    console.print(f"\n[bold]Total: {len(samples)} test samples[/bold]")
    
    # Create shared RAG instances (avoids repeated initialization)
    console.print("\n[dim]Initializing RAG instances...[/dim]")
    single_rag = ComparativeRAG(enable_multi_query=False, verbose=False)
    multi_rag = ComparativeRAG(enable_multi_query=True, verbose=False)
    
    # Pre-initialize all lazy components
    _ = single_rag.enhancer
    _ = single_rag.reranker
    _ = single_rag.answer_generator
    _ = multi_rag.enhancer
    _ = multi_rag.reranker
    _ = multi_rag.answer_generator
    console.print("[green]✓[/green] RAG instances ready\n")
    
    # Run single-query evaluations
    console.print("="*60)
    console.print("[bold yellow]PHASE 1: Single-Query Mode (50 queries)[/bold yellow]")
    console.print("="*60)
    
    single_results = []
    for i, sample in enumerate(samples, 1):
        console.print(f"\n[dim]Progress: {i}/{len(samples)}[/dim]")
        result = run_single_evaluation(sample, enable_multi_query=False, rag_instance=single_rag)
        single_results.append(result)
    
    # Run multi-query evaluations (if enabled)
    multi_results = []
    if test_multi_query:
        console.print("\n" + "="*60)
        console.print("[bold yellow]PHASE 2: Multi-Query Mode (50 queries)[/bold yellow]")
        console.print("="*60)
        
        for i, sample in enumerate(samples, 1):
            console.print(f"\n[dim]Progress: {i}/{len(samples)}[/dim]")
            result = run_single_evaluation(sample, enable_multi_query=True, rag_instance=multi_rag)
            multi_results.append(result)
    
    # Print reports
    console.print("\n" + "="*60)
    console.print("[bold green]EVALUATION RESULTS[/bold green]")
    console.print("="*60)
    
    print_aggregate_summary(single_results, "SINGLE-QUERY MODE SUMMARY")
    
    if multi_results:
        print_aggregate_summary(multi_results, "MULTI-QUERY MODE SUMMARY")
        print_summary_comparison(single_results, multi_results)
    
    print_cost_summary(single_results)
    
    # Calculate totals
    total_time_single = sum(r.latency.total_ms for r in single_results) / 1000
    total_time_multi = sum(r.latency.total_ms for r in multi_results) / 1000 if multi_results else 0
    
    console.print(Panel.fit(
        f"[bold green]Evaluation Complete[/bold green]\n"
        f"Tested: {len(samples)} queries × {'2 modes' if multi_results else '1 mode'}\n"
        f"Single-Query Total: {total_time_single:.1f}s\n"
        f"Multi-Query Total: {total_time_multi:.1f}s",
        title="✅ Done"
    ))
    
    return single_results, multi_results


if __name__ == "__main__":
    # Run with default samples: 5, 36, 41, 46, 49
    run_evaluation()
