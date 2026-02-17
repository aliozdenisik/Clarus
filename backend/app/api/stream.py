"""SSE Streaming API routes for real-time LLM responses."""

import asyncio
import json
import logging
import queue
import time
import traceback
from collections.abc import AsyncGenerator
from datetime import UTC
from typing import Any, Literal, cast

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.auth import check_rate_limit
from app.api.compare import extract_bible_verse_detail, extract_quran_verse_detail
from app.api.compare_helpers import (
    VALID_COMPARE_COLLECTIONS,
    build_paragraphs,
    build_verse_details,
    normalize_compare_collections,
    strip_markdown_headers,
)
from app.auth.api_key_validator import _resolve_user_by_id, extract_raw_session_token
from app.db import get_db
from app.i18n.detector import get_locale
from app.models import SearchHistory
from app.schemas.common import DEFAULT_TRANSLATOR, TranslatorType
from src.comparative_rag import ComparativeRAG
from src.query_translator import QueryTranslator, TranslationError
from src.ultimate_rag import UltimateRAG

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
    from datetime import datetime

    from fastapi import HTTPException
    from sqlalchemy import select

    from app.models import BetterAuthSession

    cookie_token = (
        request.cookies.get("better_auth.session_token")
        or request.cookies.get("better-auth.session_token")
        or request.cookies.get("__Secure-better-auth.session_token")
    )

    if not cookie_token:
        raise HTTPException(status_code=401, detail="Authentication required")

    raw_token = extract_raw_session_token(cookie_token)

    session_result = await db.execute(select(BetterAuthSession).where(BetterAuthSession.token == raw_token))
    session = session_result.scalar_one_or_none()

    if not session:
        raise HTTPException(status_code=401, detail="Invalid session")

    if session.expires_at.replace(tzinfo=UTC) <= datetime.now(UTC):
        raise HTTPException(status_code=401, detail="Session expired")

    logger.debug("SSE auth: Authenticated via session cookie")
    return await _resolve_user_by_id(session.user_id, db, "get_current_user_from_sse")


@router.get("/search")
async def stream_search(
    request: Request,
    q: str = Query(..., min_length=1, max_length=500, description="Arama sorgusu"),
    source: Literal["quran", "ot", "nt", "apocrypha"] = Query(
        default="quran", description="Source collection: quran, ot, nt, or apocrypha"
    ),
    language: str | None = Query(None, description="Detected user language (ISO 639-1)"),
    translator: TranslatorType | None = Query(
        default=DEFAULT_TRANSLATOR,
        description="Quran translator (diyanet, yazir, ates, bulac, ozturk, vakfi, yildirim, yuksel)",
    ),
    db: AsyncSession = Depends(get_db),
    locale: str = Depends(get_locale),
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
                ask_result = await rag.ask_quran(q, translator=quran_translator, top_k=10, locale=locale)
            elif source in ["ot", "nt", "apocrypha"]:
                ask_result = await rag.ask_bible(q, translation="kjva", testament=source, top_k=10, locale=locale)
            else:
                ask_result = await rag.ask_bible(q, top_k=10, locale=locale)

            # Extract results and answer from ask_result
            results = ask_result.search_results
            answer_obj: Any = ask_result.answer

            # Send results count
            yield f"data: {json.dumps({'status': 'found', 'count': len(results)})}\n\n"
            await asyncio.sleep(0.1)

            # Send "generating" status (already done, but keep for UI consistency)
            yield f"data: {json.dumps({'status': 'generating', 'message': 'Yanıt oluşturuluyor...'})}\n\n"
            yield ": heartbeat\n\n"  # Keep connection alive
            logger.info("[SSE /search] Ask call completed, streaming answer...")
            await asyncio.sleep(0.1)

            # Stream the answer token by token
            # Handle both dict and AnswerResult dataclass responses
            if hasattr(answer_obj, "text"):
                answer_text = answer_obj.text
            elif hasattr(answer_obj, "answer"):
                answer_text = answer_obj.answer
            elif isinstance(answer_obj, dict):
                answer_text = answer_obj.get("answer", "") or answer_obj.get("text", "")
            else:
                answer_text = str(answer_obj)

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
                    yield f"data: {json.dumps({'status': 'translating', 'message': 'Yanıt çevriliyor...'})}\n\n"
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
            for _i, word in enumerate(words):
                yield f"data: {json.dumps({'type': 'token', 'content': word + ' '})}\n\n"
                await asyncio.sleep(0.03)  # 30ms per word

            logger.info("[SSE /search] Finished streaming words, sending citations")
            # Send citations
            if isinstance(answer_obj, dict):
                citations = answer_obj.get("citations", [])
            else:
                citations = getattr(answer_obj, "citations", [])
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
                    ref_str = f"{r.book_name} {r.chapter}:{r.verse}" if hasattr(r, "book_name") else ""
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
            yield f"data: {json.dumps({'type': 'complete', 'result': {'results': results_data, 'answer': answer_text, 'citations': citations}})}\n\n"

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
    topic: str = Query(..., min_length=1, max_length=500, description="Karşılaştırma konusu"),
    collections: str = Query(
        "quran_tr,bible_ot,bible_nt,bible_apocrypha",
        description="Comma-separated list of collections to search (minimum 2)",
    ),
    language: str | None = Query(None, description="Detected user language (ISO 639-1)"),
    translator: TranslatorType | None = Query(
        default=DEFAULT_TRANSLATOR,
        description="Quran translator (diyanet, yazir, ates, bulac, ozturk, vakfi, yildirim, yuksel)",
    ),
    db: AsyncSession = Depends(get_db),
    locale: str = Depends(get_locale),
):
    """Stream comparative analysis with multi-agent output.

    Authentication: Uses session cookie.

    Args:
        collections: Comma-separated collection names (e.g., 'quran_tr,bible_ot').
                    Valid values: quran_tr (alias), quran_tr_*, bible_ot, bible_nt, bible_apocrypha
    """
    # Parse and validate collections
    quran_translator = translator or DEFAULT_TRANSLATOR
    requested_collections = [c.strip() for c in collections.split(",") if c.strip()]
    normalized_collections = normalize_compare_collections(requested_collections, quran_translator)
    collection_list = [c for c in normalized_collections if c in VALID_COMPARE_COLLECTIONS]
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
                        yield f"data: {json.dumps({'type': 'progress', 'step': step_id, 'message': message})}\n\n"
                    except queue.Empty:
                        break
                yield ": heartbeat\n\n"

            # Get the result (may raise)
            result = future.result()

            # Drain any remaining events
            while not progress_queue.empty():
                try:
                    step_id, message = progress_queue.get_nowait()
                    yield f"data: {json.dumps({'type': 'progress', 'step': step_id, 'message': message})}\n\n"
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
        yield f"data: {json.dumps({'type': 'progress', 'step': 'pipeline_started', 'message': 'Starting comparative analysis pipeline...'})}\n\n"
        yield ": heartbeat\n\n"
        await asyncio.sleep(0.1)

        try:
            # Step 1: Get search results (blocking call with real-time progress)
            logger.info(
                f"[COMPARE] Starting search_all with collections: {collection_list}, translator: {quran_translator}"
            )
            async for event in _run_with_progress(
                rag.search_all,
                topic,
                collection_list,
                on_progress,
                None,
                None,
                quran_translator,
            ):
                yield event
            search_result = _thread_result["value"]
            logger.info(
                f"[COMPARE] search_all completed, found {len(search_result.quran)} Quran, "
                f"{len(search_result.ot)} OT, {len(search_result.nt)} NT, {len(search_result.apocrypha)} Apocrypha"
            )

            # Step 2: Build verse_details from search results (using shared helper)
            yield f"data: {json.dumps({'type': 'progress', 'step': 'building_verse_details', 'message': 'Extracting verse metadata...'})}\n\n"
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
            paragraphs = cast("list[dict[str, Any]]", build_paragraphs(result, as_dict=True))

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
                yield f"data: {json.dumps({'type': 'progress', 'step': 'translating_response', 'message': 'Translating response...'})}\n\n"

            # Stream paragraphs one by one (with per-paragraph translation)
            for idx, para in enumerate(paragraphs, 1):
                if detected_language and detected_language not in ("tr", "en"):
                    try:
                        para["content"] = strip_markdown_headers(
                            compare_translator.translate_response(
                                para["content"],
                                target_lang=detected_language,
                                preserve_citations=True,
                            )
                        )
                        # Titles are kept as-is: standard section names
                        # that should stay consistent across languages
                    except TranslationError as e:
                        logger.error(
                            "Paragraph translation failed during SSE",
                            extra={"paragraph": idx, "error": str(e)},
                        )
                        # Graceful degradation: send untranslated paragraph
                yield f"data: {json.dumps({'type': 'paragraph', 'data': para})}\n\n"
                yield ": heartbeat\n\n"
                logger.info(f"[COMPARE] Sent paragraph {idx}/{len(paragraphs)}: {para['title']}")
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
            logger.info(f"[COMPARE] Sent stats: {total_verses} verses, {total_citations} citations, {latency_ms}ms")

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
