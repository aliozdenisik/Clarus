"""
Ultimate RAG Pipeline - Maximum Accuracy Search System

Bu modül tüm en iyi RAG metodolojilerini tek bir pipeline'da birleştirir:
1. Query Enhancement (LLM ile sorgu genişletme)
2. Multi-Query Generation (3 farklı perspektif)
3. Semantic Search (RRF fusion ile multi-query arama)
4. Semantic Chunk Search (paralel - gruplu ayetleri arar)

Not: Cross-encoder reranking kaldırıldı (2026-01-19).
Test sonuçları: Reranker olmadan +11% recall artışı.

Usage:
    from src.ultimate_rag import UltimateRAG

    rag = UltimateRAG(enable_semantic_chunks=True)
    results = rag.search("Kur'an'da şefaat kavramı nasıl açıklanır?")
"""

import os
import time
import logging
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor
from rich.console import Console

from src.circuit_breaker import CircuitBreakerError

console = Console()
logger = logging.getLogger(__name__)


@dataclass
class UltimateSearchResult:
    """Enhanced search result with full metadata"""

    id: str
    score: float
    text: str
    reference: str  # Surah:Verse or Book Chapter:Verse
    source: str  # quran_tr, bible_kjva, etc.
    original_score: float = 0.0
    matched_queries: List[str] = field(default_factory=list)


class UltimateRAG:
    """
    Ultimate RAG Pipeline - Maximum Accuracy

    Pipeline aşamaları:
    1. ENHANCE: LLM ile sorguyu genişlet (eşanlamlılar, ilgili kavramlar)
    2. MULTI-QUERY: 3 farklı perspektiften sorgu varyasyonları üret
    3. SEARCH: Tüm sorgularla semantic arama yap, sonuçları birleştir (RRF)
       - Single-verse collection (quran_tr)
       - Semantic chunks collection (quran_semantic_chunks) - OPSİYONEL
    4. TOP-K: En iyi sonuçları seç

    Ayarlar:
        enable_multi_query: Multi-query aşamasını aktif et (default: True)
        enable_semantic_chunks: Semantic chunk aramasını paralel çalıştır (default: True)
        search_mode: Arama modu - "semantic" önerilen (default: "semantic")
        search_pool_size: Search'ten gelen max sonuç sayısı (default: 50)
        final_top_k: Final sonuç sayısı (default: 10)
    """

    def __init__(
        self,
        qdrant_url: str = "http://localhost:6333",
        enable_multi_query: bool = True,
        enable_semantic_chunks: bool = True,  # Parallel semantic chunk search
        search_mode: str = "semantic",  # semantic performs best for Turkish
        search_pool_size: int = 50,  # Max results from Search (RRF)
        final_top_k: int = 10,
        verbose: bool = True,
        # LLM Cache settings
        enable_llm_cache: bool = True,  # Semantic LLM response cache
        llm_cache_threshold: float = 0.95,  # Similarity threshold for cache hits
        llm_cache_ttl: int = 86400 * 7,  # 7 days
    ):
        self.qdrant_url = qdrant_url
        self.enable_multi_query = enable_multi_query
        self.enable_semantic_chunks = enable_semantic_chunks
        self.search_mode = search_mode
        self.search_pool_size = search_pool_size
        self.final_top_k = final_top_k
        self.verbose = verbose

        # LLM Cache settings
        self.enable_llm_cache = enable_llm_cache
        self.llm_cache_threshold = llm_cache_threshold
        self.llm_cache_ttl = llm_cache_ttl

        # Lazy load components
        self._enhancer = None
        self._llm_cache = None
        self._answer_generator = None
        self._searchers = {}
        self._semantic_chunk_searcher = None

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
    def llm_cache(self):
        """Lazy load Semantic LLM Cache"""
        if self._llm_cache is None and self.enable_llm_cache:
            from src.llm_cache import SemanticLLMCache

            self._llm_cache = SemanticLLMCache(
                similarity_threshold=self.llm_cache_threshold,
                ttl_seconds=self.llm_cache_ttl,
            )
            if self.verbose:
                console.print(
                    f"[dim]Loaded Semantic LLM Cache (θ={self.llm_cache_threshold}, TTL={self.llm_cache_ttl // 86400}d)[/dim]"
                )
        return self._llm_cache

    @property
    def answer_generator(self):
        """Lazy load Answer Generator"""
        if self._answer_generator is None:
            from src.answer_generator import AnswerGenerator

            self._answer_generator = AnswerGenerator()
            if self.verbose:
                console.print(
                    "[dim]Loaded AnswerGenerator (Gemini 2.5 Flash Lite)[/dim]"
                )
        return self._answer_generator

    def _get_searcher(self, source: str):
        """Get appropriate searcher for source"""
        if source in self._searchers:
            return self._searchers[source]

        if source == "quran_tr":
            from src.search import QuranSearcher

            searcher = QuranSearcher(qdrant_url=self.qdrant_url)
        elif source.startswith("bible_"):
            from src.search import BibleSearcher

            suffix = source.replace("bible_", "")

            if suffix in ["ot", "nt", "apocrypha"]:
                # Testament specific search
                translation = "kjva"
                testament = suffix
                searcher = BibleSearcher(
                    translation=translation,
                    testament=testament,
                    qdrant_url=self.qdrant_url,
                )
            else:
                # Translation specific search
                translation = suffix
                searcher = BibleSearcher(
                    translation=translation, qdrant_url=self.qdrant_url
                )
        else:
            raise ValueError(f"Unknown source: {source}")

        self._searchers[source] = searcher
        return searcher

    def _get_semantic_chunk_searcher(self):
        """Get semantic chunk searcher (lazy load)"""
        if self._semantic_chunk_searcher is None:
            from src.search import SemanticChunkSearcher

            self._semantic_chunk_searcher = SemanticChunkSearcher(
                qdrant_url=self.qdrant_url
            )
        return self._semantic_chunk_searcher

    def _log(self, message: str, style: str = "dim"):
        """Log message if verbose"""
        if self.verbose:
            console.print(f"[{style}]{message}[/{style}]")

    def _enhance_query(self, query: str, source: str = "bible_kjva") -> str:
        """
        Step 1: Enhance query with LLM (with semantic caching)

        Uses semantic cache to avoid redundant LLM calls for similar queries.
        """
        import sentry_sdk

        with sentry_sdk.start_span(
            op="rag.enhance_query", description="LLM query enhancement"
        ) as span:
            # Determine corpus from source
            corpus = "quran" if "quran" in source else "bible"
            span.set_data("corpus", corpus)

            self._log("⚡ Step 1: Query Enhancement...")
            start = time.time()

            cache_key = f"{corpus}:expand"

            # Check LLM cache first
            if self.enable_llm_cache and self.llm_cache:
                cached = self.llm_cache.get(query, cache_key)
                if cached:
                    duration = (time.time() - start) * 1000
                    span.set_data("cache_hit", True)
                    sentry_sdk.set_measurement(
                        "rag.query.enhance_latency_ms", duration, "millisecond"
                    )
                    sentry_sdk.set_measurement("rag.cache.hit", 1, "none")
                    self._log(
                        f"   [CACHE HIT] Enhanced ({corpus}) in {duration:.0f}ms: {cached[:80]}..."
                    )
                    return cached

            # LLM call (cache miss)
            span.set_data("cache_hit", False)
            enhanced = self.enhancer.expand_query(query, corpus=corpus)

            # Cache the result
            if self.enable_llm_cache and self.llm_cache:
                self.llm_cache.set(query, cache_key, enhanced)

            duration = (time.time() - start) * 1000
            sentry_sdk.set_measurement(
                "rag.query.enhance_latency_ms", duration, "millisecond"
            )
            sentry_sdk.set_measurement("rag.cache.hit", 0, "none")
            self._log(f"   Enhanced ({corpus}) in {duration:.0f}ms: {enhanced[:80]}...")
            return enhanced

    def _generate_multi_queries(
        self, query: str, enhanced_query: str, source: str = "bible_kjva", n: int = 3
    ) -> List[str]:
        """
        Step 2: Generate multiple query perspectives (with semantic caching)

        Uses semantic cache to avoid redundant LLM calls.
        """
        import sentry_sdk

        with sentry_sdk.start_span(
            op="rag.multi_query", description="Multi-query generation"
        ) as span:
            span.set_data("n", n)

            if not self.enable_multi_query:
                return [enhanced_query]

            self._log("🔄 Step 2: Multi-Query Generation...")
            start = time.time()

            # Determine corpus from source
            corpus = "quran" if "quran" in source else "bible"
            span.set_data("corpus", corpus)
            cache_key = f"{corpus}:multi_query"

            # Always include original and enhanced
            queries = [query, enhanced_query]

            # Check LLM cache for multi-queries
            multi = None
            if self.enable_llm_cache and self.llm_cache:
                cached = self.llm_cache.get(enhanced_query, cache_key)
                if cached:
                    multi = cached
                    span.set_data("cache_hit", True)
                    self._log(f"   [CACHE HIT] Multi-query from cache")

            # Generate if not cached
            if multi is None:
                span.set_data("cache_hit", False)
                try:
                    multi = self.enhancer.generate_multi_query(
                        enhanced_query, n=n, corpus=corpus
                    )
                    # Cache the result
                    if self.enable_llm_cache and self.llm_cache:
                        self.llm_cache.set(enhanced_query, cache_key, multi)
                except Exception as e:
                    self._log(f"   Warning: Multi-query failed: {e}", "yellow")
                    multi = []

            queries.extend(multi)

            # Deduplicate while preserving order
            seen = set()
            unique = []
            for q in queries:
                q_lower = q.lower().strip()
                if q_lower not in seen:
                    seen.add(q_lower)
                    unique.append(q)

            duration = (time.time() - start) * 1000
            sentry_sdk.set_measurement(
                "rag.query.multi_latency_ms", duration, "millisecond"
            )
            span.set_data("query_count", len(unique))
            self._log(f"   Generated {len(unique)} queries in {duration:.0f}ms")
            return unique

    def _search_all_queries(
        self, queries: List[str], source: str, limit: int = 30
    ) -> List:
        """Step 3: Search with all queries and merge results (RRF)"""
        import sentry_sdk

        with sentry_sdk.start_span(
            op="rag.search", description=f"Search {source}"
        ) as span:
            span.set_data("source", source)
            span.set_data("query_count", len(queries))
            span.set_data("limit", limit)

            self._log(f"🔍 Step 3: Searching with {len(queries)} queries...")
            start = time.time()

            searcher = self._get_searcher(source)

            # Collect all results with their ranks
            all_results = {}  # id -> (result, rrf_score)
            k = 60  # RRF constant

            # Search single-verse collection
            for i, query in enumerate(queries):
                try:
                    results = searcher.search(query, mode=self.search_mode, limit=limit)

                    for rank, result in enumerate(results, 1):
                        result_id = (
                            result.id if hasattr(result, "id") else f"{i}_{rank}"
                        )
                        rrf_contribution = 1 / (k + rank)

                        if result_id in all_results:
                            # Accumulate RRF score
                            existing_result, existing_score, matched = all_results[
                                result_id
                            ]
                            all_results[result_id] = (
                                existing_result,
                                existing_score + rrf_contribution,
                                matched + [query],
                            )
                        else:
                            all_results[result_id] = (result, rrf_contribution, [query])

                except CircuitBreakerError:
                    logger.warning(
                        "Qdrant unavailable (circuit breaker open), returning empty results for query: %s",
                        query,
                    )
                    # Continue with other queries - don't fail entire search
                except Exception as e:
                    self._log(f"   Warning: Search failed for query: {e}", "yellow")

            # Parallel search: Semantic chunks (if enabled)
            if self.enable_semantic_chunks:
                # Handle Quran Semantic Chunks
                if source == "quran_tr":
                    try:
                        chunk_searcher = self._get_semantic_chunk_searcher()
                        if chunk_searcher.collection_exists():
                            self._log(
                                "   📦 Including semantic chunks in search (Quran)..."
                            )

                            for i, query in enumerate(queries):
                                try:
                                    chunk_results = chunk_searcher.search(
                                        query, mode=self.search_mode, limit=limit // 2
                                    )

                                    for rank, chunk_result in enumerate(
                                        chunk_results, 1
                                    ):
                                        chunk_id = chunk_result.chunk_id
                                        rrf_contribution = 1 / (k + rank)

                                        if chunk_id in all_results:
                                            existing_result, existing_score, matched = (
                                                all_results[chunk_id]
                                            )
                                            all_results[chunk_id] = (
                                                existing_result,
                                                existing_score + rrf_contribution,
                                                matched + [query],
                                            )
                                        else:
                                            all_results[chunk_id] = (
                                                chunk_result,
                                                rrf_contribution,
                                                [query],
                                            )
                                except CircuitBreakerError:
                                    logger.warning(
                                        "Qdrant unavailable for Quran semantic chunks, skipping"
                                    )
                                except Exception as e:
                                    pass
                    except Exception as e:
                        self._log(
                            f"   Warning: Quran semantic chunks error: {e}", "yellow"
                        )

                # Handle Bible Semantic Chunks
                elif source.startswith("bible_"):
                    try:
                        translation = source.replace("bible_", "")
                        # Initialize on demand
                        from src.search import BibleSemanticChunkSearcher

                        bible_chunk_searcher = BibleSemanticChunkSearcher(
                            translation=translation, qdrant_url=self.qdrant_url
                        )

                        if bible_chunk_searcher.collection_exists():
                            self._log(
                                f"   📦 Including semantic chunks in search (Bible {translation})..."
                            )

                            for i, query in enumerate(queries):
                                try:
                                    chunk_results = bible_chunk_searcher.search(
                                        query, mode=self.search_mode, limit=limit // 2
                                    )

                                    for rank, chunk_result in enumerate(
                                        chunk_results, 1
                                    ):
                                        chunk_id = chunk_result.chunk_id
                                        rrf_contribution = 1 / (k + rank)

                                        if chunk_id in all_results:
                                            existing_result, existing_score, matched = (
                                                all_results[chunk_id]
                                            )
                                            all_results[chunk_id] = (
                                                existing_result,
                                                existing_score + rrf_contribution,
                                                matched + [query],
                                            )
                                        else:
                                            all_results[chunk_id] = (
                                                chunk_result,
                                                rrf_contribution,
                                                [query],
                                            )
                                except CircuitBreakerError:
                                    logger.warning(
                                        "Qdrant unavailable for Bible semantic chunks, skipping"
                                    )
                                except Exception as e:
                                    pass
                    except Exception as e:
                        self._log(
                            f"   Warning: Bible semantic chunks error: {e}", "yellow"
                        )

            # Sort by RRF score and return top results
            sorted_results = sorted(
                all_results.values(), key=lambda x: x[1], reverse=True
            )[: self.search_pool_size]

            # Attach RRF info to results
            merged_results = []
            for result, rrf_score, matched_queries in sorted_results:
                result.score = rrf_score
                merged_results.append(result)

            duration = (time.time() - start) * 1000
            sentry_sdk.set_measurement(
                "rag.query.search_latency_ms", duration, "millisecond"
            )
            span.set_data("result_count", len(merged_results))
            self._log(
                f"   Found {len(merged_results)} unique results in {duration:.0f}ms"
            )
            return merged_results

    def _get_top_results(self, results: List, top_k: int = None) -> List:
        """
        Step 4: Return top results from Search (RRF)

        Note: Cross-encoder and MMR reranking were removed (2026-01-19).
        Test results showed +11% recall improvement without cross-encoder.
        """
        top_k = top_k or self.final_top_k

        if not results:
            return []

        self._log(f"🏆 Step 4: Returning top {min(len(results), top_k)} results")
        return results[:top_k]

    def search(
        self,
        query: str,
        source: str = "quran_tr",
        top_k: int = None,
        rerank_query: str = None,  # Optional: use different query for reranking
    ) -> List:
        """
        Execute Ultimate RAG Pipeline

        Args:
            query: User's search query
            source: Data source - "quran_tr", "bible_kjva"
            top_k: Number of final results (default: self.final_top_k)
            rerank_query: Optional query to use for reranking (useful for translated queries)

        Returns:
            List of reranked search results
        """
        top_k = top_k or self.final_top_k
        total_start = time.time()

        if self.verbose:
            console.print(f"\n[bold blue]🚀 Ultimate RAG Pipeline[/bold blue]")
            console.print(f'[dim]Query: "{query}"[/dim]\n')

        # Step 1: Enhance query
        enhanced_query = self._enhance_query(query, source=source)

        # Step 2: Generate multi-queries
        all_queries = self._generate_multi_queries(query, enhanced_query, source=source)

        # Step 3: Search with all queries (RRF merge)
        search_results = self._search_all_queries(all_queries, source)

        # Step 4: Rerank for final precision
        # Use rerank_query if provided (e.g., translated query), otherwise use original
        final_query = rerank_query or query
        final_results = self._get_top_results(search_results, top_k=top_k)

        total_duration = (time.time() - total_start) * 1000

        if self.verbose:
            console.print(
                f"\n[green]✓ Pipeline complete in {total_duration:.0f}ms[/green]"
            )
            console.print(
                f"[dim]  Enhanced → {len(all_queries)} queries → {len(search_results)} candidates → {len(final_results)} final[/dim]\n"
            )

        return final_results

    def search_quran(self, query: str, top_k: int = None) -> List:
        """Shortcut for Quran search"""
        import sentry_sdk

        with sentry_sdk.start_span(
            op="rag.pipeline.quran", description="Quran search pipeline"
        ) as span:
            span.set_data("query", query[:50])  # Truncate for privacy
            return self.search(query, source="quran_tr", top_k=top_k)

    def _search_all_bible_collections(
        self, query: str, top_k: int = None, rerank_query: str = None
    ) -> List:
        """
        Search all 3 Bible collections (OT, NT, Apocrypha) and merge with RRF fusion.

        This is used when no specific testament is requested.
        """
        from concurrent.futures import ThreadPoolExecutor, as_completed

        if top_k is None:
            top_k = self.final_top_k

        # Search each collection in parallel
        pool_size = top_k * 2  # Get more results for better fusion

        def search_collection(source: str):
            try:
                searcher = self._get_searcher(source)
                results = searcher.search(query, mode=self.search_mode, limit=pool_size)
                return (source, results)
            except CircuitBreakerError:
                logger.warning(
                    f"Qdrant unavailable (circuit breaker open) for {source}"
                )
                return (source, [])
            except Exception as e:
                logger.error(f"Search failed for {source}: {e}")
                return (source, [])

        # Parallel search across all 3 collections
        results_by_source = {}
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = [
                executor.submit(search_collection, "bible_ot"),
                executor.submit(search_collection, "bible_nt"),
                executor.submit(search_collection, "bible_apocrypha"),
            ]

            for future in as_completed(futures):
                source, results = future.result()
                results_by_source[source] = results

        # Merge results with RRF fusion
        all_results = [
            results_by_source["bible_ot"],
            results_by_source["bible_nt"],
            results_by_source["bible_apocrypha"],
        ]

        # Filter out empty result lists
        all_results = [r for r in all_results if r]

        if not all_results:
            return []

        # Apply RRF fusion
        fused_results = self._rrf_fusion(all_results, k=60)

        # Return top_k results
        return fused_results[:top_k]

    def _rrf_fusion(self, result_lists: List[List], k: int = 60) -> List:
        """
        Reciprocal Rank Fusion - merges multiple ranked lists.

        RRF score = sum(1 / (k + rank)) for each list where item appears

        Args:
            result_lists: List of search result lists
            k: RRF constant (default: 60)
        """
        rrf_scores = {}

        for result_list in result_lists:
            for rank, result in enumerate(result_list, start=1):
                # Use result ID as key
                result_id = result.id

                # Calculate RRF score contribution
                score_contribution = 1.0 / (k + rank)

                if result_id not in rrf_scores:
                    rrf_scores[result_id] = (result, 0.0)

                # Accumulate RRF score
                current_result, current_score = rrf_scores[result_id]
                rrf_scores[result_id] = (
                    current_result,
                    current_score + score_contribution,
                )

        # Sort by RRF score descending
        sorted_results = sorted(rrf_scores.values(), key=lambda x: x[1], reverse=True)
        return [item[0] for item in sorted_results]

    def search_bible(
        self,
        query: str,
        translation: str = "kjva",
        testament: str = None,
        top_k: int = None,
    ) -> List:
        """
        Shortcut for Bible search.

        For English translations (kjva, kjv), automatically translates Turkish queries to English
        and uses the translated query for reranking to ensure proper cross-lingual matching.

        If testament is specified (e.g., "ot", "nt", "apocrypha"), searches only that collection.
        Otherwise, searches all 3 Bible collections (bible_ot, bible_nt, bible_apocrypha) and
        merges results using RRF fusion.
        """
        original_query = query
        translated_query = None

        # For English Bible translations, translate Turkish query to English
        if translation in ("kjva", "kjv"):
            try:
                # Use expand_query with corpus="bible" to translate Turkish to English
                translated_query = self.enhancer.expand_query(query, corpus="bible")
                if self.verbose:
                    console.print(
                        f"[dim]📝 Translated: {query} → {translated_query}[/dim]"
                    )
                query = translated_query
            except Exception as e:
                if self.verbose:
                    console.print(f"[yellow]Translation warning: {e}[/yellow]")

        # If testament is specified, search only that collection
        if testament:
            source = f"bible_{testament}"
            return self.search(
                query, source=source, top_k=top_k, rerank_query=translated_query
            )

        # Otherwise, search all 3 Bible collections and merge with RRF
        return self._search_all_bible_collections(
            query, top_k=top_k, rerank_query=translated_query
        )

    # ============= ANSWER GENERATION (RAG) =============

    def ask(self, query: str, source: str = "quran_tr", top_k: int = None):
        """
        Full RAG Pipeline: Search + Generate Answer with Citations

        Searches for relevant verses, then generates a comprehensive answer
        that cites specific verses using [Reference] format.

        Args:
            query: User's question
            source: Data source - "quran_tr", "bible_kjva", etc.
            top_k: Number of search results to use as context

        Returns:
            AnswerResult with text, citations, and confidence
        """
        from src.answer_generator import AnswerResult

        top_k = top_k or self.final_top_k
        total_start = time.time()

        if self.verbose:
            console.print(f"\n[bold blue]🧠 Ultimate RAG Q&A Pipeline[/bold blue]")
            console.print(f'[dim]Question: "{query}"[/dim]\n')

        # Step 1-4: Search pipeline (enhance, multi-query, search, rerank)
        search_results = self.search(query, source=source, top_k=top_k)

        # Step 5: Generate answer with citations
        self._log("💬 Step 5: Generating answer with citations...")
        answer_start = time.time()

        answer = self.answer_generator.generate_answer(
            query, search_results, source=source
        )

        answer_duration = (time.time() - answer_start) * 1000
        total_duration = (time.time() - total_start) * 1000

        if self.verbose:
            self._log(f"   Answer generated in {answer_duration:.0f}ms")
            console.print(
                f"\n[green]✓ Q&A Pipeline complete in {total_duration:.0f}ms[/green]"
            )
            console.print(
                f"[dim]  {len(search_results)} verses → {len(answer.citations)} citations → confidence: {answer.confidence:.0%}[/dim]\n"
            )

        return answer

    def ask_quran(self, query: str, top_k: int = None):
        """Shortcut for Quran Q&A - Turkish in, Turkish out"""
        return self.ask(query, source="quran_tr", top_k=top_k)

    def ask_bible(
        self,
        query: str,
        translation: str = "kjva",
        testament: str = None,
        top_k: int = None,
    ):
        """
        Shortcut for Bible Q&A.

        Turkish query → English search → Turkish answer with English citations.
        """
        # For English Bible translations, translate Turkish query to English
        if translation in ("kjva", "kjv"):
            try:
                translated_query = self.enhancer.translate_for_bible(query)
                if self.verbose:
                    console.print(
                        f"[dim]📝 Translated for ask: {query} → {translated_query}[/dim]"
                    )
                query = translated_query
            except Exception as e:
                if self.verbose:
                    console.print(f"[yellow]Translation warning: {e}[/yellow]")

        source = f"bible_{testament}" if testament else f"bible_{translation}"
        return self.ask(query, source=source, top_k=top_k)


# Convenience function
def ultimate_search(query: str, source: str = "quran_tr", top_k: int = 10) -> List:
    """
    One-liner for Ultimate RAG search

    Usage:
        from src.ultimate_rag import ultimate_search
        results = ultimate_search("Kur'an'da şefaat kavramı")
    """
    rag = UltimateRAG(verbose=True)
    return rag.search(query, source=source, top_k=top_k)


if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()

    # Test the Ultimate RAG Pipeline
    console.print("[bold]Testing Ultimate RAG Pipeline[/bold]\n")

    rag = UltimateRAG()

    test_queries_quran = [
        "Kur'an'da şefaat kavramı nasıl açıklanır?",
    ]

    console.print("\n[bold green]--- QURAN TESTS ---[/bold green]")
    for query in test_queries_quran:
        results = rag.search_quran(query, top_k=3)
        console.print(f"\n[bold cyan]Query: {query}[/bold cyan]")
        for i, r in enumerate(results, 1):
            # Handle standard PointStruct or SemanticChunkSearchResult
            payload = getattr(r, "payload", {}) or {}

            # Try to get reference from object attributes or payload
            surah = getattr(r, "surah_id", payload.get("surah_id"))
            verse = getattr(
                r,
                "verse_id",
                getattr(
                    r, "verse_ids", payload.get("verse_id", payload.get("verse_ids"))
                ),
            )

            ref = f"{surah}:{verse}"
            text = getattr(r, "translation", payload.get("translation", ""))[:100]

            console.print(f"  {i}. [{ref}] (score: {r.score:.4f})")
            console.print(f"     {text}...")

    console.print("\n[bold green]--- BIBLE TESTS ---[/bold green]")
    test_queries_bible = [
        "God's love and mercy",
    ]
    for query in test_queries_bible:
        results = rag.search_bible(query, top_k=3)
        console.print(f"\n[bold cyan]Query: {query}[/bold cyan]")
        for i, r in enumerate(results, 1):
            payload = getattr(r, "payload", {}) or {}
            book = getattr(r, "book_name", payload.get("book_name", "Unknown"))
            chapter = getattr(r, "chapter_number", payload.get("chapter_number"))
            verse = getattr(r, "verse_number", payload.get("verse_number"))

            ref = f"{book} {chapter}:{verse}"
            text = getattr(r, "text", getattr(r, "content", payload.get("text", "")))[
                :100
            ]

            console.print(f"  {i}. [{ref}] (score: {r.score:.4f})")
            console.print(f"     {text}...")
