"""Compare API routes for multi-scripture comparison."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Optional
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.db import get_db
from app.models import User, SearchHistory
from app.api.auth import get_current_user, check_rate_limit
from src.comparative_rag import ComparativeRAG


router = APIRouter()

_comparative_rag: Optional[ComparativeRAG] = None


def get_comparative_rag() -> ComparativeRAG:
    """Get or create ComparativeRAG instance."""
    global _comparative_rag
    if _comparative_rag is None:
        _comparative_rag = ComparativeRAG()
    return _comparative_rag


class CompareRequest(BaseModel):
    """Compare request schema."""
    topic: str
    use_multi_agent: bool = True


class CompareResponse(BaseModel):
    """Compare response schema."""
    topic: str
    analysis: str
    sources: dict
    confidence: float
    latency_ms: int


@router.post("/", response_model=CompareResponse)
async def compare_scriptures(
    request: CompareRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Compare a topic across scriptures."""
    await check_rate_limit(current_user, db)
    
    rag = get_comparative_rag()
    
    if request.use_multi_agent:
        result = rag.compare_multi_agent(request.topic)
    else:
        result = rag.compare(request.topic)
    
    # Save to history
    history = SearchHistory(
        user_id=current_user.id,
        query=request.topic,
        search_type="compare"
    )
    db.add(history)
    await db.commit()
    
    return CompareResponse(
        topic=request.topic,
        analysis=result.get("analysis", ""),
        sources=result.get("sources", {}),
        confidence=result.get("confidence", 0.0),
        latency_ms=int(result.get("latency", 0) * 1000)
    )
