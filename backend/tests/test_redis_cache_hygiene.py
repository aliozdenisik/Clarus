"""Unit tests for Redis cache hygiene fixes (Issues #252, #253, #254).

- #252: LLM cache index (llm_cache_idx:*) now gets a TTL; stale entries are pruned.
- #253: SemanticCache stub removed — module is importable but the broken class is gone.
- #254: Keyword search endpoints cache results in Redis with fail-open resilience.
"""

from __future__ import annotations

import json
import sys
from unittest.mock import AsyncMock, MagicMock

import pytest

sys.path.insert(0, "/home/freyja/qdrant/backend")


class TestLLMCacheIndexTTL:
    @pytest.mark.asyncio
    async def test_set_calls_expire_on_index_hash(self):
        from src.llm_cache import SemanticLLMCache

        cache = SemanticLLMCache(ttl_seconds=3600)
        mock_redis = AsyncMock()
        cache._redis = mock_redis
        cache._encoder = MagicMock()
        cache._encoder.encode.return_value = [0.1, 0.2, 0.3]

        await cache.set("query", "expand", {"result": "data"}, locale="tr")

        mock_redis.hset.assert_called_once()
        mock_redis.expire.assert_called_once()
        index_key = mock_redis.expire.call_args[0][0]
        ttl_passed = mock_redis.expire.call_args[0][1]
        assert index_key == "llm_cache_idx:expand:tr"
        assert ttl_passed == 3600

    @pytest.mark.asyncio
    async def test_find_similar_key_removes_stale_entry(self):
        from src.llm_cache import SemanticLLMCache

        cache = SemanticLLMCache(similarity_threshold=0.90)
        mock_redis = AsyncMock()
        cache._redis = mock_redis

        stale_key = "abc123deadbeef"
        mock_redis.hgetall.return_value = {stale_key.encode(): json.dumps([0.9, 0.9, 0.9]).encode()}
        mock_redis.exists.return_value = 0

        result = await cache._find_similar_key([0.9, 0.9, 0.9], "expand", "tr")

        assert result is None
        mock_redis.hdel.assert_called_once_with("llm_cache_idx:expand:tr", stale_key)

    @pytest.mark.asyncio
    async def test_find_similar_key_returns_live_entry(self):
        from src.llm_cache import SemanticLLMCache

        cache = SemanticLLMCache(similarity_threshold=0.90)
        mock_redis = AsyncMock()
        cache._redis = mock_redis

        valid_key = "def456deadbeef"
        mock_redis.hgetall.return_value = {valid_key.encode(): json.dumps([0.9, 0.9, 0.9]).encode()}
        mock_redis.exists.return_value = 1

        result = await cache._find_similar_key([0.9, 0.9, 0.9], "expand", "tr")

        assert result is not None
        found_key, similarity = result
        assert found_key == valid_key
        assert similarity >= 0.90
        mock_redis.hdel.assert_not_called()


class TestSemanticCacheStubRemoved:
    def test_semantic_cache_module_is_importable(self):
        import importlib

        mod = importlib.import_module("src.semantic_cache")
        assert mod is not None

    def test_semantic_cache_broken_class_is_gone(self):
        import src.semantic_cache as sc

        assert not hasattr(sc, "SemanticCache"), (
            "SemanticCache stub must be removed — it raised NotImplementedError on instantiation"
        )


class TestKeywordSearchCaching:
    def _make_mock_result(self):
        from src.quran_morphology import MorphologySearchResult

        return MorphologySearchResult(
            query="كتب",
            root="كتب",
            root_source="exact_match",
            total_occurrences=319,
            unique_words=["كتب", "كتاب"],
            surah_distribution=[],
            verses=[],
            page=1,
            per_page=20,
            total_verses=319,
            root_buckwalter="ktb",
            word_transliterations={},
        )

    def _cached_search_payload(self) -> dict:
        return {
            "query": "كتب",
            "root": "كتب",
            "root_source": "exact_match",
            "total_occurrences": 319,
            "unique_words": ["كتب"],
            "surah_distribution": [],
            "verses": [],
            "pagination": {
                "page": 1,
                "per_page": 20,
                "total_verses": 319,
                "total_pages": 16,
                "has_next": True,
                "has_prev": False,
            },
            "root_buckwalter": "ktb",
            "word_transliterations": {},
        }

    @pytest.mark.asyncio
    async def test_search_keyword_cache_hit_skips_db(self, monkeypatch: pytest.MonkeyPatch):
        import app.api.keyword_search as ks_module
        from app.redis_client import redis_manager
        from app.schemas.keyword_search import KeywordSearchRequest

        mock_redis = AsyncMock()
        mock_redis.get.return_value = json.dumps(self._cached_search_payload()).encode()
        monkeypatch.setattr(redis_manager, "client", mock_redis)

        db_called = False

        def mock_get_search():
            nonlocal db_called
            m = MagicMock()

            async def fake_search(**_kwargs):
                nonlocal db_called
                db_called = True
                return self._make_mock_result()

            m.search_by_root = fake_search
            return m

        monkeypatch.setattr(ks_module, "get_morphology_search", mock_get_search)

        response = await ks_module.search_keyword(KeywordSearchRequest(query="كتب", page=1, per_page=20))

        assert response.root == "كتب"
        assert response.total_occurrences == 319
        assert not db_called

    @pytest.mark.asyncio
    async def test_search_keyword_cache_miss_stores_result(self, monkeypatch: pytest.MonkeyPatch):
        import app.api.keyword_search as ks_module
        from app.redis_client import redis_manager
        from app.schemas.keyword_search import KeywordSearchRequest

        mock_redis = AsyncMock()
        mock_redis.get.return_value = None
        monkeypatch.setattr(redis_manager, "client", mock_redis)

        def mock_get_search():
            m = MagicMock()
            m.search_by_root = AsyncMock(return_value=self._make_mock_result())
            return m

        monkeypatch.setattr(ks_module, "get_morphology_search", mock_get_search)

        response = await ks_module.search_keyword(KeywordSearchRequest(query="كتب", page=1, per_page=20))

        assert response.root == "كتب"
        mock_redis.setex.assert_called_once()
        call_args = mock_redis.setex.call_args[0]
        assert call_args[1] == ks_module.KEYWORD_CACHE_TTL
        stored = json.loads(call_args[2])
        assert stored["root"] == "كتب"

    @pytest.mark.asyncio
    async def test_search_keyword_redis_failure_falls_through(self, monkeypatch: pytest.MonkeyPatch):
        import app.api.keyword_search as ks_module
        from app.redis_client import redis_manager
        from app.schemas.keyword_search import KeywordSearchRequest

        mock_redis = AsyncMock()
        mock_redis.get.side_effect = ConnectionError("Redis down")
        monkeypatch.setattr(redis_manager, "client", mock_redis)

        def mock_get_search():
            m = MagicMock()
            m.search_by_root = AsyncMock(return_value=self._make_mock_result())
            return m

        monkeypatch.setattr(ks_module, "get_morphology_search", mock_get_search)

        response = await ks_module.search_keyword(KeywordSearchRequest(query="كتب", page=1, per_page=20))

        assert response.root == "كتب"

    @pytest.mark.asyncio
    async def test_list_roots_cache_hit_skips_db(self, monkeypatch: pytest.MonkeyPatch):
        import app.api.keyword_search as ks_module
        from app.redis_client import redis_manager

        cached_payload = {
            "roots": [{"root": "كتب", "count": 319}],
            "total": 1651,
            "page": 1,
            "per_page": 50,
        }
        mock_redis = AsyncMock()
        mock_redis.get.return_value = json.dumps(cached_payload).encode()
        monkeypatch.setattr(redis_manager, "client", mock_redis)

        db_called = False

        def mock_get_search():
            nonlocal db_called
            m = MagicMock()

            async def fake_list(**_kwargs):
                nonlocal db_called
                db_called = True
                return {"roots": [], "total": 0, "page": 1, "per_page": 50}

            m.list_roots = fake_list
            return m

        monkeypatch.setattr(ks_module, "get_morphology_search", mock_get_search)

        response = await ks_module.list_roots(page=1, per_page=50)

        assert response.total == 1651
        assert not db_called

    @pytest.mark.asyncio
    async def test_get_root_info_cache_hit_skips_db(self, monkeypatch: pytest.MonkeyPatch):
        import app.api.keyword_search as ks_module
        from app.redis_client import redis_manager

        cached_payload = {
            "query": "كتب",
            "root": "كتب",
            "root_source": "exact_match",
            "total_occurrences": 319,
            "unique_words": [],
            "surah_distribution": [],
            "verses": [],
            "pagination": {
                "page": 1,
                "per_page": 0,
                "total_verses": 319,
                "total_pages": 1,
                "has_next": False,
                "has_prev": False,
            },
            "root_buckwalter": "ktb",
            "word_transliterations": {},
        }
        mock_redis = AsyncMock()
        mock_redis.get.return_value = json.dumps(cached_payload).encode()
        monkeypatch.setattr(redis_manager, "client", mock_redis)

        db_called = False

        def mock_get_search():
            nonlocal db_called
            m = MagicMock()

            async def fake_search(**_kwargs):
                nonlocal db_called
                db_called = True
                return self._make_mock_result()

            m.search_by_root = fake_search
            return m

        monkeypatch.setattr(ks_module, "get_morphology_search", mock_get_search)

        response = await ks_module.get_root_info(root="كتب", page=1, per_page=0)

        assert response.root == "كتب"
        assert not db_called
