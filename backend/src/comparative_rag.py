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

import time
import logging
from typing import List, Optional, Dict, Tuple, Callable
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor, as_completed
from rich.console import Console

from src.circuit_breaker import CircuitBreakerError
from src.query_translator import QueryTranslator, TranslationResult, TranslationError
from src.query_translator import CORPUS_LANGUAGES

console = Console()
logger = logging.getLogger(__name__)


@dataclass
class ComparativeScriptureResult:
    """Combined results from all scripture searches - 80 verses total (20 per testament)"""

    quran: List = field(default_factory=list)  # 20 from Quran
    ot: List = field(default_factory=list)  # 20 from Old Testament
    nt: List = field(default_factory=list)  # 20 from New Testament
    apocrypha: List = field(default_factory=list)  # 20 from Apocrypha
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
        verbose: bool = True,
    ):
        self.qdrant_url = qdrant_url
        self.bible_translation = bible_translation
        self.verses_per_search = verses_per_search
        self.enable_multi_query = enable_multi_query
        self.verbose = verbose

        # Lazy load components
        self._enhancer = None
        self._translator = None
        self._answer_generator = None
        self._quran_searcher = None
        # Testament-specific Bible searchers (replaces single _bible_searcher)
        self._ot_searcher = None
        self._nt_searcher = None
        self._apocrypha_searcher = None

        # Per-collection result statistics for confidence scoring
        self._last_collection_stats: dict = {}
        # Detected user language from last query (for response translation)
        self._last_detected_language: Optional[str] = None

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
    def translator(self):
        """Lazy load Query Translator"""
        if self._translator is None:
            self._translator = QueryTranslator()
            if self.verbose:
                console.print("[dim]Loaded QueryTranslator[/dim]")
        return self._translator

    @property
    def answer_generator(self):
        """Lazy load Comparative Answer Generator"""
        if self._answer_generator is None:
            from src.comparative_answer_generator import ComparativeAnswerGenerator

            self._answer_generator = ComparativeAnswerGenerator()
            if self.verbose:
                console.print(
                    "[dim]Loaded ComparativeAnswerGenerator (Gemini 2.5 Flash)[/dim]"
                )
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
                testament="ot", qdrant_url=self.qdrant_url
            )
        return self._ot_searcher

    def _get_nt_searcher(self):
        """Get New Testament searcher (lazy load)"""
        if self._nt_searcher is None:
            from src.search import BibleSearcher

            self._nt_searcher = BibleSearcher(
                testament="nt", qdrant_url=self.qdrant_url
            )
        return self._nt_searcher

    def _get_apocrypha_searcher(self):
        """Get Apocrypha searcher (lazy load)"""
        if self._apocrypha_searcher is None:
            from src.search import BibleSearcher

            self._apocrypha_searcher = BibleSearcher(
                testament="apocrypha", qdrant_url=self.qdrant_url
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
                rid = (
                    getattr(result, "id", None)
                    or getattr(result, "chunk_id", None)
                    or id(result)
                )
                rrf_contribution = 1 / (k + rank)

                if rid in rrf_scores:
                    existing_result, existing_score = rrf_scores[rid]
                    rrf_scores[rid] = (
                        existing_result,
                        existing_score + rrf_contribution,
                    )
                else:
                    rrf_scores[rid] = (result, rrf_contribution)

        # Sort by RRF score descending
        sorted_results = sorted(rrf_scores.values(), key=lambda x: x[1], reverse=True)
        return [item[0] for item in sorted_results]

    def _generate_multi_queries(self, query: str, corpus: str, n: int = 3) -> List[str]:
        """
        Generate multiple query variations for a corpus.

        OPTIMIZED: enhance + multi-query run in PARALLEL (was sequential).
        Multi-query uses original query instead of waiting for enhanced.
        Enhanced query is merged into the final list.

        Returns: [original, enhanced, multi_1, multi_2, multi_3] (deduplicated)
        """
        queries = [query]

        try:
            # Run enhance + multi-query in PARALLEL
            with ThreadPoolExecutor(max_workers=2) as executor:
                enhance_future = executor.submit(
                    self.enhancer.expand_query, query, corpus
                )
                multi_future = executor.submit(
                    self.enhancer.generate_multi_query, query, n, corpus
                )

                enhanced = enhance_future.result()
                multi = multi_future.result()

            queries.append(enhanced)
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
        self, queries: List[str], searcher, limit_per_query: int = 30
    ) -> List:
        """
        Execute multiple queries on a single searcher and merge with RRF.

        OPTIMIZED: All queries are batch-encoded in a single API call,
        then Qdrant searches use pre-computed vectors (no per-query embedding).
        """
        all_results = []

        # Batch encode ALL queries in one API call (was: N individual encode calls)
        if not hasattr(self, "_dense_encoder") or self._dense_encoder is None:
            from src.embeddings import DenseEncoder

            self._dense_encoder = DenseEncoder()

        vectors = self._dense_encoder.encode_batch(
            queries, batch_size=len(queries), show_progress=False
        )

        def search_with_vector(vector):
            try:
                return searcher.search_with_vector(vector, limit=limit_per_query)
            except CircuitBreakerError:
                logger.warning(
                    "Qdrant unavailable (circuit breaker open), returning empty results",
                )
                return []
            except Exception:
                return []

        # Parallel Qdrant searches with pre-computed vectors
        with ThreadPoolExecutor(max_workers=len(queries)) as executor:
            futures = [executor.submit(search_with_vector, v) for v in vectors]
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
        pool_size: int = 20,
        collections: Optional[List[str]] = None,
    ) -> Tuple[List, List, List, List]:
        """
        Step 2 (Multi-Query Version): Execute testament searches with multi-query + RRF.

        Searches only the specified collections (default: all 4).
        Each returns up to pool_size results.

        Args:
            quran_queries: Query variations for Quran search
            bible_queries: Query variations for Bible search
            pool_size: Max results per collection
            collections: List of collections to search. If None, searches all 4.
                        Valid values: 'quran_tr', 'bible_ot', 'bible_nt', 'bible_apocrypha'
        """
        import sentry_sdk

        # Default to all collections if not specified
        if collections is None:
            collections = ["quran_tr_diyanet", "bible_ot", "bible_nt", "bible_apocrypha"]

        def search_all(
        self,
        query: str,
        collections: Optional[List[str]] = None,
        progress_callback: Optional[Callable[[str, str], None]] = None,
        quran_keywords: Optional[List[str]] = None,
        bible_keywords: Optional[List[str]] = None,
    ) -> ComparativeScriptureResult:
        """
        Execute full search pipeline without answer generation.

        Returns up to 80 verses (20 per collection) from specified collections.

        Args:
            query: The search query
            collections: List of collections to search. If None, searches all 4.
                        Valid values: 'quran_tr', 'bible_ot', 'bible_nt', 'bible_apocrypha'
            progress_callback: Optional callback(step_id, message) for streaming progress.
                              Called at each pipeline stage to report progress.
            quran_keywords: Optional list of Turkish keywords for Quran per-keyword search
            bible_keywords: Optional list of English keywords for Bible per-keyword search

        If enable_multi_query=True: Uses 5 queries + RRF fusion for better accuracy.
        If enable_multi_query=False: Uses single enhanced query (faster).

        If quran_keywords or bible_keywords are provided, per-keyword search results
        are merged with normal results using RRF fusion.

        Translation is applied first: the user's query is translated to Turkish
        (for Quran) and English (for Bible) before any enhancement or search.
        The detected source language is stored in ``search_stats`` for downstream
        response translation.
        """
        # Default to all collections if not specified
        if collections is None:
            collections = ["quran_tr_diyanet", "bible_ot", "bible_nt", "bible_apocrypha"]
        total_start = time.time()

        def _emit(step_id: str, message: str):
            if progress_callback:
                try:
                    progress_callback(step_id, message)
                except Exception:
                    pass  # Never let callback errors break the pipeline

        mode_label = "Multi-Query" if self.enable_multi_query else "Single-Query"

        if self.verbose:
            console.print(
                f"\n[bold blue]🔄 Comparative Search Pipeline ({mode_label})[/bold blue]"
            )
            console.print(f'[dim]Query: "{query}"[/dim]\n')

        # ===== Step 0: Translate query for both corpora =====
        _emit("translating_query", "Translating query for Quran (TR) and Bible (EN)...")
        quran_translated, bible_translated, detected_language = (
            self._translate_query_parallel(query)
        )
        _emit(
            "query_translated",
            f'Query translated — Quran: "{quran_translated[:60]}" / Bible: "{bible_translated[:60]}"',
        )

        if self.enable_multi_query:
            # ===== MULTI-QUERY PATH (5 queries + RRF) =====
            _emit(
                "generating_queries", "Enhancing & generating multi-query variants..."
            )
            self._log("⚡ Step 1: Generating Multi-Queries...")
            start = time.time()

            # Generate query variations in parallel (using translated queries)
            def gen_quran():
                return self._generate_multi_queries(
                    quran_translated, corpus="quran", n=3
                )

            def gen_bible():
                return self._generate_multi_queries(
                    bible_translated, corpus="bible", n=3
                )

            with ThreadPoolExecutor(max_workers=2) as executor:
                quran_future = executor.submit(gen_quran)
                bible_future = executor.submit(gen_bible)
                quran_queries = quran_future.result()
                bible_queries = bible_future.result()

            duration = (time.time() - start) * 1000
            self._log(
                f"   Quran: {len(quran_queries)} queries, Bible: {len(bible_queries)} queries"
            )
            self._log(f"   Generated in {duration:.0f}ms")
            _emit(
                "queries_generated",
                f"{len(quran_queries)} Quran + {len(bible_queries)} Bible query variants generated",
            )

            # Step 2: Multi-query search with RRF fusion - now returns (quran, ot, nt, apocrypha)
            total_queries = len(quran_queries) + len(bible_queries)
            _emit(
                "searching_vectors",
                f"Searching {len(collections)} collections ({total_queries} queries)...",
            )
            quran_results, ot_results, nt_results, apocrypha_results = (
                self._search_all_multi_query(
                    quran_queries, bible_queries, pool_size=20, collections=collections
                )
            )

            # Compute per-collection statistics for confidence scoring
            collection_results = {
                "quran": len(quran_results),
                "ot": len(ot_results),
                "nt": len(nt_results),
                "apocrypha": len(apocrypha_results),
            }
            collections_with_results = sum(
                1 for v in collection_results.values() if v > 0
            )
            total_verses = sum(collection_results.values())

            all_rrf_scores = sorted(
                [r.score for r in quran_results]
                + [r.score for r in ot_results]
                + [r.score for r in nt_results]
                + [r.score for r in apocrypha_results],
                reverse=True,
            )

            self._last_collection_stats = {
                "collection_results": collection_results,
                "collections_with_results": collections_with_results,
                "total_collections": 4,
                "total_verses": total_verses,
                "all_rrf_scores": all_rrf_scores,
                "num_queries": len(quran_queries),
            }
            _emit(
                "vectors_found",
                f"Found {total_verses} verses — Quran: {collection_results['quran']}, OT: {collection_results['ot']}, NT: {collection_results['nt']}, Apoc: {collection_results['apocrypha']}",
            )

            quran_query = quran_translated
            bible_query = bible_translated

        else:
            # ===== SINGLE-QUERY PATH =====
            # Step 1: Parallel query enhancement (using translated queries)
            _emit("generating_queries", "Enhancing query for search...")
            quran_query, bible_query = self._enhance_query_parallel(
                quran_translated, bible_translated
            )
            _emit("queries_generated", "Query enhanced for Quran and Bible corpora")

            # Map collection names to internal keys
            collection_to_key = {
                "quran_tr_diyanet": "quran",
                "quran_tr_yazir": "quran",
                "quran_tr_ates": "quran",
                "quran_tr_bulac": "quran",
                "quran_tr_ozturk": "quran",
                "quran_tr_vakfi": "quran",
                "quran_tr_yildirim": "quran",
                "quran_tr_yuksel": "quran",
                "bible_ot": "ot",
                "bible_nt": "nt",
                "bible_apocrypha": "apocrypha",
                "bible_tr_ot": "ot",
                "bible_tr_nt": "nt",
            }
            active_keys = [
                collection_to_key[c] for c in collections if c in collection_to_key
            ]

            # Step 2: Parallel testament searches (only active collections)
            _emit(
                "searching_vectors",
                f"Searching {len(active_keys)} collections...",
            )
            self._log(
                f"🔍 Step 2: Parallel Testament Searches ({len(active_keys)} collections)..."
            )
            start = time.time()

            def search_quran():
                return self._get_quran_searcher().search(
                    quran_query, mode="semantic", limit=20
                )

            def search_ot():
                return self._get_ot_searcher().search(
                    bible_query, mode="semantic", limit=20
                )

            def search_nt():
                return self._get_nt_searcher().search(
                    bible_query, mode="semantic", limit=20
                )

            def search_apocrypha():
                return self._get_apocrypha_searcher().search(
                    bible_query, mode="semantic", limit=20
                )

            # Map keys to search functions
            search_funcs = {
                "quran": search_quran,
                "ot": search_ot,
                "nt": search_nt,
                "apocrypha": search_apocrypha,
            }

            # Only search active collections
            with ThreadPoolExecutor(max_workers=len(active_keys)) as executor:
                futures = {
                    executor.submit(search_funcs[key]): key for key in active_keys
                }
                results = {"quran": [], "ot": [], "nt": [], "apocrypha": []}
                for future in as_completed(futures):
                    key = futures[future]
                    results[key] = future.result()

            quran_results = results["quran"]
            ot_results = results["ot"]
            nt_results = results["nt"]
            apocrypha_results = results["apocrypha"]

            # Compute per-collection statistics for confidence scoring
            collection_results = {
                "quran": len(quran_results),
                "ot": len(ot_results),
                "nt": len(nt_results),
                "apocrypha": len(apocrypha_results),
            }
            collections_with_results = sum(
                1 for v in collection_results.values() if v > 0
            )
            total_verses = sum(collection_results.values())

            all_rrf_scores = sorted(
                [r.score for r in quran_results]
                + [r.score for r in ot_results]
                + [r.score for r in nt_results]
                + [r.score for r in apocrypha_results],
                reverse=True,
            )

            self._last_collection_stats = {
                "collection_results": collection_results,
                "collections_with_results": collections_with_results,
                "total_collections": 4,
                "total_verses": total_verses,
                "all_rrf_scores": all_rrf_scores,
                "num_queries": 1,
            }
            _emit(
                "vectors_found",
                f"Found {total_verses} verses — Quran: {collection_results['quran']}, OT: {collection_results['ot']}, NT: {collection_results['nt']}, Apoc: {collection_results['apocrypha']}",
            )

            duration = (time.time() - start) * 1000
            self._log(
                f"   Quran: {len(quran_results)}, OT: {len(ot_results)}, NT: {len(nt_results)}, Apoc: {len(apocrypha_results)}"
            )
            self._log(f"   Searches completed in {duration:.0f}ms")

        # Per-keyword search (if keywords provided)
        if quran_keywords or bible_keywords:
            _emit(
                "searching_keywords",
                f"Searching per-keyword: {len(quran_keywords or [])} Quran + {len(bible_keywords or [])} Bible keywords...",
            )
            keyword_results = self._search_per_keyword_multi_collection(
                quran_keywords=quran_keywords,
                bible_keywords=bible_keywords,
                limit_per_keyword=10,
            )

            # Merge keyword results with normal results using RRF fusion
            if keyword_results["quran"]:
                quran_results = self._rrf_fusion(
                    [quran_results, keyword_results["quran"]], k=60
                )[: self.verses_per_search]
            if keyword_results["ot"]:
                ot_results = self._rrf_fusion(
                    [ot_results, keyword_results["ot"]], k=60
                )[: self.verses_per_search]
            if keyword_results["nt"]:
                nt_results = self._rrf_fusion(
                    [nt_results, keyword_results["nt"]], k=60
                )[: self.verses_per_search]
            if keyword_results["apocrypha"]:
                apocrypha_results = self._rrf_fusion(
                    [apocrypha_results, keyword_results["apocrypha"]], k=60
                )[: self.verses_per_search]

            _emit(
                "keywords_merged",
                f"Merged keyword results — Quran: {len(quran_results)}, OT: {len(ot_results)}, NT: {len(nt_results)}, Apoc: {len(apocrypha_results)}",
            )

        total_duration = (time.time() - total_start) * 1000

        # Store detected_language in search_stats for response translation (Task 5)
        result = ComparativeScriptureResult(
            quran=quran_results,
            ot=ot_results,
            nt=nt_results,
            apocrypha=apocrypha_results,
            search_stats={
                "duration_ms": total_duration,
                "quran_query": quran_query,
                "bible_query": bible_query,
                "mode": mode_label,
                "detected_language": detected_language,
            },
        )

        if self.verbose:
            console.print(
                f"\n[green]✓ Search complete: {result.total_verses} verses in {total_duration:.0f}ms[/green]\n"
            )

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
            console.print(f'[dim]Question: "{query}"[/dim]\n')

        # Steps 0-3: Translate, enhance, search and select top results
        search_result = self.search_all(query)

        # Store detected language for response translation (Task 5)
        self._last_detected_language = search_result.search_stats.get(
            "detected_language"
        )

        # Step 4: Generate comparative essay
        # Combine testament results for the answer generator
        self._log("📝 Step 4: Generating comparative theological essay...")
        essay_start = time.time()

        # Map new testament-based results to answer generator format
        # quran_semantic = Quran verses
        # bible_semantic = combined OT + NT + Apocrypha
        quran_verses = search_result.quran
        bible_verses = search_result.ot + search_result.nt + search_result.apocrypha

        answer = self.answer_generator.generate_comparative_answer(
            query=query,
            quran_semantic=quran_verses,
            quran_chunks=[],  # No chunk search in new architecture
            bible_semantic=bible_verses,
            bible_chunks=[],  # No chunk search in new architecture
        )

        essay_duration = (time.time() - essay_start) * 1000
        total_duration = (time.time() - total_start) * 1000

        if self.verbose:
            self._log(f"   Essay generated in {essay_duration:.0f}ms")
            console.print(
                f"\n[green]✨ Analysis complete in {total_duration:.0f}ms[/green]"
            )
            console.print(
                f"[dim]  {search_result.total_verses} verses → {len(answer.all_references)} citations → confidence: {answer.confidence:.0%}[/dim]\n"
            )

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
            testament = getattr(r, "testament", None)
            if testament is None and hasattr(r, "payload"):
                testament = r.payload.get("testament", "")

            if testament == "OT":
                ot_results.append(r)
            elif testament == "NT":
                nt_results.append(r)
            elif testament == "Apocrypha":
                apocrypha_results.append(r)
            else:
                # Default to OT for unknown
                ot_results.append(r)

        return ot_results, nt_results, apocrypha_results

    @property
    def multi_agent_generator(self):
        """Lazy load Multi-Agent Answer Generator"""
        if (
            not hasattr(self, "_multi_agent_generator")
            or self._multi_agent_generator is None
        ):
            from src.multi_agent_answer_generator import MultiAgentOrchestrator

            self._multi_agent_generator = MultiAgentOrchestrator(verbose=self.verbose)
            if self.verbose:
                console.print(
                    "[dim]Loaded MultiAgentOrchestrator (4 specialists + summary)[/dim]"
                )
        return self._multi_agent_generator

    def compare_multi_agent(
        self,
        query: str,
        quran_keywords: Optional[List[str]] = None,
        bible_keywords: Optional[List[str]] = None,
    ):
        """
        Full comparative pipeline with Multi-Agent answer generation.

        Uses 4 testament-specific searches (Quran, OT, NT, Apocrypha) in parallel,
        each returning 20 verses. Then runs 4 specialist agents + 1 summary agent.

        Args:
            query: User's religious/philosophical question
            quran_keywords: Optional list of Turkish keywords for Quran per-keyword search
            bible_keywords: Optional list of English keywords for Bible per-keyword search

        Returns:
            MultiAgentAnswer with 5 paragraphs (OT, NT, Apocrypha, Quran, Synthesis)
        """
        import sentry_sdk

        with sentry_sdk.start_span(
            op="rag.compare", description="Multi-agent comparison"
        ) as span:
            span.set_data("query", query[:50])  # Truncate for privacy

            total_start = time.time()

            if self.verbose:
                console.print(
                    f"\n[bold blue]📚 Multi-Agent Comparative Scripture Analysis[/bold blue]"
                )
                console.print(f'[dim]Question: "{query}"[/dim]\n')

            # Steps 0-2: Translate, search all 4 collections (pre-separated by testament)
            search_result = self.search_all(
                query,
                quran_keywords=quran_keywords,
                bible_keywords=bible_keywords,
            )

            # Store detected language for response translation (Task 5)
            self._last_detected_language = search_result.search_stats.get(
                "detected_language"
            )

            # Results are now directly available per testament - no splitting needed!
            quran_verses = search_result.quran
            ot_verses = search_result.ot
            nt_verses = search_result.nt
            apocrypha_verses = search_result.apocrypha

            span.set_data(
                "verse_counts",
                {
                    "quran": len(quran_verses),
                    "ot": len(ot_verses),
                    "nt": len(nt_verses),
                    "apocrypha": len(apocrypha_verses),
                },
            )

            self._log(
                f"📋 Verses: Quran={len(quran_verses)}, OT={len(ot_verses)}, "
                f"NT={len(nt_verses)}, Apoc={len(apocrypha_verses)}"
            )

            # Step 3: Multi-agent generation
            self._log("📝 Step 3: Running 4 specialist agents + summary agent...")
            gen_start = time.time()

            answer = self.multi_agent_generator.generate(
                query=query,
                quran_verses=quran_verses,
                ot_verses=ot_verses,
                nt_verses=nt_verses,
                apocrypha_verses=apocrypha_verses,
                collection_stats=self._last_collection_stats,
            )

            gen_duration = (time.time() - gen_start) * 1000
            total_duration = (time.time() - total_start) * 1000
            sentry_sdk.set_measurement(
                "rag.compare.total_latency_ms", total_duration, "millisecond"
            )

            if self.verbose:
                self._log(
                    f"   Multi-agent generation completed in {gen_duration:.0f}ms"
                )
                console.print(
                    f"\n[green]✨ Multi-Agent Analysis complete in {total_duration:.0f}ms[/green]"
                )
                total_citations = sum(len(c) for c in answer.citations.values())
                console.print(
                    f"[dim]  {search_result.total_verses} verses → 5 paragraphs → "
                    f"{total_citations} citations → confidence: {answer.confidence:.0%}[/dim]\n"
                )

            return answer


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
