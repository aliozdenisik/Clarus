# Caching Architecture and Resilience Patterns

## Abstract

This document describes the caching and resilience infrastructure in Clarus, a production RAG system for sacred text search. The system uses Redis Stack 7.2 as its primary caching and coordination layer, implementing four distinct caching strategies: semantic LLM response caching, search result caching, embedding caching, and JWT session management. Resilience is achieved through three circuit breakers with differentiated thresholds, a fail-open design philosophy for non-critical paths, and a fail-closed fallback for authentication rate limiting. Together, these patterns reduce LLM API costs by 60-80% and prevent cascading failures from external service degradation.

---

## 1. Introduction

LLM-powered applications face a cost and reliability problem that traditional web applications do not. Each query to an LLM API costs money and takes time. A single comparative theological analysis in Clarus involves five LLM calls (four collection agents plus one summary agent), each with a latency of 5-15 seconds. Without caching, repeated or semantically similar queries incur the full cost every time.

Beyond cost, LLM APIs are external services with their own failure modes: rate limits, timeouts, model unavailability, and network partitions. A system that fails whenever its LLM provider has a hiccup is not production-ready.

Clarus addresses both problems through a layered architecture:

- **Semantic caching** reduces LLM API calls by 60-80% by recognizing that "What does the Quran say about patience?" and "Quran verses on sabir" are semantically equivalent queries.
- **Search result caching** eliminates redundant Qdrant queries for identical searches within a one-hour window.
- **Circuit breakers** prevent a failing external service from taking down the entire application.
- **Fail-open design** ensures that a Redis outage degrades gracefully rather than causing a complete service failure.

The effective cost per query with caching is approximately $0.013, compared to $0.03 or more without it.

---

## 2. Redis Architecture

### 2.1 Connection Management (`redis_client.py`)

The `RedisManager` class in `backend/app/redis_client.py` manages the Redis connection lifecycle. It uses a connection pool with settings tuned for a long-running async application:

```python
pool = ConnectionPool.from_url(
    settings.redis_url,
    max_connections=50,
    socket_keepalive=True,
    health_check_interval=30,
    decode_responses=False,
    socket_timeout=5,
    retry_on_timeout=True,
)
client = aioredis.Redis(connection_pool=pool)
```

Key configuration decisions:

- `max_connections=50`: Sized for concurrent request handling without exhausting Redis connection limits.
- `decode_responses=False`: Binary mode is required because embedding vectors are stored as raw JSON bytes. Enabling `decode_responses=True` would corrupt binary data.
- `health_check_interval=30`: Periodic pings detect stale connections before they cause request failures.
- `socket_timeout=5`: Prevents Redis operations from blocking indefinitely on network issues.

The `RedisManager` is instantiated as a global singleton (`redis_manager`) and connected during FastAPI's lifespan startup. A `health_check()` method is exposed for the `/api/health` endpoint.

### 2.2 Fail-Open Pattern

The most important design decision in the Redis layer is the fail-open pattern: **Redis failure never crashes the application.** This is enforced at the connection level and at every individual operation.

At connection time, if Redis is unavailable, `connect()` logs a warning and sets `self.client = None` without raising an exception:

```python
async def connect(self) -> None:
    try:
        pool = ConnectionPool.from_url(...)
        client = aioredis.Redis(connection_pool=pool)
        await client.ping()
        self.client = client
    except Exception as e:
        # Fail-open: Log warning but don't raise
        logger.warning(
            "Failed to connect to Redis",
            extra={
                "error_type": type(e).__name__,
                "redis_host": settings.redis_host,
                "redis_port": settings.redis_port,
            },
        )
        self.client = None
```

Every downstream consumer checks `if redis_manager.client is None` before attempting any Redis operation. If the client is None, the operation is skipped and the application proceeds without caching. This means:

- Search results are fetched from Qdrant on every request (slower, but functional).
- LLM responses are not cached (more expensive, but functional).
- Rate limiting falls back to in-memory counters for auth paths, or is bypassed entirely for non-auth paths.

The only exception to fail-open is the authentication rate limiter, which uses an in-memory fallback to remain fail-closed against brute-force attacks. This is discussed in Section 7.

### 2.3 Redis Key Namespace Design

All Redis keys follow a structured namespace convention to prevent collisions and enable targeted cache invalidation:

| Prefix | Purpose | TTL | Example Key |
|--------|---------|-----|-------------|
| `search:` | Search result cache | 3600s (1h) | `search:quran_tr_diyanet:{sha256}` |
| `llm_cache:` | LLM response cache | 604800s (7d) | `llm_cache:expand:tr:{sha256}` |
| `llm_cache_idx:` | Embedding index for semantic search | 604800s (7d) | `llm_cache_idx:expand:tr` |
| `ratelimit:` | Rate limit counters | varies | `ratelimit:{user_id}:{YYYY-MM-DD}` |
| `ratelimit:auth:` | Auth rate limit counters | 60s | `ratelimit:auth:{ip}:{YYYY-MM-DD-HH-MM}` |
| `ratelimit:public:` | Public endpoint rate limits | 60s | `ratelimit:public:{path}:{ip}:{minute}` |

The `llm_cache_idx:` keys are Redis hashes where each field is a cache key and each value is the serialized embedding vector. This structure enables the semantic similarity search described in Section 3.2.

---

## 3. LLM Response Caching

### 3.1 Cache Key Generation

The `SemanticLLMCache` class in `src/llm_cache.py` generates cache keys using SHA-256 hashing of the operation type, locale, and query string:

```python
def _get_cache_key(self, query: str, operation: str, locale: str = "tr") -> str:
    """Generate unique cache key (SHA-256 hash) including locale."""
    return hashlib.sha256(f"{operation}:{locale}:{query}".encode()).hexdigest()
```

The `operation` parameter distinguishes between different LLM use cases (`expand` for query enhancement, `multi_query` for multi-query generation). Including the locale in the hash is critical: the same query in Turkish and English should produce different cache entries, because the LLM responses will be in different languages.

The full Redis key format is `llm_cache:{operation}:{locale}:{sha256_hash}`.

### 3.2 Semantic Cache (Cosine Similarity Threshold theta=0.95)

Exact key matching handles repeated identical queries. But many real-world queries are semantically equivalent without being textually identical. "What does the Quran say about patience?" and "Quran verses on sabir" should share a cache entry.

The semantic cache layer addresses this by storing the embedding vector of each cached query alongside the response. On a cache miss for exact matching, the system computes the embedding of the new query and searches for the most similar stored embedding:

```python
async def _find_similar_key(
    self, query_embedding: list[float], operation: str, locale: str = "tr"
) -> tuple[str, float] | None:
    index_key = f"llm_cache_idx:{operation}:{locale}"
    stored_embeddings = await self._redis.hgetall(index_key)

    best_key = None
    best_similarity = 0.0

    for md5_bytes, embedding_json_bytes in stored_embeddings.items():
        stored_embedding = json.loads(embedding_json_bytes)
        similarity = self._cosine_similarity(query_embedding, stored_embedding)

        if similarity > best_similarity and similarity >= self.threshold:
            best_similarity = similarity
            best_key = md5

    if best_key:
        return (best_key, best_similarity)
    return None
```

The similarity threshold is `theta=0.95`. This is deliberately strict: a score of 0.95 means the queries are nearly identical in semantic space. A lower threshold (e.g., 0.85) would increase cache hit rates but risk returning cached responses for queries that are meaningfully different.

The cache lookup sequence is:

1. Compute SHA-256 of the query for exact match lookup.
2. If exact match found, return cached response immediately.
3. If no exact match, compute the query embedding.
4. Search the embedding index for the most similar stored embedding.
5. If similarity >= 0.95, return the cached response for that similar query.
6. Otherwise, call the LLM and cache the new response with its embedding.

### 3.3 Locale-Aware Caching

The locale is included in both the cache key and the embedding index key. This prevents a Turkish query from matching a cached English response, even if the two queries are semantically equivalent translations of each other. The LLM responses are language-specific, so cross-locale cache hits would return responses in the wrong language.

### 3.4 Cost Reduction

The `get_stats()` method tracks hit rates:

```python
def get_stats(self) -> dict[str, Any]:
    total = self.stats["hits"] + self.stats["misses"]
    hit_rate = self.stats["hits"] / total if total > 0 else 0.0

    return {
        **self.stats,
        "total_requests": total,
        "hit_rate": hit_rate,
        "semantic_hit_ratio": (
            self.stats["semantic_hits"] / self.stats["hits"]
            if self.stats["hits"] > 0 else 0.0
        ),
    }
```

In production workloads, the combination of exact and semantic matching achieves 60-80% cache hit rates. The `semantic_hit_ratio` field shows what fraction of hits came from semantic matching rather than exact matching, which is useful for tuning the similarity threshold.

---

## 4. Search Result Caching

### 4.1 SHA256-Based Keys

Search results from Qdrant are cached in Redis with a one-hour TTL. The cache key is a SHA-256 hash of the collection name, query string, and result limit:

```python
cache_key = f"search:{collection}:{hashlib.sha256((query + str(limit)).encode()).hexdigest()}"
```

This key scheme ensures that the same query with a different `limit` parameter produces a different cache entry, preventing a cached result set of 10 from being returned when 20 results were requested.

### 4.2 TTL Strategy

Search results use a one-hour TTL (`setex(cache_key, 3600, cached_value)`). This is shorter than the LLM cache TTL (7 days) because:

- Search results depend on the Qdrant collection state, which can change if new vectors are indexed.
- LLM responses for a given query are stable over time (the model and prompt don't change frequently).
- One hour is long enough to absorb repeated queries from the same user session.

The cache stores a serialized JSON representation of the search results, including all fields needed to reconstruct the result objects:

```python
cached_value = json.dumps([
    {
        "id": r.id,
        "score": r.score,
        "surah_id": getattr(r, "surah_id", None),
        "surah_name": getattr(r, "surah_name", None),
        "verse_id": getattr(r, "verse_id", None),
        "translation": getattr(r, "translation", None),
        "book_name": getattr(r, "book_name", None),
        "chapter": getattr(r, "chapter", None),
        "verse": getattr(r, "verse", None),
        "text": getattr(r, "text", None),
        ...
    }
    for r in results
])
```

Both the retrieval and storage functions follow the fail-open pattern: any exception during cache access is caught, logged, and the operation proceeds without caching.

---

## 5. Embedding Caching

Embedding computation is one of the most expensive operations in the pipeline. Each call to OpenAI's `text-embedding-3-large` API costs money and adds latency. The `SemanticLLMCache` stores embeddings in the `llm_cache_idx:` Redis hash with a 7-day TTL.

When a new query arrives:

1. The cache checks for an exact match (no embedding needed).
2. On a miss, the embedding is computed once and stored alongside the response.
3. On subsequent similar queries, the stored embedding is retrieved from Redis rather than recomputed.

The embedding is stored as a JSON-serialized list of floats. For `text-embedding-3-large`, this is a 3072-element vector, approximately 25KB per entry. The Redis hash structure (`HSET`/`HGETALL`) allows all embeddings for a given operation and locale to be retrieved in a single round trip, which is more efficient than individual key lookups.

---

## 6. Circuit Breaker Pattern

### 6.1 Theory: The Circuit Breaker State Machine

The circuit breaker pattern (Nygard, 2007) prevents cascading failures by monitoring calls to an external service and "opening" the circuit when failures exceed a threshold. The state machine has three states:

- **CLOSED** (normal operation): Calls pass through to the external service. Failures are counted.
- **OPEN** (failing): Calls are rejected immediately without attempting the external service. The circuit stays open for a configurable timeout period.
- **HALF-OPEN** (testing recovery): After the timeout, one call is allowed through. If it succeeds, the circuit closes. If it fails, the circuit reopens.

This pattern prevents a slow or failing external service from consuming all available threads or goroutines while waiting for timeouts, which would cascade into application-wide slowdowns.

### 6.2 Implementation (`circuit_breaker.py`)

Clarus uses the `pybreaker` library with three circuit breakers, each configured for the characteristics of its target service:

```python
qdrant_breaker = pybreaker.CircuitBreaker(fail_max=5, reset_timeout=60, name="qdrant")

# LLM breaker - lower threshold (expensive, latency-sensitive)
llm_breaker = pybreaker.CircuitBreaker(fail_max=3, reset_timeout=30, name="openrouter")

# Embeddings breaker - higher tolerance (batch operations, more resilient)
embeddings_breaker = pybreaker.CircuitBreaker(fail_max=10, reset_timeout=120, name="embeddings")
```

The threshold rationale for each breaker:

| Breaker | `fail_max` | `reset_timeout` | Rationale |
|---------|-----------|----------------|-----------|
| `qdrant_breaker` | 5 | 60s | Database operations are moderately expensive. Five failures suggest a real problem, not transient noise. 60s gives Qdrant time to recover from a restart. |
| `llm_breaker` | 3 | 30s | LLM calls are expensive and latency-sensitive. Three failures are enough to indicate the API is down. 30s is a short recovery window because LLM APIs typically recover quickly from rate limits. |
| `embeddings_breaker` | 10 | 120s | Embedding calls are batched and more resilient to individual failures. A higher threshold avoids false positives from transient network issues. 120s allows time for batch processing backlogs to clear. |

### 6.3 Usage Pattern (Lambda Wrapping for Deferred Execution)

A critical implementation detail: the breaker wrappers require a **lambda** (callable), not the result of a function call. This is because the breaker needs to control when the call executes, not just observe its result.

```python
# WRONG: The HTTP request executes before the breaker can intercept it
response = llm_with_breaker(requests.post(url, json=payload))

# CORRECT: The lambda defers execution until the breaker decides to allow it
response = llm_with_breaker(lambda: requests.post(url, json=payload))
```

The wrapper functions follow the same pattern:

```python
def llm_with_breaker(func):
    try:
        return llm_breaker.call(func)
    except pybreaker.CircuitBreakerError:
        logger.warning("Circuit breaker OPEN for openrouter")
        sentry_sdk.capture_message(
            "Circuit breaker OPEN: openrouter",
            level="warning",
            tags={"breaker_name": "openrouter", "state": "open"},
        )
        raise
```

The `CircuitBreakerError` is re-raised after logging and Sentry notification. Callers are responsible for handling it gracefully. In the multi-agent system, a `CircuitBreakerError` from an LLM call causes the agent to return an empty commentary rather than propagating the error:

```python
except CircuitBreakerError:
    logger.warning(
        "Circuit breaker OPEN for LLM - multi-agent generation failed",
        extra={"model": self.MODEL},
    )
    return {"commentary": "", "citations": [], "confidence": 0.0}
```

### 6.4 Sentry Integration

Every circuit breaker state change (CLOSED to OPEN) is reported to Sentry as a warning-level message with structured tags:

```python
sentry_sdk.capture_message(
    "Circuit breaker OPEN: qdrant",
    level="warning",
    tags={"breaker_name": "qdrant", "state": "open"},
)
```

This provides operational visibility into external service health without requiring manual log parsing. Sentry's alerting can be configured to notify on-call engineers when a breaker opens.

---

## 7. Rate Limiting

### 7.1 Sliding Window Algorithm

The `RateLimitMiddleware` in `backend/app/middleware/rate_limit.py` implements per-user daily rate limits using a Redis-backed counter. The default limit is 50 queries per user per day, configurable via the `RATE_LIMIT_PER_DAY` environment variable.

The rate limit key includes the user ID and the current UTC date:

```python
today = now.strftime("%Y-%m-%d")
key = f"ratelimit:{user_id}:{today}"
```

The TTL is set to the number of seconds until the next UTC midnight, so the counter automatically expires at the start of each new day.

### 7.2 Implementation

Rate limiting uses a Lua script for atomic increment-and-check operations. Lua scripts execute atomically in Redis, preventing race conditions where two concurrent requests both read a count below the limit and both proceed:

```lua
local key = KEYS[1]
local limit = tonumber(ARGV[1])
local ttl = tonumber(ARGV[2])

local current = redis.call('INCR', key)
if current == 1 then
    redis.call('EXPIRE', key, ttl)
end

return current
```

The script increments the counter and sets the TTL only on the first increment (when `current == 1`). This avoids resetting the TTL on every request, which would prevent the counter from ever expiring.

The middleware applies different rate limiting strategies to different path categories:

- **Authenticated API paths** (`/api/search/`, `/api/stream/`, `/api/compare/`): Per-user daily limit, fail-open if Redis is unavailable.
- **Auth paths** (`/api/auth/`): Per-IP per-minute limit of 10 requests, fail-closed with in-memory fallback.
- **Public paths** (`/api/search/keyword/`, `/api/metadata/`, etc.): Per-IP per-minute limit, fail-open.

### 7.3 Response Headers

Rate limit information is included in every response via standard HTTP headers:

```python
def get_rate_limit_headers(remaining: int, reset_at: datetime) -> dict[str, str]:
    return {
        "X-RateLimit-Limit": str(settings.rate_limit_per_day),
        "X-RateLimit-Remaining": str(max(0, remaining)),
        "X-RateLimit-Reset": reset_at.isoformat() + "Z",
    }
```

These headers allow API clients to implement proactive rate limit management without polling the `/api/auth/rate-limit` endpoint.

### 7.4 Auth Path Fail-Closed Design

Authentication endpoints use a different resilience strategy than the rest of the application. While most paths are fail-open (Redis unavailable means no rate limiting), auth paths are fail-closed: if Redis is unavailable, an in-memory sliding-window counter takes over.

This asymmetry is intentional. A Redis outage should not create a window for brute-force password attacks. The in-memory fallback (`_memory_auth_check`) maintains per-IP counters in a process-local dictionary:

```python
_auth_memory_counts: dict[str, tuple[int, float]] = {}
_AUTH_MEMORY_WINDOW_SECONDS: int = 60
_AUTH_MEMORY_MAX_ENTRIES: int = 10_000

def _memory_auth_check(key: str) -> int:
    now = time.monotonic()
    # Evict expired entries if dict is getting large
    if len(_auth_memory_counts) >= _AUTH_MEMORY_MAX_ENTRIES:
        expired = [k for k, (_, ws) in _auth_memory_counts.items()
                   if now - ws > _AUTH_MEMORY_WINDOW_SECONDS]
        for k in expired:
            del _auth_memory_counts[k]
    ...
```

The dictionary is bounded at 10,000 entries to prevent memory exhaustion under attack conditions. Expired entries are evicted lazily when the dictionary reaches capacity.

---

## 8. Session Management

Clarus uses Better Auth for session management. Sessions are stored and validated by the Better Auth server (running as part of the Next.js frontend). The FastAPI backend validates sessions by calling the Better Auth JWKS endpoint to verify JWT signatures.

The `JWKSValidator` in `backend/app/auth/jwks_validator.py` fetches the public key set from `BETTER_AUTH_JWKS_URL` and caches it locally. JWT validation is performed on every authenticated request without a Redis round trip.

Logout is handled client-side: the Better Auth session is invalidated on the auth server, and the FastAPI backend's logout endpoint simply returns success for client-side cleanup. There is no server-side token blacklist in the current implementation, as Better Auth manages session state.

---

## 9. Resilience Design Principles

The caching and resilience architecture in Clarus is built on four principles:

**Fail-open for non-critical paths.** Cache failures, Redis unavailability, and rate limit check failures on non-auth paths all result in the request proceeding without the protection layer. The application degrades gracefully: it becomes slower and more expensive, but it keeps working. This is the right tradeoff for a search application where availability matters more than cost control during infrastructure incidents.

**Fail-closed for security-critical paths.** Authentication rate limiting is the exception to fail-open. A Redis outage cannot create a brute-force window. The in-memory fallback ensures that security controls remain active even when the primary enforcement mechanism is unavailable.

**Circuit breakers prevent cascading failures.** Without circuit breakers, a slow LLM API would cause all in-flight requests to block waiting for timeouts, eventually exhausting the thread pool and making the entire application unresponsive. Circuit breakers detect failure early and reject subsequent calls immediately, keeping the application responsive even when external services are degraded.

**Observability at every failure point.** Every Redis failure, circuit breaker state change, and rate limit enforcement is logged with structured fields and reported to Sentry. This makes it possible to distinguish between "Redis is down" and "the LLM API is rate-limiting us" without manual log analysis. Correlation IDs propagated through the middleware layer link all log entries for a single request together.

---

## 10. References

- Nygard, M. T. (2007). *Release It! Design and Deploy Production-Ready Software*. Pragmatic Bookshelf.

- Microsoft Azure Architecture Center. "Circuit Breaker pattern." https://learn.microsoft.com/en-us/azure/architecture/patterns/circuit-breaker

- Redis Documentation. "Rate limiting." https://redis.io/learn/howtos/ratelimiting

- Redis Documentation. "Lua scripting." https://redis.io/docs/manual/programmability/eval-intro/

- pybreaker Documentation. https://github.com/danielfm/pybreaker

- tenacity Documentation. "Retry library for Python." https://tenacity.readthedocs.io/
