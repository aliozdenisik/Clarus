# Backend Structured Logging System

This document describes the structured logging system for the Clarus backend, providing patterns, field references, and code examples for consistent logging across all modules.

---

## Overview

The backend uses Python's standard `logging` module with custom formatters and context injection:

- **JSON format** for production (machine-parseable, aggregation-friendly)
- **Console format** for development (human-readable with colors)
- **Request correlation** for distributed tracing
- **Performance logging** helpers for latency tracking
- **Context injection** via Python contextvars

**Key file**: `backend/app/logging_config.py`

---

## Quick Start

```python
from app.logging_config import get_logger

logger = get_logger(__name__)

# Basic logging
logger.info("User searched", extra={"query": "test", "results": 10})
logger.warning("Cache miss", extra={"cache_key": "abc123"})
logger.error("Search failed", exc_info=True)
```

---

## Python Logging Patterns

### 1. Module Logger Setup

Every module should create a logger at the top of the file:

```python
"""
My Module Description
"""

from app.logging_config import get_logger

logger = get_logger(__name__)
```

**Never use:**
- `print()` for logging (use `logger.info()` or `logger.debug()`)
- `logging.getLogger()` directly (use `get_logger()` for consistency)

### 2. Logging Levels

| Level | Use Case | Example |
|-------|----------|---------|
| `DEBUG` | Detailed diagnostic info (dev only) | `logger.debug("Query vector shape", extra={"shape": vec.shape})` |
| `INFO` | Normal operational messages | `logger.info("Search completed", extra={"results": 10})` |
| `WARNING` | Potential issues, degraded state | `logger.warning("Cache miss, calling LLM")` |
| `ERROR` | Errors that prevent normal operation | `logger.error("Database connection failed", exc_info=True)` |
| `CRITICAL` | System-level failures | `logger.critical("Qdrant unavailable, circuit breaker OPEN")` |

### 3. Adding Context with `extra`

Always use the `extra` parameter for structured data:

```python
# Good - structured context
logger.info(
    "Search completed",
    extra={
        "collection": "quran_tr",
        "query_length": len(query),
        "results_count": len(results),
        "latency_ms": 150.5,
    }
)

# Bad - interpolating data into message
logger.info(f"Search completed: {len(results)} results in {latency_ms}ms")
```

**Why structured?** JSON logs can be filtered, aggregated, and queried in log management tools (e.g., `results_count > 100`).

---

## Structured Logging Field Reference

### Standard Fields (Auto-Injected)

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `timestamp` | string | ISO 8601 timestamp (UTC) | `"2024-01-15T10:30:00.123Z"` |
| `level` | string | Log level | `"INFO"`, `"ERROR"` |
| `logger` | string | Logger name (module path) | `"src.ultimate_rag"` |
| `message` | string | Log message | `"Search completed"` |

### Context Fields (Injected via Middleware)

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `request_id` | string | Unique ID for this HTTP request | `"abc12345"` |
| `correlation_id` | string | User action tracking ID | `"550e8400-e29b-41d4-a716..."` |
| `user_id` | int | Authenticated user ID | `42` |

### Error Fields (Auto-Added for ERROR+)

| Field | Type | Description |
|-------|------|-------------|
| `source.file` | string | Source file path |
| `source.line` | int | Line number |
| `source.function` | string | Function name |
| `exception.type` | string | Exception class name |
| `exception.message` | string | Exception message |
| `exception.traceback` | string | Full stack trace |

### Example JSON Output

```json
{
  "timestamp": "2024-01-15T10:30:00.123Z",
  "level": "ERROR",
  "logger": "app.api.search",
  "message": "Search failed",
  "request_id": "abc12345",
  "correlation_id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": 42,
  "source": {
    "file": "/app/api/search.py",
    "line": 85,
    "function": "search_quran"
  },
  "exception": {
    "type": "CircuitBreakerError",
    "message": "Qdrant circuit breaker is OPEN",
    "traceback": "Traceback (most recent call last):\n..."
  }
}
```

---

## Performance Logging Patterns

### Using `log_performance` Helper

For measuring operation latency:

```python
import time
from app.logging_config import get_logger, log_performance

logger = get_logger(__name__)

def search(query: str) -> list:
    start = time.perf_counter()

    # ... perform search ...
    results = do_search(query)

    latency_ms = (time.perf_counter() - start) * 1000
    log_performance(
        logger,
        operation="search",
        latency_ms=latency_ms,
        collection="quran_tr",
        results=len(results),
    )
    return results
```

**Output (JSON):**
```json
{
  "timestamp": "2024-01-15T10:30:00.123Z",
  "level": "INFO",
  "logger": "src.search",
  "message": "search completed",
  "operation": "search",
  "latency_ms": 150.25,
  "collection": "quran_tr",
  "results": 10
}
```

### Manual Performance Logging

For more control over the message:

```python
start = time.perf_counter()
# ... work ...
latency_ms = (time.perf_counter() - start) * 1000

logger.info(
    "Embedding batch completed",
    extra={
        "operation": "embed_batch",
        "latency_ms": round(latency_ms, 2),
        "batch_size": len(texts),
        "avg_ms_per_item": round(latency_ms / len(texts), 2),
    }
)
```

---

## Error Logging Best Practices

### Always Use `exc_info=True`

When logging exceptions, include the traceback:

```python
try:
    results = await qdrant_client.query_points(...)
except Exception as e:
    # Good - includes full traceback
    logger.error(
        "Qdrant query failed",
        extra={"collection": collection, "query_length": len(query)},
        exc_info=True
    )
    raise

# Wrong - loses traceback
logger.error(f"Qdrant query failed: {e}")
```

### Error Context

Include relevant context for debugging:

```python
try:
    response = await llm_client.complete(prompt)
except Exception as e:
    logger.error(
        "LLM call failed",
        extra={
            "model": "gemini-2.5-flash",
            "prompt_length": len(prompt),
            "error_type": type(e).__name__,
        },
        exc_info=True
    )
```

### Expected vs. Unexpected Errors

```python
from src.circuit_breaker import CircuitBreakerError

try:
    results = search(query)
except CircuitBreakerError:
    # Expected - use WARNING (service degraded but expected)
    logger.warning("Circuit breaker OPEN, returning cached results")
    return cached_results
except Exception as e:
    # Unexpected - use ERROR
    logger.error("Unexpected search failure", exc_info=True)
    raise
```

---

## Context Injection

### Request-Scoped Context

The `CorrelationIDMiddleware` automatically sets request context for all logs:

```python
# In middleware (automatic)
from app.logging_config import set_request_id, set_correlation_id, set_user_id

set_request_id("abc12345")
set_correlation_id("550e8400-e29b-41d4-a716-446655440000")
set_user_id(42)

# All subsequent logs in this request include these fields
logger.info("Processing search")  # Automatically includes request_id, correlation_id, user_id
```

### Manual Context Setting

For background tasks or CLI commands:

```python
from app.logging_config import set_request_id, set_user_id, clear_context

# Set context for a batch job
set_request_id("batch-001")

# Process items
for item in items:
    logger.info("Processing item", extra={"item_id": item.id})

# Clear context when done
clear_context()
```

### Using `LogContext` Context Manager

For scoped context:

```python
from app.logging_config import LogContext

def process_user_request(user_id: int, request_id: str):
    with LogContext(request_id=request_id, user_id=user_id):
        logger.info("Starting request")  # Includes request_id and user_id

        # All logs within this block have the context
        do_work()

        logger.info("Request complete")

    # Context is automatically cleared after the block
```

### Adding Extra Context

For temporary context fields:

```python
from app.logging_config import set_extra_context

def search_with_agent(query: str, agent_name: str):
    set_extra_context(agent=agent_name, query_hash=hash(query))

    # All logs now include agent and query_hash
    logger.info("Agent search started")
    results = do_search(query)
    logger.info("Agent search completed", extra={"results": len(results)})
```

---

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `LOG_LEVEL` | `INFO` | Minimum log level (`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`) |
| `LOG_FORMAT` | `console` | Output format (`console` for development, `json` for production) |
| `LOG_FILE` | `None` | Optional file path for log output (rotates at 10MB, keeps 5 backups) |

### Configuration in `backend/.env`

```env
# Development (human-readable)
LOG_LEVEL=DEBUG
LOG_FORMAT=console

# Production (machine-parseable)
LOG_LEVEL=INFO
LOG_FORMAT=json
LOG_FILE=/var/log/clarus/backend.log
```

### Initializing Logging

Logging is initialized during FastAPI lifespan:

```python
# In app/main.py
from contextlib import asynccontextmanager
from app.logging_config import setup_logging, LoggingConfig

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize logging from settings
    from app.config import settings
    config = LoggingConfig.from_settings(settings)
    setup_logging(config)

    yield  # App runs here
```

---

## Code Examples

### Complete Module Example

```python
"""
Search API endpoints.
"""

import time
from fastapi import APIRouter, Depends
from app.logging_config import get_logger, log_performance
from app.auth.dependencies import get_current_user

logger = get_logger(__name__)
router = APIRouter()


@router.post("/search")
async def search_endpoint(
    query: str,
    user = Depends(get_current_user),
):
    start = time.perf_counter()
    logger.info("Search request received", extra={"query_length": len(query)})

    try:
        results = await perform_search(query)

        latency_ms = (time.perf_counter() - start) * 1000
        log_performance(
            logger,
            operation="api_search",
            latency_ms=latency_ms,
            results_count=len(results),
        )

        return {"results": results}

    except CircuitBreakerError:
        logger.warning("Search degraded - circuit breaker open")
        return {"results": [], "degraded": True}

    except Exception as e:
        logger.error(
            "Search failed",
            extra={"query_length": len(query)},
            exc_info=True,
        )
        raise
```

### Background Task Example

```python
"""
Batch indexing job.
"""

from app.logging_config import get_logger, LogContext, log_performance
import time

logger = get_logger(__name__)


def run_indexing_job(job_id: str, items: list):
    with LogContext(request_id=f"job-{job_id}"):
        logger.info("Indexing job started", extra={"item_count": len(items)})

        start = time.perf_counter()
        success = 0
        failed = 0

        for item in items:
            try:
                index_item(item)
                success += 1
            except Exception as e:
                failed += 1
                logger.error(
                    "Failed to index item",
                    extra={"item_id": item.id},
                    exc_info=True,
                )

        latency_ms = (time.perf_counter() - start) * 1000
        logger.info(
            "Indexing job completed",
            extra={
                "success": success,
                "failed": failed,
                "latency_ms": round(latency_ms, 2),
            }
        )
```

### Multi-Agent Pipeline Example

```python
"""
Multi-agent answer generation.
"""

from app.logging_config import get_logger, set_extra_context, log_performance
import time

logger = get_logger(__name__)


class QuranAgent:
    def __init__(self):
        self.name = "QuranAgent"

    async def generate(self, query: str) -> str:
        set_extra_context(agent=self.name)
        start = time.perf_counter()

        logger.info("Agent starting", extra={"query_length": len(query)})

        try:
            # Search and generate
            results = await self.search(query)
            answer = await self.synthesize(results)

            latency_ms = (time.perf_counter() - start) * 1000
            log_performance(
                logger,
                operation="agent_generate",
                latency_ms=latency_ms,
                results_used=len(results),
                answer_length=len(answer),
            )

            return answer

        except Exception as e:
            logger.error("Agent generation failed", exc_info=True)
            raise
```

---

## Third-Party Library Logging

The logging configuration automatically reduces noise from third-party libraries:

```python
# In setup_logging()
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("asyncio").setLevel(logging.WARNING)
logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
```

To add more exclusions:

```python
# Suppress noisy library logs
logging.getLogger("some_library").setLevel(logging.ERROR)
```

---

## Integration with Sentry

Errors are automatically captured by Sentry when enabled. The logging system works alongside Sentry:

- **INFO/DEBUG**: Console/file only (not sent to Sentry)
- **WARNING**: Logged + Sentry breadcrumb
- **ERROR/CRITICAL**: Logged + Sentry exception capture

```python
# This error is automatically captured by Sentry
logger.error("Critical failure", exc_info=True)

# This warning becomes a Sentry breadcrumb
logger.warning("Cache miss, performance degraded")
```

See `backend/RUNBOOKS.md` for Sentry alert response procedures.

---

## Anti-Patterns

**Never:**

```python
# Bad: Using print for logging
print(f"Search took {latency}ms")

# Bad: Interpolating data into message (loses structure)
logger.info(f"Search found {count} results in {latency}ms")

# Bad: Swallowing exceptions without logging
try:
    do_something()
except Exception:
    pass

# Bad: Missing exc_info on errors
except Exception as e:
    logger.error(f"Failed: {e}")  # Loses traceback!

# Bad: Using logging.getLogger() directly
import logging
logger = logging.getLogger(__name__)  # Use get_logger() instead
```

**Always:**

```python
# Good: Structured logging
logger.info("Search completed", extra={"count": count, "latency_ms": latency})

# Good: Including traceback
except Exception as e:
    logger.error("Operation failed", exc_info=True)

# Good: Using get_logger()
from app.logging_config import get_logger
logger = get_logger(__name__)
```

---

## Console Output Example (Development)

```
[2024-01-15 10:30:00] INFO    app.api.search - Search request received [req=abc12345, user=42, query_length=25]
[2024-01-15 10:30:00] DEBUG   src.ultimate_rag - Enhancing query [req=abc12345, original_length=25]
[2024-01-15 10:30:01] INFO    src.search - semantic_search completed [req=abc12345, latency_ms=150.25, results=10]
[2024-01-15 10:30:01] INFO    app.api.search - api_search completed [req=abc12345, latency_ms=1250.50, results_count=10]
```

## JSON Output Example (Production)

```json
{"timestamp": "2024-01-15T10:30:00.123Z", "level": "INFO", "logger": "app.api.search", "message": "Search request received", "request_id": "abc12345", "user_id": 42, "query_length": 25}
{"timestamp": "2024-01-15T10:30:01.500Z", "level": "INFO", "logger": "src.search", "message": "semantic_search completed", "request_id": "abc12345", "operation": "semantic_search", "latency_ms": 150.25, "results": 10}
```
