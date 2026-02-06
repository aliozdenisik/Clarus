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
    - 10 queries/minute for auth endpoints
    - Calendar day reset (UTC midnight)
    - Fail-open if Redis unavailable
    - Atomic increment using Lua script
    """

    RATE_LIMITED_PATHS = [
        "/api/search/",
        "/api/stream/",
        "/api/compare/",
    ]

    AUTH_RATE_LIMITED_PATHS = ["/api/auth/"]
    AUTH_RATE_LIMIT_PER_MINUTE = 10

    async def dispatch(self, request: Request, call_next):
        """Apply rate limiting to configured paths."""
        # Skip if rate limiting disabled
        if not settings.rate_limit_enabled:
            return await call_next(request)

        path = request.url.path

        # Check if path should be rate limited
        is_rate_limited_path = any(path.startswith(p) for p in self.RATE_LIMITED_PATHS)
        is_auth_path = any(path.startswith(p) for p in self.AUTH_RATE_LIMITED_PATHS)

        if not is_rate_limited_path and not is_auth_path:
            return await call_next(request)

        # Get user ID from request state (set by auth middleware)
        user_id = getattr(request.state, "user_id", None)

        # Auth endpoints: rate limit even without user_id (by IP or allow anonymous)
        # For now, skip rate limiting if no user_id (auth endpoints before login)
        if user_id is None and not is_auth_path:
            return await call_next(request)

        # For auth endpoints without user_id, use IP-based rate limiting
        if user_id is None and is_auth_path:
            # Get client IP for anonymous auth requests
            user_id = request.client.host if request.client else "anonymous"

        # Perform rate limit check
        try:
            from app.redis_client import redis_manager

            now = datetime.utcnow()

            # If Redis unavailable, fail-open (allow request)
            if redis_manager.client is None:
                logger.warning("Redis unavailable, allowing request (fail-open)")
                return await call_next(request)

            # AUTH ENDPOINTS: Per-minute rate limiting
            if is_auth_path:
                # Use minute-based key: ratelimit:auth:{user_id}:{timestamp_minute}
                minute_key = now.strftime("%Y-%m-%d-%H-%M")
                key = f"ratelimit:auth:{user_id}:{minute_key}"
                limit = self.AUTH_RATE_LIMIT_PER_MINUTE
                ttl_seconds = 60  # 1 minute TTL

                # Register and execute Lua script
                script = redis_manager.client.register_script(RATE_LIMIT_SCRIPT)
                current_count = await script(
                    keys=[key],
                    args=[limit, ttl_seconds],
                )

                if current_count > limit:
                    request_id = getattr(request.state, "request_id", "unknown")
                    return JSONResponse(
                        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                        content={
                            "success": False,
                            "error": {
                                "code": "RATE_LIMIT_EXCEEDED",
                                "message": f"Cok fazla giris denemesi. Lutfen 1 dakika bekleyin ({limit}/dakika)",
                                "details": [],
                            },
                            "request_id": request_id,
                            "timestamp": now.isoformat(),
                        },
                        headers={
                            "X-RateLimit-Limit": str(limit),
                            "X-RateLimit-Remaining": str(max(0, limit - current_count)),
                            "Retry-After": "60",
                        },
                    )

                # Auth endpoints: don't add rate limit headers to successful responses
                return await call_next(request)

            # REGULAR ENDPOINTS: Per-day rate limiting
            # Calculate reset time (next UTC midnight)
            tomorrow = (now + timedelta(days=1)).replace(
                hour=0, minute=0, second=0, microsecond=0
            )

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
