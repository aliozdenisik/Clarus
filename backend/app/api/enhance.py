"""REST API endpoint for query enhancement and keyword extraction."""

import time
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.auth import check_rate_limit
from app.auth.api_key_validator import get_current_user_flexible
from app.db import get_db
from app.logging_config import get_logger, log_performance
from src.query_enhancer import EnhanceResponse, KeywordSuggestion, QueryEnhancer

logger = get_logger(__name__)

router = APIRouter()

_enhancer_instance: QueryEnhancer | None = None


def get_enhancer() -> QueryEnhancer:
    global _enhancer_instance
    if _enhancer_instance is None:
        _enhancer_instance = QueryEnhancer()
    return _enhancer_instance


class EnhanceRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=500)
    corpus: str = Field(default="quran", pattern="^(quran|bible)$")


@router.post("/enhance", response_model=EnhanceResponse)
async def enhance_query(
    request: EnhanceRequest,
    current_user: dict[str, Any] = Depends(get_current_user_flexible),
    db: AsyncSession = Depends(get_db),
):
    """Extract structured keywords from a search query.

    This endpoint uses the QueryEnhancer to extract keywords from a user's search query.
    Keywords are extracted using a hybrid approach:
    - Rule-based: Splits on conjunctions (Turkish: ve, veya, ile; English: and, or, with)
    - LLM-based: Uses language model for semantic keyword extraction
    - Fallback: Simple word splitting if LLM fails

    Args:
        request: EnhanceRequest with query and corpus
        current_user: Authenticated user (from JWT token or API key)
        db: Database session for rate limiting

    Returns:
        EnhanceResponse with original_query, keywords list, and corpus

    Raises:
        HTTPException: 401 if not authenticated, 429 if rate limited
    """
    start_time = time.time()
    try:
        await check_rate_limit(current_user, db)

        logger.info(
            "Enhance query request received",
            extra={
                "query": request.query[:50],
                "corpus": request.corpus,
                "user_id": current_user["id"],
            },
        )

        enhancer = get_enhancer()
        keywords = enhancer.extract_keywords(request.query, corpus=request.corpus)

        latency_ms = (time.time() - start_time) * 1000
        log_performance(
            logger,
            "enhance_query",
            latency_ms,
            corpus=request.corpus,
            keyword_count=len(keywords),
        )

        return EnhanceResponse(
            original_query=request.query,
            keywords=keywords,
            corpus=request.corpus,
        )
    except HTTPException:
        # Re-raise HTTP exceptions (auth, rate limit)
        raise
    except Exception as e:
        logger.error(
            f"Enhance query failed: {e}",
            extra={"query": request.query[:50], "corpus": request.corpus},
            exc_info=True,
        )
        # Fallback: return original query as single keyword
        return EnhanceResponse(
            original_query=request.query,
            keywords=[KeywordSuggestion(text=request.query, source="fallback")],
            corpus=request.corpus,
        )
