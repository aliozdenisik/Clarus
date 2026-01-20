"""Compare API routes for multi-scripture comparison."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Optional
import sys
import os
from dotenv import load_dotenv

# Load .env before importing RAG modules
load_dotenv()

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
    import time
    start_time = time.time()
    
    await check_rate_limit(current_user, db)
    
    rag = get_comparative_rag()
    
    if request.use_multi_agent:
        result = rag.compare_multi_agent(request.topic)
    else:
        result = rag.compare(request.topic)
    
    latency_ms = int((time.time() - start_time) * 1000)
    
    # Save to history
    history = SearchHistory(
        user_id=current_user.id,
        query=request.topic,
        search_type="compare"
    )
    db.add(history)
    await db.commit()
    
    # Handle both dataclass (ComparativeAnswer) and MultiAgentAnswer response types
    if hasattr(result, 'essay'):
        # ComparativeAnswer dataclass
        return CompareResponse(
            topic=request.topic,
            analysis=result.essay,
            sources={
                "quran": result.quran_references,
                "bible": result.bible_references
            },
            confidence=result.confidence,
            latency_ms=latency_ms
        )
    else:
        # MultiAgentAnswer dataclass
        return CompareResponse(
            topic=request.topic,
            analysis=result.full_text if hasattr(result, 'full_text') else str(result),
            sources={},
            confidence=result.confidence if hasattr(result, 'confidence') else 0.9,
            latency_ms=latency_ms
        )
