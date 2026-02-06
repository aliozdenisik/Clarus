"""
Semantic Search Module

Provides semantic search capabilities for Quran and Bible data.
Uses dense vectors only (text-embedding-3-large).
"""

import time
from typing import List, Optional
from dataclasses import dataclass

from qdrant_client import QdrantClient

from .embeddings import DenseEncoder
from .circuit_breaker import qdrant_with_breaker
from .turkish_utils import expand_turkish_query
from app.logging_config import get_logger, log_performance

logger = get_logger(__name__)


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
    original_score: float = 0.0

    def __str__(self) -> str:
        return (
            f"[{self.surah_id}:{self.verse_id}] {self.surah_name} "
            f"({self.surah_transliteration}) - Score: {self.score:.3f}\n"
            f"  {self.translation[:100]}{'...' if len(self.translation) > 100 else ''}"
        )


class QuranSearcher:
    """
    Semantic search engine for Quran Turkish translation.
    Uses dense vectors only (text-embedding-3-large).
    """

    COLLECTION_NAME = "quran_tr"

    def __init__(
        self,
        qdrant_url: str = "http://localhost:6333",
        in_memory: bool = False,
        client: Optional[QdrantClient] = None,
        dense_encoder: Optional[DenseEncoder] = None,
    ):
        if client:
            self.client = client
        elif in_memory:
            self.client = QdrantClient(location=":memory:")
        else:
            self.client = QdrantClient(url=qdrant_url)
        self.dense_encoder = dense_encoder or DenseEncoder()

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
                original_score=point.score,
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
        start = time.perf_counter()
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

        parsed = self._parse_results(results)
        latency_ms = (time.perf_counter() - start) * 1000
        log_performance(
            logger,
            "semantic_search",
            latency_ms,
            collection=self.COLLECTION_NAME,
            mode="semantic",
            results=len(parsed),
        )
        return parsed

    def search_with_vector(
        self, query_vector: List[float], limit: int = 10
    ) -> List[SearchResult]:
        """
        Search using a pre-computed dense vector.
        Skips embedding computation — use when vectors are batch-encoded upfront.
        """
        start = time.perf_counter()

        results = qdrant_with_breaker(
            lambda: self.client.query_points(
                collection_name=self.COLLECTION_NAME,
                query=query_vector,
                using="dense",
                limit=limit,
                with_payload=True,
            )
        )

        parsed = self._parse_results(results)
        latency_ms = (time.perf_counter() - start) * 1000
        log_performance(
            logger,
            "semantic_search",
            latency_ms,
            collection=self.COLLECTION_NAME,
            mode="semantic_precomputed",
            results=len(parsed),
        )
        return parsed

    def search(
        self, query: str, mode: str = "semantic", limit: int = 10
    ) -> List[SearchResult]:
        """
        Search interface. Only semantic search is supported.

        Args:
            query: Search query text
            mode: Search mode (only "semantic" supported, kept for API compatibility)
            limit: Number of results
        """
        return self.semantic_search(query, limit)


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
    original_score: float = 0.0

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
    Semantic search engine for Bible translations.
    Uses dense vectors only (text-embedding-3-large).

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
                original_score=point.score,
            )
            search_results.append(result)
        return search_results

    def semantic_search(self, query: str, limit: int = 10) -> List[BibleSearchResult]:
        """
        Perform semantic search using dense vectors only.
        Good for conceptual/meaning-based queries.
        """
        start = time.perf_counter()
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

        parsed = self._parse_results(results)
        latency_ms = (time.perf_counter() - start) * 1000
        log_performance(
            logger,
            "semantic_search",
            latency_ms,
            collection=self.collection_name,
            mode="semantic",
            results=len(parsed),
        )
        return parsed

    def search_with_vector(
        self, query_vector: List[float], limit: int = 10
    ) -> List[BibleSearchResult]:
        """
        Search using a pre-computed dense vector.
        Skips embedding computation — use when vectors are batch-encoded upfront.
        """
        start = time.perf_counter()

        results = qdrant_with_breaker(
            lambda: self.client.query_points(
                collection_name=self.collection_name,
                query=query_vector,
                using="dense",
                limit=limit,
                with_payload=True,
            )
        )

        parsed = self._parse_results(results)
        latency_ms = (time.perf_counter() - start) * 1000
        log_performance(
            logger,
            "semantic_search",
            latency_ms,
            collection=self.collection_name,
            mode="semantic_precomputed",
            results=len(parsed),
        )
        return parsed

    def search(
        self, query: str, mode: str = "semantic", limit: int = 10
    ) -> List[BibleSearchResult]:
        """
        Search interface. Only semantic search is supported.

        Args:
            query: Search query text
            mode: Search mode (only "semantic" supported, kept for API compatibility)
            limit: Number of results
        """
        return self.semantic_search(query, limit)


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
    original_score: float = 0.0

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
    Uses dense vectors only (text-embedding-3-large).

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
    ):
        if client:
            self.client = client
        elif in_memory:
            self.client = QdrantClient(location=":memory:")
        else:
            self.client = QdrantClient(url=qdrant_url)

        self.dense_encoder = dense_encoder or DenseEncoder()

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
                    original_score=result.score,
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
        start = time.perf_counter()
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

        parsed = self._parse_results(results.points)
        latency_ms = (time.perf_counter() - start) * 1000
        log_performance(
            logger,
            "semantic_chunk_search",
            latency_ms,
            collection=self.COLLECTION_NAME,
            mode="semantic",
            results=len(parsed),
        )
        return parsed

    def search_with_vector(
        self, query_vector: List[float], limit: int = 10
    ) -> List[SemanticChunkSearchResult]:
        """
        Search using a pre-computed dense vector.
        Skips embedding computation — use when vectors are batch-encoded upfront.
        """
        start = time.perf_counter()

        results = qdrant_with_breaker(
            lambda: self.client.query_points(
                collection_name=self.COLLECTION_NAME,
                query=query_vector,
                using="dense",
                limit=limit,
            )
        )

        parsed = self._parse_results(results.points)
        latency_ms = (time.perf_counter() - start) * 1000
        log_performance(
            logger,
            "semantic_chunk_search",
            latency_ms,
            collection=self.COLLECTION_NAME,
            mode="semantic_precomputed",
            results=len(parsed),
        )
        return parsed

    def search(
        self, query: str, mode: str = "semantic", limit: int = 10
    ) -> List[SemanticChunkSearchResult]:
        """
        Unified search interface. Only semantic search is supported.

        Args:
            query: Search query text
            mode: Search mode (only "semantic" is supported)
            limit: Number of results
        """
        return self.semantic_search(query, limit)

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
    original_score: float = 0.0

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
                    original_score=result.score,
                )
            )
        return parsed

    def semantic_search(
        self, query: str, limit: int = 10
    ) -> List[BibleSemanticChunkSearchResult]:
        """Perform semantic search on chunk collection."""
        start = time.perf_counter()
        query_vector = self.dense_encoder.encode(query)

        results = qdrant_with_breaker(
            lambda: self.client.query_points(
                collection_name=self.collection_name,
                query=query_vector,
                using="dense",
                limit=limit,
            )
        )

        parsed = self._parse_results(results.points)
        latency_ms = (time.perf_counter() - start) * 1000
        log_performance(
            logger,
            "bible_semantic_chunk_search",
            latency_ms,
            collection=self.collection_name,
            mode="semantic",
            results=len(parsed),
        )
        return parsed

    def search_with_vector(
        self, query_vector: List[float], limit: int = 10
    ) -> List[BibleSemanticChunkSearchResult]:
        """
        Search using a pre-computed dense vector.
        Skips embedding computation — use when vectors are batch-encoded upfront.
        """
        start = time.perf_counter()

        results = qdrant_with_breaker(
            lambda: self.client.query_points(
                collection_name=self.collection_name,
                query=query_vector,
                using="dense",
                limit=limit,
            )
        )

        parsed = self._parse_results(results.points)
        latency_ms = (time.perf_counter() - start) * 1000
        log_performance(
            logger,
            "bible_semantic_chunk_search",
            latency_ms,
            collection=self.collection_name,
            mode="semantic_precomputed",
            results=len(parsed),
        )
        return parsed

    def search(
        self, query: str, mode: str = "semantic", limit: int = 10
    ) -> List[BibleSemanticChunkSearchResult]:
        """Unified search interface. Only semantic search is supported."""
        return self.semantic_search(query, limit)

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
