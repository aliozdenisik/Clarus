from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from datetime import datetime, timedelta
from typing import Optional
from collections import defaultdict
import asyncio

from app.config import settings


class RateLimitState:
    def __init__(self):
        self._user_counts: dict[int, dict] = defaultdict(
            lambda: {"count": 0, "reset_at": None}
        )
        self._lock = asyncio.Lock()

    async def check_and_increment(self, user_id: int) -> tuple[int, int, datetime]:
        async with self._lock:
            now = datetime.utcnow()
            tomorrow = (now + timedelta(days=1)).replace(
                hour=0, minute=0, second=0, microsecond=0
            )

            user_data = self._user_counts[user_id]

            if user_data["reset_at"] is None or now >= user_data["reset_at"]:
                user_data["count"] = 0
                user_data["reset_at"] = tomorrow

            remaining = settings.rate_limit_per_day - user_data["count"]

            return user_data["count"], remaining, user_data["reset_at"]

    async def increment(self, user_id: int) -> None:
        async with self._lock:
            self._user_counts[user_id]["count"] += 1

    async def get_info(self, user_id: int) -> tuple[int, int, datetime]:
        async with self._lock:
            now = datetime.utcnow()
            tomorrow = (now + timedelta(days=1)).replace(
                hour=0, minute=0, second=0, microsecond=0
            )

            user_data = self._user_counts[user_id]

            if user_data["reset_at"] is None:
                user_data["reset_at"] = tomorrow

            remaining = max(0, settings.rate_limit_per_day - user_data["count"])

            return user_data["count"], remaining, user_data["reset_at"]


rate_limit_state = RateLimitState()


def get_rate_limit_headers(remaining: int, reset_at: datetime) -> dict[str, str]:
    return {
        "X-RateLimit-Limit": str(settings.rate_limit_per_day),
        "X-RateLimit-Remaining": str(max(0, remaining)),
        "X-RateLimit-Reset": reset_at.isoformat() + "Z",
    }


class RateLimitMiddleware(BaseHTTPMiddleware):
    RATE_LIMITED_PATHS = [
        "/api/search/",
        "/api/stream/",
        "/api/compare/",
    ]

    async def dispatch(self, request: Request, call_next):
        if not settings.rate_limit_enabled:
            return await call_next(request)

        path = request.url.path

        is_rate_limited_path = any(path.startswith(p) for p in self.RATE_LIMITED_PATHS)

        if not is_rate_limited_path:
            return await call_next(request)

        user_id = getattr(request.state, "user_id", None)

        if user_id is None:
            return await call_next(request)

        count, remaining, reset_at = await rate_limit_state.check_and_increment(user_id)

        headers = get_rate_limit_headers(remaining, reset_at)

        if count >= settings.rate_limit_per_day:
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

        await rate_limit_state.increment(user_id)

        response = await call_next(request)

        _, updated_remaining, _ = await rate_limit_state.get_info(user_id)
        for key, value in get_rate_limit_headers(updated_remaining, reset_at).items():
            response.headers[key] = value

        return response


async def get_user_rate_limit_info(user_id: int) -> dict:
    count, remaining, reset_at = await rate_limit_state.get_info(user_id)
    return {
        "limit": settings.rate_limit_per_day,
        "used": count,
        "remaining": remaining,
        "reset_at": reset_at.isoformat() + "Z",
    }
