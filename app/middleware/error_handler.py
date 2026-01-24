from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Optional
from datetime import datetime
import uuid
import traceback
import logging

logger = logging.getLogger(__name__)


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
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4())[:8])
        request.state.request_id = request_id

        try:
            response = await call_next(request)
            response.headers["X-Request-ID"] = request_id
            return response

        except APIError as e:
            logger.warning(f"[{request_id}] APIError: {e.code} - {e.message}")
            return create_error_response(
                request_id=request_id,
                code=e.code,
                message=e.message,
                status_code=e.status_code,
                details=e.details,
            )

        except Exception as e:
            logger.error(
                f"[{request_id}] Unhandled error: {str(e)}\n{traceback.format_exc()}"
            )
            return create_error_response(
                request_id=request_id,
                code="INTERNAL_ERROR",
                message="Beklenmeyen bir hata olustu",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
