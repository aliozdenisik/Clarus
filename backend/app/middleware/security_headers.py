"""Security headers middleware — addresses #236, #238, #240, #243."""

import logging

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from app.config import settings

logger = logging.getLogger(__name__)

_DOCS_PATHS = frozenset({"/docs", "/docs/", "/redoc", "/redoc/", "/openapi.json"})

_DOCS_CSP = (
    "default-src 'self'; "
    "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
    "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
    "img-src 'self' data: https://cdn.jsdelivr.net; "
    "font-src 'self' https://cdn.jsdelivr.net; "
    "frame-ancestors 'none'"
)

_API_CSP = "default-src 'self'; frame-ancestors 'none'"


def _is_https_request(request: Request) -> bool:
    if request.url.scheme == "https":
        return True
    forwarded_proto = request.headers.get("x-forwarded-proto", "").split(",", 1)[0].strip().lower()
    return forwarded_proto == "https"


def _is_docs_path(path: str) -> bool:
    return path in _DOCS_PATHS


def _is_json_response(response) -> bool:
    content_type = response.headers.get("content-type", "")
    return content_type.startswith("application/json")


def log_hsts_startup_warning() -> None:
    if settings.is_production:
        logger.warning(
            "HSTS is conditional on HTTPS detection. Ensure your reverse proxy "
            "forwards 'X-Forwarded-Proto: https' to apply Strict-Transport-Security. "
            "Without this header, HSTS will NOT be sent to browsers.",
            extra={"app_env": settings.app_env},
        )


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            path = request.url.path

            response.headers["Server"] = "Clarus"

            if _is_https_request(request):
                if settings.is_production:
                    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
                else:
                    response.headers["Strict-Transport-Security"] = "max-age=300"

            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["X-Frame-Options"] = "DENY"
            response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
            response.headers["X-XSS-Protection"] = "0"
            response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"

            if _is_docs_path(path):
                response.headers["Content-Security-Policy"] = _DOCS_CSP
            else:
                response.headers["Content-Security-Policy"] = _API_CSP

            if _is_json_response(response):
                response.headers["Cache-Control"] = "no-store, max-age=0"

            return response

        except Exception as e:
            logger.error(
                f"Error adding security headers: {e!s}",
                extra={"error_type": type(e).__name__},
            )
            raise
