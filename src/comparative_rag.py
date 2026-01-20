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
    """Combined results from all scripture searches - 80 verses total (20 per testament)"""
    quran: List = field(default_factory=list)       # 20 from Quran
    ot: List = field(default_factory=list)          # 20 from Old Testament
    nt: List = field(default_factory=list)          # 20 from New Testament
    apocrypha: List = field(default_factory=list)   # 20 from Apocrypha
    search_stats: Dict = field(default_factory=dict)  # Timing, counts per source
    
    @property
    def total_verses(self) -> int:
        return len(self.quran) + len(self.ot) + len(self.nt) + len(self.apocrypha)


class ComparativeRAG:
    """
    Multi-Scripture RAG Pipeline
    
    Executes 4 parallel searches (2 scriptures × 2 search types),
    executes 4 parallel searches, and generates comparative theological essay.
    
    Args:
        qdrant_url: Qdrant server URL
        bible_translation: Bible translation to use (default: "kjva")
        verses_per_search: Number of verses per search type (default: 20)
        enable_multi_query: Use 5 queries + RRF fusion for better accuracy (default: False)
        verbose: Print progress messages
    """
    
    def __init__(
        self,
        qdrant_url: str = "http://localhost:6333",
        bible_translation: str = "kjva",
        verses_per_search: int = 20,
        enable_multi_query: bool = True,  # Multi-Query + RRF for maximum accuracy
        verbose: bool = True
    ):
        self.qdrant_url = qdrant_url
        self.bible_translation = bible_translation
        self.verses_per_search = verses_per_search
        self.enable_multi_query = enable_multi_query
        self.verbose = verbose
        
        # Lazy load components
        self._enhancer = None
        self._answer_generator = None
        self._quran_searcher = None
        # Testament-specific Bible searchers (replaces single _bible_searcher)
        self._ot_searcher = None
        self._nt_searcher = None
        self._apocrypha_searcher = None
    
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
    
    def _get_ot_searcher(self):
        """Get Old Testament searcher (lazy load)"""
        if self._ot_searcher is None:
            from src.search import BibleSearcher
            self._ot_searcher = BibleSearcher(
                testament="ot",
                qdrant_url=self.qdrant_url
            )
        return self._ot_searcher
    
    def _get_nt_searcher(self):
        """Get New Testament searcher (lazy load)"""
        if self._nt_searcher is None:
            from src.search import BibleSearcher
            self._nt_searcher = BibleSearcher(
                testament="nt",
                qdrant_url=self.qdrant_url
            )
        return self._nt_searcher
    
    def _get_apocrypha_searcher(self):
        """Get Apocrypha searcher (lazy load)"""
        if self._apocrypha_searcher is None:
            from src.search import BibleSearcher
            self._apocrypha_searcher = BibleSearcher(
                testament="apocrypha",
                qdrant_url=self.qdrant_url
            )
        return self._apocrypha_searcher
    
    def _log(self, message: str, style: str = "dim"):
        """Log message if verbose"""
        if self.verbose:
            console.print(f"[{style}]{message}[/{style}]")
    
    # ==================== MULTI-QUERY SUPPORT ====================
    
    def _rrf_fusion(self, results_list: List[List], k: int = 60) -> List:
        """
        Reciprocal Rank Fusion - combine multiple ranked result lists.
        
        Results appearing in multiple lists get boosted scores.
        Formula: RRF_score = sum(1 / (k + rank)) across all lists
        
        Args:
            results_list: List of result lists from different queries
            k: Smoothing constant (default 60)
            
        Returns:
            Merged and sorted list of results by RRF score
        """
        rrf_scores = {}  # id -> (result, score)
        
        for results in results_list:
            for rank, result in enumerate(results, 1):
                # Get unique ID
                rid = getattr(result, 'id', None) or getattr(result, 'chunk_id', None) or id(result)
                rrf_contribution = 1 / (k + rank)
                
                if rid in rrf_scores:
                    existing_result, existing_score = rrf_scores[rid]
                    rrf_scores[rid] = (existing_result, existing_score + rrf_contribution)
                else:
                    rrf_scores[rid] = (result, rrf_contribution)
        
        # Sort by RRF score descending
        sorted_results = sorted(rrf_scores.values(), key=lambda x: x[1], reverse=True)
        return [item[0] for item in sorted_results]
    
    def _generate_multi_queries(self, query: str, corpus: str, n: int = 3) -> List[str]:
        """
        Generate multiple query variations for a corpus.
        
        Returns: [original, enhanced, multi_1, multi_2, multi_3] (deduplicated)
        """
        queries = [query]
        
        try:
            # Enhanced query
            enhanced = self.enhancer.expand_query(query, corpus=corpus)
            queries.append(enhanced)
            
            # Multi-query perspectives
            multi = self.enhancer.generate_multi_query(enhanced, n=n, corpus=corpus)
            queries.extend(multi)
        except Exception as e:
            self._log(f"   Warning: Multi-query generation failed: {e}", "yellow")
        
        # Deduplicate while preserving order
        seen = set()
        unique = []
        for q in queries:
            q_lower = q.lower().strip()
            if q_lower not in seen:
                seen.add(q_lower)
                unique.append(q)
        
        return unique[:5]  # Max 5 queries
    
    def _search_quadrant_multi_query(
        self,
        queries: List[str],
        searcher,
        limit_per_query: int = 30
    ) -> List:
        """
        Execute multiple queries on a single searcher and merge with RRF.
        
        This is the core Multi-Query search logic for one quadrant.
        All queries run in parallel, then results are fused.
        """
        all_results = []
        
        def search_single_query(q):
            try:
                return searcher.search(q, mode="semantic", limit=limit_per_query)
            except Exception:
                return []
        
        # Parallel execution of all queries
        with ThreadPoolExecutor(max_workers=len(queries)) as executor:
            futures = [executor.submit(search_single_query, q) for q in queries]
            for future in as_completed(futures):
                result = future.result()
                if result:
                    all_results.append(result)
        
        # Merge with RRF
        if all_results:
            return self._rrf_fusion(all_results)
        return []
    
    def _search_all_multi_query(
        self,
        quran_queries: List[str],
        bible_queries: List[str],
        pool_size: int = 20
    ) -> Tuple[List, List, List, List]:
        """
        Step 2 (Multi-Query Version): Execute 4 testament searches with multi-query + RRF.
        
        Searches: Quran, Old Testament, New Testament, Apocrypha
        Each returns up to pool_size results.
        """
        self._log(f"🔍 Step 2: Multi-Query Search ({len(quran_queries)}q×4 collections)...")
        start = time.time()
        
        results = {
            "quran": [],
            "ot": [],
            "nt": [],
            "apocrypha": []
        }
        
        def search_quran():
            searcher = self._get_quran_searcher()
            return ("quran", self._search_quadrant_multi_query(
                quran_queries, searcher, limit_per_query=30
            )[:pool_size])
        
        def search_ot():
            searcher = self._get_ot_searcher()
            return ("ot", self._search_quadrant_multi_query(
                bible_queries, searcher, limit_per_query=30
            )[:pool_size])
        
        def search_nt():
            searcher = self._get_nt_searcher()
            return ("nt", self._search_quadrant_multi_query(
                bible_queries, searcher, limit_per_query=30
            )[:pool_size])
        
        def search_apocrypha():
            searcher = self._get_apocrypha_searcher()
            return ("apocrypha", self._search_quadrant_multi_query(
                bible_queries, searcher, limit_per_query=30
            )[:pool_size])
        
        # All 4 collections in parallel
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = [
                executor.submit(search_quran),
                executor.submit(search_ot),
                executor.submit(search_nt),
                executor.submit(search_apocrypha)
            ]
            
            for future in as_completed(futures):
                key, result = future.result()
                results[key] = result
        
        duration = (time.time() - start) * 1000
        
        counts = {k: len(v) for k, v in results.items()}
        self._log(f"   Quran: {counts['quran']}, OT: {counts['ot']}, NT: {counts['nt']}, Apoc: {counts['apocrypha']}")
        self._log(f"   Multi-Query searches completed in {duration:.0f}ms")
        
        return (
            results["quran"],
            results["ot"],
            results["nt"],
            results["apocrypha"]
        )
    
    # ==================== END MULTI-QUERY SUPPORT ====================
    
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
            pool_size: Results per search before selection
            
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
    
    def _select_top_results(
        self,
        quran_semantic: List,
        quran_chunks: List,
        bible_semantic: List,
        bible_chunks: List
    ) -> Tuple[List, List, List, List]:
        """
        Step 3: Select top results from each search (20 each)
        
        Results are already ranked by search relevance score.
        """
        self._log(f"📋 Step 3: Selecting top {self.verses_per_search} from each result set...")
        start = time.time()
        
        quran_semantic_top = quran_semantic[:self.verses_per_search]
        quran_chunks_top = quran_chunks[:self.verses_per_search]
        bible_semantic_top = bible_semantic[:self.verses_per_search]
        bible_chunks_top = bible_chunks[:self.verses_per_search]
        
        duration = (time.time() - start) * 1000
        total = (
            len(quran_semantic_top) + len(quran_chunks_top) +
            len(bible_semantic_top) + len(bible_chunks_top)
        )
        self._log(f"   Selected {total} total verses in {duration:.0f}ms")
        
        return (
            quran_semantic_top,
            quran_chunks_top,
            bible_semantic_top,
            bible_chunks_top
        )
    
    def search_all(self, query: str) -> ComparativeScriptureResult:
        """
        Execute full search pipeline without answer generation.
        
        Returns 80 verses (20 per testament × 4 collections: Quran, OT, NT, Apocrypha).
        
        If enable_multi_query=True: Uses 5 queries + RRF fusion for better accuracy.
        If enable_multi_query=False: Uses single enhanced query (faster).
        """
        total_start = time.time()
        
        mode_label = "Multi-Query" if self.enable_multi_query else "Single-Query"
        
        if self.verbose:
            console.print(f"\n[bold blue]🔄 Comparative Search Pipeline ({mode_label})[/bold blue]")
            console.print(f"[dim]Query: \"{query}\"[/dim]\n")
        
        if self.enable_multi_query:
            # ===== MULTI-QUERY PATH (5 queries + RRF) =====
            self._log("⚡ Step 1: Generating Multi-Queries...")
            start = time.time()
            
            # Generate query variations in parallel
            def gen_quran():
                return self._generate_multi_queries(query, corpus="quran", n=3)
            def gen_bible():
                return self._generate_multi_queries(query, corpus="bible", n=3)
            
            with ThreadPoolExecutor(max_workers=2) as executor:
                quran_future = executor.submit(gen_quran)
                bible_future = executor.submit(gen_bible)
                quran_queries = quran_future.result()
                bible_queries = bible_future.result()
            
            duration = (time.time() - start) * 1000
            self._log(f"   Quran: {len(quran_queries)} queries, Bible: {len(bible_queries)} queries")
            self._log(f"   Generated in {duration:.0f}ms")
            
            # Step 2: Multi-query search with RRF fusion - now returns (quran, ot, nt, apocrypha)
            quran_results, ot_results, nt_results, apocrypha_results = self._search_all_multi_query(
                quran_queries, bible_queries, pool_size=20
            )
            
            quran_query = query
            bible_query = query
            
        else:
            # ===== SINGLE-QUERY PATH =====
            # Step 1: Parallel query enhancement
            quran_query, bible_query = self._enhance_query_parallel(query)
            
            # Step 2: 4 parallel testament searches (fallback for single query mode)
            self._log("🔍 Step 2: Parallel Testament Searches...")
            start = time.time()
            
            def search_quran():
                return self._get_quran_searcher().search(quran_query, mode="semantic", limit=20)
            def search_ot():
                return self._get_ot_searcher().search(bible_query, mode="semantic", limit=20)
            def search_nt():
                return self._get_nt_searcher().search(bible_query, mode="semantic", limit=20)
            def search_apocrypha():
                return self._get_apocrypha_searcher().search(bible_query, mode="semantic", limit=20)
            
            with ThreadPoolExecutor(max_workers=4) as executor:
                futures = {
                    executor.submit(search_quran): "quran",
                    executor.submit(search_ot): "ot",
                    executor.submit(search_nt): "nt",
                    executor.submit(search_apocrypha): "apocrypha"
                }
                results = {}
                for future in as_completed(futures):
                    key = futures[future]
                    results[key] = future.result()
            
            quran_results = results["quran"]
            ot_results = results["ot"]
            nt_results = results["nt"]
            apocrypha_results = results["apocrypha"]
            
            duration = (time.time() - start) * 1000
            self._log(f"   Quran: {len(quran_results)}, OT: {len(ot_results)}, NT: {len(nt_results)}, Apoc: {len(apocrypha_results)}")
            self._log(f"   Searches completed in {duration:.0f}ms")
        
        total_duration = (time.time() - total_start) * 1000
        
        result = ComparativeScriptureResult(
            quran=quran_results,
            ot=ot_results,
            nt=nt_results,
            apocrypha=apocrypha_results,
            search_stats={
                "duration_ms": total_duration,
                "quran_query": quran_query,
                "bible_query": bible_query,
                "mode": mode_label
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
        
        # Steps 1-3: Search and select top results
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
    
    # ==================== MULTI-AGENT SUPPORT ====================
    
    def _split_bible_by_testament(self, results: List) -> Tuple[List, List, List]:
        """
        Split Bible results into Old Testament, New Testament, and Apocrypha.
        
        Args:
            results: List of Bible search results
            
        Returns:
            (ot_results, nt_results, apocrypha_results) tuple
        """
        ot_results = []
        nt_results = []
        apocrypha_results = []
        
        for r in results:
            testament = getattr(r, 'testament', None)
            if testament is None and hasattr(r, 'payload'):
                testament = r.payload.get('testament', '')
            
            if testament == 'OT':
                ot_results.append(r)
            elif testament == 'NT':
                nt_results.append(r)
            elif testament == 'Apocrypha':
                apocrypha_results.append(r)
            else:
                # Default to OT for unknown
                ot_results.append(r)
        
        return ot_results, nt_results, apocrypha_results
    
    @property
    def multi_agent_generator(self):
        """Lazy load Multi-Agent Answer Generator"""
        if not hasattr(self, '_multi_agent_generator') or self._multi_agent_generator is None:
            from src.multi_agent_answer_generator import MultiAgentOrchestrator
            self._multi_agent_generator = MultiAgentOrchestrator(verbose=self.verbose)
            if self.verbose:
                console.print("[dim]Loaded MultiAgentOrchestrator (4 specialists + summary)[/dim]")
        return self._multi_agent_generator
    
    def compare_multi_agent(self, query: str):
        """
        Full comparative pipeline with Multi-Agent answer generation.
        
        Uses 4 testament-specific searches (Quran, OT, NT, Apocrypha) in parallel,
        each returning 20 verses. Then runs 4 specialist agents + 1 summary agent.
        
        Args:
            query: User's religious/philosophical question
            
        Returns:
            MultiAgentAnswer with 5 paragraphs (OT, NT, Apocrypha, Quran, Synthesis)
        """
        total_start = time.time()
        
        if self.verbose:
            console.print(f"\n[bold blue]📚 Multi-Agent Comparative Scripture Analysis[/bold blue]")
            console.print(f"[dim]Question: \"{query}\"[/dim]\n")
        
        # Steps 1-2: Search all 4 collections (now pre-separated by testament)
        search_result = self.search_all(query)
        
        # Results are now directly available per testament - no splitting needed!
        quran_verses = search_result.quran
        ot_verses = search_result.ot
        nt_verses = search_result.nt
        apocrypha_verses = search_result.apocrypha
        
        self._log(f"📋 Verses: Quran={len(quran_verses)}, OT={len(ot_verses)}, "
                  f"NT={len(nt_verses)}, Apoc={len(apocrypha_verses)}")
        
        # Step 3: Multi-agent generation
        self._log("📝 Step 3: Running 4 specialist agents + summary agent...")
        gen_start = time.time()
        
        answer = self.multi_agent_generator.generate(
            query=query,
            quran_verses=quran_verses,
            ot_verses=ot_verses,
            nt_verses=nt_verses,
            apocrypha_verses=apocrypha_verses
        )
        
        gen_duration = (time.time() - gen_start) * 1000
        total_duration = (time.time() - total_start) * 1000
        
        if self.verbose:
            self._log(f"   Multi-agent generation completed in {gen_duration:.0f}ms")
            console.print(f"\n[green]✨ Multi-Agent Analysis complete in {total_duration:.0f}ms[/green]")
            total_citations = sum(len(c) for c in answer.citations.values())
            console.print(f"[dim]  {search_result.total_verses} verses → 5 paragraphs → "
                          f"{total_citations} citations → confidence: {answer.confidence:.0%}[/dim]\n")
        
        return answer


# Convenience function
def comparative_search(query: str) -> ComparativeScriptureResult:
    """One-liner for comparative scripture search"""
    rag = ComparativeRAG(verbose=True)
    return rag.search_all(query)


def comparative_analysis(query: str):
    """One-liner for full comparative analysis (single essay)"""
    rag = ComparativeRAG(verbose=True)
    return rag.compare(query)


def multi_agent_analysis(query: str):
    """
    One-liner for multi-agent comparative analysis.
    
    Returns 5 paragraphs: OT, NT, Apocrypha, Quran, Synthesis
    """
    rag = ComparativeRAG(verbose=True)
    return rag.compare_multi_agent(query)


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
