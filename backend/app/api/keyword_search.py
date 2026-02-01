"""REST API endpoints for Quran morphological keyword search."""

import logging
from typing import Optional
from fastapi import APIRouter, HTTPException, Query

from app.schemas.keyword_search import (
    KeywordSearchRequest,
    KeywordSearchResponse,
    PaginationInfo,
    SurahDistItem,
    VerseMatchItem,
    RootListItem,
    RootListResponse,
)
from src.quran_morphology import QuranMorphologySearch

logger = logging.getLogger(__name__)

router = APIRouter()

# Lazy singleton
_search_instance: Optional[QuranMorphologySearch] = None


def get_morphology_search() -> QuranMorphologySearch:
    global _search_instance
    if _search_instance is None:
        _search_instance = QuranMorphologySearch(
            "postgresql+asyncpg://postgres:postgres@localhost:54322/postgres"
        )
    return _search_instance


@router.post("/", response_model=KeywordSearchResponse)
async def search_keyword(request: KeywordSearchRequest):
    """Search Quran by morphological root."""
    search = get_morphology_search()
    result = await search.search_by_root(
        query=request.query,
        page=request.page,
        per_page=request.per_page,
    )

    total_pages = (
        (result.total_verses + result.per_page - 1) // result.per_page
        if result.per_page > 0
        else 0
    )

    return KeywordSearchResponse(
        query=result.query,
        root=result.root,
        root_source=result.root_source,
        total_occurrences=result.total_occurrences,
        unique_words=result.unique_words,
        surah_distribution=[
            SurahDistItem(
                surah_id=sd.surah_id, surah_name=sd.surah_name, count=sd.count
            )
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
    )


@router.get("/roots", response_model=RootListResponse)
async def list_roots(
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=50, ge=1, le=200),
):
    """List all available Arabic roots with occurrence counts."""
    search = get_morphology_search()
    data = await search.list_roots(page=page, per_page=per_page)
    return RootListResponse(
        roots=[RootListItem(root=r["root"], count=r["count"]) for r in data["roots"]],
        total=data["total"],
        page=data["page"],
        per_page=data["per_page"],
    )


@router.get("/root/{root}", response_model=KeywordSearchResponse)
async def get_root_info(
    root: str,
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=50, ge=1, le=200),
):
    """Get information for a specific root."""
    search = get_morphology_search()
    result = await search.search_by_root(query=root, page=page, per_page=per_page)

    total_pages = (
        (result.total_verses + result.per_page - 1) // result.per_page
        if result.per_page > 0
        else 0
    )

    return KeywordSearchResponse(
        query=result.query,
        root=result.root,
        root_source=result.root_source,
        total_occurrences=result.total_occurrences,
        unique_words=result.unique_words,
        surah_distribution=[
            SurahDistItem(
                surah_id=sd.surah_id, surah_name=sd.surah_name, count=sd.count
            )
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
    )
