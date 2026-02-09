"""
Circuit Breaker for External Service Protection

Prevents cascading failures from Qdrant and OpenRouter by opening the circuit
after consecutive failures and allowing recovery after a timeout period.

Breaker Configurations:
- qdrant_breaker: fail_max=5, reset_timeout=60s (database operations)
- llm_breaker: fail_max=3, reset_timeout=30s (expensive, latency-sensitive)
- embeddings_breaker: fail_max=10, reset_timeout=120s (batch operations)

Usage:
    from src.circuit_breaker import qdrant_with_breaker, llm_with_breaker, CircuitBreakerError

    # CRITICAL: Pass a LAMBDA, not the function call directly
    # ❌ WRONG: qdrant_with_breaker(client.query_points(...))
    # ✅ CORRECT: qdrant_with_breaker(lambda: client.query_points(...))

    try:
        results = qdrant_with_breaker(lambda: client.query_points(...))
        response = llm_with_breaker(lambda: requests.post(url, json=payload))
    except CircuitBreakerError:
        logger.warning("Circuit breaker OPEN")
        raise
"""

import logging

import pybreaker
import sentry_sdk

logger = logging.getLogger(__name__)

# Re-export CircuitBreakerError for convenience
from pybreaker import CircuitBreakerError  # noqa: E402

qdrant_breaker = pybreaker.CircuitBreaker(fail_max=5, reset_timeout=60, name="qdrant")

# LLM breaker - lower threshold (expensive, latency-sensitive)
llm_breaker = pybreaker.CircuitBreaker(fail_max=3, reset_timeout=30, name="openrouter")

# Embeddings breaker - higher tolerance (batch operations, more resilient)
embeddings_breaker = pybreaker.CircuitBreaker(fail_max=10, reset_timeout=120, name="embeddings")


def qdrant_with_breaker(func):
    """
    SYNC wrapper for Qdrant calls.

    CRITICAL: Pass a LAMBDA, not the function call directly.
    ❌ WRONG: qdrant_with_breaker(client.query_points(...))
    ✅ CORRECT: qdrant_with_breaker(lambda: client.query_points(...))

    Args:
        func: A callable (lambda) that executes the Qdrant operation

    Returns:
        Result from the Qdrant operation

    Raises:
        CircuitBreakerError: When circuit is open (too many failures)
    """
    try:
        return qdrant_breaker.call(func)
    except pybreaker.CircuitBreakerError:
        logger.warning("Circuit breaker OPEN for qdrant")
        sentry_sdk.capture_message(
            "Circuit breaker OPEN: qdrant",
            level="warning",
            tags={"breaker_name": "qdrant", "state": "open"},
        )
        raise


def llm_with_breaker(func):
    """
    SYNC wrapper for LLM calls (OpenRouter).

    CRITICAL: Pass a LAMBDA, not the function call directly.
    ❌ WRONG: llm_with_breaker(requests.post(...))
    ✅ CORRECT: llm_with_breaker(lambda: requests.post(...))

    Args:
        func: A callable (lambda) that executes the LLM HTTP request

    Returns:
        Result from the LLM API call

    Raises:
        CircuitBreakerError: When circuit is open (too many failures)
    """
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


def embeddings_with_breaker(func):
    """
    SYNC wrapper for embedding calls (OpenRouter embeddings API).

    CRITICAL: Pass a LAMBDA, not the function call directly.
    ❌ WRONG: embeddings_with_breaker(requests.post(...))
    ✅ CORRECT: embeddings_with_breaker(lambda: requests.post(...))

    Args:
        func: A callable (lambda) that executes the embeddings HTTP request

    Returns:
        Result from the embeddings API call

    Raises:
        CircuitBreakerError: When circuit is open (too many failures)
    """
    try:
        return embeddings_breaker.call(func)
    except pybreaker.CircuitBreakerError:
        logger.warning("Circuit breaker OPEN for embeddings")
        sentry_sdk.capture_message(
            "Circuit breaker OPEN: embeddings",
            level="warning",
            tags={"breaker_name": "embeddings", "state": "open"},
        )
        raise


__all__ = [
    "qdrant_breaker",
    "llm_breaker",
    "embeddings_breaker",
    "qdrant_with_breaker",
    "llm_with_breaker",
    "embeddings_with_breaker",
    "CircuitBreakerError",
]
