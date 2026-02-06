from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
from pydantic import BaseModel
import secrets
import hashlib

from app.db import get_db
from app.models import BetterAuthUser, UserStats
from app.config import settings
from app.auth.jwks_validator import get_current_user_from_jwt
from app.auth.api_key_validator import get_current_user_flexible
from app.middleware.rate_limit import get_user_rate_limit_info


router = APIRouter()


class ApiKeyResponse(BaseModel):
    api_key: str
    created_at: datetime
    message: str = "Store this key securely. It will not be shown again."


async def check_rate_limit(user: dict, db: AsyncSession) -> None:
    """
    Check rate limit for user (works with dict from get_current_user_flexible).
    Queries UserStats table for Better Auth users.
    """
    if not settings.rate_limit_enabled:
        return

    user_id = user["id"]  # Extract user ID from dict
    now = datetime.utcnow()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

    # Query UserStats for this user
    from app.models import UserStats

    result = await db.execute(select(UserStats).where(UserStats.user_id == user_id))
    stats = result.scalar_one_or_none()

    if not stats:
        # Create UserStats if it doesn't exist (should have been created by get_current_user_flexible)
        stats = UserStats(
            id=f"stats_{user_id}",
            user_id=user_id,
            query_count_today=0,
            last_query_date=None,
            created_at=now,
            updated_at=now,
        )
        db.add(stats)
        await db.commit()
        await db.refresh(stats)

    # Reset count if new day
    if stats.last_query_date is None or stats.last_query_date < today_start:
        stats.query_count_today = 0
        stats.last_query_date = now

    # Check limit
    if stats.query_count_today >= settings.rate_limit_per_day:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Gunluk sorgu limitine ulastiniz ({settings.rate_limit_per_day}/gun)",
        )

    # Increment count
    stats.query_count_today += 1
    stats.updated_at = now
    await db.commit()


@router.get("/me")
async def get_me(current_user: dict = Depends(get_current_user_flexible)):
    """Get current user info (from Better Auth JWT or API key)."""
    return {
        "id": current_user["id"],
        "email": current_user["email"],
        "name": current_user.get("name"),
        "email_verified": current_user.get("email_verified", False),
        "image": current_user.get("image"),
        "created_at": current_user.get("created_at"),
    }


@router.post("/logout")
async def logout(
    current_user: dict = Depends(get_current_user_flexible),
):
    """
    Logout endpoint.
    Note: Better Auth sessions are managed by the auth server.
    This endpoint just returns success for client-side cleanup.
    """
    return {"success": True, "message": "Cikis yapildi"}


@router.get("/rate-limit")
async def get_rate_limit_status(
    current_user: dict = Depends(get_current_user_flexible),
):
    """Get current user's rate limit status."""
    rate_info = await get_user_rate_limit_info(current_user["id"])
    return {"success": True, "data": rate_info}


@router.post("/api-key", response_model=ApiKeyResponse)
async def generate_api_key(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Generate a new API key for CLI access.

    Requires JWT authentication. Generates a 64-character URL-safe random token,
    stores its SHA256 hash in the database, and returns the raw key.
    The key is shown only once - users must store it securely.

    Maximum 1 active API key per user (overwrites previous key).

    Args:
        request: FastAPI request (for JWT extraction)
        db: Database session

    Returns:
        ApiKeyResponse with the raw API key and creation timestamp

    Raises:
        HTTPException 401: Missing or invalid JWT token
    """
    # Authenticate with JWT (from jwks_validator)
    jwt_payload = await get_current_user_from_jwt(request)
    user_id = jwt_payload.get("sub")

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token missing 'sub' claim",
        )

    # Verify user exists
    result = await db.execute(
        select(BetterAuthUser).where(BetterAuthUser.id == user_id)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    # Generate 64-character API key (secrets.token_urlsafe(48) produces ~64 chars)
    raw_api_key = secrets.token_urlsafe(48)

    # Hash the API key with SHA256
    api_key_hash = hashlib.sha256(raw_api_key.encode()).hexdigest()

    # Update or create user_stats record
    stats_result = await db.execute(
        select(UserStats).where(UserStats.user_id == user_id)
    )
    stats = stats_result.scalar_one_or_none()

    now = datetime.utcnow()

    if stats:
        # Update existing record (overwrites previous API key)
        stats.api_key = api_key_hash
        stats.api_key_created_at = now
        stats.updated_at = now
    else:
        # Create new user_stats record
        stats = UserStats(
            id=f"stats_{user_id}",
            user_id=user_id,
            query_count_today=0,
            last_query_date=None,
            api_key=api_key_hash,
            api_key_created_at=now,
            created_at=now,
            updated_at=now,
        )
        db.add(stats)

    await db.commit()

    return ApiKeyResponse(
        api_key=raw_api_key,
        created_at=now,
    )
