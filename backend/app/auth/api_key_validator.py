"""API key authentication for CLI access."""

import hashlib
import logging
from datetime import UTC
from typing import Any

from fastapi import Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.models import BetterAuthSession, BetterAuthUser, UserStats

logger = logging.getLogger(__name__)


async def get_current_user_from_api_key(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
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

    _stats, user = row

    # Return user dict (same format as JWT auth)
    return {
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "email_verified": user.email_verified,
        "image": user.image,
        "created_at": user.created_at,
    }


async def _resolve_user_by_id(user_id: str, db: AsyncSession, operation: str) -> dict[str, Any]:
    """
    Fetch user from database and ensure user_stats exists.

    Shared helper for all auth methods (cookie, JWT, API key).

    Args:
        user_id: Better Auth user ID (from JWT sub claim or session lookup)
        db: Database session
        operation: Calling operation name for logging

    Returns:
        User dict with id, email, name, and other profile fields

    Raises:
        HTTPException 401: User not found in database
    """
    from datetime import datetime

    result = await db.execute(select(BetterAuthUser).where(BetterAuthUser.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        logger.warning(
            "User not found in database",
            extra={"user_id": user_id, "operation": operation},
        )
        raise HTTPException(status_code=401, detail="User not found")

    # Ensure user_stats exists
    stats_result = await db.execute(select(UserStats).where(UserStats.user_id == user_id))
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
            extra={"user_id": user_id, "operation": operation},
        )

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
) -> dict[str, Any]:
    """
    Flexible authentication: tries cookie, then API key.

    FastAPI dependency that:
    1. Tries Better Auth session cookie (preferred for browser clients)
    2. Tries API key from X-API-Key header
    3. If none succeed, raises HTTPException(401)

    This is the dependency that all protected endpoints should use.

    Args:
        request: FastAPI request object
        db: Database session

    Returns:
        User dict with id, email, name, and other profile fields

    Raises:
        HTTPException 401: No valid authentication method provided
    """
    # 1. Try Better Auth session cookie (preferred for browser clients)
    #    Session token is opaque (not a JWT) — validate via DB lookup.
    cookie_token = (
        request.cookies.get("better_auth.session_token")
        or request.cookies.get("better-auth.session_token")
        or request.cookies.get("__Secure-better-auth.session_token")
    )
    logger.debug(
        "Cookie auth check",
        extra={
            "cookie_token_present": bool(cookie_token),
            "operation": "get_current_user_flexible",
        },
    )
    if cookie_token:
        try:
            from datetime import datetime
            from urllib.parse import unquote

            # Better Auth cookie format: <token>.<hmac-signature> (URL-encoded)
            # The DB stores only the raw token without the signature.
            raw_token = (
                unquote(cookie_token).rsplit(".", 1)[0] if "." in unquote(cookie_token) else unquote(cookie_token)
            )

            session_result = await db.execute(select(BetterAuthSession).where(BetterAuthSession.token == raw_token))
            session = session_result.scalar_one_or_none()

            if session and session.expires_at.replace(tzinfo=UTC) > datetime.now(UTC):
                logger.debug(
                    "Authenticated via session cookie",
                    extra={
                        "user_id": session.user_id,
                        "operation": "get_current_user_flexible",
                    },
                )
                return await _resolve_user_by_id(session.user_id, db, "get_current_user_flexible")
            elif session:
                logger.warning(
                    "Session cookie expired",
                    extra={"operation": "get_current_user_flexible"},
                )
        except Exception as exc:
            # Cookie auth failed, fall through to try other methods
            logger.debug(
                "Cookie DB lookup failed: %s",
                exc,
            )
    # 2. Try API key
    api_key = request.headers.get("X-API-Key")
    if api_key:
        return await get_current_user_from_api_key(request, db)

    # No valid authentication method provided
    raise HTTPException(
        status_code=401,
        detail="Missing authentication. Provide either a session cookie or X-API-Key header.",
        headers={"WWW-Authenticate": "ApiKey"},
    )
