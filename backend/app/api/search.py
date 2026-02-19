import time
from typing import Any

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.auth import check_rate_limit
from app.api.compare import (
    VerseDetail,
    extract_bible_verse_detail,
    extract_quran_verse_detail,
)
from app.auth.api_key_validator import get_current_user_flexible
from app.config import settings
from app.db import get_db
from app.i18n.detector import get_locale
from app.i18n.messages import get_error_message
from app.logging_config import get_logger, log_performance
from app.middleware.error_handler import NotFoundError, ValidationError
from app.models import SearchHistory, UserPreferences
from app.schemas.common import DEFAULT_TRANSLATOR, QueryValidation, TranslatorType
from src.ultimate_rag import UltimateRAG

logger = get_logger(__name__)


router = APIRouter()

_rag_instance: UltimateRAG | None = None


def get_rag() -> UltimateRAG:
    global _rag_instance
    if _rag_instance is None:
        _rag_instance = UltimateRAG()
    return _rag_instance


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=500)
    mode: str = Field(default="semantic", pattern="^(semantic|keyword)$")
    top_k: int = Field(default=10, ge=1, le=50)
    language: str | None = Field(
        None,
        pattern=r"^(en|tr|es|fr|it|pt|ar|de)$",
        description="Response language (auto-detect if omitted)",
    )
    translator: TranslatorType | None = Field(
        default=DEFAULT_TRANSLATOR,
        description="Quran translator (diyanet, yazir, ates, bulac, ozturk, vakfi, yildirim, yuksel)",
    )


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
    verse_details: dict[str, VerseDetail] | None = None  # NEW: Rich verse metadata for citations
    detected_language: str | None = None


class HistoryItem(BaseModel):
    id: int
    query: str
    search_type: str
    created_at: str
    result_count: int | None = None


def _sanitize_query(query: str) -> str:
    return QueryValidation.sanitize(query)


def _validate_query(query: str, locale: str = "tr") -> str:
    sanitized = _sanitize_query(query)

    if len(sanitized) < settings.query_min_length:
        raise ValidationError(
            message=get_error_message("query_too_short", locale, min_length=settings.query_min_length)
        )

    if len(sanitized) > settings.query_max_length:
        raise ValidationError(message=get_error_message("query_too_long", locale, max_length=settings.query_max_length))

    return sanitized


@router.post("/quran", response_model=SearchResponse)
async def search_quran(
    request: SearchRequest,
    current_user: dict[str, Any] = Depends(get_current_user_flexible),
    db: AsyncSession = Depends(get_db),
    locale: str = Depends(get_locale),
):
    start = time.perf_counter()
    translator = request.translator or DEFAULT_TRANSLATOR
    collection_name = f"quran_tr_{translator}"
    logger.info(
        "Search request received",
        extra={
            "query": request.query[:50],
            "collection": collection_name,
            "translator": translator,
            "top_k": request.top_k,
            "user_id": current_user["id"],
        },
    )

    await check_rate_limit(current_user, db, locale)

    prefs_result = await db.execute(select(UserPreferences).where(UserPreferences.user_id == current_user["id"]))
    user_preferences = prefs_result.scalar_one_or_none()
    usage_purpose = user_preferences.usage_purpose if user_preferences else None
    _ = usage_purpose  # Available for future prompt customization

    validated_query = _validate_query(request.query, locale)

    rag = get_rag()
    results = await rag.search_quran(validated_query, translator=translator, top_k=request.top_k, locale=locale)

    # Build verse_details dict for citation navigation
    verse_details: dict[str, VerseDetail] = {}
    for r in results:
        ref, detail = extract_quran_verse_detail(r)
        if ref not in verse_details:  # Deduplicate
            verse_details[ref] = detail

    history = SearchHistory(
        user_id=current_user["id"],
        query=validated_query,
        search_type="search_quran",
        result_count=len(results) if results else 0,
    )
    db.add(history)
    await db.commit()

    verses = [
        VerseResult(
            source="Kuran",
            reference=f"{r.surah_name}:{r.verse_id}",  # FIXED: Match citation format (removed surah_id)
            text=r.translation,
            score=r.score,
        )
        for r in results
    ]

    latency_ms = (time.perf_counter() - start) * 1000
    log_performance(
        logger,
        "search_quran",
        latency_ms,
        collection=collection_name,
        results=len(results),
    )

    return SearchResponse(
        query=validated_query,
        results=verses,
        total=len(verses),
        verse_details=verse_details,  # NEW: Include verse metadata
        detected_language=request.language or "tr",  # Use provided language or default to Turkish (Quran corpus)
    )


@router.post("/bible", response_model=SearchResponse)
async def search_bible(
    request: SearchRequest,
    testament: str | None = Query(None, pattern="^(ot|nt|apocrypha)$"),
    current_user: dict[str, Any] = Depends(get_current_user_flexible),
    db: AsyncSession = Depends(get_db),
    locale: str = Depends(get_locale),
):
    start = time.perf_counter()
    collection = f"bible_{testament}" if testament else "bible_all"
    logger.info(
        "Search request received",
        extra={
            "query": request.query[:50],
            "collection": collection,
            "top_k": request.top_k,
            "user_id": current_user["id"],
        },
    )

    await check_rate_limit(current_user, db, locale)

    prefs_result = await db.execute(select(UserPreferences).where(UserPreferences.user_id == current_user["id"]))
    user_preferences = prefs_result.scalar_one_or_none()
    usage_purpose = user_preferences.usage_purpose if user_preferences else None
    _ = usage_purpose  # Available for future prompt customization

    validated_query = _validate_query(request.query, locale)

    rag = get_rag()
    results = await rag.search_bible(validated_query, testament=testament, top_k=request.top_k, locale=locale)

    # Build verse_details dict for citation navigation
    verse_details: dict[str, VerseDetail] = {}
    for r in results:
        # Determine source collection from testament parameter or result attributes
        if testament == "ot":
            source = "bible_ot"
        elif testament == "nt":
            source = "bible_nt"
        elif testament == "apocrypha":
            source = "bible_apocrypha"
        else:
            # Fallback: Try to infer from result object
            testament_attr = getattr(r, "testament", "OT")
            if testament_attr == "OT":
                source = "bible_ot"
            elif testament_attr == "NT":
                source = "bible_nt"
            else:
                source = "bible_apocrypha"

        ref, detail = extract_bible_verse_detail(r, source)
        if ref not in verse_details:  # Deduplicate
            verse_details[ref] = detail

    history = SearchHistory(
        user_id=current_user["id"],
        query=validated_query,
        search_type=f"search_bible_{testament or 'all'}",
        result_count=len(results) if results else 0,
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

    latency_ms = (time.perf_counter() - start) * 1000
    log_performance(logger, "search_bible", latency_ms, collection=collection, results=len(results))

    return SearchResponse(
        query=validated_query,
        results=verses,
        total=len(verses),
        verse_details=verse_details,  # NEW: Include verse metadata
        detected_language=request.language or "en",  # Use provided language or default to English (Bible corpus)
    )


@router.get("/history")
async def get_search_history(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    search_type: str | None = Query(None),
    current_user: dict[str, Any] = Depends(get_current_user_flexible),
    db: AsyncSession = Depends(get_db),
):
    base_query = select(SearchHistory).where(SearchHistory.user_id == current_user["id"])

    if search_type:
        base_query = base_query.where(SearchHistory.search_type.contains(search_type))

    total_result = await db.execute(
        select(func.count(SearchHistory.id)).where(SearchHistory.user_id == current_user["id"])
    )
    total_items = total_result.scalar() or 0

    offset = (page - 1) * limit
    result = await db.execute(base_query.order_by(SearchHistory.created_at.desc()).offset(offset).limit(limit))
    history = result.scalars().all()

    items = [
        HistoryItem(
            id=h.id,
            query=h.query,
            search_type=h.search_type,
            created_at=h.created_at.isoformat(),
            result_count=h.result_count,
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
    current_user: dict[str, Any] = Depends(get_current_user_flexible),
    db: AsyncSession = Depends(get_db),
    locale: str = Depends(get_locale),
):
    result = await db.execute(
        select(SearchHistory).where(SearchHistory.id == history_id).where(SearchHistory.user_id == current_user["id"])
    )
    history_item = result.scalar_one_or_none()

    if not history_item:
        raise NotFoundError(message=get_error_message("history_not_found", locale), locale=locale)

    await db.delete(history_item)
    await db.commit()

    return {"success": True, "message": get_error_message("history_deleted", locale)}


@router.delete("/history")
async def clear_history(
    current_user: dict[str, Any] = Depends(get_current_user_flexible),
    db: AsyncSession = Depends(get_db),
    locale: str = Depends(get_locale),
):
    from sqlalchemy import delete

    await db.execute(delete(SearchHistory).where(SearchHistory.user_id == current_user["id"]))
    await db.commit()

    return {"success": True, "message": get_error_message("all_history_cleared", locale)}
