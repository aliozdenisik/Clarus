"""SSE Streaming API routes for real-time LLM responses."""

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import AsyncGenerator
import asyncio
import json
import logging
import sys
import os
import time
import traceback
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

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
from app.api.auth import get_current_user, get_current_user_from_token, check_rate_limit
from app.api.compare_helpers import build_verse_details, build_paragraphs
from app.api.compare import extract_quran_verse_detail, extract_bible_verse_detail
from src.ultimate_rag import UltimateRAG
from src.comparative_rag import ComparativeRAG


router = APIRouter()
logger = logging.getLogger(__name__)


async def generate_sse_events(data_generator) -> AsyncGenerator[str, None]:
    """Convert data generator to SSE format."""
    try:
        for chunk in data_generator:
            if chunk:
                # SSE format: data: {json}\n\n
                yield f"data: {json.dumps({'token': chunk})}\n\n"
                await asyncio.sleep(0.01)  # Small delay for smooth streaming

        yield f"data: {json.dumps({'type': 'complete'})}\n\n"
    except Exception as e:
        yield f"data: {json.dumps({'error': str(e)})}\n\n"


@router.get("/search")
async def stream_search(
    q: str = Query(..., description="Arama sorgusu"),
    source: str = Query(default="quran", description="quran veya bible"),
    token: str = Query(
        ...,
        description="JWT access token (required for SSE - EventSource can't send headers)",
    ),
    db: AsyncSession = Depends(get_db),
):
    """Stream search results with AI answer generation.

    Note: SSE/EventSource API doesn't support custom headers, so token must be passed as query param.
    """
    current_user = await get_current_user_from_token(token, db)
    await check_rate_limit(current_user, db)

    # Save to history
    history = SearchHistory(
        user_id=current_user.id,
        query=q,
        search_type=f"stream_search_{source}",
        result_count=None,
    )
    db.add(history)
    await db.commit()

    async def generate():
        logger.info(f"[SSE /search] Starting stream for query: {q}, source: {source}")
        rag = UltimateRAG()

        # First, send search status
        yield f"data: {json.dumps({'status': 'searching', 'message': 'Aranıyor...'})}\n\n"
        logger.info("[SSE /search] Sent search status")
        await asyncio.sleep(0.1)

        # Perform search
        if source == "quran":
            results = rag.search_quran(q, top_k=10)
        elif source in ["ot", "nt", "apocrypha"]:
            results = rag.search_bible(
                q, translation="kjva", testament=source, top_k=10
            )
        else:
            results = rag.search_bible(q, top_k=10)

        # Send results count
        yield f"data: {json.dumps({'status': 'found', 'count': len(results)})}\n\n"
        await asyncio.sleep(0.1)

        # Send "generating" status
        yield f"data: {json.dumps({'status': 'generating', 'message': 'Yanıt oluşturuluyor...'})}\n\n"
        yield ": heartbeat\n\n"  # Keep connection alive during LLM call
        logger.info("[SSE /search] Sent generating status + heartbeat, calling LLM...")
        await asyncio.sleep(0.1)

        # Generate answer (simulated streaming - actual LLM may not stream)
        try:
            logger.info("[SSE /search] Starting LLM call...")
            if source == "quran":
                answer = rag.ask_quran(q)
            elif source in ["ot", "nt", "apocrypha"]:
                answer = rag.ask_bible(q, translation="kjva", testament=source)
            else:
                answer = rag.ask_bible(q)

            # Stream the answer token by token
            # Handle both dict and AnswerResult dataclass responses
            if hasattr(answer, "text"):
                answer_text = answer.text
            elif hasattr(answer, "answer"):
                answer_text = answer.answer
            elif isinstance(answer, dict):
                answer_text = answer.get("answer", "") or answer.get("text", "")
            else:
                answer_text = str(answer)
            words = answer_text.split()

            logger.info(
                f"[SSE /search] LLM returned answer, streaming {len(words)} words"
            )
            for i, word in enumerate(words):
                yield f"data: {json.dumps({'type': 'token', 'content': word + ' '})}\n\n"
                await asyncio.sleep(0.03)  # 30ms per word

            logger.info("[SSE /search] Finished streaming words, sending citations")
            # Send citations
            if hasattr(answer, "citations"):
                citations = answer.citations
            elif isinstance(answer, dict):
                citations = answer.get("citations", [])
            else:
                citations = []
            yield f"data: {json.dumps({'citations': citations})}\n\n"

            # Build verse_details and results_data from search results
            verse_details: dict[str, dict] = {}
            results_data = []

            for r in results:
                # Determine source and build reference string
                if source == "quran":
                    # Quran result: use surah_name:verse_id format
                    ref_str = (
                        f"{r.surah_name}:{r.verse_id}"
                        if hasattr(r, "surah_name")
                        else ""
                    )
                    ref, detail = extract_quran_verse_detail(r)
                    if ref not in verse_details:
                        verse_details[ref] = detail.model_dump()
                    result_source = "quran"
                else:
                    # Bible result: use book_name chapter:verse format
                    ref_str = (
                        f"{r.book_name} {r.chapter}:{r.verse}"
                        if hasattr(r, "book_name")
                        else ""
                    )
                    # Map source to bible_ot, bible_nt, or bible_apocrypha
                    if source == "ot":
                        bible_source = "bible_ot"
                    elif source == "nt":
                        bible_source = "bible_nt"
                    else:
                        bible_source = "bible_apocrypha"
                    ref, detail = extract_bible_verse_detail(r, bible_source)
                    if ref not in verse_details:
                        verse_details[ref] = detail.model_dump()
                    result_source = bible_source

                results_data.append(
                    {
                        "source": result_source,
                        "reference": ref_str,
                        "text": r.text if hasattr(r, "text") else str(r),
                        "score": r.score if hasattr(r, "score") else 0.0,
                    }
                )

            # Send verse_details before complete (so frontend has it ready for lookups)
            yield f"data: {json.dumps({'verse_details': verse_details})}\n\n"
            await asyncio.sleep(0.05)

            logger.info("[SSE /search] Stream complete, sending complete with results")
            yield f"data: {
                json.dumps(
                    {
                        'type': 'complete',
                        'result': {
                            'results': results_data,
                            'answer': answer_text,
                            'citations': citations,
                        },
                    }
                )
            }\n\n"

        except Exception as e:
            logger.error(f"[SSE /search] Error during generation: {e}")
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
            yield f"data: {json.dumps({'type': 'complete'})}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/compare")
async def stream_compare(
    topic: str = Query(..., description="Karşılaştırma konusu"),
    token: str = Query(
        ...,
        description="JWT access token (required for SSE - EventSource can't send headers)",
    ),
    db: AsyncSession = Depends(get_db),
):
    """Stream comparative analysis with multi-agent output.

    Note: SSE/EventSource API doesn't support custom headers, so token must be passed as query param.
    """
    current_user = await get_current_user_from_token(token, db)
    await check_rate_limit(current_user, db)

    # Save to history
    history = SearchHistory(
        user_id=current_user.id,
        query=topic,
        search_type="stream_compare",
        result_count=None,
    )
    db.add(history)
    await db.commit()

    async def generate() -> AsyncGenerator[str, None]:
        logger.info(f"[COMPARE] Starting compare for topic: {topic}")

        start_time = time.time()

        try:
            logger.info("[COMPARE] Creating ComparativeRAG instance...")
            rag = ComparativeRAG(verbose=True)
            logger.info("[COMPARE] ComparativeRAG created successfully")
        except Exception as e:
            logger.error(f"[COMPARE] Failed to create RAG: {e}")
            logger.error(traceback.format_exc())
            yield f"data: {json.dumps({'error': f'RAG creation failed: {str(e)}'})}\n\n"
            yield f"data: {json.dumps({'type': 'complete'})}\n\n"
            return

        # Status updates
        yield f"data: {json.dumps({'status': 'analyzing', 'message': 'Metinler analiz ediliyor...'})}\n\n"
        yield ": heartbeat\n\n"
        await asyncio.sleep(0.1)

        try:
            # Step 1: Get search results first (same pattern as non-streaming endpoint)
            logger.info("[COMPARE] Starting search_all...")
            search_result = rag.search_all(topic)
            logger.info(
                f"[COMPARE] search_all completed, found {len(search_result.quran)} Quran, "
                f"{len(search_result.ot)} OT, {len(search_result.nt)} NT, {len(search_result.apocrypha)} Apocrypha"
            )
            yield ": heartbeat\n\n"

            # Step 2: Build verse_details from search results (using shared helper)
            verse_details = build_verse_details(
                quran_results=search_result.quran,
                ot_results=search_result.ot,
                nt_results=search_result.nt,
                apocrypha_results=search_result.apocrypha,
                as_dict=True,
            )

            # Send verse_details BEFORE streaming text (so frontend has it ready for lookups)
            yield f"data: {json.dumps({'verse_details': verse_details})}\n\n"
            yield ": heartbeat\n\n"

            # Step 3: Generate multi-agent answer using search results
            logger.info("[COMPARE] Starting multi_agent_generator.generate...")
            result = rag.multi_agent_generator.generate(
                query=topic,
                quran_verses=search_result.quran,
                ot_verses=search_result.ot,
                nt_verses=search_result.nt,
                apocrypha_verses=search_result.apocrypha,
            )
            logger.info(
                f"[COMPARE] multi_agent_generator completed, result type: {type(result)}"
            )

            # Build structured paragraphs (using shared helper)
            paragraphs = build_paragraphs(result, as_dict=True)

            logger.info(
                f"[COMPARE] Streaming {len(paragraphs)} structured paragraphs..."
            )

            # Stream paragraphs one by one
            for idx, para in enumerate(paragraphs, 1):
                yield f"data: {json.dumps({'type': 'paragraph', 'data': para})}\n\n"
                yield ": heartbeat\n\n"
                logger.info(
                    f"[COMPARE] Sent paragraph {idx}/{len(paragraphs)}: {para['title']}"
                )
                await asyncio.sleep(0.1)  # Small delay for UI smoothness

            # Calculate and send complete statistics
            total_citations = sum(len(refs) for refs in result.citations.values())
            total_verses = sum(
                result.verses_provided.values()
            )  # Align with batch endpoint
            latency_ms = int((time.time() - start_time) * 1000)

            stats_data = {
                "confidence": result.confidence,
                "confidence_breakdown": getattr(result, "confidence_breakdown", None),
                "latency_ms": latency_ms,
                "total_verses": total_verses,
                "total_citations": total_citations,
            }
            yield f"data: {json.dumps({'type': 'stats', 'data': stats_data})}\n\n"
            logger.info(
                f"[COMPARE] Sent stats: {total_verses} verses, {total_citations} citations, {latency_ms}ms"
            )

            logger.info("[COMPARE] Streaming completed successfully")

        except Exception as e:
            logger.error(f"[COMPARE] Error during compare: {e}")
            logger.error(traceback.format_exc())
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

        yield f"data: {json.dumps({'type': 'complete'})}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
