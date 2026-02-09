"""
Embedding Module for Dense and Sparse Vectors

Provides both semantic (dense) and BM25 (sparse) embeddings for hybrid search.
Uses OpenRouter API with OpenAI text-embedding-3-large model for dense embeddings.
This model has excellent multilingual support including Turkish.

Optimizations:
- Redis-based embedding cache (7-day TTL)
- Rate limiting (20 RPM for free tier safety)
- Circuit breaker for API failures
"""

from typing import List, Tuple
import os
import requests
import hashlib
import time
import json
from tqdm import tqdm

import sentry_sdk

from src.circuit_breaker import embeddings_with_breaker, CircuitBreakerError

# Optional imports for Redis caching
try:
    import redis as sync_redis
    from redis import asyncio as aioredis

    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    print(
        "Warning: redis not installed. Embedding cache disabled. Install with: pip install redis[hiredis]"
    )


class DenseEncoder:
    """
    Dense vector encoder using OpenRouter API with OpenAI text-embedding-3-large.
    Provides semantic understanding of text with 3072-dimension embeddings.
    This model has excellent multilingual and Turkish language support.

    Features:
    - Redis-based cache (7-day TTL) for repeated queries
    - Rate limiting (20 RPM safe default for free tier)
    - Automatic retries with exponential backoff
    """

    OPENROUTER_API_URL = "https://openrouter.ai/api/v1/embeddings"
    DEFAULT_MODEL = "openai/text-embedding-3-large"
    EMBEDDING_DIMENSION = 3072

    # Rate limiting: OpenRouter free tier = 20 RPM
    # Paid tier ($10+ credits) = no limits
    RATE_LIMIT_RPM = 20

    # Cache settings
    CACHE_EXPIRE = 86400 * 7  # 7 days

    def __init__(
        self, model_name: str = None, api_key: str = None, use_cache: bool = True
    ):
        """
        Initialize the OpenRouter Dense Encoder.

        Args:
            model_name: Model identifier (default: openai/text-embedding-3-large)
            api_key: OpenRouter API key (default: from OPENROUTER_API_KEY env var)
            use_cache: Enable Redis-based embedding cache (default: True)
        """
        self.model_name = model_name or self.DEFAULT_MODEL
        self.api_key = api_key or os.environ.get("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError(
                "OpenRouter API key required. Set OPENROUTER_API_KEY environment variable "
                "or pass api_key parameter."
            )
        self._headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        # Initialize Redis cache (sync client for DenseEncoder)
        self._redis = None
        self._use_cache = use_cache and REDIS_AVAILABLE
        if self._use_cache:
            try:
                from app.config import settings

                self._redis = sync_redis.Redis(
                    host=settings.redis_host,
                    port=settings.redis_port,
                    password=settings.redis_password or None,
                    db=settings.redis_db,
                    decode_responses=False,
                    socket_timeout=5,
                )
                self._redis.ping()
            except Exception:
                # Fail-open: cache disabled if Redis unavailable
                self._redis = None
                self._use_cache = False

        # Rate limiting tracking
        self._last_request_time = 0
        self._min_request_interval = (
            60.0 / self.RATE_LIMIT_RPM
        )  # seconds between requests

        print(f"Initialized OpenRouter dense encoder: {self.model_name}")
        if self._use_cache and self._redis:
            print("  Cache: enabled (Redis)")

    def _get_cache_key(self, text: str) -> str:
        """Generate Redis cache key: embedding:{model}:{md5(text)}"""
        text_hash = hashlib.md5(text.encode()).hexdigest()
        return f"embedding:{self.model_name}:{text_hash}"

    def _rate_limit_wait(self):
        """Wait if needed to respect rate limits"""
        elapsed = time.time() - self._last_request_time
        if elapsed < self._min_request_interval:
            time.sleep(self._min_request_interval - elapsed)
        self._last_request_time = time.time()

    def _api_call(self, text: str) -> List[float]:
        """Make API call with rate limiting and circuit breaker"""
        with sentry_sdk.start_span(
            op="embedding.openai.single", description="Single embedding"
        ) as span:
            start_time = time.time()
            span.set_data("model", self.model_name)
            span.set_data("text_length", len(text))

            self._rate_limit_wait()

            response = embeddings_with_breaker(
                lambda: requests.post(
                    self.OPENROUTER_API_URL,
                    headers=self._headers,
                    json={"model": self.model_name, "input": text},
                    timeout=60,
                )
            )
            response.raise_for_status()
            data = response.json()
            result = data["data"][0]["embedding"]

            span.set_data("latency_ms", (time.time() - start_time) * 1000)
            return result

    def encode(self, text: str) -> List[float]:
        """
        Encode a single text to dense vector using OpenRouter API.
        Uses Redis cache if available.
        """
        # Check Redis cache first
        cache_key = None
        if self._redis is not None:
            try:
                cache_key = self._get_cache_key(text)
                cached_bytes = self._redis.get(cache_key)
                if cached_bytes is not None:
                    return json.loads(cached_bytes.decode())
            except Exception as e:
                # Fail-open: continue to API call if cache fails
                import logging

                logger = logging.getLogger(__name__)
                logger.warning(
                    "Redis cache read failed, proceeding with API call",
                    extra={
                        "operation": "embedding_cache_get",
                        "error_type": type(e).__name__,
                    },
                )

        # API call
        embedding = self._api_call(text)

        # Store in Redis cache
        if self._redis is not None and cache_key is not None:
            try:
                self._redis.set(cache_key, json.dumps(embedding), ex=self.CACHE_EXPIRE)
            except Exception as e:
                # Fail-open: cache write failure doesn't affect response
                import logging

                logger = logging.getLogger(__name__)
                logger.warning(
                    "Redis cache write failed",
                    extra={
                        "operation": "embedding_cache_set",
                        "error_type": type(e).__name__,
                    },
                )

        return embedding

    def encode_batch(
        self,
        texts: List[str],
        batch_size: int = 32,
        show_progress: bool = True,
        max_retries: int = 3,
    ) -> List[List[float]]:
        """
        Encode multiple texts to dense vectors.
        Processes in batches to avoid API limits.
        Includes retry logic for handling timeouts.

        Args:
            texts: List of texts to encode
            batch_size: Number of texts per API call
            show_progress: Show progress bar
            max_retries: Maximum retry attempts per batch
        """
        with sentry_sdk.start_span(
            op="embedding.openai.batch", description="Batch embedding"
        ) as span:
            start_time = time.time()
            span.set_data("model", self.model_name)
            span.set_data("batch_size", batch_size)
            span.set_data("total_texts", len(texts))

            all_embeddings = []

            iterator = range(0, len(texts), batch_size)
            if show_progress:
                iterator = tqdm(iterator, desc="Encoding dense vectors")

            for i in iterator:
                batch = texts[i : i + batch_size]

                # Retry logic with exponential backoff
                for attempt in range(max_retries):
                    try:
                        response = embeddings_with_breaker(
                            lambda: requests.post(
                                self.OPENROUTER_API_URL,
                                headers=self._headers,
                                json={"model": self.model_name, "input": batch},
                                timeout=180,  # Increased timeout
                            )
                        )
                        response.raise_for_status()
                        data = response.json()

                        # Sort by index to maintain order
                        sorted_data = sorted(data["data"], key=lambda x: x["index"])
                        batch_embeddings = [item["embedding"] for item in sorted_data]
                        all_embeddings.extend(batch_embeddings)
                        break  # Success, exit retry loop

                    except CircuitBreakerError:
                        print(
                            "\nCircuit breaker OPEN for embeddings - batch encoding failed"
                        )
                        raise  # Propagate immediately, no retry

                    except (
                        requests.exceptions.Timeout,
                        requests.exceptions.ReadTimeout,
                    ) as e:
                        if attempt < max_retries - 1:
                            wait_time = 2**attempt * 5  # 5s, 10s, 20s
                            print(
                                f"\nTimeout error, retrying in {wait_time}s... (attempt {attempt + 1}/{max_retries})"
                            )
                            time.sleep(wait_time)
                        else:
                            print(
                                f"\nFailed after {max_retries} attempts. Raising error."
                            )
                            raise

                    except requests.exceptions.RequestException as e:
                        if attempt < max_retries - 1:
                            wait_time = 2**attempt * 5
                            print(
                                f"\nAPI error: {e}, retrying in {wait_time}s... (attempt {attempt + 1}/{max_retries})"
                            )
                            time.sleep(wait_time)
                        else:
                            raise

            span.set_data("latency_ms", (time.time() - start_time) * 1000)
            span.set_data("embeddings_generated", len(all_embeddings))
            return all_embeddings

    @property
    def dimension(self) -> int:
        """Get the embedding dimension (3072 for text-embedding-3-large)"""
        return self.EMBEDDING_DIMENSION


class AsyncDenseEncoder:
    """
    Async version of DenseEncoder using aiohttp for concurrent API calls.
    Provides 2-3x faster batch processing while respecting rate limits.

    Usage:
        import asyncio

        async def main():
            encoder = AsyncDenseEncoder()
            await encoder.init_cache()
            embeddings = await encoder.encode_batch_async(texts, max_concurrent=5)

        asyncio.run(main())
    """

    OPENROUTER_API_URL = "https://openrouter.ai/api/v1/embeddings"
    DEFAULT_MODEL = "openai/text-embedding-3-large"
    EMBEDDING_DIMENSION = 3072
    RATE_LIMIT_RPM = 20

    CACHE_EXPIRE = 86400 * 7  # 7 days

    def __init__(
        self, model_name: str = None, api_key: str = None, use_cache: bool = True
    ):
        """
        Initialize the Async Dense Encoder.

        Args:
            model_name: Model identifier (default: openai/text-embedding-3-large)
            api_key: OpenRouter API key (default: from OPENROUTER_API_KEY env var)
            use_cache: Enable Redis-based embedding cache (default: True)
        """
        self.model_name = model_name or self.DEFAULT_MODEL
        self.api_key = api_key or os.environ.get("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError(
                "OpenRouter API key required. Set OPENROUTER_API_KEY environment variable "
                "or pass api_key parameter."
            )
        self._headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        # Redis cache (async) - initialized in init_cache()
        self._redis = None
        self._use_cache = use_cache and REDIS_AVAILABLE

        print(f"Initialized Async OpenRouter encoder: {self.model_name}")

    async def init_cache(self):
        """Initialize async Redis connection for caching."""
        if not self._use_cache:
            return

        try:
            from app.redis_client import redis_manager

            self._redis = redis_manager.client
            if self._redis:
                await self._redis.ping()
                print("  Cache: enabled (Redis async)")
        except Exception:
            # Fail-open: cache disabled if Redis unavailable
            self._redis = None
            self._use_cache = False

    def _get_cache_key(self, text: str) -> str:
        """Generate Redis cache key: embedding:{model}:{md5(text)}"""
        text_hash = hashlib.md5(text.encode()).hexdigest()
        return f"embedding:{self.model_name}:{text_hash}"

    async def _check_cache(
        self, texts: List[str]
    ) -> Tuple[List[str], List[int], List[List[float]]]:
        """
        Check Redis cache for texts and return: uncached texts, their indices, cached embeddings.
        """
        if self._redis is None:
            return texts, list(range(len(texts))), [None] * len(texts)

        uncached_texts = []
        uncached_indices = []
        cached_embeddings = [None] * len(texts)

        for i, text in enumerate(texts):
            try:
                cache_key = self._get_cache_key(text)
                cached_bytes = await self._redis.get(cache_key)
                if cached_bytes is not None:
                    cached_embeddings[i] = json.loads(cached_bytes.decode())
                else:
                    uncached_texts.append(text)
                    uncached_indices.append(i)
            except Exception as e:
                # Fail-open: cache read failure, treat as cache miss
                print(f"Redis cache read failed: {type(e).__name__}")
                uncached_texts.append(text)
                uncached_indices.append(i)

        return uncached_texts, uncached_indices, cached_embeddings

    async def _encode_batch_async(
        self, session, batch: List[str], semaphore, retry_count: int = 3
    ) -> List[List[float]]:
        """Encode a single batch with rate limiting via semaphore."""
        import asyncio

        async with semaphore:
            for attempt in range(retry_count):
                try:
                    async with session.post(
                        self.OPENROUTER_API_URL,
                        headers=self._headers,
                        json={"model": self.model_name, "input": batch},
                        timeout=180,
                    ) as response:
                        response.raise_for_status()
                        data = await response.json()

                        # Sort by index to maintain order
                        sorted_data = sorted(data["data"], key=lambda x: x["index"])
                        return [item["embedding"] for item in sorted_data]

                except asyncio.TimeoutError:
                    if attempt < retry_count - 1:
                        wait_time = 2**attempt * 5
                        print(
                            f"\nAsync timeout, retrying in {wait_time}s... (attempt {attempt + 1}/{retry_count})"
                        )
                        await asyncio.sleep(wait_time)
                    else:
                        raise
                except Exception:
                    if attempt < retry_count - 1:
                        wait_time = 2**attempt * 5
                        print(f"\nAsync error, retrying in {wait_time}s...")
                        await asyncio.sleep(wait_time)
                    else:
                        raise

    async def encode_batch_async(
        self,
        texts: List[str],
        batch_size: int = 256,  # Increased from 32 - OpenRouter supports up to 2048
        max_concurrent: int = 10,  # Increased from 5 - OpenRouter has no rate limits with credits
        show_progress: bool = True,
    ) -> List[List[float]]:
        """
        Encode multiple texts concurrently with controlled parallelism.

        Optimized for maximum throughput:
        - batch_size=256: Larger batches reduce API overhead
        - max_concurrent=10: Parallel API calls (OpenRouter has no rate limits with $10+ credits)
        - Connection pooling via aiohttp.TCPConnector

        Args:
            texts: List of texts to encode
            batch_size: Number of texts per API call (default: 256, max ~2048)
            max_concurrent: Maximum concurrent API calls (default: 10)
            show_progress: Show progress bar

        Returns:
            List of embedding vectors
        """
        import asyncio

        try:
            import aiohttp
        except ImportError:
            raise ImportError(
                "aiohttp required for async encoding. Install with: pip install aiohttp"
            )

        # Check Redis cache first
        uncached_texts, uncached_indices, embeddings = await self._check_cache(texts)

        if not uncached_texts:
            print("All embeddings found in cache!")
            return [e for e in embeddings if e is not None]

        cache_hits = len(texts) - len(uncached_texts)
        if cache_hits > 0:
            print(f"Cache hits: {cache_hits}/{len(texts)}")

        print(
            f"Processing {len(uncached_texts)} texts in {(len(uncached_texts) + batch_size - 1) // batch_size} batches (size={batch_size}, concurrent={max_concurrent})"
        )

        # Create batches from uncached texts
        batches = []
        for i in range(0, len(uncached_texts), batch_size):
            batches.append(uncached_texts[i : i + batch_size])

        # Semaphore for rate limiting
        semaphore = asyncio.Semaphore(max_concurrent)

        # High-performance connection pooling
        connector = aiohttp.TCPConnector(
            limit=max_concurrent * 2,  # Total connection pool size
            limit_per_host=max_concurrent,  # Per-host limit
            ttl_dns_cache=300,  # DNS cache for 5 minutes
            enable_cleanup_closed=True,
        )

        timeout = aiohttp.ClientTimeout(
            total=300, connect=30
        )  # 5 min total, 30s connect

        async with aiohttp.ClientSession(
            connector=connector, timeout=timeout
        ) as session:
            if show_progress:
                from tqdm.asyncio import tqdm_asyncio

                tasks = [
                    self._encode_batch_async(session, batch, semaphore)
                    for batch in batches
                ]
                results = await tqdm_asyncio.gather(*tasks, desc="Async encoding")
            else:
                tasks = [
                    self._encode_batch_async(session, batch, semaphore)
                    for batch in batches
                ]
                results = await asyncio.gather(*tasks)

        # Flatten results
        new_embeddings = []
        for batch_result in results:
            new_embeddings.extend(batch_result)

        # Cache new embeddings in Redis
        if self._redis is not None:
            for text, embedding in zip(uncached_texts, new_embeddings):
                try:
                    cache_key = self._get_cache_key(text)
                    await self._redis.set(
                        cache_key, json.dumps(embedding), ex=self.CACHE_EXPIRE
                    )
                except Exception as e:
                    # Fail-open: cache write failure doesn't affect response
                    print(f"Redis cache write failed: {type(e).__name__}")

        # Merge cached and new embeddings
        for idx, embedding in zip(uncached_indices, new_embeddings):
            embeddings[idx] = embedding

        return [e for e in embeddings if e is not None]

    async def encode_async(self, text: str) -> List[float]:
        """Encode a single text asynchronously."""
        embeddings = await self.encode_batch_async([text], show_progress=False)
        return embeddings[0]

    @property
    def dimension(self) -> int:
        """Get the embedding dimension"""
        return self.EMBEDDING_DIMENSION


if __name__ == "__main__":
    # Test encoders
    test_text = "Rahman ve Rahim olan Allah'ın adıyla"

    print("Testing Dense Encoder...")
    dense = DenseEncoder()
    dense_vec = dense.encode(test_text)
    print(f"Dense vector dimension: {len(dense_vec)}")
    print(f"Dense vector sample: {dense_vec[:5]}...")
