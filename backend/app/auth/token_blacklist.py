"""JWT token blacklist using Redis."""

import hashlib
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


async def revoke_token(token: str, expires_at: datetime) -> bool:
    """
    Add token to blacklist with TTL matching JWT expiry.

    Args:
        token: The JWT token to revoke
        expires_at: When the token expires (from JWT 'exp' claim)

    Returns:
        True if token was revoked, False if Redis unavailable
    """
    try:
        from app.redis_client import redis_manager

        if redis_manager.client is None:
            logger.warning("Redis unavailable, cannot revoke token")
            return False

        # Use hash of token as key (shorter, no sensitive data in key)
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        key = f"blacklist:{token_hash}"

        # TTL = time until JWT expires
        ttl_seconds = int((expires_at - datetime.utcnow()).total_seconds())
        if ttl_seconds <= 0:
            return True  # Already expired

        await redis_manager.client.set(key, "1", ex=ttl_seconds)
        logger.info(f"Token revoked with TTL {ttl_seconds}s")
        return True
    except Exception as e:
        logger.warning(
            "Failed to revoke token",
            extra={"operation": "token_revoke", "error_type": type(e).__name__},
        )
        return False


async def is_revoked(token: str) -> bool:
    """
    Check if token is in blacklist.

    Args:
        token: The JWT token to check

    Returns:
        True if token is blacklisted, False otherwise (fail-open if Redis unavailable)
    """
    try:
        from app.redis_client import redis_manager

        if redis_manager.client is None:
            return False  # Fail-open

        token_hash = hashlib.sha256(token.encode()).hexdigest()
        key = f"blacklist:{token_hash}"

        result = await redis_manager.client.exists(key)
        return bool(result)
    except Exception as e:
        logger.warning(
            "Token blacklist check failed, allowing request",
            extra={
                "operation": "token_blacklist_check",
                "error_type": type(e).__name__,
            },
        )
        return False  # Fail-open
