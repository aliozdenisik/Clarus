"""
Security headers middleware for HTTP response hardening.

Adds security headers to all API responses to protect against common web vulnerabilities:
- HSTS: Enforce HTTPS-only communication
- X-Content-Type-Options: Prevent MIME type sniffing
- X-Frame-Options: Prevent clickjacking
- Referrer-Policy: Control referrer information leakage
- X-XSS-Protection: Legacy XSS protection (disabled in favor of CSP)
- Permissions-Policy: Restrict browser features
- Content-Security-Policy: Prevent injection attacks

This middleware applies to all HTTP responses, including error responses.
"""

import logging

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from app.config import settings

logger = logging.getLogger(__name__)


def _is_https_request(request: Request) -> bool:
    if request.url.scheme == "https":
        return True
    forwarded_proto = request.headers.get("x-forwarded-proto", "").split(",", 1)[0].strip().lower()
    return forwarded_proto == "https"


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware that adds security headers to all HTTP responses.

    Headers added:
    - Strict-Transport-Security: Enforce HTTPS for 1 year
    - X-Content-Type-Options: Prevent MIME type sniffing
    - X-Frame-Options: Deny framing (prevent clickjacking)
    - Referrer-Policy: Strict referrer policy
    - X-XSS-Protection: Disable legacy XSS protection (rely on CSP)
    - Permissions-Policy: Restrict browser features (camera, microphone, geolocation)
    - Content-Security-Policy: Minimal CSP for JSON API (no inline scripts)

    Usage:
        # In main.py, add BEFORE ErrorHandlerMiddleware
        app.add_middleware(SecurityHeadersMiddleware)
    """

    async def dispatch(self, request: Request, call_next):
        """
        Process request and add security headers to response.

        Args:
            request: Incoming HTTP request
            call_next: Next middleware/route handler

        Returns:
            Response with security headers added
        """
        try:
            response = await call_next(request)

            # Strict-Transport-Security: Enforce HTTPS for 1 year, include subdomains
            if settings.is_production and _is_https_request(request):
                response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

            # X-Content-Type-Options: Prevent MIME type sniffing
            response.headers["X-Content-Type-Options"] = "nosniff"

            # X-Frame-Options: Deny framing to prevent clickjacking
            response.headers["X-Frame-Options"] = "DENY"

            # Referrer-Policy: Only send referrer for same-origin requests
            response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

            # X-XSS-Protection: Disable legacy XSS protection (modern browsers use CSP)
            response.headers["X-XSS-Protection"] = "0"

            # Permissions-Policy: Restrict access to browser features
            # Deny: camera, microphone, geolocation
            response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"

            # Content-Security-Policy: Minimal policy for JSON API
            # - default-src 'self': Only allow resources from same origin
            # - frame-ancestors 'none': Prevent framing
            response.headers["Content-Security-Policy"] = "default-src 'self'; frame-ancestors 'none'"

            return response

        except Exception as e:
            # Log security header errors but don't break the request
            logger.error(
                f"Error adding security headers: {e!s}",
                extra={"error_type": type(e).__name__},
            )
            raise
