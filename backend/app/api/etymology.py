import json

from fastapi import APIRouter, HTTPException
from redis import asyncio as aioredis
from sqlalchemy import select

from app.db import async_session_maker
from app.logging_config import get_logger
from app.models import QMRootEtymology
from app.redis_client import redis_manager
from app.schemas.etymology import MorphologicalForm, RelatedRoot, RootEtymologyResponse

logger = get_logger(__name__)

router = APIRouter()

ETYMOLOGY_CACHE_TTL = 86400


async def get_etymology_from_cache(redis: aioredis.Redis | None, root: str) -> dict | None:
    if not redis:
        return None
    try:
        cache_key = f"etymology:{root}"
        cached = await redis.get(cache_key)
        if cached:
            logger.info("Etymology cache hit", extra={"root": root})
            return json.loads(cached)
        return None
    except Exception as e:
        logger.warning(
            "Redis get failed in etymology endpoint",
            extra={"error_type": type(e).__name__, "root": root},
        )
        return None


async def set_etymology_cache(redis: aioredis.Redis | None, root: str, data: dict) -> None:
    if not redis:
        return
    try:
        cache_key = f"etymology:{root}"
        await redis.setex(cache_key, ETYMOLOGY_CACHE_TTL, json.dumps(data))
        logger.info("Etymology cache set", extra={"root": root, "ttl_seconds": ETYMOLOGY_CACHE_TTL})
    except Exception as e:
        logger.warning(
            "Redis set failed in etymology endpoint",
            extra={"error_type": type(e).__name__, "root": root},
        )


async def query_etymology_from_db(root: str) -> QMRootEtymology | None:
    async with async_session_maker() as session:
        stmt = select(QMRootEtymology).where((QMRootEtymology.root == root) | (QMRootEtymology.root_buckwalter == root))
        result = await session.execute(stmt)
        return result.scalar_one_or_none()


@router.get("/{root}", response_model=RootEtymologyResponse)
async def get_etymology(root: str):
    redis = redis_manager.client

    cached_data = await get_etymology_from_cache(redis, root)
    if cached_data:
        return RootEtymologyResponse(**cached_data)

    etym = await query_etymology_from_db(root)

    if not etym:
        logger.warning("Etymology root not found", extra={"root": root})
        raise HTTPException(status_code=404, detail="Root not found")

    morphological_forms_list: list[MorphologicalForm] = []
    if etym.morphological_forms:
        if isinstance(etym.morphological_forms, list):
            forms_data = etym.morphological_forms[:15]
        else:
            forms_data = []
        morphological_forms_list = [MorphologicalForm(**form) for form in forms_data]

    related_roots_list: list[RelatedRoot] = []
    if etym.related_roots:
        if isinstance(etym.related_roots, list):
            roots_data = etym.related_roots[:20]
        else:
            roots_data = []
        related_roots_list = [RelatedRoot(**root_data) for root_data in roots_data]

    response = RootEtymologyResponse(
        id=etym.id,
        root=etym.root,
        root_buckwalter=etym.root_buckwalter,
        definition_en=etym.definition_en,
        definition_tr=etym.definition_tr,
        semantic_field=etym.semantic_field,
        morphological_forms=morphological_forms_list,
        related_roots=related_roots_list,
        quran_frequency=etym.quran_frequency,
        source=etym.source,
        lane_match_type=etym.lane_match_type,
        lane_volume=etym.lane_volume,
        confidence=etym.confidence,
        tr_translation_source=etym.tr_translation_source,
        tr_translation_confidence=etym.tr_translation_confidence,
        created_at=etym.created_at,
        updated_at=etym.updated_at,
    )

    response_dict = response.model_dump(mode="json")
    await set_etymology_cache(redis, root, response_dict)

    logger.info(
        "Etymology data retrieved",
        extra={
            "root": root,
            "root_buckwalter": etym.root_buckwalter,
            "source": etym.source,
            "quran_frequency": etym.quran_frequency,
        },
    )

    return response
