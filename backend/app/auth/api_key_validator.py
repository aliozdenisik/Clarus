"""API key authentication for CLI access."""

import hashlib
import logging
from typing import Dict, Any, Optional

from fastapi import HTTPException, Request, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.models import BetterAuthUser, UserStats
from app.auth.jwks_validator import get_current_user_from_jwt

logger = logging.getLogger(__name__)


async def get_current_user_from_api_key(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """
    Extract and validate API key from X-API-Key header.

    FastAPI dependency that extracts the API key from the X-API-Key header,
    hashes it, looks up the user in the database, and returns user info.

    Args:
        request: FastAPI request object
        db: Database session

    Returns:
        User dict with id, email, name, and other profile fields

    Raises:
        HTTPException 401: API key missing or invalid
    """
    # Extract X-API-Key header
    api_key = request.headers.get("X-API-Key")
    if not api_key:
        raise HTTPException(
            status_code=401,
            detail="Missing X-API-Key header",
            headers={"WWW-Authenticate": "ApiKey"},
        )

    # Hash the API key
    api_key_hash = hashlib.sha256(api_key.encode()).hexdigest()

    # Look up user_stats by api_key hash
    result = await db.execute(
        select(UserStats, BetterAuthUser)
        .join(BetterAuthUser, UserStats.user_id == BetterAuthUser.id)
        .where(UserStats.api_key == api_key_hash)
    )
    row = result.first()

    if not row:
        logger.warning(
            "Invalid API key",
            extra={"operation": "get_current_user_from_api_key"},
        )
        raise HTTPException(
            status_code=401,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "ApiKey"},
        )

    stats, user = row

    # Return user dict (same format as JWT auth)
    return {
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "email_verified": user.email_verified,
        "image": user.image,
        "created_at": user.created_at,
    }


async def get_current_user_flexible(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """
    Flexible authentication: tries JWT first, then API key.

    FastAPI dependency that:
    1. Tries JWT Bearer token from Authorization header (via get_current_user_from_jwt)
    2. If no Bearer token, tries API key from X-API-Key header
    3. If neither present, raises HTTPException(401)

    This is the dependency that all protected endpoints should use.

    Args:
        request: FastAPI request object
        db: Database session

    Returns:
        User dict with id, email, name, and other profile fields

    Raises:
        HTTPException 401: Neither JWT nor API key provided or both invalid
    """
    # Try JWT first
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.lower().startswith("bearer "):
        try:
            jwt_payload = await get_current_user_from_jwt(request)

            # Fetch user from database (same logic as jwks_validator.get_current_user)
            user_id = jwt_payload.get("sub")
            if not user_id:
                raise HTTPException(status_code=401, detail="Token missing 'sub' claim")

            result = await db.execute(
                select(BetterAuthUser).where(BetterAuthUser.id == user_id)
            )
            user = result.scalar_one_or_none()

            if not user:
                logger.warning(
                    "User not found in database",
                    extra={
                        "user_id": user_id,
                        "operation": "get_current_user_flexible",
                    },
                )
                raise HTTPException(status_code=401, detail="User not found")

            # Ensure user_stats exists
            from datetime import datetime

            stats_result = await db.execute(
                select(UserStats).where(UserStats.user_id == user_id)
            )
            stats = stats_result.scalar_one_or_none()

            if not stats:
                stats = UserStats(
                    id=f"stats_{user_id}",
                    user_id=user_id,
                    query_count_today=0,
                    last_query_date=None,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                )
                db.add(stats)
                await db.commit()
                logger.info(
                    "Created user_stats record",
                    extra={
                        "user_id": user_id,
                        "operation": "get_current_user_flexible",
                    },
                )

            return {
                "id": user.id,
                "email": user.email,
                "name": user.name,
                "email_verified": user.email_verified,
                "image": user.image,
                "created_at": user.created_at,
            }
        except HTTPException:
            # JWT auth failed, fall through to try API key
            pass

    # Try API key
    api_key = request.headers.get("X-API-Key")
    if api_key:
        return await get_current_user_from_api_key(request, db)

    # Neither JWT nor API key provided
    raise HTTPException(
        status_code=401,
        detail="Missing authentication. Provide either Authorization: Bearer <token> or X-API-Key: <key>",
        headers={"WWW-Authenticate": "Bearer, ApiKey"},
    )
