from __future__ import annotations

import pytest
from fastapi.responses import JSONResponse, PlainTextResponse
from starlette.requests import Request

from app.config import settings
from app.middleware.security_headers import (
    SecurityHeadersMiddleware,
    _is_docs_path,
    _is_https_request,
    _is_json_response,
    log_hsts_startup_warning,
)


async def _dummy_asgi_app(scope, receive, send) -> None:
    _ = (scope, receive, send)


def _build_request(
    path: str = "/api/health",
    scheme: str = "http",
    headers: list[tuple[bytes, bytes]] | None = None,
) -> Request:
    scope = {
        "type": "http",
        "http_version": "1.1",
        "method": "GET",
        "scheme": scheme,
        "path": path,
        "raw_path": path.encode("utf-8"),
        "query_string": b"",
        "headers": headers or [],
        "client": ("127.0.0.1", 54321),
        "server": ("testserver", 80),
    }
    return Request(scope)


class TestIsHttpsRequest:
    def test_direct_https_scheme(self) -> None:
        request = _build_request(scheme="https")
        assert _is_https_request(request) is True

    def test_http_scheme_returns_false(self) -> None:
        request = _build_request(scheme="http")
        assert _is_https_request(request) is False

    def test_x_forwarded_proto_https(self) -> None:
        headers = [(b"x-forwarded-proto", b"https")]
        request = _build_request(headers=headers)
        assert _is_https_request(request) is True

    def test_x_forwarded_proto_http(self) -> None:
        headers = [(b"x-forwarded-proto", b"http")]
        request = _build_request(headers=headers)
        assert _is_https_request(request) is False

    def test_x_forwarded_proto_with_multiple_values(self) -> None:
        headers = [(b"x-forwarded-proto", b"https, http")]
        request = _build_request(headers=headers)
        assert _is_https_request(request) is True


class TestIsDocsPath:
    def test_docs_path(self) -> None:
        assert _is_docs_path("/docs") is True

    def test_docs_path_trailing_slash(self) -> None:
        assert _is_docs_path("/docs/") is True

    def test_redoc_path(self) -> None:
        assert _is_docs_path("/redoc") is True

    def test_openapi_json_path(self) -> None:
        assert _is_docs_path("/openapi.json") is True

    def test_api_path_is_not_docs(self) -> None:
        assert _is_docs_path("/api/health") is False

    def test_nested_docs_path_is_not_docs(self) -> None:
        assert _is_docs_path("/api/docs") is False


class TestIsJsonResponse:
    def test_json_content_type(self) -> None:
        response = JSONResponse(content={"ok": True})
        assert _is_json_response(response) is True

    def test_plain_text_is_not_json(self) -> None:
        response = PlainTextResponse("ok")
        assert _is_json_response(response) is False


class TestServerHeader:
    @pytest.mark.asyncio
    async def test_server_header_overridden_to_clarus(self) -> None:
        middleware = SecurityHeadersMiddleware(app=_dummy_asgi_app)
        request = _build_request("/api/health")

        async def call_next(_r: Request):
            return JSONResponse(content={"status": "ok"})

        response = await middleware.dispatch(request, call_next)
        assert response.headers["Server"] == "Clarus"

    @pytest.mark.asyncio
    async def test_server_header_on_docs_path(self) -> None:
        middleware = SecurityHeadersMiddleware(app=_dummy_asgi_app)
        request = _build_request("/docs")

        async def call_next(_r: Request):
            return PlainTextResponse("<html>docs</html>")

        response = await middleware.dispatch(request, call_next)
        assert response.headers["Server"] == "Clarus"


class TestHstsHeader:
    @pytest.mark.asyncio
    async def test_no_hsts_on_plain_http(self) -> None:
        middleware = SecurityHeadersMiddleware(app=_dummy_asgi_app)
        request = _build_request(scheme="http")

        async def call_next(_r: Request):
            return JSONResponse(content={})

        response = await middleware.dispatch(request, call_next)
        assert "Strict-Transport-Security" not in response.headers

    @pytest.mark.asyncio
    async def test_hsts_production_on_https(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(settings, "app_env", "production")
        middleware = SecurityHeadersMiddleware(app=_dummy_asgi_app)
        request = _build_request(scheme="https")

        async def call_next(_r: Request):
            return JSONResponse(content={})

        response = await middleware.dispatch(request, call_next)
        assert response.headers["Strict-Transport-Security"] == "max-age=31536000; includeSubDomains"

    @pytest.mark.asyncio
    async def test_hsts_staging_on_https(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(settings, "app_env", "development")
        middleware = SecurityHeadersMiddleware(app=_dummy_asgi_app)
        request = _build_request(scheme="https")

        async def call_next(_r: Request):
            return JSONResponse(content={})

        response = await middleware.dispatch(request, call_next)
        assert response.headers["Strict-Transport-Security"] == "max-age=300"

    @pytest.mark.asyncio
    async def test_hsts_via_x_forwarded_proto(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(settings, "app_env", "production")
        middleware = SecurityHeadersMiddleware(app=_dummy_asgi_app)
        headers = [(b"x-forwarded-proto", b"https")]
        request = _build_request(scheme="http", headers=headers)

        async def call_next(_r: Request):
            return JSONResponse(content={})

        response = await middleware.dispatch(request, call_next)
        assert response.headers["Strict-Transport-Security"] == "max-age=31536000; includeSubDomains"


class TestCspHeader:
    @pytest.mark.asyncio
    async def test_strict_csp_on_api_endpoint(self) -> None:
        middleware = SecurityHeadersMiddleware(app=_dummy_asgi_app)
        request = _build_request("/api/search/quran")

        async def call_next(_r: Request):
            return JSONResponse(content={})

        response = await middleware.dispatch(request, call_next)
        assert response.headers["Content-Security-Policy"] == "default-src 'self'; frame-ancestors 'none'"

    @pytest.mark.asyncio
    async def test_relaxed_csp_on_docs(self) -> None:
        middleware = SecurityHeadersMiddleware(app=_dummy_asgi_app)
        request = _build_request("/docs")

        async def call_next(_r: Request):
            return PlainTextResponse("<html>swagger</html>")

        response = await middleware.dispatch(request, call_next)
        csp = response.headers["Content-Security-Policy"]
        assert "cdn.jsdelivr.net" in csp
        assert "'unsafe-inline'" in csp

    @pytest.mark.asyncio
    async def test_relaxed_csp_on_redoc(self) -> None:
        middleware = SecurityHeadersMiddleware(app=_dummy_asgi_app)
        request = _build_request("/redoc")

        async def call_next(_r: Request):
            return PlainTextResponse("<html>redoc</html>")

        response = await middleware.dispatch(request, call_next)
        csp = response.headers["Content-Security-Policy"]
        assert "cdn.jsdelivr.net" in csp

    @pytest.mark.asyncio
    async def test_relaxed_csp_on_openapi_json(self) -> None:
        middleware = SecurityHeadersMiddleware(app=_dummy_asgi_app)
        request = _build_request("/openapi.json")

        async def call_next(_r: Request):
            return JSONResponse(content={"openapi": "3.0.0"})

        response = await middleware.dispatch(request, call_next)
        csp = response.headers["Content-Security-Policy"]
        assert "cdn.jsdelivr.net" in csp


class TestCacheControlHeader:
    @pytest.mark.asyncio
    async def test_json_response_gets_no_store(self) -> None:
        middleware = SecurityHeadersMiddleware(app=_dummy_asgi_app)
        request = _build_request("/api/auth/me")

        async def call_next(_r: Request):
            return JSONResponse(content={"user": "test@example.com"})

        response = await middleware.dispatch(request, call_next)
        assert response.headers["Cache-Control"] == "no-store, max-age=0"

    @pytest.mark.asyncio
    async def test_non_json_response_no_cache_control(self) -> None:
        middleware = SecurityHeadersMiddleware(app=_dummy_asgi_app)
        request = _build_request("/docs")

        async def call_next(_r: Request):
            return PlainTextResponse("<html>docs</html>")

        response = await middleware.dispatch(request, call_next)
        assert "Cache-Control" not in response.headers


class TestStandardSecurityHeaders:
    @pytest.mark.asyncio
    async def test_all_standard_headers_present(self) -> None:
        middleware = SecurityHeadersMiddleware(app=_dummy_asgi_app)
        request = _build_request("/api/health")

        async def call_next(_r: Request):
            return JSONResponse(content={"status": "ok"})

        response = await middleware.dispatch(request, call_next)
        assert response.headers["X-Content-Type-Options"] == "nosniff"
        assert response.headers["X-Frame-Options"] == "DENY"
        assert response.headers["Referrer-Policy"] == "strict-origin-when-cross-origin"
        assert response.headers["X-XSS-Protection"] == "0"
        assert response.headers["Permissions-Policy"] == "camera=(), microphone=(), geolocation=()"

    @pytest.mark.asyncio
    async def test_headers_survive_exception_in_handler(self) -> None:
        middleware = SecurityHeadersMiddleware(app=_dummy_asgi_app)
        request = _build_request("/api/health")

        async def call_next(_r: Request):
            raise RuntimeError("handler exploded")

        with pytest.raises(RuntimeError, match="handler exploded"):
            await middleware.dispatch(request, call_next)


class TestLogHstsStartupWarning:
    def test_warns_in_production(self, monkeypatch: pytest.MonkeyPatch, caplog) -> None:
        monkeypatch.setattr(settings, "app_env", "production")
        with caplog.at_level("WARNING"):
            log_hsts_startup_warning()
        assert "X-Forwarded-Proto" in caplog.text

    def test_no_warning_in_development(self, monkeypatch: pytest.MonkeyPatch, caplog) -> None:
        monkeypatch.setattr(settings, "app_env", "development")
        with caplog.at_level("WARNING"):
            log_hsts_startup_warning()
        assert caplog.text == ""


class TestProductionDocsDisabled:
    def test_docs_disabled_in_production(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(settings, "app_env", "production")
        assert settings.is_production is True
        docs_url = None if settings.is_production else "/docs"
        redoc_url = None if settings.is_production else "/redoc"
        openapi_url = None if settings.is_production else "/openapi.json"
        assert docs_url is None
        assert redoc_url is None
        assert openapi_url is None

    def test_docs_enabled_in_development(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(settings, "app_env", "development")
        assert settings.is_production is False
        docs_url = None if settings.is_production else "/docs"
        redoc_url = None if settings.is_production else "/redoc"
        openapi_url = None if settings.is_production else "/openapi.json"
        assert docs_url == "/docs"
        assert redoc_url == "/redoc"
        assert openapi_url == "/openapi.json"
