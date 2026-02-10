"""Pydantic schemas for API requests and responses."""

from app.schemas.common import (
    ErrorDetail,
    ErrorResponse,
    PaginatedResponse,
    PaginationParams,
    SuccessResponse,
)
from app.schemas.verse_lookup import (
    VerseLookupRequest,
    VerseLookupResponse,
    VerseResult,
)

__all__ = [
    "ErrorDetail",
    "ErrorResponse",
    "PaginatedResponse",
    "PaginationParams",
    "SuccessResponse",
    "VerseLookupRequest",
    "VerseLookupResponse",
    "VerseResult",
]
