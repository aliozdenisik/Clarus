"""REST API endpoint for verse-level word tokenization (Issue #60)."""

import json

from fastapi import APIRouter, HTTPException, Path
from sqlalchemy import exists, select
from sqlalchemy.orm import joinedload

from app.db import async_session_maker
from app.logging_config import get_logger
from app.models import QMAyah, QMRootEtymology, QMSurah
from app.redis_client import redis_manager
from app.schemas.etymology import VerseWordsResponse, WordItem

logger = get_logger(__name__)

router = APIRouter()

CACHE_TTL_SECONDS = 60 * 60 * 24 * 7


def _get_cache_key(surah_id: int, ayah_number: int) -> str:
    return f"verse_words:{surah_id}:{ayah_number}"


@router.get("/{surah_id}/{ayah_number}/words", response_model=VerseWordsResponse)
async def get_verse_words(
    surah_id: int = Path(..., ge=1, le=114, description="Surah ID (1-114)"),
    ayah_number: int = Path(..., ge=1, description="Ayah number within the surah"),
):
    cache_key = _get_cache_key(surah_id, ayah_number)

    if redis_manager.client:
        try:
            cached = await redis_manager.client.get(cache_key)
            if cached:
                data = json.loads(cached)
                logger.info(
                    "Cache hit for verse words",
                    extra={"surah_id": surah_id, "ayah_number": ayah_number},
                )
                return VerseWordsResponse(**data)
        except Exception as e:
            logger.warning(
                "Redis get failed (fail-open)",
                extra={
                    "cache_key": cache_key,
                    "error_type": type(e).__name__,
                },
            )

    async with async_session_maker() as session:
        surah_exists = await session.scalar(select(exists().where(QMSurah.id == surah_id)))
        if not surah_exists:
            raise HTTPException(
                status_code=404,
                detail={
                    "success": False,
                    "error": "SURAH_NOT_FOUND",
                    "message": f"Surah {surah_id} not found (valid range: 1-114)",
                },
            )

        surah = await session.scalar(select(QMSurah).where(QMSurah.id == surah_id))
        if surah and ayah_number > surah.total_verses:
            raise HTTPException(
                status_code=404,
                detail={
                    "success": False,
                    "error": "AYAH_OUT_OF_BOUNDS",
                    "message": f"Ayah {ayah_number} out of bounds for Surah {surah_id} (max: {surah.total_verses})",
                },
            )

        stmt = (
            select(QMAyah)
            .options(joinedload(QMAyah.words))
            .join(QMSurah)
            .where(QMSurah.id == surah_id, QMAyah.ayah_number == ayah_number)
        )
        result = await session.execute(stmt)
        ayah = result.scalars().first()

        if not ayah:
            raise HTTPException(
                status_code=404,
                detail={
                    "success": False,
                    "error": "AYAH_NOT_FOUND",
                    "message": f"Ayah {ayah_number} not found in Surah {surah_id}",
                },
            )

        etymology_roots_stmt = select(QMRootEtymology.root)
        etymology_roots_result = await session.execute(etymology_roots_stmt)
        etymology_roots = {row[0] for row in etymology_roots_result}

        words = sorted(ayah.words, key=lambda w: w.position)
        word_items = [
            WordItem(
                position=word.position,
                token=word.token,
                token_clean=word.token_clean,
                root=word.root,
                root_buckwalter=word.root_buckwalter,
                lemma=word.lemma,
                pos_tag=word.pos_tag,
                has_etymology=word.root in etymology_roots if word.root else False,
            )
            for word in words
        ]

        response = VerseWordsResponse(
            surah_id=surah_id,
            ayah_number=ayah_number,
            words=word_items,
            word_count=len(word_items),
        )

        if redis_manager.client:
            try:
                await redis_manager.client.setex(
                    cache_key,
                    CACHE_TTL_SECONDS,
                    json.dumps(response.model_dump()),
                )
                logger.info(
                    "Cached verse words",
                    extra={"surah_id": surah_id, "ayah_number": ayah_number, "ttl_seconds": CACHE_TTL_SECONDS},
                )
            except Exception as e:
                logger.warning(
                    "Redis set failed (fail-open)",
                    extra={
                        "cache_key": cache_key,
                        "error_type": type(e).__name__,
                    },
                )

        return response
