"""JWT token utilities."""

from datetime import datetime, timedelta
from typing import Optional
import bcrypt
import jwt
from jwt.exceptions import InvalidTokenError

from app.config import settings


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash."""
    return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())


def get_password_hash(password: str) -> str:
    """Hash a password."""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token."""
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.jwt_access_expire_minutes
        )

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm
    )
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """Decode and verify JWT token."""
    try:
        payload = jwt.decode(
            token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm]
        )
        return payload
    except InvalidTokenError:
        return None


async def is_token_blacklisted(token: str) -> bool:
    """
    Check if token has been revoked.

    Args:
        token: The JWT token to check

    Returns:
        True if token is blacklisted, False otherwise (fail-open if Redis unavailable)
    """
    try:
        from app.auth.token_blacklist import is_revoked

        return await is_revoked(token)
    except Exception as e:
        import logging

        logger = logging.getLogger(__name__)
        logger.warning(
            "Token blacklist check failed, allowing request",
            extra={"operation": "is_token_blacklisted", "error_type": type(e).__name__},
        )
        return False  # Fail-open
