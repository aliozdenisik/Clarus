"""SSE Streaming API routes for real-time LLM responses."""

import asyncio
import json
import logging
import os
import queue
import sys
import time
import traceback
from typing import AsyncGenerator, Literal

from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

# Load .env before importing RAG modules
env_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), ".env"
)
load_dotenv(env_path)

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from typing import Optional  # noqa: E402

from app.api.auth import check_rate_limit  # noqa: E402
from app.api.compare import extract_bible_verse_detail, extract_quran_verse_detail  # noqa: E402
from app.api.compare_helpers import (  # noqa: E402
    build_paragraphs,
    build_verse_details,
    strip_markdown_headers,
)
from app.db import get_db  # noqa: E402
from app.models import SearchHistory  # noqa: E402
from app.schemas.common import DEFAULT_TRANSLATOR, TranslatorType  # noqa: E402
from src.comparative_rag import ComparativeRAG  # noqa: E402
from src.query_translator import QueryTranslator, TranslationError  # noqa: E402
from src.ultimate_rag import UltimateRAG  # noqa: E402

router = APIRouter()
logger = logging.getLogger(__name__)


async def get_current_user_from_sse(db: AsyncSession, request: Request):
    """
    Validate auth for SSE endpoints via Better Auth session cookie.

    Reads the session cookie, validates it via DB lookup, and returns
    user dict. SSE endpoints use GET requests so cookies are the only
    viable auth mechanism (no Authorization header in EventSource).

    Args:
        db: Database session
        request: Request object for cookie access

    Returns:
        User dict with id, email, name, and other profile fields

    Raises:
        HTTPException 401: No valid session cookie or session expired
    """
    from datetime import datetime, timezone

    from fastapi import HTTPException
    from sqlalchemy import select

    from app.auth.api_key_validator import _resolve_user_by_id
    from app.models import BetterAuthSession

    cookie_token = (
        request.cookies.get("better_auth.session_token")
        or request.cookies.get("better-auth.session_token")
        or request.cookies.get("__Secure-better-auth.session_token")
    )

    if not cookie_token:
        raise HTTPException(status_code=401, detail="Authentication required")

    from urllib.parse import unquote

    # Better Auth cookie format: <token>.<hmac-signature> (URL-encoded)
    # The DB stores only the raw token without the signature.
    raw_token = (
        unquote(cookie_token).rsplit(".", 1)[0]
        if "." in unquote(cookie_token)
        else unquote(cookie_token)
    )

    session_result = await db.execute(
        select(BetterAuthSession).where(BetterAuthSession.token == raw_token)
    )
    session = session_result.scalar_one_or_none()

    if not session:
        raise HTTPException(status_code=401, detail="Invalid session")

    if session.expires_at.replace(tzinfo=timezone.utc) <= datetime.now(timezone.utc):
        raise HTTPException(status_code=401, detail="Session expired")

    logger.debug("SSE auth: Authenticated via session cookie")
    return await _resolve_user_by_id(session.user_id, db, "get_current_user_from_sse")


@router.get("/search")
async def stream_search(
    request: Request,
    q: str = Query(..., description="Arama sorgusu"),
    source: Literal["quran", "ot", "nt", "apocrypha"] = Query(
        default="quran", description="Source collection: quran, ot, nt, or apocrypha"
    ),
    language: Optional[str] = Query(None, description="Detected user language (ISO 639-1)"),
    translator: Optional[TranslatorType] = Query(
        default=DEFAULT_TRANSLATOR,
        description="Quran translator (diyanet, yazir, ates, bulac, ozturk, vakfi, yildirim, yuksel)",  # noqa: E501
    ),
    db: AsyncSession = Depends(get_db),
):
    """Stream search results with AI answer generation.

    Authentication: Uses session cookie.
    """
    current_user = await get_current_user_from_sse(db, request)
    await check_rate_limit(current_user, db)

    # Save to history
    history = SearchHistory(
        user_id=current_user["id"],
        query=q,
        search_type=f"stream_search_{source}",
        result_count=None,
    )
    db.add(history)
    await db.commit()

    async def generate():
        logger.info(f"[SSE /search] Starting stream for query: {q}, source: {source}")
        rag = UltimateRAG()
        query_translator = QueryTranslator()

        # First, send search status
        yield f"data: {json.dumps({'status': 'searching', 'message': 'Aranıyor...'})}\n\n"
        logger.info("[SSE /search] Sent search status")
        await asyncio.sleep(0.1)

        # Perform ask (which includes search + answer generation)
        # This eliminates the duplicate search call
        try:
            logger.info("[SSE /search] Starting ask call (search + answer generation)...")
            quran_translator = translator or DEFAULT_TRANSLATOR
            if source == "quran":
                ask_result = await rag.ask_quran(q, translator=quran_translator, top_k=10)
            elif source in ["ot", "nt", "apocrypha"]:
                ask_result = await rag.ask_bible(q, translation="kjva", testament=source, top_k=10)
            else:
                ask_result = await rag.ask_bible(q, top_k=10)

            # Extract results and answer from ask_result
            results = ask_result.search_results
            answer = ask_result.answer

            # Send results count
            yield f"data: {json.dumps({'status': 'found', 'count': len(results)})}\n\n"
            await asyncio.sleep(0.1)

            # Send "generating" status (already done, but keep for UI consistency)
            yield f"data: {json.dumps({'status': 'generating', 'message': 'Yanıt oluşturuluyor...'})}\n\n"  # noqa: E501
            yield ": heartbeat\n\n"  # Keep connection alive
            logger.info("[SSE /search] Ask call completed, streaming answer...")
            await asyncio.sleep(0.1)

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

        except Exception as e:
            logger.error(f"[SSE /search] Error during ask: {e}")
            yield f"data: {json.dumps({'error': 'An internal error occurred'})}\n\n"
            yield f"data: {json.dumps({'type': 'complete'})}\n\n"
            return

        try:
            # Detect language for response translation
            detected_language = language  # From query param
            if not detected_language:
                try:
                    detect_result = query_translator.translate_query(q, corpus=None)
                    detected_language = detect_result.detected_language
                except Exception:
                    detected_language = None

            # Translate answer if user's language differs from corpus language
            if detected_language and detected_language not in ("tr", "en"):
                try:
                    yield f"data: {json.dumps({'status': 'translating', 'message': 'Yanıt çevriliyor...'})}\n\n"  # noqa: E501
                    answer_text = query_translator.translate_response(
                        answer_text,
                        target_lang=detected_language,
                        preserve_citations=True,
                    )
                except TranslationError:
                    logger.error(
                        "Search stream response translation failed, sending original",
                        exc_info=True,
                    )

            words = answer_text.split()

            logger.info(f"[SSE /search] LLM returned answer, streaming {len(words)} words")
            for i, word in enumerate(words):
                yield f"data: {json.dumps({'type': 'token', 'content': word + ' '})}\n\n"
                await asyncio.sleep(0.03)  # 30ms per word

            logger.info("[SSE /search] Finished streaming words, sending citations")
            # Send citations
            if isinstance(answer, dict):
                citations = answer.get("citations", [])
            elif hasattr(answer, "citations"):
                citations = getattr(answer, "citations", [])
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
                    ref_str = f"{r.surah_name}:{r.verse_id}" if hasattr(r, "surah_name") else ""
                    ref, detail = extract_quran_verse_detail(r)
                    if ref not in verse_details:
                        verse_details[ref] = detail.model_dump()
                    result_source = "quran"
                else:
                    # Bible result: use book_name chapter:verse format
                    ref_str = (
                        f"{r.book_name} {r.chapter}:{r.verse}" if hasattr(r, "book_name") else ""
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
            yield f"data: {json.dumps({'type': 'complete', 'result': {'results': results_data, 'answer': answer_text, 'citations': citations}})}\n\n"  # noqa: E501

        except Exception as e:
            logger.error(f"[SSE /search] Error during generation: {e}")
            yield f"data: {json.dumps({'error': 'An internal error occurred'})}\n\n"
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
    request: Request,
    topic: str = Query(..., description="Karşılaştırma konusu"),
    collections: str = Query(
        "quran_tr,bible_ot,bible_nt,bible_apocrypha",
        description="Comma-separated list of collections to search (minimum 2)",
    ),
    language: Optional[str] = Query(None, description="Detected user language (ISO 639-1)"),
    translator: Optional[TranslatorType] = Query(
        default=DEFAULT_TRANSLATOR,
        description="Quran translator (diyanet, yazir, ates, bulac, ozturk, vakfi, yildirim, yuksel)",  # noqa: E501
    ),
    quran_keywords: Optional[list[str]] = Query(
        default=None,
        description="Optional Turkish keywords for Quran per-keyword search",
    ),
    bible_keywords: Optional[list[str]] = Query(
        default=None,
        description="Optional English keywords for Bible per-keyword search",
    ),
    db: AsyncSession = Depends(get_db),
):
    """Stream comparative analysis with multi-agent output.

    Authentication: Uses session cookie.

    Args:
        collections: Comma-separated collection names (e.g., 'quran_tr,bible_ot').
                    Valid values: quran_tr, bible_ot, bible_nt, bible_apocrypha
    """
    # Parse and validate collections
    # Valid collections: all quran_tr_* translators + bible collections
    valid_collections = {
        "quran_tr_diyanet",
        "quran_tr_yazir",
        "quran_tr_ates",
        "quran_tr_bulac",
        "quran_tr_ozturk",
        "quran_tr_vakfi",
        "quran_tr_yildirim",
        "quran_tr_yuksel",
        "bible_ot",
        "bible_nt",
        "bible_apocrypha",
        "bible_tr_ot",
        "bible_tr_nt",
    }
    collection_list = [c.strip() for c in collections.split(",") if c.strip() in valid_collections]
    if len(collection_list) < 2:
        raise HTTPException(
            status_code=400,
            detail="At least 2 valid collections required for comparison",
        )
    current_user = await get_current_user_from_sse(db, request)
    await check_rate_limit(current_user, db)

    # Save to history
    history = SearchHistory(
        user_id=current_user["id"],
        query=topic,
        search_type="stream_compare",
        result_count=None,
    )
    db.add(history)
    await db.commit()

    async def generate() -> AsyncGenerator[str, None]:
        logger.info(f"[COMPARE] Starting compare for topic: {topic}")

        start_time = time.time()

        # Thread-safe queue for progress events from sync callbacks
        progress_queue: queue.Queue = queue.Queue()

        def on_progress(step_id: str, message: str):
            """Callback invoked from sync code; pushes events to queue."""
            progress_queue.put((step_id, message))

        # Container for passing results out of the async generator helper
        _thread_result: dict = {}

        async def _run_with_progress(func, *args):
            """Run a blocking function in a thread while polling for progress events.

            Yields SSE-formatted progress events in real-time as the blocking
            function emits them via on_progress callback. Stores the function
            return value in _thread_result["value"].
            """
            loop = asyncio.get_event_loop()
            future = loop.run_in_executor(None, func, *args)

            # Poll queue every 300ms while the blocking call runs
            while not future.done():
                await asyncio.sleep(0.3)
                while not progress_queue.empty():
                    try:
                        step_id, message = progress_queue.get_nowait()
                        yield f"data: {json.dumps({'type': 'progress', 'step': step_id, 'message': message})}\n\n"  # noqa: E501
                    except queue.Empty:
                        break
                yield ": heartbeat\n\n"

            # Get the result (may raise)
            result = future.result()

            # Drain any remaining events
            while not progress_queue.empty():
                try:
                    step_id, message = progress_queue.get_nowait()
                    yield f"data: {json.dumps({'type': 'progress', 'step': step_id, 'message': message})}\n\n"  # noqa: E501
                except queue.Empty:
                    break

            _thread_result["value"] = result

        try:
            logger.info("[COMPARE] Creating ComparativeRAG instance...")
            rag = ComparativeRAG(verbose=True)
            compare_translator = QueryTranslator()
            logger.info("[COMPARE] ComparativeRAG created successfully")
        except Exception as e:
            logger.error(f"[COMPARE] Failed to create RAG: {e}")
            logger.error(traceback.format_exc())
            yield f"data: {json.dumps({'error': 'An internal error occurred'})}\n\n"
            yield f"data: {json.dumps({'type': 'complete'})}\n\n"
            return

        # Initial status
        yield f"data: {json.dumps({'type': 'progress', 'step': 'pipeline_started', 'message': 'Starting comparative analysis pipeline...'})}\n\n"  # noqa: E501
        yield ": heartbeat\n\n"
        await asyncio.sleep(0.1)

        try:
            # Step 1: Get search results (blocking call with real-time progress)
            quran_translator = translator or DEFAULT_TRANSLATOR
            logger.info(
                f"[COMPARE] Starting search_all with collections: {collection_list}, translator: {quran_translator}"  # noqa: E501
            )
            async for event in _run_with_progress(
                rag.search_all,
                topic,
                collection_list,
                on_progress,
                quran_keywords,
                bible_keywords,
                quran_translator,
            ):
                yield event
            search_result = _thread_result["value"]
            logger.info(
                f"[COMPARE] search_all completed, found {len(search_result.quran)} Quran, "
                f"{len(search_result.ot)} OT, {len(search_result.nt)} NT, {len(search_result.apocrypha)} Apocrypha"  # noqa: E501
            )

            # Step 2: Build verse_details from search results (using shared helper)
            yield f"data: {json.dumps({'type': 'progress', 'step': 'building_verse_details', 'message': 'Extracting verse metadata...'})}\n\n"  # noqa: E501
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

            # Step 3: Generate multi-agent answer (blocking call with real-time progress)
            logger.info("[COMPARE] Starting multi_agent_generator.generate...")
            async for event in _run_with_progress(
                rag.multi_agent_generator.generate,
                topic,
                search_result.quran,
                search_result.ot,
                search_result.nt,
                search_result.apocrypha,
                None,  # collection_stats (uses internal)
                on_progress,
            ):
                yield event
            result = _thread_result["value"]
            logger.info(f"[COMPARE] multi_agent_generator completed, result type: {type(result)}")

            # Build structured paragraphs (using shared helper)
            paragraphs = build_paragraphs(result, as_dict=False)

            # Determine detected language for response translation
            detected_language = language  # From query param (may be None)
            if not detected_language:
                detected_language = search_result.search_stats.get("detected_language")

            logger.info(
                f"[COMPARE] Streaming {len(paragraphs)} structured paragraphs..."
                + (
                    f" (translating to {detected_language})"
                    if detected_language and detected_language not in ("tr", "en")
                    else ""
                )
            )

            # Notify frontend if translation is happening
            if detected_language and detected_language not in ("tr", "en"):
                yield f"data: {json.dumps({'type': 'progress', 'step': 'translating_response', 'message': 'Translating response...'})}\n\n"  # noqa: E501

            # Stream paragraphs one by one (with per-paragraph translation)
            for idx, para in enumerate(paragraphs, 1):
                if isinstance(para, dict):
                    para_content = str(para.get("content", ""))
                    para_title = str(para.get("title", ""))
                else:
                    para_content = para.content
                    para_title = para.title

                if detected_language and detected_language not in ("tr", "en"):
                    try:
                        para_content = strip_markdown_headers(
                            compare_translator.translate_response(
                                para_content,
                                target_lang=detected_language,
                                preserve_citations=True,
                            )
                        )
                        if isinstance(para, dict):
                            para["content"] = para_content
                        else:
                            para.content = para_content
                        # Titles are kept as-is: standard section names
                        # that should stay consistent across languages
                    except TranslationError as e:
                        logger.error(
                            "Paragraph translation failed during SSE",
                            extra={"paragraph": idx, "error": str(e)},
                        )
                        # Graceful degradation: send untranslated paragraph
                para_payload = para if isinstance(para, dict) else para.model_dump()
                yield f"data: {json.dumps({'type': 'paragraph', 'data': para_payload})}\n\n"
                yield ": heartbeat\n\n"
                logger.info(f"[COMPARE] Sent paragraph {idx}/{len(paragraphs)}: {para_title}")
                await asyncio.sleep(0.1)  # Small delay for UI smoothness

            # Calculate and send complete statistics
            total_citations = sum(len(refs) for refs in result.citations.values())
            total_verses = sum(result.verses_provided.values())  # Align with batch endpoint
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
                f"[COMPARE] Sent stats: {total_verses} verses, {total_citations} citations, {latency_ms}ms"  # noqa: E501
            )

            logger.info("[COMPARE] Streaming completed successfully")

        except Exception as e:
            logger.error(f"[COMPARE] Error during compare: {e}")
            logger.error(traceback.format_exc())
            yield f"data: {json.dumps({'error': 'An internal error occurred'})}\n\n"

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
