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

import time
from typing import List, Optional, Any
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor

from src.circuit_breaker import CircuitBreakerError
from src.query_translator import QueryTranslator, TranslationError
from src.query_translator import CORPUS_LANGUAGES
from app.logging_config import get_logger, log_performance

logger = get_logger(__name__)


@dataclass
class AskResult:
    """Result from ask() containing both search results and generated answer"""

    answer: Any  # AnswerResult from answer_generator
    search_results: List  # List of search results used to generate the answer


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
        self._translator = None
        self._llm_cache = None
        self._answer_generator = None
        self._searchers = {}
        self._semantic_chunk_searcher = None

        # RRF score statistics (populated after search)
        self._last_score_stats: dict = {}

    @property
    def enhancer(self):
        """Lazy load Query Enhancer"""
        if self._enhancer is None:
            from src.query_enhancer import QueryEnhancer

            self._enhancer = QueryEnhancer()
            logger.debug("Loaded QueryEnhancer")
        return self._enhancer

    @property
    def translator(self):
        """Lazy load Query Translator"""
        if self._translator is None:
            self._translator = QueryTranslator()
            logger.debug("Loaded QueryTranslator")
        return self._translator

    async def _get_llm_cache(self):
        """Lazy load and initialize Semantic LLM Cache (async)"""
        if self._llm_cache is None and self.enable_llm_cache:
            from src.llm_cache import SemanticLLMCache

            self._llm_cache = SemanticLLMCache(
                similarity_threshold=self.llm_cache_threshold,
                ttl_seconds=self.llm_cache_ttl,
            )
            # Initialize Redis connection
            await self._llm_cache.init()
            logger.debug(
                "Loaded Semantic LLM Cache",
                extra={
                    "threshold": self.llm_cache_threshold,
                    "ttl_days": self.llm_cache_ttl // 86400,
                },
            )
        return self._llm_cache

    @property
    def answer_generator(self):
        """Lazy load Answer Generator"""
        if self._answer_generator is None:
            from src.answer_generator import AnswerGenerator

            self._answer_generator = AnswerGenerator()
            logger.debug("Loaded AnswerGenerator", extra={"model": "gemini-flash"})
        return self._answer_generator

    def _get_searcher(self, source: str):
        """Get appropriate searcher for source"""
        if source in self._searchers:
            return self._searchers[source]

        if source.startswith("quran_tr_"):
            from src.search import QuranSearcher

            # Extract translator from source (e.g., "quran_tr_diyanet" -> "diyanet")
            translator = source.replace("quran_tr_", "")
            searcher = QuranSearcher(translator=translator, qdrant_url=self.qdrant_url)
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

    def _log(self, message: str, style: str = "dim", **extra):
        """Log message if verbose"""
        if self.verbose:
            logger.info(message, extra=extra)

    async def _enhance_query(
        self,
        query: str,
        source: str = "bible_kjva",
        detected_language: Optional[str] = None,
    ) -> str:
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

            logger.info(
                "Pipeline stage started",
                extra={"stage": "enhance", "query": query[:50], "corpus": corpus},
            )
            start = time.perf_counter()

            cache_key = f"{corpus}:expand"

            # Check LLM cache first
            if self.enable_llm_cache:
                cache = await self._get_llm_cache()
                if cache:
                    cached = await cache.get(query, cache_key)
                    if cached:
                        latency_ms = (time.perf_counter() - start) * 1000
                        span.set_data("cache_hit", True)
                        sentry_sdk.set_measurement(
                            "rag.query.enhance_latency_ms", latency_ms, "millisecond"
                        )
                        sentry_sdk.set_measurement("rag.cache.hit", 1, "none")
                        logger.info(
                            "Cache hit",
                            extra={
                                "cache": "llm",
                                "stage": "enhance",
                                "corpus": corpus,
                            },
                        )
                        log_performance(
                            logger,
                            "enhance_query",
                            latency_ms,
                            corpus=corpus,
                            cache_hit=True,
                        )
                        return cached

            # LLM call (cache miss)
            span.set_data("cache_hit", False)
            enhanced = self.enhancer.expand_query(query, corpus=corpus)

            # Cache the result
            if self.enable_llm_cache:
                cache = await self._get_llm_cache()
                if cache:
                    await cache.set(
                        query, cache_key, enhanced, source_language=detected_language
                    )

            latency_ms = (time.perf_counter() - start) * 1000
            sentry_sdk.set_measurement(
                "rag.query.enhance_latency_ms", latency_ms, "millisecond"
            )
            sentry_sdk.set_measurement("rag.cache.hit", 0, "none")
            logger.info(
                "Cache miss",
                extra={"cache": "llm", "stage": "enhance", "corpus": corpus},
            )
            log_performance(
                logger, "enhance_query", latency_ms, corpus=corpus, cache_hit=False
            )
            return enhanced

    async def _generate_multi_queries(
        self,
        query: str,
        enhanced_query: str,
        source: str = "bible_kjva",
        n: int = 3,
        detected_language: Optional[str] = None,
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

            logger.info(
                "Pipeline stage started", extra={"stage": "multi_query", "n": n}
            )
            start = time.perf_counter()

            # Determine corpus from source
            corpus = "quran" if "quran" in source else "bible"
            span.set_data("corpus", corpus)
            cache_key = f"{corpus}:multi_query"

            # Always include original and enhanced
            queries = [query, enhanced_query]

            # Check LLM cache for multi-queries
            multi = None
            cache_hit = False
            if self.enable_llm_cache:
                cache = await self._get_llm_cache()
                if cache:
                    cached = await cache.get(enhanced_query, cache_key)
                    if cached:
                        multi = cached
                        cache_hit = True
                        span.set_data("cache_hit", True)
                        logger.info(
                            "Cache hit", extra={"cache": "llm", "stage": "multi_query"}
                        )

            # Generate if not cached
            if multi is None:
                span.set_data("cache_hit", False)
                try:
                    multi = self.enhancer.generate_multi_query(
                        enhanced_query, n=n, corpus=corpus
                    )
                    # Cache the result
                    if self.enable_llm_cache:
                        cache = await self._get_llm_cache()
                        if cache:
                            await cache.set(
                                enhanced_query,
                                cache_key,
                                multi,
                                source_language=detected_language,
                            )
                except Exception as e:
                    logger.warning(
                        "Multi-query generation failed", extra={"error": str(e)}
                    )
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

            latency_ms = (time.perf_counter() - start) * 1000
            sentry_sdk.set_measurement(
                "rag.query.multi_latency_ms", latency_ms, "millisecond"
            )
            span.set_data("query_count", len(unique))
            log_performance(
                logger,
                "multi_query",
                latency_ms,
                query_count=len(unique),
                cache_hit=cache_hit,
            )
            return unique

    async def _parallel_query_preparation(
        self,
        query: str,
        source: str = "quran_tr_diyanet",
        detected_language: Optional[str] = None,
    ) -> List[str]:
        """
        Run query enhancement and multi-query generation in PARALLEL.

        Previously these were sequential (enhance → multi-query), adding 2-6s latency.
        Now both LLM calls run concurrently via asyncio.gather.
        Multi-query uses the original query; enhanced query is merged into the final list.

        Returns:
            Deduplicated list of all query variants
        """
        import sentry_sdk
        import asyncio

        with sentry_sdk.start_span(
            op="rag.parallel_query_prep",
            description="Parallel query enhancement + multi-query",
        ) as span:
            start = time.perf_counter()

            # Run both LLM calls in parallel using asyncio.gather
            enhanced_query, multi_queries = await asyncio.gather(
                self._enhance_query(query, source, detected_language),
                self._generate_multi_queries(
                    query,
                    query,  # Use original query instead of waiting for enhanced
                    source,
                    3,
                    detected_language,
                ),
            )

            # Merge: enhanced query + multi-queries, deduplicate
            all_queries = [query, enhanced_query] + multi_queries
            seen = set()
            unique = []
            for q in all_queries:
                q_lower = q.lower().strip()
                if q_lower not in seen:
                    seen.add(q_lower)
                    unique.append(q)

            latency_ms = (time.perf_counter() - start) * 1000
            span.set_data("total_queries", len(unique))
            span.set_data("parallel", True)
            log_performance(
                logger,
                "parallel_query_prep",
                latency_ms,
                total_queries=len(unique),
                source=source,
            )

            logger.info(
                "Parallel query preparation complete",
                extra={
                    "total_queries": len(unique),
                    "latency_ms": round(latency_ms, 1),
                    "source": source,
                },
            )

            return unique

    def _batch_encode_queries(self, queries: List[str]) -> List[List[float]]:
        """
        Batch encode all queries in a single API call.

        Previously each query was encoded individually inside searcher.search(),
        causing N sequential API calls with rate limiting (3s each).
        Now all queries are encoded in one batch call.
        """
        import sentry_sdk

        with sentry_sdk.start_span(
            op="rag.batch_encode", description=f"Batch encode {len(queries)} queries"
        ) as span:
            start = time.perf_counter()
            span.set_data("query_count", len(queries))

            # Lazy-init shared encoder (all searchers use the same DenseEncoder model)
            if not hasattr(self, "_dense_encoder") or self._dense_encoder is None:
                from src.embeddings import DenseEncoder

                self._dense_encoder = DenseEncoder()

            # Use encode_batch for single API call instead of N individual calls
            vectors = self._dense_encoder.encode_batch(
                queries, batch_size=len(queries), show_progress=False
            )

            latency_ms = (time.perf_counter() - start) * 1000
            span.set_data("latency_ms", latency_ms)
            log_performance(
                logger,
                "batch_encode",
                latency_ms,
                query_count=len(queries),
            )

            return vectors

    def _search_per_keyword(
        self, keywords: List[str], source: str, limit_per_keyword: int = 10
    ) -> List:
        """
        Search with individual keywords in parallel, accumulate with RRF fusion.

        For each keyword:
        1. Encode to vector
        2. Search single-verse collection
        3. Search semantic chunks (if enabled)
        4. Accumulate RRF scores

        Apply keyword coverage boost for results matching 2+ keywords.

        Args:
            keywords: List of keyword strings to search
            source: Data source - "quran_tr_diyanet", "bible_ot", etc.
            limit_per_keyword: Results per keyword (default: 10)

        Returns:
            List of results sorted by final score (RRF + coverage boost)
        """
        import sentry_sdk

        with sentry_sdk.start_span(
            op="rag.search_per_keyword", description=f"Search {source} per keyword"
        ) as span:
            span.set_data("source", source)
            span.set_data("keyword_count", len(keywords))
            span.set_data("limit_per_keyword", limit_per_keyword)

            logger.info(
                "Per-keyword search started",
                extra={
                    "stage": "search_per_keyword",
                    "source": source,
                    "keyword_count": len(keywords),
                    "limit_per_keyword": limit_per_keyword,
                },
            )
            start = time.perf_counter()

            searcher = self._get_searcher(source)

            # Batch encode ALL keywords in a single API call
            keyword_vectors = self._batch_encode_queries(keywords)

            # Collect all results with their ranks
            all_results = {}  # id -> (result, rrf_score, matched_keywords)
            k = 60  # RRF constant

            # Search single-verse collection with pre-computed vectors
            for i, (keyword, vector) in enumerate(zip(keywords, keyword_vectors)):
                try:
                    results = searcher.search_with_vector(
                        vector, limit=limit_per_keyword
                    )

                    for rank, result in enumerate(results, 1):
                        result_id = (
                            result.id if hasattr(result, "id") else f"{i}_{rank}"
                        )
                        rrf_contribution = 1 / (k + rank)

                        if result_id in all_results:
                            # Accumulate RRF score and track matched keywords
                            existing_result, existing_score, matched = all_results[
                                result_id
                            ]
                            all_results[result_id] = (
                                existing_result,
                                existing_score + rrf_contribution,
                                matched + [keyword],
                            )
                        else:
                            all_results[result_id] = (
                                result,
                                rrf_contribution,
                                [keyword],
                            )

                except CircuitBreakerError:
                    logger.warning(
                        "Qdrant unavailable (circuit breaker open), returning empty results for keyword: %s",
                        keyword,
                    )
                    # Continue with other keywords - don't fail entire search
                except Exception as e:
                    self._log(f"   Warning: Search failed for keyword: {e}", "yellow")

            # Parallel search: Semantic chunks (if enabled) — reuse pre-computed vectors
            if self.enable_semantic_chunks:
                # Handle Quran Semantic Chunks
                if source.startswith("quran_tr_"):
                    try:
                        chunk_searcher = self._get_semantic_chunk_searcher()
                        if chunk_searcher.collection_exists():
                            self._log(
                                "   📦 Including semantic chunks in per-keyword search (Quran)..."
                            )

                            for i, (keyword, vector) in enumerate(
                                zip(keywords, keyword_vectors)
                            ):
                                try:
                                    chunk_results = chunk_searcher.search_with_vector(
                                        vector, limit=limit_per_keyword // 2
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
                                                matched + [keyword],
                                            )
                                        else:
                                            all_results[chunk_id] = (
                                                chunk_result,
                                                rrf_contribution,
                                                [keyword],
                                            )
                                except CircuitBreakerError:
                                    logger.warning(
                                        "Qdrant unavailable for Quran semantic chunks, skipping"
                                    )
                                except Exception:
                                    pass
                    except Exception:
                        self._log("   Warning: Quran semantic chunks error", "yellow")

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
                                f"   📦 Including semantic chunks in per-keyword search (Bible {translation})..."
                            )

                            for i, (keyword, vector) in enumerate(
                                zip(keywords, keyword_vectors)
                            ):
                                try:
                                    chunk_results = (
                                        bible_chunk_searcher.search_with_vector(
                                            vector, limit=limit_per_keyword // 2
                                        )
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
                                                matched + [keyword],
                                            )
                                        else:
                                            all_results[chunk_id] = (
                                                chunk_result,
                                                rrf_contribution,
                                                [keyword],
                                            )
                                except CircuitBreakerError:
                                    logger.warning(
                                        "Qdrant unavailable for Bible semantic chunks, skipping"
                                    )
                                except Exception:
                                    pass
                    except Exception:
                        self._log("   Warning: Bible semantic chunks error", "yellow")

            # Apply keyword coverage boost: results matching 2+ keywords get boosted
            boosted_results = []
            for result_id, (result, rrf_score, matched_keywords) in all_results.items():
                match_count = len(matched_keywords)
                # Boost formula: score * (1 + match_count * 0.15)
                # 1 match: no boost
                # 2 matches: +15%
                # 3 matches: +30%
                if match_count >= 2:
                    boosted_score = rrf_score * (1 + match_count * 0.15)
                else:
                    boosted_score = rrf_score
                boosted_results.append((result, boosted_score, matched_keywords))

            # Sort by final score descending
            sorted_results = sorted(boosted_results, key=lambda x: x[1], reverse=True)

            # Attach final scores to results
            merged_results = []
            for result, final_score, matched_keywords in sorted_results:
                result.score = final_score
                merged_results.append(result)

            latency_ms = (time.perf_counter() - start) * 1000
            sentry_sdk.set_measurement(
                "rag.query.search_per_keyword_latency_ms", latency_ms, "millisecond"
            )
            span.set_data("result_count", len(merged_results))
            log_performance(
                logger,
                "search_per_keyword",
                latency_ms,
                source=source,
                keyword_count=len(keywords),
                result_count=len(merged_results),
            )

            logger.info(
                "Per-keyword search complete",
                extra={
                    "stage": "search_per_keyword",
                    "source": source,
                    "keyword_count": len(keywords),
                    "result_count": len(merged_results),
                    "latency_ms": round(latency_ms, 1),
                },
            )

            return merged_results

    def _search_all_queries(
        self, queries: List[str], source: str, limit: int = 30
    ) -> List:
        """Step 3: Search with all queries and merge results (RRF)

        Optimized: All query embeddings are computed in a single batch API call,
        then Qdrant searches use pre-computed vectors (no per-query embedding overhead).
        """
        import sentry_sdk

        with sentry_sdk.start_span(
            op="rag.search", description=f"Search {source}"
        ) as span:
            span.set_data("source", source)
            span.set_data("query_count", len(queries))
            span.set_data("limit", limit)

            logger.info(
                "Pipeline stage started",
                extra={
                    "stage": "search",
                    "source": source,
                    "query_count": len(queries),
                    "limit": limit,
                },
            )
            start = time.perf_counter()

            searcher = self._get_searcher(source)

            # Batch encode ALL queries in a single API call (was: N individual calls)
            query_vectors = self._batch_encode_queries(queries)

            # Collect all results with their ranks
            all_results = {}  # id -> (result, rrf_score)
            k = 60  # RRF constant

            # Search single-verse collection with pre-computed vectors
            for i, (query, vector) in enumerate(zip(queries, query_vectors)):
                try:
                    results = searcher.search_with_vector(vector, limit=limit)

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

            # Parallel search: Semantic chunks (if enabled) — reuse pre-computed vectors
            if self.enable_semantic_chunks:
                # Handle Quran Semantic Chunks
                if source.startswith("quran_tr_"):
                    try:
                        chunk_searcher = self._get_semantic_chunk_searcher()
                        if chunk_searcher.collection_exists():
                            self._log(
                                "   📦 Including semantic chunks in search (Quran)..."
                            )

                            for i, (query, vector) in enumerate(
                                zip(queries, query_vectors)
                            ):
                                try:
                                    chunk_results = chunk_searcher.search_with_vector(
                                        vector, limit=limit // 2
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
                                except Exception:
                                    pass
                    except Exception:
                        self._log("   Warning: Quran semantic chunks error", "yellow")

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

                            for i, (query, vector) in enumerate(
                                zip(queries, query_vectors)
                            ):
                                try:
                                    chunk_results = (
                                        bible_chunk_searcher.search_with_vector(
                                            vector, limit=limit // 2
                                        )
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
                                except Exception:
                                    pass
                    except Exception:
                        self._log("   Warning: Bible semantic chunks error", "yellow")

            # Sort by RRF score and return top results
            sorted_results = sorted(
                all_results.values(), key=lambda x: x[1], reverse=True
            )[: self.search_pool_size]

            # Compute score statistics for confidence scoring
            rrf_scores = [rrf_score for _, rrf_score, _ in sorted_results]
            self._last_score_stats = {
                "max": max(rrf_scores) if rrf_scores else 0.0,
                "min": min(rrf_scores) if rrf_scores else 0.0,
                "mean": sum(rrf_scores) / len(rrf_scores) if rrf_scores else 0.0,
                "count": len(rrf_scores),
                "num_queries": len(queries),
            }

            # Attach RRF info to results
            merged_results = []
            for result, rrf_score, matched_queries in sorted_results:
                result.score = rrf_score
                merged_results.append(result)

            latency_ms = (time.perf_counter() - start) * 1000
            sentry_sdk.set_measurement(
                "rag.query.search_latency_ms", latency_ms, "millisecond"
            )
            span.set_data("result_count", len(merged_results))
            log_performance(
                logger,
                "search",
                latency_ms,
                source=source,
                query_count=len(queries),
                result_count=len(merged_results),
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

    async def search(
        self,
        query: str,
        source: str = "quran_tr_diyanet",
        top_k: int = None,
        rerank_query: str = None,  # Optional: use different query for reranking
        detected_language: Optional[str] = None,
        keywords: Optional[List[str]] = None,  # Optional: per-keyword parallel search
    ) -> List:
        """
        Execute Ultimate RAG Pipeline

        Args:
            query: User's search query
            source: Data source - "quran_tr_diyanet", "bible_ot", "bible_nt", etc.
            top_k: Number of final results (default: self.final_top_k)
            rerank_query: Optional query to use for reranking (useful for translated queries)
            detected_language: Detected language of the query (for cache metadata)
            keywords: Optional list of keywords for per-keyword parallel search

        Returns:
            List of reranked search results
        """
        top_k = top_k or self.final_top_k
        total_start = time.perf_counter()

        logger.info(
            "Pipeline started",
            extra={
                "pipeline": "search",
                "source": source,
                "top_k": top_k,
                "query": query[:50],
                "keywords": keywords,
            },
        )

        # Step 1+2: Enhance query AND generate multi-queries in PARALLEL
        # Both are independent LLM calls - no need to wait sequentially.
        # Multi-query uses original query; enhanced query is added to the final list.
        all_queries = await self._parallel_query_preparation(
            query, source=source, detected_language=detected_language
        )

        # Step 3: Search with all queries (RRF merge)
        search_results = self._search_all_queries(all_queries, source)

        # If keywords provided, run per-keyword search and merge results
        if keywords:
            logger.info(
                "Performing per-keyword search",
                extra={"keyword_count": len(keywords), "source": source},
            )
            keyword_results = self._search_per_keyword(
                keywords, source, limit_per_keyword=10
            )

            # Merge keyword results with query results using RRF fusion
            search_results = self._rrf_fusion([search_results, keyword_results], k=60)

        # Step 4: Rerank for final precision
        final_results = self._get_top_results(search_results, top_k=top_k)

        total_latency_ms = (time.perf_counter() - total_start) * 1000

        log_performance(
            logger,
            "pipeline_search",
            total_latency_ms,
            source=source,
            query_count=len(all_queries),
            candidates=len(search_results),
            final_results=len(final_results),
            with_keywords=keywords is not None,
        )

        return final_results

    async def search_quran(
        self,
        query: str,
        translator: str = "diyanet",
        top_k: int = None,
        detected_language: Optional[str] = None,
    ) -> List:
        """
        Shortcut for Quran search

        Args:
            query: Search query
            translator: Quran translator (diyanet, yazir, ates, bulac, ozturk, vakfi, yildirim, yuksel)
            top_k: Number of results
            detected_language: Detected language of query
        """
        import sentry_sdk

        with sentry_sdk.start_span(
            op="rag.pipeline.quran", description="Quran search pipeline"
        ) as span:
            span.set_data("query", query[:50])  # Truncate for privacy
            span.set_data("translator", translator)

            # Translate query to Turkish if needed (Quran corpus is Turkish)
            if detected_language is None:
                try:
                    result = self.translator.translate_query(query, "quran")
                    detected_language = result.detected_language
                    if result.was_translated:
                        query = result.translated_query
                        logger.info(
                            "Query translated for Quran search",
                            extra={
                                "from": result.detected_language,
                                "to": CORPUS_LANGUAGES.get("quran", "tr"),
                                "original": query[:50],
                                "translated": result.translated_query[:50],
                            },
                        )
                except TranslationError as e:
                    logger.error(
                        "Translation failed for Quran search",
                        extra={"error": str(e)},
                    )
                    raise

            return await self.search(
                query,
                source=f"quran_tr_{translator}",
                top_k=top_k,
                detected_language=detected_language,
            )

    def _search_all_bible_collections(
        self,
        query: str,
        top_k: int = None,
        rerank_query: str = None,
        detected_language: Optional[str] = None,
        collections: List[str] = None,
    ) -> List:
        """
        Search Bible collections and merge with RRF fusion.

        This is used when no specific testament is requested.

        Args:
            collections: List of collection names to search. Defaults to English Bible collections.
        """
        from concurrent.futures import as_completed

        if top_k is None:
            top_k = self.final_top_k

        if collections is None:
            collections = ["bible_ot", "bible_nt", "bible_apocrypha"]

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

        # Parallel search across all collections
        results_by_source = {}
        with ThreadPoolExecutor(max_workers=len(collections)) as executor:
            futures = [executor.submit(search_collection, col) for col in collections]

            for future in as_completed(futures):
                source, results = future.result()
                results_by_source[source] = results

        # Merge results with RRF fusion - use collections list to preserve order
        all_results = [results_by_source.get(col, []) for col in collections]

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

    async def search_bible(
        self,
        query: str,
        translation: str = "kjva",
        testament: str = None,
        top_k: int = None,
        detected_language: Optional[str] = None,
        language: str = "en",
    ) -> List:
        """
        Shortcut for Bible search.

        Automatically translates non-English queries to English using QueryTranslator
        and uses the translated query for reranking to ensure proper cross-lingual matching.

        If testament is specified (e.g., "ot", "nt", "apocrypha"), searches only that collection.
        Otherwise, searches all 3 Bible collections (bible_ot, bible_nt, bible_apocrypha) and
        merges results using RRF fusion.

        Args:
            language: "en" for English Bible (default) or "tr" for Turkish Bible
        """
        original_query = query
        translated_query = None

        # Handle Turkish Bible search
        if language == "tr":
            # Turkish Bible - no translation needed, query is already Turkish
            detected_language = "tr"
            translated_query = None

            if testament:
                source = f"bible_tr_{testament}"
                return await self.search(
                    query,
                    source=source,
                    top_k=top_k,
                    rerank_query=None,
                    detected_language="tr",
                )

            # Search all Turkish Bible collections
            return self._search_all_bible_collections(
                query,
                top_k=top_k,
                rerank_query=None,
                detected_language="tr",
                collections=["bible_tr_ot", "bible_tr_nt"],
            )

        # English Bible search - translate query to English
        if detected_language is None:
            try:
                result = self.translator.translate_query(query, "bible")
                detected_language = result.detected_language
                if result.was_translated:
                    translated_query = result.translated_query
                    query = translated_query
                    logger.info(
                        "Query translated for Bible search",
                        extra={
                            "from": result.detected_language,
                            "to": CORPUS_LANGUAGES.get("bible", "en"),
                            "original": original_query[:50],
                            "translated": result.translated_query[:50],
                        },
                    )
            except TranslationError as e:
                logger.error(
                    "Translation failed for Bible search",
                    extra={"error": str(e)},
                )
                raise

        # If testament is specified, search only that collection
        if testament:
            source = f"bible_{testament}"
            return await self.search(
                query,
                source=source,
                top_k=top_k,
                rerank_query=translated_query,
                detected_language=detected_language,
            )

        # Otherwise, search all 3 Bible collections and merge with RRF
        return self._search_all_bible_collections(
            query,
            top_k=top_k,
            rerank_query=translated_query,
            detected_language=detected_language,
        )

    # ============= ANSWER GENERATION (RAG) =============

    async def ask(
        self, query: str, source: str = "quran_tr_diyanet", top_k: int = None
    ):
        """
        Full RAG Pipeline: Search + Generate Answer with Citations

        Searches for relevant verses, then generates a comprehensive answer
        that cites specific verses using [Reference] format.

        Args:
            query: User's question
            source: Data source - "quran_tr_diyanet", "bible_ot", "bible_nt", etc.
            top_k: Number of search results to use as context

        Returns:
            AskResult with answer (AnswerResult) and search_results
        """

        top_k = top_k or self.final_top_k
        total_start = time.perf_counter()

        logger.info(
            "Pipeline started",
            extra={
                "pipeline": "ask",
                "source": source,
                "top_k": top_k,
                "query": query[:50],
            },
        )

        # Step 1-4: Search pipeline (enhance, multi-query, search, rerank)
        search_results = await self.search(query, source=source, top_k=top_k)

        # Step 5: Generate answer with citations
        logger.info("Pipeline stage started", extra={"stage": "answer_generation"})
        answer_start = time.perf_counter()

        answer = self.answer_generator.generate_answer(
            query,
            search_results,
            source=source,
            score_stats=self._last_score_stats,
        )

        answer_latency_ms = (time.perf_counter() - answer_start) * 1000
        total_latency_ms = (time.perf_counter() - total_start) * 1000

        log_performance(
            logger,
            "answer_generation",
            answer_latency_ms,
            citations=len(answer.citations),
            confidence=answer.confidence,
        )
        log_performance(
            logger,
            "pipeline_ask",
            total_latency_ms,
            source=source,
            verses=len(search_results),
            citations=len(answer.citations),
            confidence=answer.confidence,
        )

        return AskResult(answer=answer, search_results=search_results)

    async def ask_quran(
        self,
        query: str,
        translator: str = "diyanet",
        top_k: int = None,
        detected_language: Optional[str] = None,
    ):
        """
        Shortcut for Quran Q&A - Turkish in, Turkish out

        Args:
            query: Question to ask
            translator: Quran translator (diyanet, yazir, ates, bulac, ozturk, vakfi, yildirim, yuksel)
            top_k: Number of verses to use as context
            detected_language: Detected language of query
        """
        # Translate query to Turkish if needed (Quran corpus is Turkish)
        if detected_language is None:
            try:
                result = self.translator.translate_query(query, "quran")
                detected_language = result.detected_language
                if result.was_translated:
                    query = result.translated_query
                    logger.info(
                        "Query translated for Quran Q&A",
                        extra={
                            "from": result.detected_language,
                            "to": CORPUS_LANGUAGES.get("quran", "tr"),
                            "original": query[:50],
                            "translated": result.translated_query[:50],
                        },
                    )
            except TranslationError as e:
                logger.error(
                    "Translation failed for Quran Q&A",
                    extra={"error": str(e)},
                )
                raise

        return await self.ask(query, source=f"quran_tr_{translator}", top_k=top_k)

    async def ask_bible(
        self,
        query: str,
        translation: str = "kjva",
        testament: str = None,
        top_k: int = None,
        detected_language: Optional[str] = None,
    ):
        """
        Shortcut for Bible Q&A.

        Non-English query → English search → answer with English citations.
        """
        # Translate query to English for Bible search
        if detected_language is None:
            try:
                result = self.translator.translate_query(query, "bible")
                detected_language = result.detected_language
                if result.was_translated:
                    query = result.translated_query
                    logger.info(
                        "Query translated for Bible Q&A",
                        extra={
                            "from": result.detected_language,
                            "to": CORPUS_LANGUAGES.get("bible", "en"),
                            "original": query[:50],
                            "translated": result.translated_query[:50],
                        },
                    )
            except TranslationError as e:
                logger.error(
                    "Translation failed for Bible Q&A",
                    extra={"error": str(e)},
                )
                raise

        source = f"bible_{testament}" if testament else f"bible_{translation}"
        return await self.ask(query, source=source, top_k=top_k)


# Convenience function
def ultimate_search(
    query: str, source: str = "quran_tr_diyanet", top_k: int = 10
) -> List:
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
    from app.logging_config import setup_logging, LoggingConfig

    load_dotenv()

    # Setup logging for test
    setup_logging(LoggingConfig(level="DEBUG", format="console"))

    # Test the Ultimate RAG Pipeline
    logger.info("Testing Ultimate RAG Pipeline")

    rag = UltimateRAG()

    test_queries_quran = [
        "Kur'an'da şefaat kavramı nasıl açıklanır?",
    ]

    logger.info("--- QURAN TESTS ---")
    for query in test_queries_quran:
        results = rag.search_quran(query, top_k=3)
        logger.info(f"Query: {query}")
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

            print(f"  {i}. [{ref}] (score: {r.score:.4f})")
            print(f"     {text}...")

    logger.info("--- BIBLE TESTS ---")
    test_queries_bible = [
        "God's love and mercy",
    ]
    for query in test_queries_bible:
        results = rag.search_bible(query, top_k=3)
        logger.info(f"Query: {query}")
        for i, r in enumerate(results, 1):
            payload = getattr(r, "payload", {}) or {}
            book = getattr(r, "book_name", payload.get("book_name", "Unknown"))
            chapter = getattr(r, "chapter_number", payload.get("chapter_number"))
            verse = getattr(r, "verse_number", payload.get("verse_number"))

            ref = f"{book} {chapter}:{verse}"
            text = getattr(r, "text", getattr(r, "content", payload.get("text", "")))[
                :100
            ]

            print(f"  {i}. [{ref}] (score: {r.score:.4f})")
            print(f"     {text}...")
