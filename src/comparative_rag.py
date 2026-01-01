"""
Comparative Scripture RAG Pipeline

Multi-scripture search and analysis system that performs parallel queries
across Quran and Bible, then generates comparative theological interpretations.

Architecture:
    User Question
         │
    ┌────┴────┐
    ▼         ▼
  Quran     Bible
  Enhancer  Enhancer
    │         │
  ┌─┴─┐     ┌─┴─┐
  ▼   ▼     ▼   ▼
 Sem Chunk Sem Chunk
  │   │     │   │
  └───┼─────┼───┘
      ▼
   80 verses → LLM → Comparative Essay

Usage:
    from src.comparative_rag import ComparativeRAG
    
    rag = ComparativeRAG()
    result = rag.compare("What do scriptures say about patience?")
    print(result.essay)
"""
import os
import time
from typing import List, Optional, Dict, Any, Tuple
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor, as_completed
from rich.console import Console

console = Console()


@dataclass
class ComparativeScriptureResult:
    """Combined results from all scripture searches - 80 verses total"""
    quran_semantic: List = field(default_factory=list)    # 20 from Quran Semantic Search
    quran_chunks: List = field(default_factory=list)      # 20 from Quran Chunk Search
    bible_semantic: List = field(default_factory=list)    # 20 from Bible Semantic Search
    bible_chunks: List = field(default_factory=list)      # 20 from Bible Chunk Search
    search_stats: Dict = field(default_factory=dict)      # Timing, counts per source
    
    @property
    def total_verses(self) -> int:
        return (
            len(self.quran_semantic) + len(self.quran_chunks) +
            len(self.bible_semantic) + len(self.bible_chunks)
        )


class ComparativeRAG:
    """
    Multi-Scripture RAG Pipeline
    
    Executes 4 parallel searches (2 scriptures × 2 search types),
    reranks each set of 20, and generates comparative theological essay.
    
    Args:
        qdrant_url: Qdrant server URL
        bible_translation: Bible translation to use (default: "kjva")
        verses_per_search: Number of verses per search type (default: 20)
        verbose: Print progress messages
    """
    
    def __init__(
        self,
        qdrant_url: str = "http://localhost:6333",
        bible_translation: str = "kjva",
        verses_per_search: int = 20,
        verbose: bool = True
    ):
        self.qdrant_url = qdrant_url
        self.bible_translation = bible_translation
        self.verses_per_search = verses_per_search
        self.verbose = verbose
        
        # Lazy load components
        self._enhancer = None
        self._reranker = None
        self._answer_generator = None
        self._quran_searcher = None
        self._bible_searcher = None
        self._quran_chunk_searcher = None
        self._bible_chunk_searcher = None
    
    @property
    def enhancer(self):
        """Lazy load Query Enhancer"""
        if self._enhancer is None:
            from src.query_enhancer import QueryEnhancer
            self._enhancer = QueryEnhancer()
            if self.verbose:
                console.print("[dim]Loaded QueryEnhancer[/dim]")
        return self._enhancer
    
    @property
    def reranker(self):
        """Lazy load Reranker"""
        if self._reranker is None:
            from src.reranker import Reranker
            self._reranker = Reranker()
            if self.verbose:
                console.print("[dim]Loaded Qwen3-Reranker[/dim]")
        return self._reranker
    
    @property
    def answer_generator(self):
        """Lazy load Comparative Answer Generator"""
        if self._answer_generator is None:
            from src.comparative_answer_generator import ComparativeAnswerGenerator
            self._answer_generator = ComparativeAnswerGenerator()
            if self.verbose:
                console.print("[dim]Loaded ComparativeAnswerGenerator (Gemini 2.5 Flash)[/dim]")
        return self._answer_generator
    
    def _get_quran_searcher(self):
        """Get Quran searcher (lazy load)"""
        if self._quran_searcher is None:
            from src.search import QuranSearcher
            self._quran_searcher = QuranSearcher(qdrant_url=self.qdrant_url)
        return self._quran_searcher
    
    def _get_bible_searcher(self):
        """Get Bible searcher (lazy load)"""
        if self._bible_searcher is None:
            from src.search import BibleSearcher
            self._bible_searcher = BibleSearcher(
                translation=self.bible_translation,
                qdrant_url=self.qdrant_url
            )
        return self._bible_searcher
    
    def _get_quran_chunk_searcher(self):
        """Get Quran semantic chunk searcher (lazy load)"""
        if self._quran_chunk_searcher is None:
            from src.search import SemanticChunkSearcher
            self._quran_chunk_searcher = SemanticChunkSearcher(qdrant_url=self.qdrant_url)
        return self._quran_chunk_searcher
    
    def _get_bible_chunk_searcher(self):
        """Get Bible semantic chunk searcher (lazy load)"""
        if self._bible_chunk_searcher is None:
            from src.search import BibleSemanticChunkSearcher
            self._bible_chunk_searcher = BibleSemanticChunkSearcher(
                translation=self.bible_translation,
                qdrant_url=self.qdrant_url
            )
        return self._bible_chunk_searcher
    
    def _log(self, message: str, style: str = "dim"):
        """Log message if verbose"""
        if self.verbose:
            console.print(f"[{style}]{message}[/{style}]")
    
    def _enhance_query_parallel(self, query: str) -> Tuple[str, str]:
        """
        Step 1: Enhance query for both scriptures in parallel
        
        Returns:
            (quran_enhanced, bible_enhanced) tuple
        """
        self._log("⚡ Step 1: Parallel Query Enhancement...")
        start = time.time()
        
        def enhance_quran():
            return self.enhancer.expand_query(query, corpus="quran")
        
        def enhance_bible():
            return self.enhancer.expand_query(query, corpus="bible")
        
        with ThreadPoolExecutor(max_workers=2) as executor:
            quran_future = executor.submit(enhance_quran)
            bible_future = executor.submit(enhance_bible)
            
            quran_enhanced = quran_future.result()
            bible_enhanced = bible_future.result()
        
        duration = (time.time() - start) * 1000
        self._log(f"   Quran: {quran_enhanced[:60]}...")
        self._log(f"   Bible: {bible_enhanced[:60]}...")
        self._log(f"   Enhanced in {duration:.0f}ms")
        
        return quran_enhanced, bible_enhanced
    
    def _search_single(
        self, 
        searcher, 
        query: str, 
        limit: int,
        search_name: str
    ) -> List:
        """Execute a single search"""
        try:
            results = searcher.search(query, mode="semantic", limit=limit)
            return results
        except Exception as e:
            self._log(f"   Warning: {search_name} failed: {e}", "yellow")
            return []
    
    def _search_all_parallel(
        self, 
        quran_query: str, 
        bible_query: str,
        pool_size: int = 50
    ) -> Tuple[List, List, List, List]:
        """
        Step 2: Execute 4 parallel searches
        
        Args:
            quran_query: Enhanced query for Quran
            bible_query: Enhanced query for Bible
            pool_size: Results per search before reranking
            
        Returns:
            (quran_semantic, quran_chunks, bible_semantic, bible_chunks)
        """
        self._log(f"🔍 Step 2: Executing 4 parallel searches...")
        start = time.time()
        
        results = {
            "quran_semantic": [],
            "quran_chunks": [],
            "bible_semantic": [],
            "bible_chunks": []
        }
        
        def search_quran_semantic():
            searcher = self._get_quran_searcher()
            return ("quran_semantic", self._search_single(
                searcher, quran_query, pool_size, "Quran Semantic"
            ))
        
        def search_quran_chunks():
            searcher = self._get_quran_chunk_searcher()
            if searcher.collection_exists():
                return ("quran_chunks", self._search_single(
                    searcher, quran_query, pool_size, "Quran Chunks"
                ))
            return ("quran_chunks", [])
        
        def search_bible_semantic():
            searcher = self._get_bible_searcher()
            return ("bible_semantic", self._search_single(
                searcher, bible_query, pool_size, "Bible Semantic"
            ))
        
        def search_bible_chunks():
            searcher = self._get_bible_chunk_searcher()
            if searcher.collection_exists():
                return ("bible_chunks", self._search_single(
                    searcher, bible_query, pool_size, "Bible Chunks"
                ))
            return ("bible_chunks", [])
        
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = [
                executor.submit(search_quran_semantic),
                executor.submit(search_quran_chunks),
                executor.submit(search_bible_semantic),
                executor.submit(search_bible_chunks)
            ]
            
            for future in as_completed(futures):
                key, result = future.result()
                results[key] = result
        
        duration = (time.time() - start) * 1000
        
        counts = {k: len(v) for k, v in results.items()}
        self._log(f"   Quran Semantic: {counts['quran_semantic']}, Quran Chunks: {counts['quran_chunks']}")
        self._log(f"   Bible Semantic: {counts['bible_semantic']}, Bible Chunks: {counts['bible_chunks']}")
        self._log(f"   Searches completed in {duration:.0f}ms")
        
        return (
            results["quran_semantic"],
            results["quran_chunks"],
            results["bible_semantic"],
            results["bible_chunks"]
        )
    
    def _rerank_each(
        self,
        quran_query: str,
        bible_query: str,
        quran_semantic: List,
        quran_chunks: List,
        bible_semantic: List,
        bible_chunks: List
    ) -> Tuple[List, List, List, List]:
        """
        Step 3: Rerank each set of results separately (20 each)
        
        Each scripture's results are reranked with their respective query.
        """
        self._log(f"🏆 Step 3: Reranking each result set to top {self.verses_per_search}...")
        start = time.time()
        
        def rerank_set(query: str, results: List, name: str) -> List:
            if not results:
                return []
            try:
                return self.reranker.rerank(query, results, top_k=self.verses_per_search)
            except Exception as e:
                self._log(f"   Warning: Rerank {name} failed: {e}", "yellow")
                return results[:self.verses_per_search]
        
        # Rerank each set
        quran_semantic_reranked = rerank_set(quran_query, quran_semantic, "Quran Semantic")
        quran_chunks_reranked = rerank_set(quran_query, quran_chunks, "Quran Chunks")
        bible_semantic_reranked = rerank_set(bible_query, bible_semantic, "Bible Semantic")
        bible_chunks_reranked = rerank_set(bible_query, bible_chunks, "Bible Chunks")
        
        duration = (time.time() - start) * 1000
        total = (
            len(quran_semantic_reranked) + len(quran_chunks_reranked) +
            len(bible_semantic_reranked) + len(bible_chunks_reranked)
        )
        self._log(f"   Reranked to {total} total verses in {duration:.0f}ms")
        
        return (
            quran_semantic_reranked,
            quran_chunks_reranked,
            bible_semantic_reranked,
            bible_chunks_reranked
        )
    
    def search_all(self, query: str) -> ComparativeScriptureResult:
        """
        Execute full search pipeline without answer generation.
        
        Returns 80 verses (20 per search type × 4 searches), all reranked.
        """
        total_start = time.time()
        
        if self.verbose:
            console.print(f"\n[bold blue]🔄 Comparative Search Pipeline[/bold blue]")
            console.print(f"[dim]Query: \"{query}\"[/dim]\n")
        
        # Step 1: Parallel query enhancement
        quran_query, bible_query = self._enhance_query_parallel(query)
        
        # Step 2: 4 parallel searches
        quran_sem, quran_chunks, bible_sem, bible_chunks = self._search_all_parallel(
            quran_query, bible_query, pool_size=50
        )
        
        # Step 3: Rerank each set
        quran_sem, quran_chunks, bible_sem, bible_chunks = self._rerank_each(
            quran_query, bible_query,
            quran_sem, quran_chunks, bible_sem, bible_chunks
        )
        
        total_duration = (time.time() - total_start) * 1000
        
        result = ComparativeScriptureResult(
            quran_semantic=quran_sem,
            quran_chunks=quran_chunks,
            bible_semantic=bible_sem,
            bible_chunks=bible_chunks,
            search_stats={
                "duration_ms": total_duration,
                "quran_query": quran_query,
                "bible_query": bible_query
            }
        )
        
        if self.verbose:
            console.print(f"\n[green]✓ Search complete: {result.total_verses} verses in {total_duration:.0f}ms[/green]\n")
        
        return result
    
    def compare(self, query: str):
        """
        Full comparative pipeline: Search + Generate Comparative Essay
        
        Args:
            query: User's religious/philosophical question
            
        Returns:
            ComparativeAnswer with essay, citations, and confidence
        """
        total_start = time.time()
        
        if self.verbose:
            console.print(f"\n[bold blue]📚 Comparative Scripture Analysis[/bold blue]")
            console.print(f"[dim]Question: \"{query}\"[/dim]\n")
        
        # Steps 1-3: Search and rerank
        search_result = self.search_all(query)
        
        # Step 4: Generate comparative essay
        self._log("📝 Step 4: Generating comparative theological essay...")
        essay_start = time.time()
        
        answer = self.answer_generator.generate_comparative_answer(
            query=query,
            quran_semantic=search_result.quran_semantic,
            quran_chunks=search_result.quran_chunks,
            bible_semantic=search_result.bible_semantic,
            bible_chunks=search_result.bible_chunks
        )
        
        essay_duration = (time.time() - essay_start) * 1000
        total_duration = (time.time() - total_start) * 1000
        
        if self.verbose:
            self._log(f"   Essay generated in {essay_duration:.0f}ms")
            console.print(f"\n[green]✨ Analysis complete in {total_duration:.0f}ms[/green]")
            console.print(f"[dim]  {search_result.total_verses} verses → {len(answer.all_references)} citations → confidence: {answer.confidence:.0%}[/dim]\n")
        
        return answer


# Convenience function
def comparative_search(query: str) -> ComparativeScriptureResult:
    """One-liner for comparative scripture search"""
    rag = ComparativeRAG(verbose=True)
    return rag.search_all(query)


def comparative_analysis(query: str):
    """One-liner for full comparative analysis"""
    rag = ComparativeRAG(verbose=True)
    return rag.compare(query)


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    
    console.print("[bold]Testing Comparative Scripture RAG[/bold]\n")
    
    rag = ComparativeRAG()
    
    test_query = "What do the scriptures say about patience and perseverance?"
    result = rag.compare(test_query)
    
    console.print("\n[bold cyan]═══ COMPARATIVE ESSAY ═══[/bold cyan]\n")
    console.print(result.essay)
    
    console.print("\n[bold cyan]═══ REFERENCES ═══[/bold cyan]")
    for i, ref in enumerate(result.all_references, 1):
        console.print(f"  {i}. {ref}")
