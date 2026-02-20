from __future__ import annotations

import pytest
from fastapi.responses import PlainTextResponse
from starlette.requests import Request

from app.config import settings
from app.middleware import rate_limit as rl_module
from app.middleware.rate_limit import RateLimitMiddleware
from app.redis_client import redis_manager


class _FakeRedisClient:
    def __init__(self, values: list[int]) -> None:
        self._values = values

    def register_script(self, _script: str):
        async def _runner(*, keys: list[str], args: list[int]) -> int:
            _ = (keys, args)
            if self._values:
                return self._values.pop(0)
            return 1

        return _runner


def _build_request(path: str) -> Request:
    scope = {
        "type": "http",
        "http_version": "1.1",
        "method": "GET",
        "scheme": "http",
        "path": path,
        "raw_path": path.encode("utf-8"),
        "query_string": b"",
        "headers": [],
        "client": ("127.0.0.1", 54321),
        "server": ("testserver", 80),
    }
    return Request(scope)


async def _dummy_asgi_app(scope, receive, send) -> None:
    _ = (scope, receive, send)


@pytest.mark.asyncio
async def test_public_path_adds_headers_when_under_limit(monkeypatch: pytest.MonkeyPatch) -> None:
    middleware = RateLimitMiddleware(app=_dummy_asgi_app)
    monkeypatch.setattr(settings, "rate_limit_enabled", True)
    monkeypatch.setattr(settings, "public_rate_limit_per_minute", 2)
    monkeypatch.setattr(redis_manager, "client", _FakeRedisClient([1]))

    request = _build_request("/api/metadata/collections")

    async def call_next(_request: Request):
        return PlainTextResponse("ok", status_code=200)

    response = await middleware.dispatch(request, call_next)

    assert response.status_code == 200
    assert response.headers["X-RateLimit-Limit"] == "2"
    assert response.headers["X-RateLimit-Remaining"] == "1"


@pytest.mark.asyncio
async def test_public_path_returns_429_when_limit_exceeded(monkeypatch: pytest.MonkeyPatch) -> None:
    middleware = RateLimitMiddleware(app=_dummy_asgi_app)
    monkeypatch.setattr(settings, "rate_limit_enabled", True)
    monkeypatch.setattr(settings, "public_rate_limit_per_minute", 2)
    monkeypatch.setattr(redis_manager, "client", _FakeRedisClient([3]))

    request = _build_request("/api/metadata/collections")
    called = False

    async def call_next(_request: Request):
        nonlocal called
        called = True
        return PlainTextResponse("ok", status_code=200)

    response = await middleware.dispatch(request, call_next)

    assert response.status_code == 429
    assert response.headers["X-RateLimit-Limit"] == "2"
    assert response.headers["X-RateLimit-Remaining"] == "0"
    assert response.headers["Retry-After"] == "60"
    assert called is False


@pytest.mark.asyncio
async def test_non_rate_limited_path_bypasses_middleware(monkeypatch: pytest.MonkeyPatch) -> None:
    middleware = RateLimitMiddleware(app=_dummy_asgi_app)
    monkeypatch.setattr(settings, "rate_limit_enabled", True)
    monkeypatch.setattr(redis_manager, "client", None)

    request = _build_request("/api/health")

    async def call_next(_request: Request):
        return PlainTextResponse("ok", status_code=200)

    response = await middleware.dispatch(request, call_next)

    assert response.status_code == 200
    assert bytes(response.body).decode("utf-8") == "ok"


@pytest.mark.asyncio
async def test_public_path_fails_open_when_redis_unavailable(monkeypatch: pytest.MonkeyPatch) -> None:
    middleware = RateLimitMiddleware(app=_dummy_asgi_app)
    monkeypatch.setattr(settings, "rate_limit_enabled", True)
    monkeypatch.setattr(redis_manager, "client", None)

    request = _build_request("/api/search/keyword/roots")

    async def call_next(_request: Request):
        return PlainTextResponse("ok", status_code=200)

    response = await middleware.dispatch(request, call_next)

    assert response.status_code == 200
    assert bytes(response.body).decode("utf-8") == "ok"


@pytest.mark.asyncio
async def test_auth_path_returns_429_when_limit_exceeded_with_redis(monkeypatch: pytest.MonkeyPatch) -> None:
    middleware = RateLimitMiddleware(app=_dummy_asgi_app)
    monkeypatch.setattr(settings, "rate_limit_enabled", True)
    monkeypatch.setattr(redis_manager, "client", _FakeRedisClient([11]))

    request = _build_request("/api/auth/me")
    called = False

    async def call_next(_request: Request):
        nonlocal called
        called = True
        return PlainTextResponse("unauthorized", status_code=401)

    response = await middleware.dispatch(request, call_next)

    assert response.status_code == 429
    assert response.headers["X-RateLimit-Limit"] == "10"
    assert response.headers["X-RateLimit-Remaining"] == "0"
    assert response.headers["Retry-After"] == "60"
    assert called is False


@pytest.mark.asyncio
async def test_auth_path_fails_closed_when_redis_unavailable(monkeypatch: pytest.MonkeyPatch) -> None:
    middleware = RateLimitMiddleware(app=_dummy_asgi_app)
    monkeypatch.setattr(settings, "rate_limit_enabled", True)
    monkeypatch.setattr(redis_manager, "client", None)
    monkeypatch.setattr(rl_module, "_auth_memory_counts", {})

    request = _build_request("/api/auth/sign-in")

    async def call_next(_request: Request):
        return PlainTextResponse("ok", status_code=200)

    for _ in range(10):
        response = await middleware.dispatch(request, call_next)
        assert response.status_code == 200

    response = await middleware.dispatch(request, call_next)
    assert response.status_code == 429
    assert response.headers["Retry-After"] == "60"


@pytest.mark.asyncio
async def test_auth_path_fails_closed_on_redis_exception(monkeypatch: pytest.MonkeyPatch) -> None:
    class _BrokenRedisClient:
        def register_script(self, _script: str):
            async def _runner(*, keys: list[str], args: list[int]) -> int:
                raise RuntimeError("simulated Redis failure")

            return _runner

    middleware = RateLimitMiddleware(app=_dummy_asgi_app)
    monkeypatch.setattr(settings, "rate_limit_enabled", True)
    monkeypatch.setattr(redis_manager, "client", _BrokenRedisClient())
    monkeypatch.setattr(rl_module, "_auth_memory_counts", {})

    request = _build_request("/api/auth/sign-in")

    async def call_next(_request: Request):
        return PlainTextResponse("ok", status_code=200)

    for _ in range(10):
        response = await middleware.dispatch(request, call_next)
        assert response.status_code == 200

    response = await middleware.dispatch(request, call_next)
    assert response.status_code == 429
    assert response.headers["Retry-After"] == "60"


@pytest.mark.asyncio
async def test_auth_path_allows_requests_under_limit(monkeypatch: pytest.MonkeyPatch) -> None:
    middleware = RateLimitMiddleware(app=_dummy_asgi_app)
    monkeypatch.setattr(settings, "rate_limit_enabled", True)
    monkeypatch.setattr(redis_manager, "client", _FakeRedisClient([5]))

    request = _build_request("/api/auth/me")

    async def call_next(_request: Request):
        return PlainTextResponse("unauthorized", status_code=401)

    response = await middleware.dispatch(request, call_next)

    assert response.status_code == 401
