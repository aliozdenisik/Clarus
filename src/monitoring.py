"""
Observability Module

Provides monitoring, metrics, and logging for the RAG system.

Features:
- Prometheus metrics (latency, API calls, cache hits)
- Structured logging
- Performance timing decorators

Usage:
    from src.monitoring import metrics, log_search
    
    with metrics.search_latency("hybrid"):
        results = searcher.search(query)
    
    log_search(query, mode="hybrid", results_count=len(results))
"""
import time
import logging
from typing import Optional, Any
from functools import wraps
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("sacred_texts_search")


@dataclass
class MetricsCollector:
    """
    Simple in-memory metrics collector.
    
    Can be extended to export to Prometheus if prometheus_client is available.
    """
    search_count: int = 0
    embedding_api_calls: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    rerank_count: int = 0
    
    search_latencies: list = field(default_factory=list)
    embedding_latencies: list = field(default_factory=list)
    rerank_latencies: list = field(default_factory=list)
    
    _prometheus_available: bool = False
    
    def __post_init__(self):
        """Try to initialize Prometheus metrics if available"""
        try:
            from prometheus_client import Counter, Histogram, Gauge
            
            self.prom_search_count = Counter(
                'sacred_texts_search_total', 
                'Total search requests',
                ['mode', 'source']  # mode: hybrid/semantic/keyword, source: quran/bible
            )
            self.prom_search_latency = Histogram(
                'sacred_texts_search_latency_seconds',
                'Search latency in seconds',
                ['mode']
            )
            self.prom_embedding_calls = Counter(
                'sacred_texts_embedding_api_calls_total',
                'Total embedding API calls',
                ['cached']  # 'hit' or 'miss'
            )
            self.prom_cache_hit_rate = Gauge(
                'sacred_texts_cache_hit_rate',
                'Cache hit rate (0-1)'
            )
            
            self._prometheus_available = True
            logger.info("Prometheus metrics initialized")
            
        except ImportError:
            logger.debug("prometheus_client not installed, using in-memory metrics only")
    
    @contextmanager
    def search_timer(self, mode: str = "hybrid", source: str = "quran"):
        """Context manager to time search operations"""
        start = time.time()
        try:
            yield
        finally:
            latency = time.time() - start
            self.search_count += 1
            self.search_latencies.append(latency)
            
            # Keep only last 1000 latencies
            if len(self.search_latencies) > 1000:
                self.search_latencies = self.search_latencies[-1000:]
            
            if self._prometheus_available:
                self.prom_search_count.labels(mode=mode, source=source).inc()
                self.prom_search_latency.labels(mode=mode).observe(latency)
    
    def record_embedding_call(self, cached: bool):
        """Record an embedding API call"""
        self.embedding_api_calls += 1
        if cached:
            self.cache_hits += 1
        else:
            self.cache_misses += 1
        
        if self._prometheus_available:
            self.prom_embedding_calls.labels(cached='hit' if cached else 'miss').inc()
            
            # Update cache hit rate
            total = self.cache_hits + self.cache_misses
            if total > 0:
                self.prom_cache_hit_rate.set(self.cache_hits / total)
    
    def record_rerank(self, latency: float):
        """Record a rerank operation"""
        self.rerank_count += 1
        self.rerank_latencies.append(latency)
        
        if len(self.rerank_latencies) > 1000:
            self.rerank_latencies = self.rerank_latencies[-1000:]
    
    def get_stats(self) -> dict:
        """Get current metrics as dictionary"""
        total_cache = self.cache_hits + self.cache_misses
        
        return {
            "search_count": self.search_count,
            "embedding_api_calls": self.embedding_api_calls,
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
            "cache_hit_rate": self.cache_hits / total_cache if total_cache > 0 else 0,
            "rerank_count": self.rerank_count,
            "avg_search_latency_ms": (
                sum(self.search_latencies) / len(self.search_latencies) * 1000
                if self.search_latencies else 0
            ),
            "p95_search_latency_ms": (
                sorted(self.search_latencies)[int(len(self.search_latencies) * 0.95)] * 1000
                if len(self.search_latencies) > 10 else 0
            ),
            "avg_rerank_latency_ms": (
                sum(self.rerank_latencies) / len(self.rerank_latencies) * 1000
                if self.rerank_latencies else 0
            ),
        }
    
    def print_stats(self):
        """Print formatted stats"""
        stats = self.get_stats()
        print("\n=== Search System Metrics ===")
        print(f"Total Searches: {stats['search_count']}")
        print(f"Embedding API Calls: {stats['embedding_api_calls']}")
        print(f"Cache Hit Rate: {stats['cache_hit_rate']:.1%}")
        print(f"Avg Search Latency: {stats['avg_search_latency_ms']:.0f}ms")
        print(f"P95 Search Latency: {stats['p95_search_latency_ms']:.0f}ms")
        print(f"Rerank Calls: {stats['rerank_count']}")


# Global metrics instance
metrics = MetricsCollector()


def log_search(
    query: str,
    mode: str,
    results_count: int,
    latency_ms: Optional[float] = None,
    source: str = "quran"
):
    """Log a search operation"""
    logger.info(json.dumps({
        "event": "search",
        "query": query[:100],  # Truncate long queries
        "mode": mode,
        "source": source,
        "results_count": results_count,
        "latency_ms": latency_ms,
        "timestamp": datetime.now().isoformat()
    }))


def log_error(operation: str, error: Exception, context: Optional[dict] = None):
    """Log an error"""
    logger.error(json.dumps({
        "event": "error",
        "operation": operation,
        "error_type": type(error).__name__,
        "error_message": str(error),
        "context": context or {},
        "timestamp": datetime.now().isoformat()
    }))


def timed(metric_name: str = "operation"):
    """Decorator to time function execution"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start = time.time()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                latency = time.time() - start
                logger.debug(f"{metric_name} completed in {latency*1000:.0f}ms")
        return wrapper
    return decorator


if __name__ == "__main__":
    # Test metrics
    print("Testing Observability Module...")
    
    # Simulate some operations
    with metrics.search_timer("hybrid", "quran"):
        time.sleep(0.1)  # Simulate search
    
    with metrics.search_timer("semantic", "bible"):
        time.sleep(0.05)
    
    metrics.record_embedding_call(cached=True)
    metrics.record_embedding_call(cached=True)
    metrics.record_embedding_call(cached=False)
    metrics.record_rerank(0.2)
    
    log_search("test query", "hybrid", 10, 100.0)
    
    metrics.print_stats()
