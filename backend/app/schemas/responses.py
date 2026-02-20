"""Shared Pydantic response models for OpenAPI spec completeness.

These models are used across multiple API routers to ensure every endpoint
has a typed response_model, eliminating `unknown` types in the generated
TypeScript client.
"""

from pydantic import BaseModel


class MessageResponse(BaseModel):
    """Generic success/message response used by delete and simple action endpoints."""

    success: bool = True
    message: str


class PaginationInfo(BaseModel):
    """Pagination metadata returned alongside paginated list endpoints."""

    page: int
    limit: int
    total_items: int
    total_pages: int
    has_next: bool
    has_prev: bool
