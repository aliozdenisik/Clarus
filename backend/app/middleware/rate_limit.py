"""Redis-based rate limiting middleware."""

from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from datetime import datetime, timedelta
import logging

from app.config import settings

logger = logging.getLogger(__name__)

# Lua script for atomic rate limiting
# Returns current count after increment
RATE_LIMIT_SCRIPT = """
local key = KEYS[1]
local limit = tonumber(ARGV[1])
local ttl = tonumber(ARGV[2])

local current = redis.call('INCR', key)
if current == 1 then
    redis.call('EXPIRE', key, ttl)
end

return current
"""


def get_rate_limit_headers(remaining: int, reset_at: datetime) -> dict[str, str]:
    """
    Generate rate limit headers for response.

    Args:
        remaining: Number of queries remaining
        reset_at: When the rate limit resets (UTC midnight)

    Returns:
        Dictionary of headers to add to response
    """
    return {
        "X-RateLimit-Limit": str(settings.rate_limit_per_day),
        "X-RateLimit-Remaining": str(max(0, remaining)),
        "X-RateLimit-Reset": reset_at.isoformat() + "Z",
    }


async def get_user_rate_limit_info(user_id: int) -> dict:
    """
    Get rate limit info for a user (for /rate-limit endpoint).

    Args:
        user_id: User ID to check

    Returns:
        Dictionary with limit, used, remaining, reset_at
    """
    try:
        from app.redis_client import redis_manager

        # Calculate reset time (next UTC midnight)
        now = datetime.utcnow()
        tomorrow = (now + timedelta(days=1)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )

        # If Redis unavailable, return safe defaults
        if redis_manager.client is None:
            return {
                "limit": settings.rate_limit_per_day,
                "used": 0,
                "remaining": settings.rate_limit_per_day,
                "reset_at": tomorrow.isoformat() + "Z",
            }

        # Get current count from Redis
        today = now.strftime("%Y-%m-%d")
        key = f"ratelimit:{user_id}:{today}"

        count = await redis_manager.client.get(key)
        used = int(count) if count else 0

        return {
            "limit": settings.rate_limit_per_day,
            "used": used,
            "remaining": max(0, settings.rate_limit_per_day - used),
            "reset_at": tomorrow.isoformat() + "Z",
        }

    except Exception as e:
        logger.warning(f"Failed to get rate limit info: {e}")
        # Fail-open: return safe defaults
        now = datetime.utcnow()
        tomorrow = (now + timedelta(days=1)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        return {
            "limit": settings.rate_limit_per_day,
            "used": 0,
            "remaining": settings.rate_limit_per_day,
            "reset_at": tomorrow.isoformat() + "Z",
        }


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Redis-based rate limiting middleware with sliding window.

    Features:
    - 50 queries/day per user (configurable)
    - Calendar day reset (UTC midnight)
    - Fail-open if Redis unavailable
    - Atomic increment using Lua script
    """

    RATE_LIMITED_PATHS = [
        "/api/search/",
        "/api/stream/",
        "/api/compare/",
    ]

    async def dispatch(self, request: Request, call_next):
        """Apply rate limiting to configured paths."""
        # Skip if rate limiting disabled
        if not settings.rate_limit_enabled:
            return await call_next(request)

        path = request.url.path

        # Check if path should be rate limited
        is_rate_limited_path = any(path.startswith(p) for p in self.RATE_LIMITED_PATHS)

        if not is_rate_limited_path:
            return await call_next(request)

        # Get user ID from request state (set by auth middleware)
        user_id = getattr(request.state, "user_id", None)

        if user_id is None:
            return await call_next(request)

        # Perform rate limit check
        try:
            from app.redis_client import redis_manager

            # Calculate reset time (next UTC midnight)
            now = datetime.utcnow()
            tomorrow = (now + timedelta(days=1)).replace(
                hour=0, minute=0, second=0, microsecond=0
            )

            # If Redis unavailable, fail-open (allow request)
            if redis_manager.client is None:
                logger.warning("Redis unavailable, allowing request (fail-open)")
                return await call_next(request)

            # Build Redis key: ratelimit:{user_id}:{date}
            today = now.strftime("%Y-%m-%d")
            key = f"ratelimit:{user_id}:{today}"

            # Calculate TTL (seconds until midnight UTC)
            ttl_seconds = int((tomorrow - now).total_seconds())

            # Register Lua script (idempotent)
            script = redis_manager.client.register_script(RATE_LIMIT_SCRIPT)

            # Execute Lua script atomically
            current_count = await script(
                keys=[key],
                args=[settings.rate_limit_per_day, ttl_seconds],
            )

            # Calculate remaining
            remaining = max(0, settings.rate_limit_per_day - current_count)

            # Generate headers
            headers = get_rate_limit_headers(remaining, tomorrow)

            # Check if limit exceeded (BEFORE incrementing, count is already incremented by script)
            if current_count > settings.rate_limit_per_day:
                request_id = getattr(request.state, "request_id", "unknown")
                return JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content={
                        "success": False,
                        "error": {
                            "code": "RATE_LIMIT_EXCEEDED",
                            "message": f"Gunluk sorgu limitine ulastiniz ({settings.rate_limit_per_day}/gun)",
                            "details": [],
                        },
                        "request_id": request_id,
                        "timestamp": datetime.utcnow().isoformat(),
                    },
                    headers=headers,
                )

            # Allow request and add headers
            response = await call_next(request)

            # Add rate limit headers to response
            for key, value in headers.items():
                response.headers[key] = value

            return response

        except Exception as e:
            # Fail-open: log error and allow request
            logger.warning(
                "Rate limit check failed, allowing request",
                extra={"operation": "rate_limit_check", "error_type": type(e).__name__},
            )
            return await call_next(request)
