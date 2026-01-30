"""Compare API routes for multi-scripture comparison."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Optional, List, Dict, Tuple
import sys
import os
import time as time_module
from dotenv import load_dotenv

from app.logging_config import get_logger, log_performance

logger = get_logger(__name__)

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
from src.search import SearchResult, BibleSearchResult
from src.citation_sanitizer import sanitize_citations
from src.query_translator import QueryTranslator, TranslationError


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

    model_config = {"ser_json_timedelta": "iso8601"}  # Force all fields to serialize

    text: str  # Full verse text (max ~400 chars)
    book_name: str  # "Genesis", "Bakara", etc.
    chapter: int  # Chapter/Surah number
    verse: int  # Verse number
    source: str  # Collection: 'quran_tr', 'bible_ot', 'bible_nt', 'bible_apocrypha'
    translation: (
        str  # "Diyanet Isleri Baskanligi" or "King James Version with Apocrypha"
    )
    book_nr: int | None = None  # Bible book number (None for Quran)

    # Quran-specific fields (optional for backward compatibility)
    surah_id: int | None = None  # Quran surah ID (required for Quran URLs)
    surah_name: str | None = None  # Quran surah name
    verse_id: int | None = None  # Quran verse ID


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
    confidence_breakdown: Optional[dict] = None
    total_verses: int
    total_citations: int
    latency_ms: int
    # Rich verse metadata for citations
    verse_details: Optional[Dict[str, VerseDetail]] = None
    # Language metadata (for multilingual support)
    detected_language: Optional[str] = None
    response_language: Optional[str] = None


def extract_quran_verse_detail(result: SearchResult) -> Tuple[str, VerseDetail]:
    """Extract citation reference and verse detail from a Quran SearchResult."""
    # Citation format: "SurahName:VerseId" e.g., "Bakara:153" (NO BRACKETS!)
    reference = f"{result.surah_name}:{result.verse_id}"

    return reference, VerseDetail(
        text=result.translation[:400],  # Truncate long verses
        book_name=result.surah_name,
        chapter=result.surah_id,
        verse=result.verse_id,
        source="quran_tr",
        translation="Diyanet Isleri Baskanligi",
        surah_id=result.surah_id,  # NEW: Required for Quran URL construction
        surah_name=result.surah_name,  # NEW: Required for Quran URL construction
        verse_id=result.verse_id,  # NEW: Required for Quran URL construction
    )


def extract_bible_verse_detail(
    result: BibleSearchResult, source: str
) -> Tuple[str, VerseDetail]:
    """Extract citation reference and verse detail from a Bible BibleSearchResult."""
    # Citation format: "BookName Chapter:Verse" e.g., "Genesis 1:1" (NO BRACKETS!)
    reference = f"{result.book_name} {result.chapter}:{result.verse}"

    return reference, VerseDetail(
        text=result.text[:400],  # Truncate long verses
        book_name=result.book_name,
        chapter=result.chapter,
        verse=result.verse,
        source=source,
        translation="King James Version with Apocrypha",
        book_nr=result.book_id,
    )


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
    start_time = time_module.perf_counter()
    logger.info(
        "Compare request received",
        extra={
            "topic": request.topic[:50],
            "use_multi_agent": request.use_multi_agent,
            "user_id": current_user.id,
        },
    )

    await check_rate_limit(current_user, db)

    rag = get_comparative_rag()
    translator = QueryTranslator()

    if request.use_multi_agent:
        # Step 1: Get search results directly (bypass compare_multi_agent)
        search_result = rag.search_all(request.topic)

        # Step 2: Build verse_details from search results
        verse_details: Dict[str, VerseDetail] = {}

        for r in search_result.quran:
            ref, detail = extract_quran_verse_detail(r)
            if ref not in verse_details:  # Deduplicate
                verse_details[ref] = detail

        for r in search_result.ot:
            ref, detail = extract_bible_verse_detail(r, "bible_ot")
            if ref not in verse_details:
                verse_details[ref] = detail

        for r in search_result.nt:
            ref, detail = extract_bible_verse_detail(r, "bible_nt")
            if ref not in verse_details:
                verse_details[ref] = detail

        for r in search_result.apocrypha:
            ref, detail = extract_bible_verse_detail(r, "bible_apocrypha")
            if ref not in verse_details:
                verse_details[ref] = detail

        # Step 3: Generate multi-agent answer using search results
        result = rag.multi_agent_generator.generate(
            query=request.topic,
            quran_verses=search_result.quran,
            ot_verses=search_result.ot,
            nt_verses=search_result.nt,
            apocrypha_verses=search_result.apocrypha,
        )

        # Sanitize agent output (defense-in-depth against malformed citations)
        result.old_testament_commentary = sanitize_citations(
            result.old_testament_commentary
        )
        result.new_testament_commentary = sanitize_citations(
            result.new_testament_commentary
        )
        result.apocrypha_commentary = sanitize_citations(result.apocrypha_commentary)
        result.quran_commentary = sanitize_citations(result.quran_commentary)
        result.synthesis = sanitize_citations(result.synthesis)

        # Sanitize citations dict values
        for source_key, citation_list in result.citations.items():
            result.citations[source_key] = [
                sanitize_citations(c) for c in citation_list
            ]

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

        latency_ms = int((time_module.perf_counter() - start_time) * 1000)

        # Log performance with agent breakdown
        log_performance(
            logger,
            "compare_multi_agent",
            latency_ms,
            agents=5,
            total_verses=total_verses,
            total_citations=total_citations,
            confidence=result.confidence,
        )

        # Save to history
        history = SearchHistory(
            user_id=current_user.id,
            query=request.topic,
            search_type="compare_multi_agent",
            result_count=total_verses if total_verses else 0,
        )
        db.add(history)
        await db.commit()

        # Response translation: translate essay + paragraphs for non-Turkish/English users
        detected_language = search_result.search_stats.get("detected_language")
        essay_text = result.to_essay()
        response_language = "tr"  # Default: essay is in Turkish

        if detected_language and detected_language not in ("tr", "en"):
            try:
                logger.info(
                    "Translating compare response",
                    extra={
                        "detected_language": detected_language,
                        "paragraph_count": len(paragraphs),
                    },
                )
                # Translate full essay (one LLM call)
                essay_text = translator.translate_response(
                    essay_text,
                    target_lang=detected_language,
                    preserve_citations=True,
                )
                # Translate each paragraph's content and title
                for para in paragraphs:
                    para.content = translator.translate_response(
                        para.content,
                        target_lang=detected_language,
                        preserve_citations=True,
                    )
                    para.title = translator.translate_response(
                        para.title, target_lang=detected_language
                    )
                response_language = detected_language
            except TranslationError:
                logger.error(
                    "Response translation failed, returning original text",
                    exc_info=True,
                )
                # Graceful degradation: return untranslated essay

        return CompareResponse(
            topic=request.topic,
            essay=essay_text,
            paragraphs=paragraphs,
            citations=result.citations,
            confidence=result.confidence,
            confidence_breakdown=getattr(result, "confidence_breakdown", None),
            total_verses=total_verses,
            total_citations=total_citations,
            latency_ms=latency_ms,
            verse_details=verse_details,
            detected_language=detected_language,
            response_language=response_language,
        )
    else:
        # Single essay mode (ComparativeAnswer)
        result = rag.compare(request.topic)

        # Sanitize essay output
        result.essay = sanitize_citations(result.essay)

        # Sanitize references
        result.quran_references = [
            sanitize_citations(r) for r in result.quran_references
        ]
        result.bible_references = [
            sanitize_citations(r) for r in result.bible_references
        ]
        result.all_references = [sanitize_citations(r) for r in result.all_references]

        latency_ms = int((time_module.perf_counter() - start_time) * 1000)

        total_citations_count = len(result.all_references)
        verses_count = (
            result.verses_provided if hasattr(result, "verses_provided") else 80
        )

        # Log performance for single-agent mode
        log_performance(
            logger,
            "compare_single",
            latency_ms,
            agents=1,
            total_citations=total_citations_count,
            confidence=result.confidence,
        )

        # Save to history
        history = SearchHistory(
            user_id=current_user.id,
            query=request.topic,
            search_type="compare",
            result_count=total_citations_count,
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

        # Response translation for single-essay mode
        detected_language = getattr(rag, "_last_detected_language", None)
        essay_text = result.essay
        response_language = "tr"

        if detected_language and detected_language not in ("tr", "en"):
            try:
                essay_text = translator.translate_response(
                    essay_text,
                    target_lang=detected_language,
                    preserve_citations=True,
                )
                for para in paragraphs:
                    para.content = translator.translate_response(
                        para.content,
                        target_lang=detected_language,
                        preserve_citations=True,
                    )
                    para.title = translator.translate_response(
                        para.title, target_lang=detected_language
                    )
                response_language = detected_language
            except TranslationError:
                logger.error(
                    "Response translation failed in single-essay mode",
                    exc_info=True,
                )

        return CompareResponse(
            topic=request.topic,
            essay=essay_text,
            paragraphs=paragraphs,
            citations={
                "quran": result.quran_references,
                "bible": result.bible_references,
            },
            confidence=result.confidence,
            confidence_breakdown=getattr(result, "confidence_breakdown", None),
            total_verses=verses_count,
            total_citations=total_citations_count,
            latency_ms=latency_ms,
            detected_language=detected_language,
            response_language=response_language,
        )
