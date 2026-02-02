"""REST API endpoints for Bible morphological keyword search."""

import logging
from typing import Optional
from fastapi import APIRouter, HTTPException, Query

from app.schemas.bible_keyword import (
    BibleKeywordSearchRequest,
    BibleKeywordSearchResponse,
    PaginationInfo,
    BookDistItem,
    BibleVerseMatchItem,
    BibleRootListItem,
    BibleRootListResponse,
    BibleStatsResponse,
)
from src.bible_morphology import BibleMorphologySearch

logger = logging.getLogger(__name__)

router = APIRouter()

# Lazy singleton
_search_instance: Optional[BibleMorphologySearch] = None


async def get_bible_search() -> BibleMorphologySearch:
    global _search_instance
    if _search_instance is None:
        _search_instance = await BibleMorphologySearch.get_instance()
    return _search_instance


@router.post("/", response_model=BibleKeywordSearchResponse)
async def search_bible_keyword(request: BibleKeywordSearchRequest):
    """Search Bible by morphological root (Hebrew/Aramaic)."""
    search = await get_bible_search()
    result = await search.search(
        query=request.query,
        page=request.page,
        per_page=request.per_page,
        language_filter=request.language_filter,
        word_filter=request.word_filter,
    )

    # per_page=0 means all verses returned at once (no server pagination)
    if result.per_page > 0:
        total_pages = (result.total_verses + result.per_page - 1) // result.per_page
    else:
        total_pages = 1

    return BibleKeywordSearchResponse(
        query=result.query,
        root=result.root,
        root_source=result.root_source,
        strong_number=result.strong_number,
        total_occurrences=result.total_occurrences,
        unique_words=result.unique_words,
        book_distribution=[
            BookDistItem(book_id=bd.book_id, book_name=bd.book_name, count=bd.count)
            for bd in result.book_distribution
        ],
        verses=[
            BibleVerseMatchItem(
                book_id=v.book_id,
                book_name=v.book_name,
                chapter=v.chapter,
                verse=v.verse,
                text_original=v.text_original,
                text_english=v.text_english,
                matched_words=v.matched_words,
                reference=v.reference,
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
        transliteration=result.transliteration,
        word_transliterations=result.word_transliterations,
    )


@router.get("/roots", response_model=BibleRootListResponse)
async def list_bible_roots(
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=50, ge=1, le=200),
):
    """List all available Hebrew/Aramaic roots with occurrence counts."""
    search = await get_bible_search()
    data = await search.list_roots(page=page, per_page=per_page)
    return BibleRootListResponse(
        roots=[
            BibleRootListItem(
                strong_number=r["strong_number"],
                original_word=r["original_word"],
                transliteration=r["transliteration"],
                count=r["count"],
            )
            for r in data["roots"]
        ],
        total=data["total"],
        page=data["page"],
        per_page=data["per_page"],
    )


@router.get("/root/{root}", response_model=BibleKeywordSearchResponse)
async def get_bible_root_info(
    root: str,
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=0, ge=0, le=10000),
):
    """Get information for a specific root."""
    search = await get_bible_search()
    result = await search.search(query=root, page=page, per_page=per_page)

    if result.per_page > 0:
        total_pages = (result.total_verses + result.per_page - 1) // result.per_page
    else:
        total_pages = 1

    return BibleKeywordSearchResponse(
        query=result.query,
        root=result.root,
        root_source=result.root_source,
        strong_number=result.strong_number,
        total_occurrences=result.total_occurrences,
        unique_words=result.unique_words,
        book_distribution=[
            BookDistItem(book_id=bd.book_id, book_name=bd.book_name, count=bd.count)
            for bd in result.book_distribution
        ],
        verses=[
            BibleVerseMatchItem(
                book_id=v.book_id,
                book_name=v.book_name,
                chapter=v.chapter,
                verse=v.verse,
                text_original=v.text_original,
                text_english=v.text_english,
                matched_words=v.matched_words,
                reference=v.reference,
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
        transliteration=result.transliteration,
        word_transliterations=result.word_transliterations,
    )


@router.get("/stats", response_model=BibleStatsResponse)
async def get_bible_stats():
    """Get Bible keyword search statistics."""
    search = await get_bible_search()
    stats = await search.get_stats()
    return BibleStatsResponse(
        total_words=stats["total_words"],
        unique_roots=stats["unique_roots"],
        total_books=stats["total_books"],
        total_verses=stats["total_verses"],
    )
