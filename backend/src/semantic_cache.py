"""LLM response caching for the Clarus RAG pipeline.

The active implementation is ``SemanticLLMCache`` in ``src/llm_cache.py``.
It provides Redis-backed semantic caching with cosine-similarity lookup,
TTL-based expiration, and fail-open resilience.
"""
