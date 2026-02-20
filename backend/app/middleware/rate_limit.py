"""Redis-based rate limiting middleware."""

import logging
import time
from datetime import datetime, timedelta

from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

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


# ---------------------------------------------------------------------------
# In-memory fallback for auth rate limiting (fail-closed)
# Used when Redis is unavailable so brute-force attacks are still throttled.
#
# Structure: {key: (count, window_start_monotonic)}
# Safe without an asyncio.Lock because asyncio is single-threaded cooperative
# and every coroutine suspends only at explicit `await` points — none exist
# inside _memory_auth_check, so updates are atomic from Python's perspective.
# ---------------------------------------------------------------------------
_auth_memory_counts: dict[str, tuple[int, float]] = {}
_AUTH_MEMORY_WINDOW_SECONDS: int = 60
_AUTH_MEMORY_MAX_ENTRIES: int = 10_000


def _memory_auth_check(key: str) -> int:
    """
    Apply in-memory sliding-window rate limit for auth paths.

    Called when Redis is unavailable or raised an exception (fail-closed path).
    Returns the current request count within the 60-second window.
    """
    now = time.monotonic()

    if len(_auth_memory_counts) >= _AUTH_MEMORY_MAX_ENTRIES:
        expired = [k for k, (_, ws) in _auth_memory_counts.items() if now - ws > _AUTH_MEMORY_WINDOW_SECONDS]
        for k in expired:
            del _auth_memory_counts[k]

    if key in _auth_memory_counts:
        count, window_start = _auth_memory_counts[key]
        if now - window_start > _AUTH_MEMORY_WINDOW_SECONDS:
            count, window_start = 1, now
        else:
            count += 1
    else:
        count, window_start = 1, now

    _auth_memory_counts[key] = (count, window_start)
    return count


def _to_int(value: object) -> int:
    """Convert Redis script results to int safely."""
    if isinstance(value, bytes):
        try:
            return int(value.decode())
        except ValueError:
            return 0
    if isinstance(value, str):
        try:
            return int(value)
        except ValueError:
            return 0
    if isinstance(value, int):
        return value
    return 0


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
        tomorrow = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)

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
        tomorrow = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        return {
            "limit": settings.rate_limit_per_day,
            "used": 0,
            "remaining": settings.rate_limit_per_day,
            "reset_at": tomorrow.isoformat() + "Z",
        }


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Redis-based rate limiting middleware with sliding window.

    Auth endpoints (/api/auth/) are fail-CLOSED: an in-memory sliding-window
    counter enforces the per-minute limit even when Redis is unavailable,
    preventing brute-force attacks from bypassing controls during outages.
    All other rate-limited paths remain fail-open (graceful degradation).
    """

    RATE_LIMITED_PATHS = [
        "/api/search/",
        "/api/stream/",
        "/api/compare/",
    ]

    AUTH_RATE_LIMITED_PATHS = ["/api/auth/"]
    AUTH_RATE_LIMIT_PER_MINUTE = 10
    PUBLIC_RATE_LIMITED_PATHS = [
        "/api/search/keyword/",
        "/api/keyword-search/bible/",
        "/api/metadata/",
        "/api/etymology/",
        "/api/verse/",
        "/api/quran/verses/",
    ]

    async def _check_auth_rate_limit(self, request: Request, now: datetime) -> tuple[int, int]:
        """
        Check auth-endpoint rate limit using Redis with in-memory fallback.

        Auth paths are fail-CLOSED: even when Redis is down, the in-memory
        sliding-window counter keeps enforcing the per-minute limit so that
        brute-force attacks cannot slip through infrastructure outages.

        Returns (current_count, limit).
        """
        client_ip = request.client.host if request.client else "anonymous"
        minute_key = now.strftime("%Y-%m-%d-%H-%M")
        key = f"ratelimit:auth:{client_ip}:{minute_key}"
        limit = self.AUTH_RATE_LIMIT_PER_MINUTE

        try:
            from app.redis_client import redis_manager

            if redis_manager.client is not None:
                script = redis_manager.client.register_script(RATE_LIMIT_SCRIPT)
                current_count_raw = await script(keys=[key], args=[limit, 60])
                return _to_int(current_count_raw), limit

            logger.warning(
                "Redis unavailable for auth rate limit — using in-memory fallback (fail-closed)",
                extra={"operation": "auth_rate_limit", "path": request.url.path},
            )
        except Exception:
            logger.warning(
                "Redis auth rate limit check raised an exception — using in-memory fallback (fail-closed)",
                extra={"operation": "auth_rate_limit", "path": request.url.path},
                exc_info=True,
            )

        return _memory_auth_check(key), limit

    async def dispatch(self, request: Request, call_next):
        if not settings.rate_limit_enabled:
            return await call_next(request)

        path = request.url.path

        is_rate_limited_path = any(path.startswith(p) for p in self.RATE_LIMITED_PATHS)
        is_auth_path = any(path.startswith(p) for p in self.AUTH_RATE_LIMITED_PATHS)
        matched_public_path = next((p for p in self.PUBLIC_RATE_LIMITED_PATHS if path.startswith(p)), None)
        is_public_path = matched_public_path is not None

        if not is_rate_limited_path and not is_auth_path and not is_public_path:
            return await call_next(request)

        user_id = getattr(request.state, "user_id", None)

        if user_id is None and not is_auth_path and not is_public_path:
            return await call_next(request)

        # -------------------------------------------------------------------
        # AUTH ENDPOINTS — fail-closed with Redis + in-memory fallback.
        # Isolated from the outer try/except so Redis exceptions still result
        # in enforcement via _memory_auth_check rather than silent bypass.
        # -------------------------------------------------------------------
        if is_auth_path:
            now = datetime.utcnow()
            request_id = getattr(request.state, "request_id", "unknown")
            current_count, limit = await self._check_auth_rate_limit(request, now)

            if current_count > limit:
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
                        "X-RateLimit-Remaining": "0",
                        "Retry-After": "60",
                    },
                )

            return await call_next(request)

        # -------------------------------------------------------------------
        # PUBLIC & REGULAR ENDPOINTS — fail-open if Redis unavailable.
        # -------------------------------------------------------------------
        try:
            from app.redis_client import redis_manager

            now = datetime.utcnow()

            if redis_manager.client is None:
                logger.warning(
                    "Redis unavailable, allowing request (fail-open)",
                    extra={"operation": "rate_limit_check", "path": path},
                )
                return await call_next(request)

            if is_public_path:
                minute_key = now.strftime("%Y-%m-%d-%H-%M")
                client_ip = request.client.host if request.client else "anonymous"
                path_bucket = (matched_public_path or "public").strip("/").replace("/", ":")
                key = f"ratelimit:public:{path_bucket}:{client_ip}:{minute_key}"
                limit = settings.public_rate_limit_per_minute
                ttl_seconds = 60

                script = redis_manager.client.register_script(RATE_LIMIT_SCRIPT)
                current_count_raw = await script(keys=[key], args=[limit, ttl_seconds])
                current_count = _to_int(current_count_raw)

                if current_count > limit:
                    request_id = getattr(request.state, "request_id", "unknown")
                    return JSONResponse(
                        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                        content={
                            "success": False,
                            "error": {
                                "code": "RATE_LIMIT_EXCEEDED",
                                "message": "Cok fazla istek gonderildi. Lutfen 1 dakika sonra tekrar deneyin",
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

                response = await call_next(request)
                response.headers["X-RateLimit-Limit"] = str(limit)
                response.headers["X-RateLimit-Remaining"] = str(max(0, limit - current_count))
                return response

            tomorrow = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
            today = now.strftime("%Y-%m-%d")
            key = f"ratelimit:{user_id}:{today}"
            ttl_seconds = int((tomorrow - now).total_seconds())

            script = redis_manager.client.register_script(RATE_LIMIT_SCRIPT)
            current_count_raw = await script(keys=[key], args=[settings.rate_limit_per_day, ttl_seconds])
            current_count = _to_int(current_count_raw)

            remaining = max(0, settings.rate_limit_per_day - current_count)
            headers = get_rate_limit_headers(remaining, tomorrow)

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

            response = await call_next(request)
            for key, value in headers.items():
                response.headers[key] = value
            return response

        except Exception:
            logger.warning(
                "Rate limit check failed, allowing request (fail-open for non-auth path)",
                extra={"operation": "rate_limit_check", "path": path},
                exc_info=True,
            )
            return await call_next(request)
