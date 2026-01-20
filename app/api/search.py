"""Search API routes."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Optional
import sys
import os
from dotenv import load_dotenv

# Load .env before importing RAG modules
load_dotenv()

# Add parent directory to path for src imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.db import get_db
from app.models import User, SearchHistory
from app.api.auth import get_current_user, check_rate_limit
from src.ultimate_rag import UltimateRAG


router = APIRouter()

# Lazy load RAG instance
_rag_instance: Optional[UltimateRAG] = None


def get_rag() -> UltimateRAG:
    """Get or create RAG instance."""
    global _rag_instance
    if _rag_instance is None:
        _rag_instance = UltimateRAG()
    return _rag_instance


class SearchRequest(BaseModel):
    """Search request schema."""
    query: str
    mode: str = "semantic"  # "semantic" or "keyword"
    top_k: int = 10


class VerseResult(BaseModel):
    """Single verse result."""
    source: str
    reference: str
    text: str
    score: float


class SearchResponse(BaseModel):
    """Search response schema."""
    query: str
    results: list[VerseResult]
    total: int


@router.post("/quran", response_model=SearchResponse)
async def search_quran(
    request: SearchRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Search in Quran."""
    await check_rate_limit(current_user, db)
    
    rag = get_rag()
    results = rag.search_quran(request.query, top_k=request.top_k)
    
    # Save to history
    history = SearchHistory(
        user_id=current_user.id,
        query=request.query,
        search_type="search_quran"
    )
    db.add(history)
    await db.commit()
    
    verses = [
        VerseResult(
            source="Kuran",
            reference=f"{r.surah_name} {r.surah_id}:{r.verse_id}",
            text=r.translation,
            score=r.score
        )
        for r in results
    ]
    
    return SearchResponse(
        query=request.query,
        results=verses,
        total=len(verses)
    )


@router.post("/bible", response_model=SearchResponse)
async def search_bible(
    request: SearchRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Search in Bible."""
    await check_rate_limit(current_user, db)
    
    rag = get_rag()
    results = rag.search_bible(request.query, top_k=request.top_k)
    
    # Save to history
    history = SearchHistory(
        user_id=current_user.id,
        query=request.query,
        search_type="search_bible"
    )
    db.add(history)
    await db.commit()
    
    verses = [
        VerseResult(
            source="İncil",
            reference=f"{getattr(r, 'book_name', '')} {getattr(r, 'chapter', '')}:{getattr(r, 'verse', '')}",
            text=getattr(r, 'text', getattr(r, 'translation', '')),
            score=r.score
        )
        for r in results
    ]
    
    return SearchResponse(
        query=request.query,
        results=verses,
        total=len(verses)
    )


@router.get("/history")
async def get_search_history(
    limit: int = Query(default=20, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user's search history."""
    from sqlalchemy import select
    
    result = await db.execute(
        select(SearchHistory)
        .where(SearchHistory.user_id == current_user.id)
        .order_by(SearchHistory.created_at.desc())
        .limit(limit)
    )
    history = result.scalars().all()
    
    return [
        {
            "id": h.id,
            "query": h.query,
            "search_type": h.search_type,
            "created_at": h.created_at.isoformat()
        }
        for h in history
    ]
