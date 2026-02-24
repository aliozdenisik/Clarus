from __future__ import annotations

from unittest.mock import AsyncMock

from app.polar_tier import TIER_KEY_PREFIX, get_tier, set_tier


class TestGetTierNoRedis:
    async def test_get_tier_with_none_redis_returns_free(self) -> None:
        result = await get_tier(None, "user_001")
        assert result == "free"


class TestSetTierNoRedis:
    async def test_set_tier_with_none_redis_returns_false(self) -> None:
        result = await set_tier(None, "user_001", "pro")
        assert result is False


class TestSetTierWithMockRedis:
    async def test_set_tier_calls_redis_set_without_ttl(self) -> None:
        mock_redis = AsyncMock()
        mock_redis.set = AsyncMock(return_value=True)
        result = await set_tier(mock_redis, "user_002", "pro")
        assert result is True
        mock_redis.set.assert_called_once_with(
            f"{TIER_KEY_PREFIX}user_002",
            "pro",
        )


class TestGetTierWithMockRedis:
    async def test_get_tier_decodes_bytes_to_string(self) -> None:
        mock_redis = AsyncMock()
        mock_redis.get = AsyncMock(return_value=b"pro")

        result = await get_tier(mock_redis, "user_003")

        assert result == "pro"
        mock_redis.get.assert_called_once_with(f"{TIER_KEY_PREFIX}user_003")

    async def test_get_tier_returns_free_when_key_missing(self) -> None:
        mock_redis = AsyncMock()
        mock_redis.get = AsyncMock(return_value=None)

        result = await get_tier(mock_redis, "user_004")

        assert result == "free"
