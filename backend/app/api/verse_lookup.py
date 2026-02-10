"""Verse lookup API routes for direct verse access by reference."""

from fastapi import APIRouter, Query, HTTPException
from qdrant_client import AsyncQdrantClient
from qdrant_client.http.models import Filter, FieldCondition, MatchValue
from typing import List, Optional
import sys
import os

# Add src to path for imports
sys.path.insert(
    0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

from app.schemas.verse_lookup import (
    VerseLookupResponse,
    VerseResult,
)
from app.schemas.common import TranslatorType, DEFAULT_TRANSLATOR
from src.verse_parser import (
    parse_verse_reference,
    ParsedReference,
    ParseError,
    SURAH_NAME_MAP,
)
from app.logging_config import get_logger

logger = get_logger(__name__)

router = APIRouter()

# Qdrant client singleton
_qdrant_client: AsyncQdrantClient | None = None


def get_qdrant_client() -> AsyncQdrantClient:
    """Get or create AsyncQdrantClient instance."""
    global _qdrant_client
    if _qdrant_client is None:
        _qdrant_client = AsyncQdrantClient(host="localhost", port=6333)
    return _qdrant_client


def get_bible_collection(testament: str) -> str:
    """Map testament to Qdrant collection name.

    Args:
        testament: "OT", "NT", or "Apocrypha"

    Returns:
        Collection name: "bible_ot", "bible_nt", or "bible_apocrypha"
    """
    collection_map = {
        "OT": "bible_ot",
        "NT": "bible_nt",
        "Apocrypha": "bible_apocrypha",
    }
    return collection_map[testament]


async def fetch_quran_verses(
    client: AsyncQdrantClient,
    parsed: ParsedReference,
    translator: str = DEFAULT_TRANSLATOR,
) -> List[VerseResult]:
    """Fetch Quran verses from Qdrant using payload filter.

    Args:
        client: AsyncQdrantClient instance
        parsed: ParsedReference with surah_id and verses
        translator: Quran translator (default: "diyanet")

    Returns:
        List of VerseResult objects
    """
    results = []

    surah_id = parsed.surah_id
    if surah_id is None:
        raise ValueError("Surah ID is required for Quran references")

    # Get surah name from SURAH_NAME_MAP
    surah_name = None
    for name, info in SURAH_NAME_MAP.items():
        if info["id"] == surah_id:
            surah_name = name
            break

    # Build collection name from translator
    collection_name = f"quran_tr_{translator}"

    # Fetch each verse individually
    for verse_id in parsed.verses:
        # Create filter for exact surah_id and verse_id match
        filter_condition = Filter(
            must=[
                FieldCondition(key="surah_id", match=MatchValue(value=surah_id)),
                FieldCondition(key="verse_id", match=MatchValue(value=verse_id)),
            ]
        )

        # Query Qdrant with payload filter (no vector search)
        points = await client.scroll(
            collection_name=collection_name,
            scroll_filter=filter_condition,
            limit=1,
            with_payload=True,
            with_vectors=False,  # Don't need vectors
        )

        # Extract verse from response
        if points[0]:  # points is tuple (records, next_page_offset)
            for point in points[0]:
                payload = point.payload
                if payload is not None:
                    results.append(
                        VerseResult(
                            reference=f"{surah_id}:{verse_id}",
                            text=payload.get("translation", ""),
                            source="quran",
                            surah_id=surah_id,
                            surah_name=surah_name,
                            verse_id=verse_id,
                            arabic_text=payload.get("arabic_text"),
                            # Bible fields are None
                            book_id=None,
                            book_name=None,
                            chapter=None,
                            verse=None,
                        )
                    )

    return results


async def fetch_bible_verses(
    client: AsyncQdrantClient, parsed: ParsedReference
) -> List[VerseResult]:
    """Fetch Bible verses from Qdrant using payload filter.

    Args:
        client: AsyncQdrantClient instance
        parsed: ParsedReference with book_id, chapter, and verses

    Returns:
        List of VerseResult objects
    """
    results = []

    # Determine collection from testament
    testament = parsed.testament
    if testament is None:
        raise ValueError("Testament is required for Bible verses")

    book_id = parsed.book_id
    chapter = parsed.chapter
    if book_id is None or chapter is None:
        raise ValueError("Book ID and chapter are required for Bible references")

    collection_name = get_bible_collection(testament)

    # Determine source identifier (cast to Literal type)
    from typing import Literal, cast

    source_map = {
        "OT": "bible_ot",
        "NT": "bible_nt",
        "Apocrypha": "bible_apocrypha",
    }
    source = cast(
        Literal["quran", "bible_ot", "bible_nt", "bible_apocrypha"],
        source_map[testament],
    )

    # Fetch each verse individually
    for verse_num in parsed.verses:
        # Create filter for exact book_id, chapter, and verse match
        filter_condition = Filter(
            must=[
                FieldCondition(key="book_id", match=MatchValue(value=book_id)),
                FieldCondition(key="chapter", match=MatchValue(value=chapter)),
                FieldCondition(key="verse", match=MatchValue(value=verse_num)),
            ]
        )

        # Query Qdrant with payload filter (no vector search)
        points = await client.scroll(
            collection_name=collection_name,
            scroll_filter=filter_condition,
            limit=1,
            with_payload=True,
            with_vectors=False,  # Don't need vectors
        )

        # Extract verse from response
        if points[0]:  # points is tuple (records, next_page_offset)
            for point in points[0]:
                payload = point.payload
                if payload is not None:
                    results.append(
                        VerseResult(
                            reference=f"{parsed.book_name} {chapter}:{verse_num}",
                            text=payload.get("text", ""),
                            source=source,
                            book_id=book_id,
                            book_name=parsed.book_name,
                            chapter=chapter,
                            verse=verse_num,
                            # Quran fields are None
                            surah_id=None,
                            surah_name=None,
                            verse_id=None,
                            arabic_text=None,
                        )
                    )

    return results


@router.get("/lookup", response_model=VerseLookupResponse)
async def lookup_verse(
    ref: str = Query(
        ...,
        min_length=1,
        max_length=100,
        description="Verse reference: '2:183', 'Bakara 183', 'Genesis 1:1', etc.",
    ),
    translator: Optional[TranslatorType] = Query(
        default=DEFAULT_TRANSLATOR,
        description="Quran translator (diyanet, yazir, ates, bulac, ozturk, vakfi, yildirim, yuksel)",
    ),
):
    """Lookup verses by reference.

    Supported formats:
    - Quran numeric: "2:183", "2:183-185"
    - Quran Turkish: "Bakara 183", "Bakara 183-185"
    - Bible: "Genesis 1:1", "Genesis 1:1-3", "John 3:16"

    Returns:
        VerseLookupResponse with matching verses and metadata

    Raises:
        HTTPException 400: Invalid reference format or out-of-bounds verse
    """
    logger.info(f"Verse lookup request: {ref}")

    # Parse reference
    result = parse_verse_reference(ref)

    # Handle parse error
    if isinstance(result, ParseError):
        logger.warning(f"Parse error: {result.code} - {result.message}")
        raise HTTPException(
            status_code=400,
            detail={
                "success": False,
                "error": result.code,
                "message": result.message,
                "input": result.input,
            },
        )

    # Fetch verses from Qdrant
    client = get_qdrant_client()

    try:
        quran_translator = translator or DEFAULT_TRANSLATOR
        if result.source == "quran":
            verses = await fetch_quran_verses(client, result, quran_translator)
        else:  # bible
            verses = await fetch_bible_verses(client, result)

        logger.info(f"Found {len(verses)} verses for reference: {ref}")

        return VerseLookupResponse(
            success=True,
            verses=verses,
            query=ref,
            count=len(verses),
        )

    except Exception as e:
        logger.error(f"Error fetching verses: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": "INTERNAL_ERROR",
                "message": f"Failed to fetch verses: {str(e)}",
                "input": ref,
            },
        )
