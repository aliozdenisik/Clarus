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
)

from .embeddings import DenseEncoder, SparseEncoder


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
    
    COLLECTION_NAME = "quran_tr"
    
    def __init__(
        self,
        qdrant_url: str = "http://localhost:6333",
        in_memory: bool = False,
        client: Optional[QdrantClient] = None,
        dense_encoder: Optional[DenseEncoder] = None,
        sparse_encoder: Optional[SparseEncoder] = None
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
    
    def semantic_search(self, query: str, limit: int = 10) -> List[SearchResult]:
        """
        Perform semantic search using dense vectors only.
        Good for conceptual/meaning-based queries.
        """
        query_vector = self.dense_encoder.encode(query)
        
        results = self.client.query_points(
            collection_name=self.COLLECTION_NAME,
            query=query_vector,
            using="dense",
            limit=limit,
            with_payload=True
        )
        
        return self._parse_results(results)
    
    def keyword_search(self, query: str, limit: int = 10) -> List[SearchResult]:
        """
        Perform keyword search using sparse vectors (BM25).
        Good for exact term matching.
        """
        indices, values = self.sparse_encoder.query_embed(query)
        
        results = self.client.query_points(
            collection_name=self.COLLECTION_NAME,
            query=SparseVector(indices=indices, values=values),
            using="sparse",
            limit=limit,
            with_payload=True
        )
        
        return self._parse_results(results)
    
    def hybrid_search(
        self, 
        query: str, 
        limit: int = 10,
        prefetch_limit: int = 20,
        fusion: str = "rrf"
    ) -> List[SearchResult]:
        """
        Perform hybrid search combining semantic and keyword search.
        Uses Reciprocal Rank Fusion (RRF) or DBSF to merge results.
        
        Args:
            query: Search query text
            limit: Number of final results
            prefetch_limit: Number of results to fetch from each search type
            fusion: Fusion method - "rrf" or "dbsf"
        """
        # Encode query for both dense and sparse
        dense_query = self.dense_encoder.encode(query)
        sparse_indices, sparse_values = self.sparse_encoder.query_embed(query)
        
        # Choose fusion method
        fusion_method = Fusion.RRF if fusion.lower() == "rrf" else Fusion.DBSF
        
        results = self.client.query_points(
            collection_name=self.COLLECTION_NAME,
            prefetch=[
                # Sparse (BM25) search
                Prefetch(
                    query=SparseVector(indices=sparse_indices, values=sparse_values),
                    using="sparse",
                    limit=prefetch_limit
                ),
                # Dense (semantic) search
                Prefetch(
                    query=dense_query,
                    using="dense",
                    limit=prefetch_limit
                )
            ],
            query=FusionQuery(fusion=fusion_method),
            limit=limit,
            with_payload=True
        )
        
        return self._parse_results(results)
    
    def search(
        self,
        query: str,
        mode: str = "hybrid",
        limit: int = 10
    ) -> List[SearchResult]:
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


def print_results(results: List[SearchResult], title: str = "Search Results"):
    """Pretty print search results"""
    print(f"\n{'='*60}")
    print(f"{title} ({len(results)} results)")
    print('='*60)
    
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
