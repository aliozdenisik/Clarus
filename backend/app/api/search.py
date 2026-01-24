from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from pydantic import BaseModel, Field
from typing import Optional
import sys
import os
from dotenv import load_dotenv

env_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), ".env"
)
load_dotenv(env_path)

sys.path.insert(
    0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

from app.db import get_db
from app.models import User, SearchHistory
from app.api.auth import get_current_user, check_rate_limit
from app.config import settings
from app.schemas.common import PaginatedResponse, PaginationMeta, QueryValidation
from src.ultimate_rag import UltimateRAG


router = APIRouter()

_rag_instance: Optional[UltimateRAG] = None


def get_rag() -> UltimateRAG:
    global _rag_instance
    if _rag_instance is None:
        _rag_instance = UltimateRAG()
    return _rag_instance


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=500)
    mode: str = Field(default="semantic", pattern="^(semantic|keyword)$")
    top_k: int = Field(default=10, ge=1, le=50)


class VerseResult(BaseModel):
    source: str
    reference: str
    text: str
    score: float


class SearchResponse(BaseModel):
    success: bool = True
    query: str
    results: list[VerseResult]
    total: int


class HistoryItem(BaseModel):
    id: int
    query: str
    search_type: str
    created_at: str


def _sanitize_query(query: str) -> str:
    return QueryValidation.sanitize(query)


def _validate_query(query: str) -> str:
    sanitized = _sanitize_query(query)

    if len(sanitized) < settings.query_min_length:
        raise HTTPException(
            status_code=422,
            detail=f"Sorgu en az {settings.query_min_length} karakter olmali",
        )

    if len(sanitized) > settings.query_max_length:
        raise HTTPException(
            status_code=422,
            detail=f"Sorgu en fazla {settings.query_max_length} karakter olmali",
        )

    return sanitized


@router.post("/quran", response_model=SearchResponse)
async def search_quran(
    request: SearchRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await check_rate_limit(current_user, db)

    validated_query = _validate_query(request.query)

    rag = get_rag()
    results = rag.search_quran(validated_query, top_k=request.top_k)

    history = SearchHistory(
        user_id=current_user.id, query=validated_query, search_type="search_quran"
    )
    db.add(history)
    await db.commit()

    verses = [
        VerseResult(
            source="Kuran",
            reference=f"{r.surah_name} {r.surah_id}:{r.verse_id}",
            text=r.translation,
            score=r.score,
        )
        for r in results
    ]

    return SearchResponse(query=validated_query, results=verses, total=len(verses))


@router.post("/bible", response_model=SearchResponse)
async def search_bible(
    request: SearchRequest,
    testament: Optional[str] = Query(None, pattern="^(ot|nt|apocrypha)$"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await check_rate_limit(current_user, db)

    validated_query = _validate_query(request.query)

    rag = get_rag()
    results = rag.search_bible(
        validated_query, testament=testament, top_k=request.top_k
    )

    history = SearchHistory(
        user_id=current_user.id,
        query=validated_query,
        search_type=f"search_bible_{testament or 'all'}",
    )
    db.add(history)
    await db.commit()

    verses = [
        VerseResult(
            source="Incil",
            reference=f"{getattr(r, 'book_name', '')} {getattr(r, 'chapter', '')}:{getattr(r, 'verse', '')}",
            text=getattr(r, "text", getattr(r, "translation", "")),
            score=r.score,
        )
        for r in results
    ]

    return SearchResponse(query=validated_query, results=verses, total=len(verses))


@router.get("/history")
async def get_search_history(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    search_type: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    base_query = select(SearchHistory).where(SearchHistory.user_id == current_user.id)

    if search_type:
        base_query = base_query.where(SearchHistory.search_type.contains(search_type))

    total_result = await db.execute(
        select(func.count(SearchHistory.id)).where(
            SearchHistory.user_id == current_user.id
        )
    )
    total_items = total_result.scalar() or 0

    offset = (page - 1) * limit
    result = await db.execute(
        base_query.order_by(SearchHistory.created_at.desc()).offset(offset).limit(limit)
    )
    history = result.scalars().all()

    items = [
        HistoryItem(
            id=h.id,
            query=h.query,
            search_type=h.search_type,
            created_at=h.created_at.isoformat(),
        )
        for h in history
    ]

    total_pages = (total_items + limit - 1) // limit if limit > 0 else 0

    return {
        "success": True,
        "data": [item.model_dump() for item in items],
        "pagination": {
            "page": page,
            "limit": limit,
            "total_items": total_items,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1,
        },
    }


@router.delete("/history/{history_id}")
async def delete_history_item(
    history_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(SearchHistory)
        .where(SearchHistory.id == history_id)
        .where(SearchHistory.user_id == current_user.id)
    )
    history_item = result.scalar_one_or_none()

    if not history_item:
        raise HTTPException(status_code=404, detail="Gecmis ogesi bulunamadi")

    await db.delete(history_item)
    await db.commit()

    return {"success": True, "message": "Gecmis ogesi silindi"}


@router.delete("/history")
async def clear_history(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    from sqlalchemy import delete

    await db.execute(
        delete(SearchHistory).where(SearchHistory.user_id == current_user.id)
    )
    await db.commit()

    return {"success": True, "message": "Tum gecmis temizlendi"}
