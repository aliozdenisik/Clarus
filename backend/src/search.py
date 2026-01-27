"""
Hybrid Search Module

Provides semantic, keyword, and hybrid search capabilities for Quran data.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Prefetch,
    FusionQuery,
    Fusion,
    SparseVector,
    RrfQuery,
    Rrf,
)

from .embeddings import DenseEncoder, SparseEncoder
from .turkish_utils import expand_turkish_query, normalize_turkish
from .circuit_breaker import qdrant_with_breaker, CircuitBreakerError


@dataclass
class SearchResult:
    """Represents a single search result"""

    id: str
    score: float
    surah_id: int
    surah_name: str
    surah_transliteration: str
    verse_id: int
    arabic_text: str
    translation: str
    surah_type: str

    def __str__(self) -> str:
        return (
            f"[{self.surah_id}:{self.verse_id}] {self.surah_name} "
            f"({self.surah_transliteration}) - Score: {self.score:.3f}\n"
            f"  {self.translation[:100]}{'...' if len(self.translation) > 100 else ''}"
        )


class QuranSearcher:
    """
    Hybrid search engine for Quran Turkish translation.
    Supports semantic, keyword (BM25), and hybrid search modes.
    """

    COLLECTION_NAME = "quran_tr"  # Main collection

    def __init__(
        self,
        qdrant_url: str = "http://localhost:6333",
        in_memory: bool = False,
        client: Optional[QdrantClient] = None,
        dense_encoder: Optional[DenseEncoder] = None,
        sparse_encoder: Optional[SparseEncoder] = None,
    ):
        if client:
            self.client = client
        elif in_memory:
            self.client = QdrantClient(location=":memory:")
        else:
            self.client = QdrantClient(url=qdrant_url)
        self.dense_encoder = dense_encoder or DenseEncoder()
        self.sparse_encoder = sparse_encoder or SparseEncoder()

    def _parse_results(self, results) -> List[SearchResult]:
        """Convert Qdrant results to SearchResult objects"""
        search_results = []
        for point in results.points:
            payload = point.payload
            result = SearchResult(
                id=payload.get("id", ""),
                score=point.score,
                surah_id=payload.get("surah_id", 0),
                surah_name=payload.get("surah_name", ""),
                surah_transliteration=payload.get("surah_transliteration", ""),
                verse_id=payload.get("verse_id", 0),
                arabic_text=payload.get("arabic_text", ""),
                translation=payload.get("translation", ""),
                surah_type=payload.get("surah_type", ""),
            )
            search_results.append(result)
        return search_results

    def semantic_search(
        self, query: str, limit: int = 10, normalize: bool = True
    ) -> List[SearchResult]:
        """
        Perform semantic search using dense vectors only.
        Good for conceptual/meaning-based queries.

        Args:
            query: Search query text
            limit: Number of results to return
            normalize: If True, expand query with Turkish character variants
        """
        query_vector = self.dense_encoder.encode(query)

        results = qdrant_with_breaker(
            lambda: self.client.query_points(
                collection_name=self.COLLECTION_NAME,
                query=query_vector,
                using="dense",
                limit=limit,
                with_payload=True,
            )
        )

        return self._parse_results(results)

    def keyword_search(
        self, query: str, limit: int = 10, normalize: bool = True
    ) -> List[SearchResult]:
        """
        Perform keyword search using sparse vectors (BM25).
        Good for exact term matching.

        Args:
            query: Search query text
            limit: Number of results to return
            normalize: If True, expand query with Turkish character variants
        """
        # Expand query with Turkish character variants
        search_query = expand_turkish_query(query) if normalize else query
        indices, values = self.sparse_encoder.query_embed(search_query)

        results = qdrant_with_breaker(
            lambda: self.client.query_points(
                collection_name=self.COLLECTION_NAME,
                query=SparseVector(indices=indices, values=values),
                using="sparse",
                limit=limit,
                with_payload=True,
            )
        )

        return self._parse_results(results)

    def hybrid_search(
        self,
        query: str,
        limit: int = 10,
        prefetch_limit: int = 100,
        fusion: str = "rrf",
        rrf_k: int = 40,  # Optimized from 60 based on tuning research
        normalize: bool = True,
    ) -> List[SearchResult]:
        """
        Perform hybrid search combining semantic and keyword search.
        Uses Reciprocal Rank Fusion (RRF) or DBSF to merge results.

        Args:
            query: Search query text
            limit: Number of final results
            prefetch_limit: Number of results to fetch from each search type
            fusion: Fusion method - "rrf" or "dbsf"
            rrf_k: RRF k parameter (higher = more consensus-based ranking)
            normalize: If True, expand query with Turkish character variants for keyword search
        """
        # Encode query for both dense and sparse
        dense_query = self.dense_encoder.encode(query)
        # Apply Turkish normalization for keyword search
        keyword_query = expand_turkish_query(query) if normalize else query
        sparse_indices, sparse_values = self.sparse_encoder.query_embed(keyword_query)

        # Choose fusion method - use parameterized RRF or DBSF
        if fusion.lower() == "rrf":
            fusion_query = RrfQuery(rrf=Rrf(k=rrf_k))
        else:
            fusion_query = FusionQuery(fusion=Fusion.DBSF)

        results = qdrant_with_breaker(
            lambda: self.client.query_points(
                collection_name=self.COLLECTION_NAME,
                prefetch=[
                    # Sparse (BM25) search
                    Prefetch(
                        query=SparseVector(
                            indices=sparse_indices, values=sparse_values
                        ),
                        using="sparse",
                        limit=prefetch_limit,
                    ),
                    # Dense (semantic) search
                    Prefetch(query=dense_query, using="dense", limit=prefetch_limit),
                ],
                query=fusion_query,
                limit=limit,
                with_payload=True,
            )
        )

        return self._parse_results(results)

    def multi_query_search(
        self,
        query: str,
        limit: int = 10,
        prefetch_limit: int = 20,
        n_queries: int = 3,
        rrf_k: int = 60,
    ) -> List[SearchResult]:
        """
        Multi-Query RAG search (RAG-Fusion).

        Tek sorguyu birden fazla varyasyona dönüştürür, her biri için
        ayrı arama yapar, sonuçları RRF ile birleştirir.

        Args:
            query: Original search query
            limit: Number of final results
            prefetch_limit: Results per query prefetch
            n_queries: Number of query variations (3 optimal)
            rrf_k: RRF k parameter
        """
        from src.multi_query import MultiQueryGenerator, create_multi_query_prefetches

        # Generate query variations
        generator = MultiQueryGenerator()
        queries = generator.generate(query, n=n_queries)

        # Create prefetches for all queries
        prefetches = create_multi_query_prefetches(
            queries=queries,
            sparse_encoder=self.sparse_encoder,
            dense_encoder=self.dense_encoder,
            limit_per_query=prefetch_limit,
        )

        # RRF fusion
        results = self.client.query_points(
            collection_name=self.COLLECTION_NAME,
            prefetch=prefetches,
            query=RrfQuery(rrf=Rrf(k=rrf_k)),
            limit=limit,
            with_payload=True,
        )

        return self._parse_results(results)

    def parallel_keyword_search(
        self, query: str, limit: int = 10, prefetch_limit: int = 20, rrf_k: int = 60
    ) -> List[SearchResult]:
        """
        Parallel keyword search - her kelime için ayrı BM25 araması.

        "sabır ve namaz" -> "sabır" + "namaz" ayrı aranır, RRF ile birleştirilir.

        Args:
            query: Search query
            limit: Number of final results
            prefetch_limit: Results per keyword prefetch
            rrf_k: RRF k parameter
        """
        from src.multi_query import (
            ParallelKeywordParser,
            create_parallel_keyword_prefetches,
        )

        # Parse keywords
        parser = ParallelKeywordParser()
        keywords = parser.parse(query)

        # Create keyword prefetches
        keyword_prefetches = create_parallel_keyword_prefetches(
            keywords=keywords,
            sparse_encoder=self.sparse_encoder,
            limit_per_keyword=prefetch_limit,
        )

        # Also add semantic search prefetch for the full query
        dense_query = self.dense_encoder.encode(query)
        keyword_prefetches.append(
            Prefetch(query=dense_query, using="dense", limit=prefetch_limit)
        )

        # RRF fusion
        results = self.client.query_points(
            collection_name=self.COLLECTION_NAME,
            prefetch=keyword_prefetches,
            query=RrfQuery(rrf=Rrf(k=rrf_k)),
            limit=limit,
            with_payload=True,
        )

        return self._parse_results(results)

    def dual_vector_search(
        self, query: str, limit: int = 10, prefetch_limit: int = 50, rrf_k: int = 60
    ) -> List[SearchResult]:
        """
        Dual Vector Search - uses all 4 vector types for comprehensive search.

        Searches:
        - dense (original text embedding)
        - dense_normalized (normalized text embedding)
        - sparse (original text BM25)
        - sparse_normalized (normalized text BM25)

        Args:
            query: Search query
            limit: Number of final results
            prefetch_limit: Results per vector type
            rrf_k: RRF k parameter
        """
        # Normalize query
        query_norm = normalize_turkish(query.lower(), remove_punctuation=True)

        # Encode both versions
        dense_orig = self.dense_encoder.encode(query)
        dense_norm = self.dense_encoder.encode(query_norm)

        sparse_orig_idx, sparse_orig_val = self.sparse_encoder.encode(query)
        sparse_norm_idx, sparse_norm_val = self.sparse_encoder.encode(query_norm)

        # 4 prefetches for comprehensive search
        prefetches = [
            Prefetch(query=dense_orig, using="dense", limit=prefetch_limit),
            Prefetch(query=dense_norm, using="dense_normalized", limit=prefetch_limit),
            Prefetch(
                query=SparseVector(indices=sparse_orig_idx, values=sparse_orig_val),
                using="sparse",
                limit=prefetch_limit,
            ),
            Prefetch(
                query=SparseVector(indices=sparse_norm_idx, values=sparse_norm_val),
                using="sparse_normalized",
                limit=prefetch_limit,
            ),
        ]

        # RRF fusion
        results = self.client.query_points(
            collection_name=self.COLLECTION_NAME,
            prefetch=prefetches,
            query=RrfQuery(rrf=Rrf(k=rrf_k)),
            limit=limit,
            with_payload=True,
        )

        return self._parse_results(results)

    def search(
        self, query: str, mode: str = "hybrid", limit: int = 10
    ) -> List[SearchResult]:
        """
        Unified search interface.

        Args:
            query: Search query text
            mode: Search mode - "hybrid" (default), "dual-vector", "semantic", "keyword", "multi-query", "parallel-keyword"
            limit: Number of results
        """
        if mode == "semantic":
            return self.semantic_search(query, limit)
        elif mode == "keyword":
            return self.keyword_search(query, limit)
        elif mode == "multi-query":
            return self.multi_query_search(query, limit)
        elif mode == "parallel-keyword":
            return self.parallel_keyword_search(query, limit)
        elif mode == "hybrid":
            return self.hybrid_search(query, limit)
        else:  # default: dual-vector
            return self.dual_vector_search(query, limit)


@dataclass
class BibleSearchResult:
    """Represents a single Bible search result"""

    id: str
    score: float
    translation: str
    book_id: int
    book_name: str
    chapter: int
    verse: int
    text: str
    testament: str

    def __str__(self) -> str:
        testament_display = {
            "OT": "Eski Ahit",
            "NT": "Yeni Ahit",
            "Apocrypha": "Apokrif",
        }.get(self.testament, self.testament)

        return (
            f"[{self.book_name} {self.chapter}:{self.verse}] "
            f"({testament_display}) - Score: {self.score:.3f}\n"
            f"  {self.text[:100]}{'...' if len(self.text) > 100 else ''}"
        )


class BibleSearcher:
    """
    Hybrid search engine for Bible translations.
    Supports semantic, keyword (BM25), and hybrid search modes.

    Can search specific testaments via the testament parameter:
    - "ot" -> bible_ot collection (Old Testament)
    - "nt" -> bible_nt collection (New Testament)
    - "apocrypha" -> bible_apocrypha collection
    - None -> searches the combined collection if exists, otherwise raises error
    """

    # Testament to collection name mapping
    TESTAMENT_COLLECTIONS = {
        "ot": "bible_ot",
        "nt": "bible_nt",
        "apocrypha": "bible_apocrypha",
    }

    def __init__(
        self,
        translation: str = "kjva",
        testament: Optional[str] = None,
        qdrant_url: str = "http://localhost:6333",
        in_memory: bool = False,
        client: Optional[QdrantClient] = None,
        dense_encoder: Optional[DenseEncoder] = None,
        sparse_encoder: Optional[SparseEncoder] = None,
    ):
        self.translation = translation
        self.testament = testament.lower() if testament else None

        # Determine collection name based on testament
        if self.testament:
            if self.testament not in self.TESTAMENT_COLLECTIONS:
                raise ValueError(
                    f"Invalid testament: {testament}. Must be one of: ot, nt, apocrypha"
                )
            self.collection_name = self.TESTAMENT_COLLECTIONS[self.testament]
        else:
            # Legacy: use combined collection (may not exist after migration)
            self.collection_name = f"bible_{translation}"

        if client:
            self.client = client
        elif in_memory:
            self.client = QdrantClient(location=":memory:")
        else:
            self.client = QdrantClient(url=qdrant_url)
        self.dense_encoder = dense_encoder or DenseEncoder()
        self.sparse_encoder = sparse_encoder or SparseEncoder()

    def _parse_results(self, results) -> List[BibleSearchResult]:
        """Convert Qdrant results to BibleSearchResult objects"""
        search_results = []
        for point in results.points:
            payload = point.payload
            result = BibleSearchResult(
                id=payload.get("id", ""),
                score=point.score,
                translation=payload.get("translation", ""),
                book_id=payload.get("book_id", 0),
                book_name=payload.get("book_name", ""),
                chapter=payload.get("chapter", 0),
                verse=payload.get("verse", 0),
                text=payload.get("text", ""),
                testament=payload.get("testament", ""),
            )
            search_results.append(result)
        return search_results

    def semantic_search(self, query: str, limit: int = 10) -> List[BibleSearchResult]:
        """
        Perform semantic search using dense vectors only.
        Good for conceptual/meaning-based queries.
        """
        query_vector = self.dense_encoder.encode(query)

        results = qdrant_with_breaker(
            lambda: self.client.query_points(
                collection_name=self.collection_name,
                query=query_vector,
                using="dense",
                limit=limit,
                with_payload=True,
            )
        )

        return self._parse_results(results)

    def keyword_search(self, query: str, limit: int = 10) -> List[BibleSearchResult]:
        """
        Perform keyword search using sparse vectors (BM25).
        Good for exact term matching.
        """
        indices, values = self.sparse_encoder.query_embed(query)

        results = qdrant_with_breaker(
            lambda: self.client.query_points(
                collection_name=self.collection_name,
                query=SparseVector(indices=indices, values=values),
                using="sparse",
                limit=limit,
                with_payload=True,
            )
        )

        return self._parse_results(results)

    def hybrid_search(
        self,
        query: str,
        limit: int = 10,
        prefetch_limit: int = 20,
        fusion: str = "rrf",
        rrf_k: int = 60,
    ) -> List[BibleSearchResult]:
        """
        Perform hybrid search combining semantic and keyword search.
        Uses Reciprocal Rank Fusion (RRF) or DBSF to merge results.

        Args:
            query: Search query text
            limit: Number of final results
            prefetch_limit: Number of results to fetch from each search type
            fusion: Fusion method - "rrf" or "dbsf"
            rrf_k: RRF k parameter (higher = more consensus-based ranking)
        """
        # Encode query for both dense and sparse
        dense_query = self.dense_encoder.encode(query)
        sparse_indices, sparse_values = self.sparse_encoder.query_embed(query)

        # Choose fusion method - use parameterized RRF or DBSF
        if fusion.lower() == "rrf":
            fusion_query = RrfQuery(rrf=Rrf(k=rrf_k))
        else:
            fusion_query = FusionQuery(fusion=Fusion.DBSF)

        results = qdrant_with_breaker(
            lambda: self.client.query_points(
                collection_name=self.collection_name,
                prefetch=[
                    # Sparse (BM25) search
                    Prefetch(
                        query=SparseVector(
                            indices=sparse_indices, values=sparse_values
                        ),
                        using="sparse",
                        limit=prefetch_limit,
                    ),
                    # Dense (semantic) search
                    Prefetch(query=dense_query, using="dense", limit=prefetch_limit),
                ],
                query=fusion_query,
                limit=limit,
                with_payload=True,
            )
        )

        return self._parse_results(results)

    def search(
        self, query: str, mode: str = "hybrid", limit: int = 10
    ) -> List[BibleSearchResult]:
        """
        Unified search interface.

        Args:
            query: Search query text
            mode: Search mode - "hybrid", "semantic", or "keyword"
            limit: Number of results
        """
        if mode == "semantic":
            return self.semantic_search(query, limit)
        elif mode == "keyword":
            return self.keyword_search(query, limit)
        else:
            return self.hybrid_search(query, limit)


@dataclass
class SemanticChunkSearchResult:
    """Represents a semantic chunk search result (grouped verses)."""

    chunk_id: str
    score: float
    verse_ids: List[str]
    surah_id: int
    surah_name: str
    surah_transliteration: str
    start_verse: int
    end_verse: int
    combined_translation: str
    combined_arabic: str
    verse_count: int
    surah_type: str

    def __str__(self):
        verse_range = (
            f"{self.start_verse}-{self.end_verse}"
            if self.start_verse != self.end_verse
            else str(self.start_verse)
        )
        preview = (
            self.combined_translation[:200] + "..."
            if len(self.combined_translation) > 200
            else self.combined_translation
        )
        return f"[{self.surah_name} {verse_range}] (Score: {self.score:.4f}, {self.verse_count} verses)\n   {preview}"


class SemanticChunkSearcher:
    """
    Search engine for semantic chunks (grouped verses).

    Provides context-aware search by searching grouped verses instead of
    individual verses. Can be used alongside QuranSearcher for comprehensive results.
    """

    COLLECTION_NAME = "quran_semantic_chunks"

    def __init__(
        self,
        qdrant_url: str = "http://localhost:6333",
        in_memory: bool = False,
        client: Optional[QdrantClient] = None,
        dense_encoder: Optional[DenseEncoder] = None,
        sparse_encoder: Optional[SparseEncoder] = None,
    ):
        if client:
            self.client = client
        elif in_memory:
            self.client = QdrantClient(location=":memory:")
        else:
            self.client = QdrantClient(url=qdrant_url)

        self.dense_encoder = dense_encoder or DenseEncoder()
        self.sparse_encoder = sparse_encoder or SparseEncoder()

    def _parse_results(self, results) -> List[SemanticChunkSearchResult]:
        """Convert Qdrant results to SemanticChunkSearchResult objects."""
        parsed = []
        for result in results:
            payload = result.payload
            parsed.append(
                SemanticChunkSearchResult(
                    chunk_id=payload.get("chunk_id", ""),
                    score=result.score,
                    verse_ids=payload.get("verse_ids", []),
                    surah_id=payload.get("surah_id", 0),
                    surah_name=payload.get("surah_name", ""),
                    surah_transliteration=payload.get("surah_transliteration", ""),
                    start_verse=payload.get("start_verse", 0),
                    end_verse=payload.get("end_verse", 0),
                    combined_translation=payload.get("combined_translation", ""),
                    combined_arabic=payload.get("combined_arabic", ""),
                    verse_count=payload.get("verse_count", 1),
                    surah_type=payload.get("surah_type", ""),
                )
            )
        return parsed

    def semantic_search(
        self, query: str, limit: int = 10, normalize: bool = True
    ) -> List[SemanticChunkSearchResult]:
        """
        Perform semantic search on chunk collection.

        Args:
            query: Search query text
            limit: Number of results to return
            normalize: If True, expand query with Turkish character variants
        """
        if normalize:
            query = expand_turkish_query(query)

        query_vector = self.dense_encoder.encode(query)

        results = qdrant_with_breaker(
            lambda: self.client.query_points(
                collection_name=self.COLLECTION_NAME,
                query=query_vector,
                using="dense",
                limit=limit,
            )
        )

        return self._parse_results(results.points)

    def keyword_search(
        self, query: str, limit: int = 10, normalize: bool = True
    ) -> List[SemanticChunkSearchResult]:
        """
        Perform keyword (BM25) search on chunk collection.

        Args:
            query: Search query text
            limit: Number of results to return
            normalize: If True, normalize Turkish characters
        """
        if normalize:
            query = normalize_turkish(query)

        sparse_indices, sparse_values = self.sparse_encoder.query_embed(query)

        results = qdrant_with_breaker(
            lambda: self.client.query_points(
                collection_name=self.COLLECTION_NAME,
                query=SparseVector(indices=sparse_indices, values=sparse_values),
                using="sparse",
                limit=limit,
            )
        )

        return self._parse_results(results.points)

    def hybrid_search(
        self,
        query: str,
        limit: int = 10,
        prefetch_limit: int = 50,
        rrf_k: int = 40,
        normalize: bool = True,
    ) -> List[SemanticChunkSearchResult]:
        """
        Perform hybrid search combining semantic and keyword search.
        Uses Reciprocal Rank Fusion (RRF) to merge results.

        Args:
            query: Search query text
            limit: Number of final results
            prefetch_limit: Results per search type
            rrf_k: RRF k parameter (higher = more weight to lower ranks)
            normalize: If True, apply Turkish normalization
        """
        # Prepare query vectors
        if normalize:
            expanded_query = expand_turkish_query(query)
            normalized_query = normalize_turkish(query)
        else:
            expanded_query = query
            normalized_query = query

        dense_vector = self.dense_encoder.encode(expanded_query)
        sparse_indices, sparse_values = self.sparse_encoder.query_embed(
            normalized_query
        )

        # Hybrid search with RRF
        results = qdrant_with_breaker(
            lambda: self.client.query_points(
                collection_name=self.COLLECTION_NAME,
                prefetch=[
                    Prefetch(query=dense_vector, using="dense", limit=prefetch_limit),
                    Prefetch(
                        query=SparseVector(
                            indices=sparse_indices, values=sparse_values
                        ),
                        using="sparse",
                        limit=prefetch_limit,
                    ),
                ],
                query=RrfQuery(rrf=Rrf(k=rrf_k)),
                limit=limit,
            )
        )

        return self._parse_results(results.points)

    def search(
        self, query: str, mode: str = "hybrid", limit: int = 10
    ) -> List[SemanticChunkSearchResult]:
        """
        Unified search interface.

        Args:
            query: Search query text
            mode: Search mode - "hybrid" (default), "semantic", or "keyword"
            limit: Number of results
        """
        if mode == "semantic":
            return self.semantic_search(query, limit)
        elif mode == "keyword":
            return self.keyword_search(query, limit)
        else:
            return self.hybrid_search(query, limit)

    def collection_exists(self) -> bool:
        """Check if the semantic chunks collection exists."""
        try:
            collections = self.client.get_collections().collections
            return any(c.name == self.COLLECTION_NAME for c in collections)
        except Exception:
            return False


@dataclass
class BibleSemanticChunkSearchResult:
    """Represents a Bible semantic chunk search result (grouped verses)."""

    chunk_id: str
    score: float
    verse_ids: List[str]
    translation: str
    book_id: int
    book_name: str
    chapter: int
    start_verse: int
    end_verse: int
    text: str
    verse_count: int
    testament: str

    def __str__(self):
        verse_range = (
            f"{self.start_verse}-{self.end_verse}"
            if self.start_verse != self.end_verse
            else str(self.start_verse)
        )
        preview = self.text[:200] + "..." if len(self.text) > 200 else self.text
        return f"[{self.book_name} {self.chapter}:{verse_range}] (Score: {self.score:.4f}, {self.verse_count} verses)\n   {preview}"


class BibleSemanticChunkSearcher:
    """
    Search engine for Bible semantic chunks (grouped verses).
    """

    def __init__(
        self,
        translation: str = "kjva",
        qdrant_url: str = "http://localhost:6333",
        in_memory: bool = False,
        client: Optional[QdrantClient] = None,
        dense_encoder: Optional[DenseEncoder] = None,
        sparse_encoder: Optional[SparseEncoder] = None,
    ):
        self.translation = translation
        self.collection_name = f"bible_{translation}_semantic_chunks"

        if client:
            self.client = client
        elif in_memory:
            self.client = QdrantClient(location=":memory:")
        else:
            self.client = QdrantClient(url=qdrant_url)

        self.dense_encoder = dense_encoder or DenseEncoder()
        self.sparse_encoder = sparse_encoder or SparseEncoder()

    def _parse_results(self, results) -> List[BibleSemanticChunkSearchResult]:
        """Convert Qdrant results to BibleSemanticChunkSearchResult objects."""
        parsed = []
        for result in results:
            payload = result.payload
            parsed.append(
                BibleSemanticChunkSearchResult(
                    chunk_id=payload.get("chunk_id", ""),
                    score=result.score,
                    verse_ids=payload.get("verse_ids", []),
                    translation=payload.get("translation", ""),
                    book_id=payload.get("book_id", 0),
                    book_name=payload.get("book_name", ""),
                    chapter=payload.get("chapter", 0),
                    start_verse=payload.get("start_verse", 0),
                    end_verse=payload.get("end_verse", 0),
                    text=payload.get("text", ""),
                    verse_count=payload.get("verse_count", 1),
                    testament=payload.get("testament", ""),
                )
            )
        return parsed

    def semantic_search(
        self, query: str, limit: int = 10
    ) -> List[BibleSemanticChunkSearchResult]:
        """Perform semantic search on chunk collection."""
        query_vector = self.dense_encoder.encode(query)

        results = qdrant_with_breaker(
            lambda: self.client.query_points(
                collection_name=self.collection_name,
                query=query_vector,
                using="dense",
                limit=limit,
            )
        )

        return self._parse_results(results.points)

    def keyword_search(
        self, query: str, limit: int = 10
    ) -> List[BibleSemanticChunkSearchResult]:
        """Perform keyword (BM25) search on chunk collection."""
        sparse_indices, sparse_values = self.sparse_encoder.query_embed(query)

        results = qdrant_with_breaker(
            lambda: self.client.query_points(
                collection_name=self.collection_name,
                query=SparseVector(indices=sparse_indices, values=sparse_values),
                using="sparse",
                limit=limit,
            )
        )

        return self._parse_results(results.points)

    def hybrid_search(
        self, query: str, limit: int = 10, prefetch_limit: int = 50, rrf_k: int = 40
    ) -> List[BibleSemanticChunkSearchResult]:
        """Perform hybrid search combining semantic and keyword search."""
        dense_vector = self.dense_encoder.encode(query)
        sparse_indices, sparse_values = self.sparse_encoder.query_embed(query)

        results = qdrant_with_breaker(
            lambda: self.client.query_points(
                collection_name=self.collection_name,
                prefetch=[
                    Prefetch(query=dense_vector, using="dense", limit=prefetch_limit),
                    Prefetch(
                        query=SparseVector(
                            indices=sparse_indices, values=sparse_values
                        ),
                        using="sparse",
                        limit=prefetch_limit,
                    ),
                ],
                query=RrfQuery(rrf=Rrf(k=rrf_k)),
                limit=limit,
            )
        )

        return self._parse_results(results.points)

    def search(
        self, query: str, mode: str = "hybrid", limit: int = 10
    ) -> List[BibleSemanticChunkSearchResult]:
        """Unified search interface."""
        if mode == "semantic":
            return self.semantic_search(query, limit)
        elif mode == "keyword":
            return self.keyword_search(query, limit)
        else:
            return self.hybrid_search(query, limit)

    def collection_exists(self) -> bool:
        """Check if the semantic chunks collection exists."""
        try:
            collections = self.client.get_collections().collections
            return any(c.name == self.collection_name for c in collections)
        except Exception:
            return False


def print_results(results: List[SearchResult], title: str = "Search Results"):
    """Pretty print search results"""
    print(f"\n{'=' * 60}")
    print(f"{title} ({len(results)} results)")
    print("=" * 60)

    for i, result in enumerate(results, 1):
        print(f"\n{i}. {result}")

    print()


if __name__ == "__main__":
    # Test search
    searcher = QuranSearcher()

    test_query = "Allah'ın rahmeti"

    print(f"\nQuery: '{test_query}'")

    print("\n--- Semantic Search ---")
    results = searcher.semantic_search(test_query, limit=3)
    print_results(results, "Semantic Results")

    print("\n--- Keyword Search ---")
    results = searcher.keyword_search(test_query, limit=3)
    print_results(results, "Keyword Results")

    print("\n--- Hybrid Search ---")
    results = searcher.hybrid_search(test_query, limit=3)
    print_results(results, "Hybrid Results")
