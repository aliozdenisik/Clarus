from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime, timedelta
import platform
import httpx

from app.db import get_db
from app.models import User, SearchHistory
from app.api.auth import get_current_user

router = APIRouter()

ADMIN_EMAILS = ["admin@hollysearch.com", "test@example.com"]


def check_admin(user: User):
    if user.email not in ADMIN_EMAILS:
        raise HTTPException(status_code=403, detail="Admin access required")
    return True


@router.get("/stats")
async def get_stats(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    check_admin(current_user)

    total_users = await db.scalar(select(func.count(User.id)))
    total_searches = await db.scalar(select(func.count(SearchHistory.id)))

    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    today_searches = await db.scalar(
        select(func.count(SearchHistory.id)).where(SearchHistory.created_at >= today)
    )

    week_ago = datetime.utcnow() - timedelta(days=7)
    active_users = await db.scalar(
        select(func.count(func.distinct(SearchHistory.user_id))).where(
            SearchHistory.created_at >= week_ago
        )
    )

    search_type_counts_result = await db.execute(
        select(SearchHistory.search_type, func.count(SearchHistory.id)).group_by(
            SearchHistory.search_type
        )
    )
    search_type_counts = {row[0]: row[1] for row in search_type_counts_result.all()}

    return {
        "success": True,
        "data": {
            "total_users": total_users or 0,
            "total_searches": total_searches or 0,
            "today_searches": today_searches or 0,
            "active_users_7d": active_users or 0,
            "search_by_type": search_type_counts,
        },
    }


@router.get("/users")
async def get_users(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    check_admin(current_user)

    total_result = await db.execute(select(func.count(User.id)))
    total_items = total_result.scalar() or 0

    offset = (page - 1) * limit
    result = await db.execute(
        select(User).order_by(User.created_at.desc()).offset(offset).limit(limit)
    )
    users = result.scalars().all()

    user_search_counts = {}
    for user in users:
        count_result = await db.execute(
            select(func.count(SearchHistory.id)).where(SearchHistory.user_id == user.id)
        )
        user_search_counts[user.id] = count_result.scalar() or 0

    items = [
        {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "search_count": user_search_counts.get(user.id, 0),
            "has_google": user.google_id is not None,
        }
        for user in users
    ]

    total_pages = (total_items + limit - 1) // limit if limit > 0 else 0

    return {
        "success": True,
        "data": items,
        "pagination": {
            "page": page,
            "limit": limit,
            "total_items": total_items,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1,
        },
    }


@router.get("/system")
async def get_system_info(current_user: User = Depends(get_current_user)):
    check_admin(current_user)

    collections_count = 0
    qdrant_status = "unknown"

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "http://localhost:6333/collections", timeout=5.0
            )
            if response.status_code == 200:
                collections_data = response.json()
                collections_count = len(
                    collections_data.get("result", {}).get("collections", [])
                )
                qdrant_status = "connected"
            else:
                qdrant_status = "error"
    except httpx.RequestError:
        qdrant_status = "disconnected"

    return {
        "success": True,
        "data": {
            "python_version": platform.python_version(),
            "platform": platform.system(),
            "qdrant_status": qdrant_status,
            "collections_count": collections_count,
            "api_status": "running",
        },
    }


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    check_admin(current_user)

    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Kendi hesabinizi silemezsiniz")

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="Kullanici bulunamadi")

    await db.delete(user)
    await db.commit()

    return {"success": True, "message": "Kullanici silindi"}
