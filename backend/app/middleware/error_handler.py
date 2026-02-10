from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Optional
from datetime import datetime
import uuid

from app.logging_config import get_logger, set_user_id

sentry_sdk = None
try:
    import sentry_sdk

    SENTRY_AVAILABLE = True
except ImportError:
    SENTRY_AVAILABLE = False

logger = get_logger(__name__)


class APIError(Exception):
    def __init__(
        self,
        message: str,
        code: str = "INTERNAL_ERROR",
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[list[dict]] = None,
    ):
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or []
        super().__init__(message)


class ValidationError(APIError):
    def __init__(self, message: str, details: Optional[list[dict]] = None):
        super().__init__(
            message=message,
            code="VALIDATION_ERROR",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details=details,
        )


class AuthenticationError(APIError):
    def __init__(self, message: str = "Kimlik dogrulama basarisiz"):
        super().__init__(
            message=message,
            code="AUTHENTICATION_ERROR",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )


class RateLimitError(APIError):
    def __init__(self, message: str = "Gunluk sorgu limitine ulastiniz"):
        super().__init__(
            message=message,
            code="RATE_LIMIT_EXCEEDED",
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        )


class NotFoundError(APIError):
    def __init__(self, message: str = "Kaynak bulunamadi"):
        super().__init__(
            message=message,
            code="NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND,
        )


def create_error_response(
    request_id: str,
    code: str,
    message: str,
    status_code: int,
    details: Optional[list[dict]] = None,
) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "success": False,
            "error": {
                "code": code,
                "message": message,
                "details": details or [],
            },
            "request_id": request_id,
            "timestamp": datetime.utcnow().isoformat(),
        },
    )


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """
    Error handling middleware that catches and formats API errors.

    Note: This middleware runs AFTER CorrelationIDMiddleware, so correlation_id
    and request_id are already set in request.state by the time this runs.
    Context cleanup is handled by CorrelationIDMiddleware.
    """

    async def dispatch(self, request: Request, call_next):
        # Use request_id from CorrelationIDMiddleware if available, otherwise generate
        request_id = getattr(request.state, "request_id", None) or str(uuid.uuid4())[:8]

        # Set user_id in logging context if available from auth middleware
        if hasattr(request.state, "user_id") and request.state.user_id:
            set_user_id(request.state.user_id)

        try:
            response = await call_next(request)
            return response

        except APIError as e:
            logger.warning(
                "API error occurred",
                extra={
                    "error_code": e.code,
                    "error_message": e.message,
                    "status_code": e.status_code,
                    "path": request.url.path,
                    "method": request.method,
                },
            )
            # Don't capture rate limit errors in Sentry (expected behavior)
            if (
                SENTRY_AVAILABLE
                and sentry_sdk is not None
                and not isinstance(e, RateLimitError)
            ):
                sentry_sdk.capture_exception(e)
            return create_error_response(
                request_id=request_id,
                code=e.code,
                message=e.message,
                status_code=e.status_code,
                details=e.details,
            )

        except Exception as e:
            logger.error(
                "Unhandled exception",
                extra={
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                    "path": request.url.path,
                    "method": request.method,
                },
                exc_info=True,
            )
            # Capture unhandled exceptions in Sentry with user context
            if SENTRY_AVAILABLE and sentry_sdk is not None:
                if hasattr(request.state, "user_id") and request.state.user_id:
                    sentry_sdk.set_user({"id": str(request.state.user_id)})
                sentry_sdk.capture_exception(e)
            return create_error_response(
                request_id=request_id,
                code="INTERNAL_ERROR",
                message="Beklenmeyen bir hata olustu",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
