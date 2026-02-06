"""Pydantic schemas for API requests and responses."""

from app.schemas.common import (
    ErrorResponse,
    ErrorDetail,
    PaginatedResponse,
    PaginationParams,
    SuccessResponse,
)
from app.schemas.verse_lookup import (
    VerseLookupRequest,
    VerseResult,
    VerseLookupResponse,
)

__all__ = [
    "ErrorResponse",
    "ErrorDetail",
    "PaginatedResponse",
    "PaginationParams",
    "SuccessResponse",
    "VerseLookupRequest",
    "VerseResult",
    "VerseLookupResponse",
]
