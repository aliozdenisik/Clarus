"""
Correlation ID middleware for request tracing.

Provides end-to-end request correlation by:
1. Extracting X-Correlation-ID from incoming requests (or generating a new one)
2. Generating a unique X-Request-ID for each request
3. Setting context variables for structured logging
4. Adding both headers to the response

This enables tracing a user action from frontend -> backend -> logs -> monitoring.
"""

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import uuid
import logging

from app.logging_config import set_correlation_id, set_request_id, clear_context

logger = logging.getLogger(__name__)


class CorrelationIDMiddleware(BaseHTTPMiddleware):
    """
    Middleware that handles correlation ID propagation for distributed tracing.

    Header flow:
    - X-Correlation-ID: Client-provided or auto-generated UUID for tracing user actions
    - X-Request-ID: Server-generated short ID for this specific request

    Usage:
        # In main.py, add BEFORE ErrorHandlerMiddleware
        app.add_middleware(CorrelationIDMiddleware)
    """

    async def dispatch(self, request: Request, call_next):
        # Get correlation ID from header or generate new one
        # Correlation ID tracks a user action across multiple requests
        correlation_id = request.headers.get("X-Correlation-ID") or str(uuid.uuid4())

        # Request ID is unique to this specific HTTP request
        # Using first 8 chars for readability in logs
        request_id = str(uuid.uuid4())[:8]

        # Set context variables for structured logging
        # These are picked up by JSONFormatter and ConsoleFormatter
        set_correlation_id(correlation_id)
        set_request_id(request_id)

        # Store in request state for access in route handlers
        request.state.correlation_id = correlation_id
        request.state.request_id = request_id

        logger.debug(
            f"Request started: {request.method} {request.url.path}",
            extra={
                "http_method": request.method,
                "http_path": str(request.url.path),
            },
        )

        try:
            response = await call_next(request)

            # Add correlation headers to response for client-side tracing
            response.headers["X-Correlation-ID"] = correlation_id
            response.headers["X-Request-ID"] = request_id

            return response
        finally:
            # Clear context to prevent leaking between requests
            # Important for async frameworks where context can persist
            clear_context()
