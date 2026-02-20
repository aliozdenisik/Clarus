"""Shared error response models for OpenAPI documentation."""

from pydantic import BaseModel, Field


class ErrorDetail(BaseModel):
    code: str = Field(..., description="Machine-readable error code")
    message: str = Field(..., description="Human-readable error message")
    details: list[str] = Field(default_factory=list)


class ErrorResponse(BaseModel):
    success: bool = False
    error: ErrorDetail


class UnauthorizedResponse(BaseModel):
    detail: str = "Missing authentication. Provide either a session cookie or X-API-Key header."


class ForbiddenResponse(BaseModel):
    detail: str = "Admin access required"
