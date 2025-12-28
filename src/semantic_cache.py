"""
Semantic Cache Module for RAG Query Caching

Caches query-response pairs using vector similarity search in Qdrant.
Similar queries (above threshold) return cached responses instantly,
reducing API costs and latency significantly.

Features:
- Cosine similarity matching (default threshold: 0.85)
- TTL-based expiration (default: 24 hours)
- Separate Qdrant collection for cache isolation
- Cache statistics tracking

Usage:
    from src.semantic_cache import SemanticCache
    
    cache = SemanticCache(similarity_threshold=0.85)
    
    # Check cache
    cached = cache.get("Allah'ın rahmeti nedir?")
    if cached:
        return cached.response
    
    # After getting response
    cache.set(query, response, metadata={"source": "quran"})
"""
import os
import time
import hashlib
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta

from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.models import (
    VectorParams, Distance, PointStruct,
    Filter, FieldCondition, Range
)


@dataclass
class CachedResponse:
    """Represents a cached query-response pair."""
    query: str
    response: Any
    similarity: float
    cached_at: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def age_hours(self) -> float:
        """Age of cached entry in hours."""
        return (datetime.now() - self.cached_at).total_seconds() / 3600


@dataclass
class CacheStats:
    """Cache statistics."""
    total_entries: int
    hits: int
    misses: int
    hit_rate: float
    avg_similarity: float
    oldest_entry_hours: float


class SemanticCache:
    """
    Semantic cache for query-response pairs using Qdrant.
    
    Stores query embeddings and responses, returns cached responses
    for semantically similar queries above the similarity threshold.
    """
    
    COLLECTION_NAME = "semantic_cache"
    VECTOR_SIZE = 3072  # text-embedding-3-large dimension
    
    def __init__(
        self,
        similarity_threshold: float = 0.85,
        ttl_hours: int = 24,
        qdrant_url: str = "http://localhost:6333",
        encoder = None
    ):
        """
        Initialize semantic cache.
        
        Args:
            similarity_threshold: Minimum cosine similarity for cache hit (0.0-1.0)
            ttl_hours: Time-to-live for cache entries in hours
            qdrant_url: Qdrant server URL
            encoder: DenseEncoder instance (lazy loaded if not provided)
        """
        self.similarity_threshold = similarity_threshold
        self.ttl_hours = ttl_hours
        self.qdrant_url = qdrant_url
        self._encoder = encoder
        self._client = None
        
        # Statistics tracking
        self._hits = 0
        self._misses = 0
        self._similarity_sum = 0.0
        
    @property
    def client(self) -> QdrantClient:
        """Lazy load Qdrant client."""
        if self._client is None:
            self._client = QdrantClient(url=self.qdrant_url)
            self._ensure_collection()
        return self._client
    
    @property
    def encoder(self):
        """Lazy load embedding encoder."""
        if self._encoder is None:
            from src.embeddings import DenseEncoder
            self._encoder = DenseEncoder()
        return self._encoder
    
    def _ensure_collection(self):
        """Create cache collection if it doesn't exist."""
        collections = [c.name for c in self.client.get_collections().collections]
        
        if self.COLLECTION_NAME not in collections:
            self.client.create_collection(
                collection_name=self.COLLECTION_NAME,
                vectors_config=VectorParams(
                    size=self.VECTOR_SIZE,
                    distance=Distance.COSINE
                )
            )
            print(f"Created semantic cache collection: {self.COLLECTION_NAME}")
    
    def _generate_id(self, query: str) -> str:
        """Generate unique ID for a query."""
        return hashlib.md5(query.encode()).hexdigest()
    
    def _is_expired(self, cached_at: float) -> bool:
        """Check if cache entry is expired."""
        age_hours = (time.time() - cached_at) / 3600
        return age_hours > self.ttl_hours
    
    def get(self, query: str) -> Optional[CachedResponse]:
        """
        Check cache for similar query.
        
        Args:
            query: Search query to check
            
        Returns:
            CachedResponse if similar query found, None otherwise
        """
        try:
            # Embed query
            query_vector = self.encoder.encode(query)
            
            # Search for similar queries
            results = self.client.search(
                collection_name=self.COLLECTION_NAME,
                query_vector=query_vector,
                limit=1,
                score_threshold=self.similarity_threshold
            )
            
            if not results:
                self._misses += 1
                return None
            
            top_result = results[0]
            payload = top_result.payload
            
            # Check TTL
            cached_at = payload.get("cached_at", 0)
            if self._is_expired(cached_at):
                self._misses += 1
                # Optionally delete expired entry
                self.client.delete(
                    collection_name=self.COLLECTION_NAME,
                    points_selector=models.PointIdsList(
                        points=[top_result.id]
                    )
                )
                return None
            
            # Cache hit!
            self._hits += 1
            self._similarity_sum += top_result.score
            
            return CachedResponse(
                query=payload.get("query", ""),
                response=payload.get("response"),
                similarity=top_result.score,
                cached_at=datetime.fromtimestamp(cached_at),
                metadata=payload.get("metadata", {})
            )
            
        except Exception as e:
            print(f"Cache get error: {e}")
            self._misses += 1
            return None
    
    def set(
        self,
        query: str,
        response: Any,
        metadata: Dict[str, Any] = None
    ) -> bool:
        """
        Store query-response pair in cache.
        
        Args:
            query: Original query
            response: Response to cache (must be JSON-serializable)
            metadata: Optional metadata (source, mode, etc.)
            
        Returns:
            True if cached successfully
        """
        try:
            # Embed query
            query_vector = self.encoder.encode(query)
            
            # Prepare payload
            payload = {
                "query": query,
                "response": self._serialize_response(response),
                "cached_at": time.time(),
                "metadata": metadata or {}
            }
            
            # Upsert to cache
            self.client.upsert(
                collection_name=self.COLLECTION_NAME,
                points=[
                    PointStruct(
                        id=self._generate_id(query),
                        vector=query_vector,
                        payload=payload
                    )
                ]
            )
            
            return True
            
        except Exception as e:
            print(f"Cache set error: {e}")
            return False
    
    def _serialize_response(self, response: Any) -> Any:
        """Serialize response for storage."""
        # If response is a list of result objects, convert to dict
        if isinstance(response, list) and len(response) > 0:
            if hasattr(response[0], '__dict__'):
                return [self._result_to_dict(r) for r in response]
        return response
    
    def _result_to_dict(self, result) -> Dict:
        """Convert search result to dictionary."""
        # Handle QuranSearchResult
        if hasattr(result, 'surah_id'):
            return {
                "id": result.id,
                "surah_id": result.surah_id,
                "verse_id": result.verse_id,
                "surah_name": result.surah_name,
                "surah_transliteration": getattr(result, 'surah_transliteration', ''),
                "surah_type": getattr(result, 'surah_type', ''),
                "translation": result.translation,
                "arabic_text": getattr(result, 'arabic_text', ''),
                "score": result.score
            }
        # Handle BibleSearchResult
        elif hasattr(result, 'book_name'):
            return {
                "id": result.id,
                "book_name": result.book_name,
                "chapter": result.chapter,
                "verse": result.verse,
                "text": result.text,
                "testament": getattr(result, 'testament', ''),
                "translation": getattr(result, 'translation', ''),
                "score": result.score
            }
        # Fallback
        return result.__dict__ if hasattr(result, '__dict__') else result
    
    def clear(self, older_than_hours: int = None) -> int:
        """
        Clear cache entries.
        
        Args:
            older_than_hours: Only clear entries older than this (None = clear all)
            
        Returns:
            Number of entries deleted
        """
        try:
            if older_than_hours is None:
                # Clear all
                info = self.client.get_collection(self.COLLECTION_NAME)
                count = info.points_count
                self.client.delete_collection(self.COLLECTION_NAME)
                self._ensure_collection()
                return count
            else:
                # Clear expired only
                cutoff = time.time() - (older_than_hours * 3600)
                
                # Get expired entries
                results = self.client.scroll(
                    collection_name=self.COLLECTION_NAME,
                    scroll_filter=Filter(
                        must=[
                            FieldCondition(
                                key="cached_at",
                                range=Range(lt=cutoff)
                            )
                        ]
                    ),
                    limit=1000
                )
                
                points, _ = results
                if points:
                    point_ids = [p.id for p in points]
                    self.client.delete(
                        collection_name=self.COLLECTION_NAME,
                        points_selector=models.PointIdsList(points=point_ids)
                    )
                    return len(point_ids)
                return 0
                
        except Exception as e:
            print(f"Cache clear error: {e}")
            return 0
    
    def get_stats(self) -> CacheStats:
        """Get cache statistics."""
        try:
            info = self.client.get_collection(self.COLLECTION_NAME)
            total = info.points_count
            
            total_requests = self._hits + self._misses
            hit_rate = self._hits / total_requests if total_requests > 0 else 0.0
            avg_sim = self._similarity_sum / self._hits if self._hits > 0 else 0.0
            
            # Get oldest entry
            oldest_hours = 0.0
            if total > 0:
                results = self.client.scroll(
                    collection_name=self.COLLECTION_NAME,
                    limit=1,
                    with_payload=True
                )
                if results[0]:
                    cached_at = results[0][0].payload.get("cached_at", time.time())
                    oldest_hours = (time.time() - cached_at) / 3600
            
            return CacheStats(
                total_entries=total,
                hits=self._hits,
                misses=self._misses,
                hit_rate=hit_rate,
                avg_similarity=avg_sim,
                oldest_entry_hours=oldest_hours
            )
            
        except Exception as e:
            print(f"Stats error: {e}")
            return CacheStats(0, 0, 0, 0.0, 0.0, 0.0)


# Global cache instance (lazy initialized)
_cache_instance = None


def get_cache(
    similarity_threshold: float = 0.85,
    ttl_hours: int = 24
) -> SemanticCache:
    """Get or create global cache instance."""
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = SemanticCache(
            similarity_threshold=similarity_threshold,
            ttl_hours=ttl_hours
        )
    return _cache_instance


if __name__ == "__main__":
    # Test semantic cache
    print("Testing Semantic Cache...")
    
    cache = SemanticCache(similarity_threshold=0.80)
    
    # Test set
    print("\n1. Caching a query...")
    cache.set(
        query="Allah'ın rahmeti nedir?",
        response=[{"text": "Test response", "score": 0.95}],
        metadata={"source": "quran", "mode": "hybrid"}
    )
    print("   Cached successfully!")
    
    # Test get (exact match)
    print("\n2. Testing exact match...")
    result = cache.get("Allah'ın rahmeti nedir?")
    if result:
        print(f"   HIT! Similarity: {result.similarity:.3f}")
    else:
        print("   MISS")
    
    # Test get (similar query)
    print("\n3. Testing similar query...")
    result = cache.get("Allah'ın merhameti ne demek?")
    if result:
        print(f"   HIT! Similarity: {result.similarity:.3f}")
    else:
        print("   MISS (below threshold)")
    
    # Stats
    print("\n4. Cache stats:")
    stats = cache.get_stats()
    print(f"   Total entries: {stats.total_entries}")
    print(f"   Hits: {stats.hits}, Misses: {stats.misses}")
    print(f"   Hit rate: {stats.hit_rate:.1%}")
