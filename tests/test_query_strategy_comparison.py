"""
Query Strategy Comparison Test

Compares two strategies:
1. Current ComparativeRAG (Single Enhanced Query per scripture)
2. Multi-Query Strategy (Original + Enhanced +  LLM perspectives = 5 queries)

Tests 3 complex religious questions and measures:
- Execution time
- Number of unique verses retrieved (Target: 80 total/40 per scripture)
- Relevance based on key concepts from web research
"""
import os
import sys
import time
from typing import Dict, List, Tuple
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from rich.console import Console
from rich.table import Table

console = Console()


@dataclass
class QueryResult:
    """Results from a single query strategy test"""
    strategy_name: str
    query: str
    duration_ms: float
    quran_verses: List[str] = field(default_factory=list)
    bible_verses: List[str] = field(default_factory=list)
    quran_key_concepts_found: List[str] = field(default_factory=list)
    bible_key_concepts_found: List[str] = field(default_factory=list)


# 3 Complex Religious Questions with expected key concepts from web research
TEST_CASES = [
    {
        "question": "What do the scriptures say about patience and perseverance?",
        "quran_concepts": ["sabır", "sebat", "sabreden", "tahammül", "direnç", "dayanıklılık", "Allah sabredenlerle"],
        "bible_concepts": ["patience", "longsuffering", "endurance", "steadfast", "perseverance", "trials", "endure"]
    },
    {
        "question": "How do holy books describe forgiveness and mercy?",
        "quran_concepts": ["mağfiret", "rahmet", "bağışla", "af", "merhamet", "rahman", "rahim", "tövbe"],
        "bible_concepts": ["forgiveness", "mercy", "forgive", "compassion", "grace", "pardon", "sin", "repent"]
    },
    {
        "question": "What do scriptures teach about helping the poor and charity?",
        "quran_concepts": ["zekat", "sadaka", "fakir", "yoksul", "infak", "hayır", "yardım", "muhtaç"],
        "bible_concepts": ["poor", "charity", "give", "needy", "alms", "generous", "widow", "orphan"]
    }
]


def count_concepts_in_text(text: str, concepts: List[str]) -> List[str]:
    """Find which concepts appear in the text"""
    text_lower = text.lower()
    found = []
    for concept in concepts:
        if concept.lower() in text_lower:
            found.append(concept)
    return found


def extract_text_from_result(result) -> str:
    """Extract text content from various result types"""
    # Try different attribute names
    payload = getattr(result, 'payload', {}) or {}
    
    text = ""
    # For Quran results
    text += str(getattr(result, 'translation', payload.get('translation', '')))
    # For Bible results
    text += str(getattr(result, 'text', payload.get('text', '')))
    # For chunk results
    text += str(getattr(result, 'content', payload.get('content', '')))
    
    return text


def test_current_strategy(question: str, quran_concepts: List[str], bible_concepts: List[str]) -> QueryResult:
    """Test current ComparativeRAG (single enhanced query)"""
    from src.comparative_rag import ComparativeRAG
    
    start = time.time()
    rag = ComparativeRAG(verbose=False)
    search_result = rag.search_all(question)
    duration = (time.time() - start) * 1000
    
    # Collect all texts
    quran_texts = []
    bible_texts = []
    quran_found_concepts = set()
    bible_found_concepts = set()
    
    # Process Quran results (Sem + Chunk)
    for result in search_result.quran_semantic + search_result.quran_chunks:
        text = extract_text_from_result(result)
        quran_texts.append(text[:100])
        quran_found_concepts.update(count_concepts_in_text(text, quran_concepts))
    
    # Process Bible results (Sem + Chunk)
    for result in search_result.bible_semantic + search_result.bible_chunks:
        text = extract_text_from_result(result)
        bible_texts.append(text[:100])
        bible_found_concepts.update(count_concepts_in_text(text, bible_concepts))
    
    return QueryResult(
        strategy_name="Current (Single Query)",
        query=question,
        duration_ms=duration,
        quran_verses=quran_texts,
        bible_verses=bible_texts,
        quran_key_concepts_found=list(quran_found_concepts),
        bible_key_concepts_found=list(bible_found_concepts)
    )


def test_multi_query_strategy(question: str, quran_concepts: List[str], bible_concepts: List[str]) -> QueryResult:
    """Test multi-query strategy (5 queries + RRF)"""
    from src.query_enhancer import QueryEnhancer
    from src.search import QuranSearcher, BibleSearcher, SemanticChunkSearcher, BibleSemanticChunkSearcher
    from src.reranker import Reranker
    
    start = time.time()
    
    enhancer = QueryEnhancer()
    reranker = Reranker()
    
    # Generate 5 queries for each corpus (Original + Enhanced + 3 Multi)
    # Quran queries
    quran_enhanced = enhancer.expand_query(question, corpus="quran")
    quran_multi = enhancer.generate_multi_query(quran_enhanced, n=3, corpus="quran")
    quran_queries = [question, quran_enhanced] + quran_multi
    quran_queries = list(dict.fromkeys(quran_queries))[:5]  # Dedupe
    
    # Bible queries
    bible_enhanced = enhancer.expand_query(question, corpus="bible")
    bible_multi = enhancer.generate_multi_query(bible_enhanced, n=3, corpus="bible")
    bible_queries = [question, bible_enhanced] + bible_multi
    bible_queries = list(dict.fromkeys(bible_queries))[:5]  # Dedupe
    
    # Initialize searchers
    quran_searcher = QuranSearcher()
    bible_searcher = BibleSearcher(translation="kjva")
    quran_chunk_searcher = SemanticChunkSearcher()
    bible_chunk_searcher = BibleSemanticChunkSearcher(translation="kjva")
    
    # RRF parameters
    k = 60
    
    # --- Execute multi-query searches for 4 Quadrants ---
    
    def search_quadrant(queries, searcher, limit, is_chunk=False):
        rrf_scores = {} # id -> (result, rrf_score)
        
        for query in queries:
            try:
                # Reduce limit per query to keep it fast, but high enough for RRF
                results = searcher.search(query, mode="semantic", limit=20)
                for rank, r in enumerate(results, 1):
                    # Robust ID extraction
                    if is_chunk:
                         rid = getattr(r, 'chunk_id', str(rank) + "_chunk")
                    else:
                         rid = r.id if hasattr(r, 'id') else str(rank)
                         
                    rrf = 1 / (k + rank)
                    
                    if rid in rrf_scores:
                        existing_res, existing_score = rrf_scores[rid]
                        rrf_scores[rid] = (existing_res, existing_score + rrf)
                    else:
                        rrf_scores[rid] = (r, rrf)
            except Exception:
                pass
        
        # Sort by RRF and return top objects
        sorted_results = sorted(rrf_scores.values(), key=lambda x: x[1], reverse=True)
        return [item[0] for item in sorted_results]

    # 1. Quran Semantic
    q_sem_candidates = search_quadrant(quran_queries, quran_searcher, limit=20, is_chunk=False)
    q_sem_final = reranker.rerank(question, q_sem_candidates[:50], top_k=20)
    
    # 2. Quran Chunk
    q_chunk_final = []
    if quran_chunk_searcher.collection_exists():
        q_chunk_candidates = search_quadrant(quran_queries, quran_chunk_searcher, limit=20, is_chunk=True)
        q_chunk_final = reranker.rerank(question, q_chunk_candidates[:50], top_k=20)
        
    # 3. Bible Semantic
    b_sem_candidates = search_quadrant(bible_queries, bible_searcher, limit=20, is_chunk=False)
    b_sem_final = reranker.rerank(question, b_sem_candidates[:50], top_k=20)
    
    # 4. Bible Chunk
    b_chunk_final = []
    if bible_chunk_searcher.collection_exists():
        b_chunk_candidates = search_quadrant(bible_queries, bible_chunk_searcher, limit=20, is_chunk=True)
        b_chunk_final = reranker.rerank(question, b_chunk_candidates[:50], top_k=20)
    
    duration = (time.time() - start) * 1000
    
    # Debug: Print quadrant counts
    console.print(f"[dim]  Multi-Query Quadrants: Q_Sem={len(q_sem_final)}, Q_Chunk={len(q_chunk_final)}, B_Sem={len(b_sem_final)}, B_Chunk={len(b_chunk_final)}[/dim]")
    
    # Extract texts and find concepts
    quran_texts = []
    bible_texts = []
    quran_found_concepts = set()
    bible_found_concepts = set()
    
    # Gather Quran texts
    for result in q_sem_final + q_chunk_final:
        text = extract_text_from_result(result)
        quran_texts.append(text[:100])
        quran_found_concepts.update(count_concepts_in_text(text, quran_concepts))
    
    # Gather Bible texts
    for result in b_sem_final + b_chunk_final:
        text = extract_text_from_result(result)
        bible_texts.append(text[:100])
        bible_found_concepts.update(count_concepts_in_text(text, bible_concepts))
    
    return QueryResult(
        strategy_name="Multi-Query (5 queries + RRF)",
        query=question,
        duration_ms=duration,
        quran_verses=quran_texts,  
        bible_verses=bible_texts,  
        quran_key_concepts_found=list(quran_found_concepts),
        bible_key_concepts_found=list(bible_found_concepts)
    )


def run_comparison():
    """Run full comparison test"""
    console.print("\n[bold blue]═══ QUERY STRATEGY COMPARISON TEST (80 Verses) ═══[/bold blue]\n")
    console.print("[dim]Comparing: Current (Single Enhanced Query) vs Multi-Query (5 queries + RRF)[/dim]\n")
    
    all_results = []
    
    for i, test_case in enumerate(TEST_CASES, 1):
        question = test_case["question"]
        quran_concepts = test_case["quran_concepts"]
        bible_concepts = test_case["bible_concepts"]
        
        console.print(f"\n[bold cyan]{'─'*60}[/bold cyan]")
        console.print(f"[bold]Test {i}: {question}[/bold]")
        console.print(f"[dim]Expected Quran: {', '.join(quran_concepts[:5])}...[/dim]")
        console.print(f"[dim]Expected Bible: {', '.join(bible_concepts[:5])}...[/dim]")
        
        # Test current strategy
        console.print("\n[yellow]Testing Current Strategy...[/yellow]")
        current_result = test_current_strategy(question, quran_concepts, bible_concepts)
        
        # Test multi-query strategy
        console.print("[yellow]Testing Multi-Query Strategy...[/yellow]")
        multi_result = test_multi_query_strategy(question, quran_concepts, bible_concepts)
        
        all_results.append((current_result, multi_result))
        
        # Print comparison table for this question
        table = Table(title=f"Results for Test {i}")
        table.add_column("Metric", style="cyan")
        table.add_column("Current (Single)", style="green")
        table.add_column("Multi-Query (Multi)", style="magenta")
        
        table.add_row(
            "Duration",
            f"{current_result.duration_ms:.0f} ms",
            f"{multi_result.duration_ms:.0f} ms"
        )
        table.add_row(
            "Total Verses",
            str(len(current_result.quran_verses) + len(current_result.bible_verses)),
            str(len(multi_result.quran_verses) + len(multi_result.bible_verses))
        )
        table.add_row(
            "Quran Concepts",
            f"{len(current_result.quran_key_concepts_found)}/{len(quran_concepts)}",
            f"{len(multi_result.quran_key_concepts_found)}/{len(quran_concepts)}"
        )
        table.add_row(
            "Bible Concepts",
            f"{len(current_result.bible_key_concepts_found)}/{len(bible_concepts)}",
            f"{len(multi_result.bible_key_concepts_found)}/{len(bible_concepts)}"
        )
        
        console.print(table)
        
        # Show found concepts
        console.print(f"\n[dim]Current Quran: {', '.join(current_result.quran_key_concepts_found) or 'None'}[/dim]")
        console.print(f"[dim]Multi Quran: {', '.join(multi_result.quran_key_concepts_found) or 'None'}[/dim]")
        
    
    # Final summary
    console.print(f"\n\n[bold blue]{'═'*60}[/bold blue]")
    console.print("[bold blue]FINAL SUMMARY[/bold blue]")
    all_time_curr = sum(r[0].duration_ms for r in all_results)
    all_time_multi = sum(r[1].duration_ms for r in all_results)
    
    all_conc_curr = sum(len(r[0].quran_key_concepts_found) + len(r[0].bible_key_concepts_found) for r in all_results)
    all_conc_multi = sum(len(r[1].quran_key_concepts_found) + len(r[1].bible_key_concepts_found) for r in all_results)
    
    console.print(f"Total Time: Current={all_time_curr:.0f}ms | Multi={all_time_multi:.0f}ms")
    console.print(f"Total Concepts Found: Current={all_conc_curr} | Multi={all_conc_multi}")
    
    if all_conc_multi > all_conc_curr:
        console.print(f"[green]RECOMMENDATION: SWITCH TO MULTI-QUERY (Gain: +{all_conc_multi - all_conc_curr} concepts)[/green]")
    elif all_conc_curr > all_conc_multi:
        console.print(f"[green]RECOMMENDATION: STAY WITH SINGLE QUERY[/green]")
    else:
        console.print(f"[yellow]Performance is similar. Choose based on speed.[/yellow]")


if __name__ == "__main__":
    run_comparison()
