import logging

from redis import asyncio as aioredis

logger = logging.getLogger(__name__)

TIER_KEY_PREFIX = "polar:tier:"


async def get_tier(redis: aioredis.Redis | None, user_id: str) -> str:
    """Get user tier from Redis. Fail-open to 'free'."""
    if not redis:
        return "free"
    try:
        tier = await redis.get(f"{TIER_KEY_PREFIX}{user_id}")
        if tier is None:
            return "free"
        return tier.decode() if isinstance(tier, bytes) else tier
    except Exception:
        logger.warning("Redis tier lookup failed, defaulting to free", extra={"user_id": user_id})
        return "free"


async def set_tier(redis: aioredis.Redis | None, user_id: str, tier: str) -> bool:
    """Set user tier in Redis (persistent, no TTL). Returns False on failure."""
    if not redis:
        return False
    try:
        await redis.set(f"{TIER_KEY_PREFIX}{user_id}", tier)
        return True
    except Exception:
        logger.warning("Redis tier set failed", extra={"user_id": user_id, "tier": tier})
        return False
