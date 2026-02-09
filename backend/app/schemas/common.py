"""Common schemas for standardized API responses."""

import html
from datetime import datetime
from typing import Generic, Literal, Optional, TypeVar

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")

# Valid Quran translators (imported from tanzil_loader)
VALID_TRANSLATORS = {
    "diyanet",
    "yazir",
    "ates",
    "bulac",
    "ozturk",
    "vakfi",
    "yildirim",
    "yuksel",
}
DEFAULT_TRANSLATOR = "diyanet"

# Type alias for translator validation
TranslatorType = Literal[
    "diyanet", "yazir", "ates", "bulac", "ozturk", "vakfi", "yildirim", "yuksel"
]


class ErrorDetail(BaseModel):
    """Detailed error information."""

    field: Optional[str] = Field(None, description="Field that caused the error")
    message: str = Field(..., description="Human-readable error message")
    code: Optional[str] = Field(None, description="Machine-readable error code")


class ErrorResponse(BaseModel):
    """Standardized error response for all API endpoints.

    Example:
    {
        "success": false,
        "error": {
            "code": "VALIDATION_ERROR",
            "message": "Query cannot be empty",
            "details": [
                {"field": "query", "message": "String must not be empty", "code": "string_empty"}
            ]
        },
        "request_id": "req_abc123",
        "timestamp": "2026-01-24T10:30:00Z"
    }
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": False,
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Query is too long",
                    "details": [{"field": "query", "message": "Max 500 characters allowed"}],
                },
                "request_id": "req_abc123",
                "timestamp": "2026-01-24T10:30:00Z",
            }
        }
    )

    success: bool = Field(default=False, description="Always false for errors")
    error: dict = Field(..., description="Error information")
    request_id: Optional[str] = Field(None, description="Request ID for tracing")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Error timestamp")


class SuccessResponse(BaseModel, Generic[T]):
    """Standardized success response wrapper.

    Example:
    {
        "success": true,
        "data": {...},
        "request_id": "req_abc123"
    }
    """

    success: bool = Field(default=True, description="Always true for success")
    data: T = Field(..., description="Response data")
    request_id: Optional[str] = Field(None, description="Request ID for tracing")


class PaginationParams(BaseModel):
    """Pagination parameters for list endpoints."""

    page: int = Field(default=1, ge=1, description="Page number (1-indexed)")
    limit: int = Field(default=20, ge=1, le=100, description="Items per page (max 100)")

    @property
    def offset(self) -> int:
        """Calculate offset from page and limit."""
        return (self.page - 1) * self.limit


class PaginationMeta(BaseModel):
    """Pagination metadata for responses."""

    page: int = Field(..., description="Current page number")
    limit: int = Field(..., description="Items per page")
    total_items: int = Field(..., description="Total number of items")
    total_pages: int = Field(..., description="Total number of pages")
    has_next: bool = Field(..., description="Whether there is a next page")
    has_prev: bool = Field(..., description="Whether there is a previous page")


class PaginatedResponse(BaseModel, Generic[T]):
    """Standardized paginated response.

    Example:
    {
        "success": true,
        "data": [...],
        "pagination": {
            "page": 1,
            "limit": 20,
            "total_items": 150,
            "total_pages": 8,
            "has_next": true,
            "has_prev": false
        }
    }
    """

    success: bool = Field(default=True)
    data: list[T] = Field(..., description="List of items")
    pagination: PaginationMeta = Field(..., description="Pagination metadata")
    request_id: Optional[str] = Field(None, description="Request ID for tracing")

    @classmethod
    def create(
        cls,
        items: list[T],
        page: int,
        limit: int,
        total_items: int,
        request_id: Optional[str] = None,
    ) -> "PaginatedResponse[T]":
        """Factory method to create paginated response."""
        total_pages = (total_items + limit - 1) // limit if limit > 0 else 0
        return cls(
            data=items,
            pagination=PaginationMeta(
                page=page,
                limit=limit,
                total_items=total_items,
                total_pages=total_pages,
                has_next=page < total_pages,
                has_prev=page > 1,
            ),
            request_id=request_id,
        )


class QueryValidation(BaseModel):
    """Validated query input with sanitization."""

    query: str = Field(
        ..., min_length=1, max_length=500, description="Search query (1-500 characters)"
    )

    @classmethod
    def sanitize(cls, query: str) -> str:
        if not query:
            return query
        return html.escape(query).strip()
