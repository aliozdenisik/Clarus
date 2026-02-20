"""REST API endpoints for Quran morphological keyword search."""

import hashlib
import json
import logging

from fastapi import APIRouter, Query

from app.config import settings
from app.redis_client import redis_manager
from app.schemas.keyword_search import (
    KeywordSearchRequest,
    KeywordSearchResponse,
    PaginationInfo,
    RootListItem,
    RootListResponse,
    SurahDistItem,
    VerseMatchItem,
)
from src.quran_morphology import QuranMorphologySearch

logger = logging.getLogger(__name__)

router = APIRouter()

KEYWORD_CACHE_TTL = 3600

_search_instance: QuranMorphologySearch | None = None


def get_morphology_search() -> QuranMorphologySearch:
    global _search_instance
    if _search_instance is None:
        _search_instance = QuranMorphologySearch(settings.database_url)
    return _search_instance


def _make_search_cache_key(query: str, page: int, per_page: int, word_filter: str | None) -> str:
    raw = f"{query}:{page}:{per_page}:{word_filter or ''}"
    return f"keyword:{hashlib.md5(raw.encode()).hexdigest()}"


def _make_roots_cache_key(page: int, per_page: int) -> str:
    return f"keyword_roots:{page}:{per_page}"


@router.post("/", response_model=KeywordSearchResponse)
async def search_keyword(request: KeywordSearchRequest):
    """Search Quran by morphological root."""
    cache_key = _make_search_cache_key(request.query, request.page, request.per_page, request.word_filter)

    if redis_manager.client:
        try:
            cached = await redis_manager.client.get(cache_key)
            if cached:
                logger.info("Keyword search cache hit", extra={"query": request.query})
                return KeywordSearchResponse(**json.loads(cached))
        except Exception as e:
            logger.warning(
                "Redis get failed (fail-open)",
                extra={"cache_key": cache_key, "error_type": type(e).__name__},
            )

    search = get_morphology_search()
    result = await search.search_by_root(
        query=request.query,
        page=request.page,
        per_page=request.per_page,
        word_filter=request.word_filter,
    )

    if result.per_page > 0:
        total_pages = (result.total_verses + result.per_page - 1) // result.per_page
    else:
        total_pages = 1

    response = KeywordSearchResponse(
        query=result.query,
        root=result.root,
        root_source=result.root_source,
        total_occurrences=result.total_occurrences,
        unique_words=result.unique_words,
        surah_distribution=[
            SurahDistItem(surah_id=sd.surah_id, surah_name=sd.surah_name, count=sd.count)
            for sd in result.surah_distribution
        ],
        verses=[
            VerseMatchItem(
                surah_id=v.surah_id,
                surah_name=v.surah_name,
                ayah_number=v.ayah_number,
                text_uthmani=v.text_uthmani,
                text_clean=v.text_clean,
                matched_words=v.matched_words,
            )
            for v in result.verses
        ],
        pagination=PaginationInfo(
            page=result.page,
            per_page=result.per_page,
            total_verses=result.total_verses,
            total_pages=total_pages,
            has_next=result.page < total_pages,
            has_prev=result.page > 1,
        ),
        root_buckwalter=result.root_buckwalter,
        word_transliterations=result.word_transliterations,
    )

    if redis_manager.client:
        try:
            await redis_manager.client.setex(cache_key, KEYWORD_CACHE_TTL, json.dumps(response.model_dump()))
        except Exception as e:
            logger.warning(
                "Redis set failed (fail-open)",
                extra={"cache_key": cache_key, "error_type": type(e).__name__},
            )

    return response


@router.get("/roots", response_model=RootListResponse)
async def list_roots(
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=50, ge=1, le=200),
):
    """List all available Arabic roots with occurrence counts."""
    cache_key = _make_roots_cache_key(page, per_page)

    if redis_manager.client:
        try:
            cached = await redis_manager.client.get(cache_key)
            if cached:
                logger.info("Root list cache hit", extra={"page": page, "per_page": per_page})
                return RootListResponse(**json.loads(cached))
        except Exception as e:
            logger.warning(
                "Redis get failed (fail-open)",
                extra={"cache_key": cache_key, "error_type": type(e).__name__},
            )

    search = get_morphology_search()
    data = await search.list_roots(page=page, per_page=per_page)
    response = RootListResponse(
        roots=[RootListItem(root=r["root"], count=r["count"]) for r in data["roots"]],
        total=data["total"],
        page=data["page"],
        per_page=data["per_page"],
    )

    if redis_manager.client:
        try:
            await redis_manager.client.setex(cache_key, KEYWORD_CACHE_TTL, json.dumps(response.model_dump()))
        except Exception as e:
            logger.warning(
                "Redis set failed (fail-open)",
                extra={"cache_key": cache_key, "error_type": type(e).__name__},
            )

    return response


@router.get("/root/{root}", response_model=KeywordSearchResponse)
async def get_root_info(
    root: str,
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=0, ge=0, le=10000),
):
    """Get information for a specific root."""
    cache_key = _make_search_cache_key(root, page, per_page, None)

    if redis_manager.client:
        try:
            cached = await redis_manager.client.get(cache_key)
            if cached:
                logger.info("Root info cache hit", extra={"root": root})
                return KeywordSearchResponse(**json.loads(cached))
        except Exception as e:
            logger.warning(
                "Redis get failed (fail-open)",
                extra={"cache_key": cache_key, "error_type": type(e).__name__},
            )

    search = get_morphology_search()
    result = await search.search_by_root(query=root, page=page, per_page=per_page)

    if result.per_page > 0:
        total_pages = (result.total_verses + result.per_page - 1) // result.per_page
    else:
        total_pages = 1

    response = KeywordSearchResponse(
        query=result.query,
        root=result.root,
        root_source=result.root_source,
        total_occurrences=result.total_occurrences,
        unique_words=result.unique_words,
        surah_distribution=[
            SurahDistItem(surah_id=sd.surah_id, surah_name=sd.surah_name, count=sd.count)
            for sd in result.surah_distribution
        ],
        verses=[
            VerseMatchItem(
                surah_id=v.surah_id,
                surah_name=v.surah_name,
                ayah_number=v.ayah_number,
                text_uthmani=v.text_uthmani,
                text_clean=v.text_clean,
                matched_words=v.matched_words,
            )
            for v in result.verses
        ],
        pagination=PaginationInfo(
            page=result.page,
            per_page=result.per_page,
            total_verses=result.total_verses,
            total_pages=total_pages,
            has_next=result.page < total_pages,
            has_prev=result.page > 1,
        ),
        root_buckwalter=result.root_buckwalter,
        word_transliterations=result.word_transliterations,
    )

    if redis_manager.client:
        try:
            await redis_manager.client.setex(cache_key, KEYWORD_CACHE_TTL, json.dumps(response.model_dump()))
        except Exception as e:
            logger.warning(
                "Redis set failed (fail-open)",
                extra={"cache_key": cache_key, "error_type": type(e).__name__},
            )

    return response
