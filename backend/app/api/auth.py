from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
from pydantic import BaseModel
import httpx
import secrets
import hashlib

from app.db import get_db
from app.models import User, BetterAuthUser, UserStats
from app.config import settings
from app.auth import (
    verify_password,
    get_password_hash,
    create_access_token,
    decode_access_token,
)
from app.auth.schemas import (
    UserCreate,
    UserLogin,
    UserResponse,
    GoogleAuthRequest,
)
from app.auth.jwks_validator import get_current_user_from_jwt, get_validator
from app.auth.api_key_validator import get_current_user_flexible
from app.middleware.rate_limit import get_user_rate_limit_info


router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse


class ApiKeyResponse(BaseModel):
    api_key: str
    created_at: datetime
    message: str = "Store this key securely. It will not be shown again."


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Gecersiz kimlik bilgileri",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception

    # Check if token is blacklisted
    from app.auth import is_token_blacklisted

    if await is_token_blacklisted(token):
        raise credentials_exception

    user_id_str = payload.get("sub")
    if user_id_str is None:
        raise credentials_exception

    user_id = int(user_id_str)
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if user is None:
        raise credentials_exception

    return user


async def get_current_user_from_token(token: str, db: AsyncSession) -> User:
    """Get user from token string directly (for SSE endpoints that can't use headers)."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Gecersiz kimlik bilgileri",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception

    # Check if token is blacklisted
    from app.auth import is_token_blacklisted

    if await is_token_blacklisted(token):
        raise credentials_exception

    user_id_str = payload.get("sub")
    if user_id_str is None:
        raise credentials_exception

    user_id = int(user_id_str)
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if user is None:
        raise credentials_exception

    return user


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


@router.post("/register", response_model=TokenResponse)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == user_data.email))
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bu e-posta adresi zaten kayitli",
        )

    refresh_token = secrets.token_urlsafe(32)
    user = User(
        email=user_data.email,
        hashed_password=get_password_hash(user_data.password),
        name=user_data.name,
        refresh_token=refresh_token,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    access_token = create_access_token(data={"sub": str(user.id)})

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.jwt_access_expire_minutes * 60,
        user=UserResponse.model_validate(user),
    )


@router.post("/login", response_model=TokenResponse)
async def login(user_data: UserLogin, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == user_data.email))
    user = result.scalar_one_or_none()

    if not user or not user.hashed_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Gecersiz e-posta veya sifre",
        )

    if not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Gecersiz e-posta veya sifre",
        )

    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = secrets.token_urlsafe(32)

    user.refresh_token = refresh_token
    await db.commit()

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.jwt_access_expire_minutes * 60,
        user=UserResponse.model_validate(user),
    )


@router.post("/google", response_model=TokenResponse)
async def google_auth(auth_data: GoogleAuthRequest, db: AsyncSession = Depends(get_db)):
    async with httpx.AsyncClient() as client:
        token_response = await client.post(
            "https://oauth2.googleapis.com/token",
            data={
                "code": auth_data.code,
                "client_id": settings.google_client_id,
                "client_secret": settings.google_client_secret,
                "redirect_uri": auth_data.redirect_uri or settings.google_redirect_uri,
                "grant_type": "authorization_code",
            },
        )

        if token_response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Google kimlik dogrulama basarisiz",
            )

        tokens = token_response.json()

        userinfo_response = await client.get(
            "https://www.googleapis.com/oauth2/v2/userinfo",
            headers={"Authorization": f"Bearer {tokens['access_token']}"},
        )

        if userinfo_response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Google kullanici bilgileri alinamadi",
            )

        google_user = userinfo_response.json()

    result = await db.execute(select(User).where(User.google_id == google_user["id"]))
    user = result.scalar_one_or_none()

    refresh_token = secrets.token_urlsafe(32)

    if not user:
        result = await db.execute(
            select(User).where(User.email == google_user["email"])
        )
        user = result.scalar_one_or_none()

        if user:
            user.google_id = google_user["id"]
            user.refresh_token = refresh_token
        else:
            user = User(
                email=google_user["email"],
                name=google_user.get("name", google_user["email"]),
                google_id=google_user["id"],
                refresh_token=refresh_token,
            )
            db.add(user)

        await db.commit()
        await db.refresh(user)
    else:
        user.refresh_token = refresh_token
        await db.commit()

    access_token = create_access_token(data={"sub": str(user.id)})

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.jwt_access_expire_minutes * 60,
        user=UserResponse.model_validate(user),
    )


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


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    request: RefreshTokenRequest, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(User).where(User.refresh_token == request.refresh_token)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Gecersiz refresh token",
        )

    new_access_token = create_access_token(data={"sub": str(user.id)})
    new_refresh_token = secrets.token_urlsafe(32)

    user.refresh_token = new_refresh_token
    await db.commit()

    return TokenResponse(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
        expires_in=settings.jwt_access_expire_minutes * 60,
        user=UserResponse.model_validate(user),
    )


@router.post("/logout")
async def logout(
    request: Request,
    current_user: dict = Depends(get_current_user_flexible),
    db: AsyncSession = Depends(get_db),
):
    """
    Logout (revoke JWT token).
    Note: Better Auth sessions are managed by the auth server, not here.
    We only revoke the JWT token in our blacklist.
    """
    # Revoke the JWT token
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        token = auth_header[7:]
        # Validate Better Auth JWT and extract exp
        try:
            validator = get_validator()
            payload = validator.validate_token(token)
            if payload and "exp" in payload:
                from datetime import datetime
                from app.auth.token_blacklist import revoke_token

                expires_at = datetime.utcfromtimestamp(payload["exp"])
                await revoke_token(token, expires_at)
        except Exception:
            pass  # Token already invalid or expired

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
