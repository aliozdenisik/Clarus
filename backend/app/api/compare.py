"""Compare API routes for multi-scripture comparison."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Optional, List, Dict
import sys
import os
from dotenv import load_dotenv

# Load .env before importing RAG modules
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


class ParagraphData(BaseModel):
    """Individual paragraph with metadata."""

    title: str
    content: str
    citations: List[str]


class VerseDetail(BaseModel):
    """Full verse metadata for rich reference display."""

    text: str  # Full verse text (max ~400 chars)
    book_name: str  # "Genesis", "Bakara", etc.
    chapter: int  # Chapter/Surah number
    verse: int  # Verse number
    source: str  # Collection: 'quran_tr', 'bible_ot', 'bible_nt', 'bible_apocrypha'
    translation: (
        str  # "Diyanet Isleri Baskanligi" or "King James Version with Apocrypha"
    )


class CompareResponse(BaseModel):
    """Compare response schema - rich format for frontend."""

    topic: str
    # Full formatted essay (markdown)
    essay: str
    # Individual paragraphs for structured display
    paragraphs: List[ParagraphData]
    # All citations grouped by source
    citations: Dict[str, List[str]]
    # Statistics
    confidence: float
    total_verses: int
    total_citations: int
    latency_ms: int
    # Rich verse metadata for citations
    verse_details: Optional[Dict[str, VerseDetail]] = None


@router.post("/", response_model=CompareResponse)
async def compare_scriptures(
    request: CompareRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Compare a topic across scriptures (Quran, Old Testament, New Testament, Apocrypha).

    Returns structured multi-agent analysis with 5 paragraphs:
    - Old Testament perspective
    - New Testament perspective
    - Apocrypha perspective
    - Quran perspective
    - Comparative synthesis
    """
    import time

    start_time = time.time()

    await check_rate_limit(current_user, db)

    rag = get_comparative_rag()

    if request.use_multi_agent:
        result = rag.compare_multi_agent(request.topic)

        # Build structured paragraphs from MultiAgentAnswer
        paragraphs = []

        if result.old_testament_commentary:
            paragraphs.append(
                ParagraphData(
                    title="Eski Ahit (Old Testament)",
                    content=result.old_testament_commentary,
                    citations=result.citations.get("old_testament", []),
                )
            )

        if result.new_testament_commentary:
            paragraphs.append(
                ParagraphData(
                    title="Yeni Ahit (New Testament)",
                    content=result.new_testament_commentary,
                    citations=result.citations.get("new_testament", []),
                )
            )

        if result.apocrypha_commentary:
            paragraphs.append(
                ParagraphData(
                    title="Apokrifa (Apocrypha)",
                    content=result.apocrypha_commentary,
                    citations=result.citations.get("apocrypha", []),
                )
            )

        if result.quran_commentary:
            paragraphs.append(
                ParagraphData(
                    title="Kuran-ı Kerim",
                    content=result.quran_commentary,
                    citations=result.citations.get("quran", []),
                )
            )

        if result.synthesis:
            paragraphs.append(
                ParagraphData(
                    title="Karşılaştırmalı Değerlendirme",
                    content=result.synthesis,
                    citations=[],
                )
            )

        # Calculate totals
        total_citations = sum(len(refs) for refs in result.citations.values())
        total_verses = sum(result.verses_provided.values())

        latency_ms = int((time.time() - start_time) * 1000)

        # Save to history
        history = SearchHistory(
            user_id=current_user.id,
            query=request.topic,
            search_type="compare_multi_agent",
        )
        db.add(history)
        await db.commit()

        return CompareResponse(
            topic=request.topic,
            essay=result.to_essay(),
            paragraphs=paragraphs,
            citations=result.citations,
            confidence=result.confidence,
            total_verses=total_verses,
            total_citations=total_citations,
            latency_ms=latency_ms,
        )
    else:
        # Single essay mode (ComparativeAnswer)
        result = rag.compare(request.topic)

        latency_ms = int((time.time() - start_time) * 1000)

        # Save to history
        history = SearchHistory(
            user_id=current_user.id, query=request.topic, search_type="compare"
        )
        db.add(history)
        await db.commit()

        # Build single paragraph response
        paragraphs = [
            ParagraphData(
                title="Karşılaştırmalı Analiz",
                content=result.essay,
                citations=result.all_references,
            )
        ]

        return CompareResponse(
            topic=request.topic,
            essay=result.essay,
            paragraphs=paragraphs,
            citations={
                "quran": result.quran_references,
                "bible": result.bible_references,
            },
            confidence=result.confidence,
            total_verses=result.verses_provided
            if hasattr(result, "verses_provided")
            else 80,
            total_citations=len(result.all_references),
            latency_ms=latency_ms,
        )
