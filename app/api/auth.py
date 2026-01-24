from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
from pydantic import BaseModel
import httpx
import secrets

from app.db import get_db
from app.models import User
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

    user_id_str = payload.get("sub")
    if user_id_str is None:
        raise credentials_exception

    user_id = int(user_id_str)
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if user is None:
        raise credentials_exception

    return user


async def check_rate_limit(user: User, db: AsyncSession) -> None:
    if not settings.rate_limit_enabled:
        return

    now = datetime.utcnow()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

    if user.last_query_date is None or user.last_query_date < today_start:
        user.query_count_today = 0
        user.last_query_date = now

    if user.query_count_today >= settings.rate_limit_per_day:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Gunluk sorgu limitine ulastiniz ({settings.rate_limit_per_day}/gun)",
        )

    user.query_count_today += 1
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


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return UserResponse.model_validate(current_user)


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
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    current_user.refresh_token = None
    await db.commit()
    return {"success": True, "message": "Cikis yapildi"}


@router.get("/rate-limit")
async def get_rate_limit_status(current_user: User = Depends(get_current_user)):
    rate_info = await get_user_rate_limit_info(current_user.id)
    return {"success": True, "data": rate_info}
