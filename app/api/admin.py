"""Admin API routes for dashboard and user management."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime, timedelta
import sys
import os

from app.db import get_db
from app.models import User, SearchHistory
from app.api.auth import get_current_user

router = APIRouter()


def check_admin(user: User):
    """Check if user has admin privileges."""
    # For now, allow test@example.com and admin@hollysearch.com
    admin_emails = ['admin@hollysearch.com', 'test@example.com']
    if user.email not in admin_emails:
        raise HTTPException(status_code=403, detail="Admin access required")
    return True


@router.get("/stats")
async def get_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get admin dashboard statistics."""
    check_admin(current_user)
    
    # Total users
    total_users = await db.scalar(select(func.count(User.id)))
    
    # Total searches
    total_searches = await db.scalar(select(func.count(SearchHistory.id)))
    
    # Today's searches
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    today_searches = await db.scalar(
        select(func.count(SearchHistory.id)).where(SearchHistory.created_at >= today)
    )
    
    # Active users (searched in last 7 days)
    week_ago = datetime.utcnow() - timedelta(days=7)
    active_users = await db.scalar(
        select(func.count(func.distinct(SearchHistory.user_id)))
        .where(SearchHistory.created_at >= week_ago)
    )
    
    return {
        "totalUsers": total_users or 0,
        "totalSearches": total_searches or 0,
        "todaySearches": today_searches or 0,
        "activeUsers": active_users or 0
    }


@router.get("/users")
async def get_users(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all users for admin dashboard."""
    check_admin(current_user)
    
    result = await db.execute(
        select(User).order_by(User.created_at.desc()).limit(100)
    )
    users = result.scalars().all()
    
    return [
        {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "created_at": user.created_at.isoformat() if user.created_at else None
        }
        for user in users
    ]


@router.get("/system")
async def get_system_info(
    current_user: User = Depends(get_current_user)
):
    """Get system information for admin dashboard."""
    check_admin(current_user)
    
    import platform
    
    # Check Qdrant collections
    try:
        import httpx
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:6333/collections", timeout=5.0)
            collections_data = response.json()
            collections_count = len(collections_data.get("result", {}).get("collections", []))
    except:
        collections_count = 0
    
    return {
        "python_version": platform.python_version(),
        "platform": platform.system(),
        "collections": collections_count,
        "api_status": "running"
    }
