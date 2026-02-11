"""API routes for fetching all Turkish translations of a Quran verse."""

import asyncio
import os
import sys

from fastapi import APIRouter, HTTPException
from qdrant_client import AsyncQdrantClient
from qdrant_client.http.models import FieldCondition, Filter, MatchValue

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.logging_config import get_logger
from app.schemas.verse_translations import TranslationItem, VerseTranslationsResponse
from src.verse_parser import SURAH_NAME_MAP

logger = get_logger(__name__)

router = APIRouter()

_qdrant_client: AsyncQdrantClient | None = None

TRANSLATOR_DISPLAY_NAMES = {
    "diyanet": "Diyanet İşleri",
    "yazir": "Elmalılı Yazır",
    "ates": "Süleyman Ateş",
    "bulac": "Ali Bulaç",
    "ozturk": "Yaşar Nuri Öztürk",
    "vakfi": "Diyanet Vakfı",
    "yildirim": "Suat Yıldırım",
    "yuksel": "Edip Yüksel",
}

QURAN_TRANSLATORS = list(TRANSLATOR_DISPLAY_NAMES.keys())


def get_qdrant_client() -> AsyncQdrantClient:
    global _qdrant_client
    if _qdrant_client is None:
        _qdrant_client = AsyncQdrantClient(host="localhost", port=6333)
    return _qdrant_client


def validate_verse_bounds(surah_id: int, verse_id: int) -> None:
    if not 1 <= surah_id <= 114:
        raise HTTPException(
            status_code=404,
            detail={
                "success": False,
                "error": "INVALID_SURAH",
                "message": f"Surah ID must be between 1 and 114, got {surah_id}",
            },
        )

    surah_info = next((info for info in SURAH_NAME_MAP.values() if info["id"] == surah_id), None)
    if not surah_info:
        raise HTTPException(
            status_code=404,
            detail={
                "success": False,
                "error": "SURAH_NOT_FOUND",
                "message": f"Surah {surah_id} not found in metadata",
            },
        )

    max_verses = surah_info["verses"]
    if not 1 <= verse_id <= max_verses:
        raise HTTPException(
            status_code=404,
            detail={
                "success": False,
                "error": "INVALID_VERSE",
                "message": f"Verse ID must be between 1 and {max_verses} for Surah {surah_id}, got {verse_id}",
            },
        )


async def fetch_translation(
    client: AsyncQdrantClient,
    translator: str,
    surah_id: int,
    verse_id: int,
) -> tuple[TranslationItem, str] | None:
    try:
        collection_name = f"quran_tr_{translator}"

        filter_condition = Filter(
            must=[
                FieldCondition(key="surah_id", match=MatchValue(value=surah_id)),
                FieldCondition(key="verse_id", match=MatchValue(value=verse_id)),
            ]
        )

        points = await client.scroll(
            collection_name=collection_name,
            scroll_filter=filter_condition,
            limit=1,
            with_payload=True,
            with_vectors=False,
        )

        if points[0]:
            for point in points[0]:
                if point.payload:
                    translation_item = TranslationItem(
                        translator=translator,
                        translator_display=TRANSLATOR_DISPLAY_NAMES[translator],
                        text=point.payload.get("translation", ""),
                    )
                    arabic_text = point.payload.get("arabic_text", "")
                    return (translation_item, arabic_text)

        return None

    except Exception as e:
        logger.warning(
            f"Failed to fetch translation for {translator}",
            extra={
                "translator": translator,
                "surah_id": surah_id,
                "verse_id": verse_id,
                "error": str(e),
            },
        )
        return None


@router.get(
    "/quran/verses/{surah_id}/{verse_id}/translations",
    response_model=VerseTranslationsResponse,
)
async def get_verse_translations(surah_id: int, verse_id: int):
    logger.info(
        f"Verse translations request: {surah_id}:{verse_id}",
        extra={"surah_id": surah_id, "verse_id": verse_id},
    )

    validate_verse_bounds(surah_id, verse_id)

    surah_name = next(
        (name for name, info in SURAH_NAME_MAP.items() if info["id"] == surah_id),
        None,
    )
    if not surah_name:
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": "INTERNAL_ERROR",
                "message": f"Failed to resolve surah name for ID {surah_id}",
            },
        )

    client = get_qdrant_client()

    try:
        tasks = [fetch_translation(client, translator, surah_id, verse_id) for translator in QURAN_TRANSLATORS]
        results = await asyncio.gather(*tasks)

        translations = []
        arabic_text = ""

        for result in results:
            if result is not None:
                translation_item, verse_arabic_text = result
                translations.append(translation_item)
                if not arabic_text and verse_arabic_text:
                    arabic_text = verse_arabic_text

        if not translations:
            raise HTTPException(
                status_code=404,
                detail={
                    "success": False,
                    "error": "NO_TRANSLATIONS_FOUND",
                    "message": f"No translations found for verse {surah_id}:{verse_id}",
                },
            )

        logger.info(
            f"Found {len(translations)} translations for {surah_id}:{verse_id}",
            extra={"surah_id": surah_id, "verse_id": verse_id, "translations_count": len(translations)},
        )

        return VerseTranslationsResponse(
            success=True,
            surah_id=surah_id,
            verse_id=verse_id,
            surah_name=surah_name,
            arabic_text=arabic_text,
            translations=translations,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Error fetching translations: {e}",
            extra={"surah_id": surah_id, "verse_id": verse_id},
            exc_info=True,
        )
        raise HTTPException(
            status_code=503,
            detail={
                "success": False,
                "error": "QDRANT_ERROR",
                "message": f"Failed to fetch translations: {e!s}",
            },
            headers={"Retry-After": "60"},
        )
