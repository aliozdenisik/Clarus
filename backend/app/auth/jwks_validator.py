"""JWKS-based JWT validator for Better Auth integration."""

import logging
from typing import Optional, Dict, Any
from datetime import datetime

from cachetools import TTLCache
from fastapi import Depends, HTTPException, Request
from jwt import PyJWKClient, decode, PyJWKClientError
from jwt.exceptions import (
    ExpiredSignatureError,
    InvalidTokenError,
    InvalidSignatureError,
)
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.db import get_db
from app.models import BetterAuthUser, UserStats

logger = logging.getLogger(__name__)


class JWKSValidator:
    """
    Validates JWT tokens using JWKS (JSON Web Key Set) from Better Auth.

    Features:
    - Fetches public keys from JWKS endpoint
    - Caches keys with TTL to minimize network requests
    - Falls back to cached keys if endpoint is unreachable
    - Validates token signature and claims
    """

    def __init__(
        self,
        jwks_url: str,
        issuer: str,
        cache_ttl: int = 3600,
        cache_maxsize: int = 100,
    ):
        """
        Initialize JWKS validator.

        Args:
            jwks_url: URL of the JWKS endpoint (e.g., http://localhost:3000/api/auth/jwks)
            issuer: Expected JWT issuer claim (e.g., http://localhost:3000)
            cache_ttl: Cache TTL in seconds (default: 3600 = 1 hour)
            cache_maxsize: Maximum number of cached keys (default: 100)
        """
        self.jwks_url = jwks_url
        self.issuer = issuer
        self.cache_ttl = cache_ttl

        # PyJWT's built-in JWKS client with caching
        self.jwks_client = PyJWKClient(
            jwks_url,
            cache_keys=True,
            max_cached_keys=cache_maxsize,
            lifespan=cache_ttl,
        )

        # Fallback cache for when JWKS endpoint is unreachable
        self.fallback_cache: TTLCache = TTLCache(maxsize=cache_maxsize, ttl=cache_ttl)

        logger.info(
            "Initialized JWKS validator",
            extra={
                "jwks_url": jwks_url,
                "issuer": issuer,
                "cache_ttl": cache_ttl,
            },
        )

    def validate_token(self, token: str) -> Dict[str, Any]:
        """
        Validate JWT token using JWKS.

        Args:
            token: JWT token string

        Returns:
            Decoded token payload as dict

        Raises:
            ValueError: Token validation failed (expired, invalid signature, etc.)
        """
        try:
            # Get signing key from JWKS
            signing_key = self.jwks_client.get_signing_key_from_jwt(token)

            # Decode and verify token
            payload = decode(
                token,
                signing_key.key,
                algorithms=["RS256"],
                issuer=self.issuer,
                options={
                    "verify_signature": True,
                    "verify_exp": True,
                    "verify_iss": True,
                },
            )

            # Cache the signing key for fallback
            kid = signing_key.key_id
            if kid:
                self.fallback_cache[kid] = signing_key

            logger.debug(
                "Token validated successfully", extra={"user_id": payload.get("sub")}
            )
            return payload

        except ExpiredSignatureError:
            logger.warning("Token expired", extra={"operation": "validate_token"})
            raise ValueError("Token has expired")

        except InvalidSignatureError:
            logger.warning(
                "Invalid token signature", extra={"operation": "validate_token"}
            )
            raise ValueError("Invalid token signature")

        except PyJWKClientError as e:
            # JWKS endpoint unreachable - try fallback cache
            logger.warning(
                "JWKS endpoint unreachable, attempting fallback to cached keys",
                extra={"operation": "validate_token", "error": str(e)},
            )
            return self._validate_with_fallback(token)

        except InvalidTokenError as e:
            logger.warning(
                "Token validation failed",
                extra={"operation": "validate_token", "error": str(e)},
            )
            raise ValueError(f"Invalid token: {str(e)}")

        except Exception as e:
            logger.error(
                "Unexpected error during token validation",
                extra={"operation": "validate_token", "error": str(e)},
            )
            raise ValueError(f"Token validation error: {str(e)}")

    def _validate_with_fallback(self, token: str) -> Dict[str, Any]:
        """
        Validate token using cached keys when JWKS endpoint is unreachable.

        Args:
            token: JWT token string

        Returns:
            Decoded token payload

        Raises:
            ValueError: No cached keys available or validation failed
        """
        if not self.fallback_cache:
            raise ValueError("JWKS endpoint unreachable and no cached keys available")

        # Try each cached key
        for kid, signing_key in self.fallback_cache.items():
            try:
                payload = decode(
                    token,
                    signing_key.key,
                    algorithms=["RS256"],
                    issuer=self.issuer,
                    options={
                        "verify_signature": True,
                        "verify_exp": True,
                        "verify_iss": True,
                    },
                )
                logger.info(
                    "Token validated using cached key",
                    extra={"kid": kid, "user_id": payload.get("sub")},
                )
                return payload
            except InvalidTokenError:
                continue

        raise ValueError("Token validation failed with all cached keys")


# Global validator instance
_validator: Optional[JWKSValidator] = None


def get_validator() -> JWKSValidator:
    """Get or create global JWKS validator instance."""
    global _validator
    if _validator is None:
        _validator = JWKSValidator(
            jwks_url=settings.better_auth_jwks_url,
            issuer=settings.better_auth_issuer,
            cache_ttl=settings.jwt_jwks_cache_ttl,
        )
    return _validator


async def get_current_user_from_jwt(request: Request) -> Dict[str, Any]:
    """
    Extract and validate JWT token from Authorization header.

    FastAPI dependency that extracts the JWT token from the Authorization header,
    validates it using JWKS, and returns the decoded payload.

    Args:
        request: FastAPI request object

    Returns:
        Decoded JWT payload containing user claims (sub, email, name, etc.)

    Raises:
        HTTPException 401: Token missing, invalid, or expired
    """
    # Extract Authorization header
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise HTTPException(
            status_code=401,
            detail="Missing Authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Parse Bearer token
    parts = auth_header.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=401,
            detail="Invalid Authorization header format. Expected: Bearer <token>",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = parts[1]

    # Validate token
    try:
        validator = get_validator()
        payload = validator.validate_token(token)
        return payload
    except ValueError as e:
        raise HTTPException(
            status_code=401,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(
    jwt_payload: Dict[str, Any] = Depends(get_current_user_from_jwt),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """
    Get current user from JWT payload and database.

    FastAPI dependency that:
    1. Validates JWT token (via get_current_user_from_jwt)
    2. Fetches full user record from BetterAuthUser table
    3. Creates user_stats record if it doesn't exist
    4. Returns user dict with id, email, name

    Args:
        jwt_payload: Decoded JWT payload from get_current_user_from_jwt
        db: Database session

    Returns:
        User dict with id, email, name, and other profile fields

    Raises:
        HTTPException 401: User not found in database
    """
    user_id = jwt_payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="Token missing 'sub' claim",
        )

    # Fetch user from database
    result = await db.execute(
        select(BetterAuthUser).where(BetterAuthUser.id == user_id)
    )
    user = result.scalar_one_or_none()

    if not user:
        logger.warning(
            "User not found in database",
            extra={"user_id": user_id, "operation": "get_current_user"},
        )
        raise HTTPException(
            status_code=401,
            detail="User not found",
        )

    # Ensure user_stats record exists
    stats_result = await db.execute(
        select(UserStats).where(UserStats.user_id == user_id)
    )
    stats = stats_result.scalar_one_or_none()

    if not stats:
        # Create user_stats record
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
            extra={"user_id": user_id, "operation": "get_current_user"},
        )

    # Return user dict
    return {
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "email_verified": user.email_verified,
        "image": user.image,
        "created_at": user.created_at,
    }
