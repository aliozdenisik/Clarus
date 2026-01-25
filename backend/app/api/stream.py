"""SSE Streaming API routes for real-time LLM responses."""

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import AsyncGenerator
import asyncio
import json
import sys
import os
from dotenv import load_dotenv

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
from src.ultimate_rag import UltimateRAG
from src.comparative_rag import ComparativeRAG


router = APIRouter()


async def generate_sse_events(data_generator) -> AsyncGenerator[str, None]:
    """Convert data generator to SSE format."""
    try:
        for chunk in data_generator:
            if chunk:
                # SSE format: data: {json}\n\n
                yield f"data: {json.dumps({'token': chunk})}\n\n"
                await asyncio.sleep(0.01)  # Small delay for smooth streaming

        yield f"data: {json.dumps({'done': True})}\n\n"
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
        user_id=current_user.id, query=q, search_type=f"stream_search_{source}"
    )
    db.add(history)
    await db.commit()

    async def generate():
        rag = UltimateRAG()

        # First, send search status
        yield f"data: {json.dumps({'status': 'searching', 'message': 'Aranıyor...'})}\n\n"
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
        await asyncio.sleep(0.1)

        # Generate answer (simulated streaming - actual LLM may not stream)
        try:
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

            for i, word in enumerate(words):
                yield f"data: {json.dumps({'token': word + ' '})}\n\n"
                await asyncio.sleep(0.03)  # 30ms per word

            # Send citations
            if hasattr(answer, "citations"):
                citations = answer.citations
            elif isinstance(answer, dict):
                citations = answer.get("citations", [])
            else:
                citations = []
            yield f"data: {json.dumps({'citations': citations})}\n\n"

        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

        yield f"data: {json.dumps({'done': True})}\n\n"

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
        user_id=current_user.id, query=topic, search_type="stream_compare"
    )
    db.add(history)
    await db.commit()

    async def generate():
        import logging
        import traceback

        logger = logging.getLogger(__name__)

        logger.info(f"[COMPARE] Starting compare for topic: {topic}")
        print(f"[COMPARE] Starting compare for topic: {topic}")

        try:
            logger.info("[COMPARE] Creating ComparativeRAG instance...")
            print("[COMPARE] Creating ComparativeRAG instance...")
            rag = ComparativeRAG(verbose=True)
            logger.info("[COMPARE] ComparativeRAG created successfully")
            print("[COMPARE] ComparativeRAG created successfully")
        except Exception as e:
            logger.error(f"[COMPARE] Failed to create RAG: {e}")
            print(f"[COMPARE] Failed to create RAG: {e}")
            traceback.print_exc()
            yield f"data: {json.dumps({'error': f'RAG creation failed: {str(e)}'})}\n\n"
            yield f"data: {json.dumps({'done': True})}\n\n"
            return

        # Status updates
        yield f"data: {json.dumps({'status': 'analyzing', 'message': 'Metinler analiz ediliyor...'})}\n\n"
        await asyncio.sleep(0.1)

        try:
            logger.info("[COMPARE] Starting compare_multi_agent...")
            print("[COMPARE] Starting compare_multi_agent...")
            result = rag.compare_multi_agent(topic)
            logger.info(
                f"[COMPARE] compare_multi_agent completed, result type: {type(result)}"
            )
            print(
                f"[COMPARE] compare_multi_agent completed, result type: {type(result)}"
            )

            # Get analysis text - handle both MultiAgentAnswer and dict
            if hasattr(result, "to_essay"):
                logger.info("[COMPARE] Using to_essay() method")
                print("[COMPARE] Using to_essay() method")
                analysis = result.to_essay()
            elif hasattr(result, "full_text"):
                analysis = result.full_text
            elif isinstance(result, dict):
                analysis = result.get("analysis", "")
            else:
                analysis = str(result)

            logger.info(f"[COMPARE] Analysis length: {len(analysis)} chars")
            print(f"[COMPARE] Analysis length: {len(analysis)} chars")

            # Stream section by section
            sections = analysis.split("##")
            logger.info(f"[COMPARE] Streaming {len(sections)} sections...")
            print(f"[COMPARE] Streaming {len(sections)} sections...")

            for section in sections:
                if section.strip():
                    # Stream each word
                    words = section.split()
                    yield f"data: {json.dumps({'token': '## '})}\n\n"

                    for word in words:
                        yield f"data: {json.dumps({'token': word + ' '})}\n\n"
                        await asyncio.sleep(0.02)

                    yield f"data: {json.dumps({'token': '\\n\\n'})}\n\n"

            # Send metadata
            confidence = (
                getattr(result, "confidence", 0)
                if hasattr(result, "confidence")
                else result.get("confidence", 0)
                if isinstance(result, dict)
                else 0
            )
            yield f"data: {json.dumps({'confidence': confidence, 'latency': 0})}\n\n"
            logger.info("[COMPARE] Streaming completed successfully")
            print("[COMPARE] Streaming completed successfully")

        except Exception as e:
            logger.error(f"[COMPARE] Error during compare: {e}")
            print(f"[COMPARE] Error during compare: {e}")
            traceback.print_exc()
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

        yield f"data: {json.dumps({'done': True})}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
