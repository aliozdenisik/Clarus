#!/usr/bin/env python3
"""Backfill missing Turkish translations in qm_root_etymologies.

Reads rows that lack definition_tr, translates via OpenRouter LLM,
and UPDATEs them in-place — without touching other columns.

Usage:
  uv run python scripts/backfill_translations.py
  uv run python scripts/backfill_translations.py --workers 10
  uv run python scripts/backfill_translations.py --dry-run
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import re
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import requests
from pybreaker import CircuitBreakerError
from sqlalchemy import create_engine, text
from tenacity import RetryError, retry, retry_if_exception, stop_after_attempt, wait_exponential

sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:54322/postgres",
).replace("postgresql+asyncpg://", "postgresql://")

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
TRANSLATION_MODEL = "google/gemini-2.5-flash"
DEFAULT_WORKERS = 20
DEFAULT_TIMEOUT = 90.0

LANE_SYSTEM_PROMPT = (
    "You are a Quranic Arabic lexicography expert specializing in classical Arabic roots. "
    "Translate the following Lane's Arabic-English Lexicon definition to Turkish. "
    "This definition describes a Quranic Arabic root — preserve Islamic and Quranic terminology "
    "(e.g., 'tövbe' for repentance, 'salat' for prayer, 'sadaka' for charity). "
    "Use academic Turkish suitable for a Quran concordance. Return JSON: "
    '{"translation": "...", "confidence": 0.0-1.0}'
)

LANE_LONG_SYSTEM_PROMPT = (
    "You are a Quranic Arabic lexicography expert specializing in classical Arabic roots. "
    "Translate the following Lane's Arabic-English Lexicon definition to Turkish COMPLETELY. "
    "This is a LONG definition — translate ALL meanings, usages, citations and examples faithfully. "
    "Do NOT summarize or shorten. Provide a FULL, comprehensive Turkish translation. "
    "Preserve Islamic and Quranic terminology (e.g., 'tövbe' for repentance, 'salat' for prayer). "
    "Preserve Lane's scholarly references (S, K, TA, Msb etc.) as-is. "
    "Use academic Turkish suitable for a Quran concordance. Return JSON: "
    '{"translation": "...", "confidence": 0.0-1.0}'
)

LONG_DEFINITION_THRESHOLD = 1500

CORPUS_SYSTEM_PROMPT = (
    "You are a Quranic Arabic lexicography expert. "
    "Given an Arabic root and its Quran frequency, provide a concise Turkish definition "
    "of the root's primary meaning in Quranic context. "
    "Use Islamic and Quranic terminology (e.g., 'tövbe', 'salat', 'sadaka'). "
    "Use academic Turkish suitable for a Quran concordance. Return JSON: "
    '{"translation": "...", "confidence": 0.0-1.0}'
)

_TRANSLATION_RE = re.compile(r'"translation"\s*:\s*"((?:[^"\\]|\\.)*)"', re.DOTALL)
_CONFIDENCE_RE = re.compile(r'"confidence"\s*:\s*([\d.]+)')

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Rate limit / throttle
# ---------------------------------------------------------------------------
_throttle_lock = threading.Lock()
_throttle_until = 0.0


def _throttle_wait() -> None:
    """Block if we're in a rate-limit backoff window."""
    global _throttle_until
    sleep_for = 0.0
    with _throttle_lock:
        now = time.monotonic()
        if now < _throttle_until:
            sleep_for = _throttle_until - now
    if sleep_for > 0:
        logger.info("Rate-limit backoff: sleeping %.1fs", sleep_for)
        time.sleep(sleep_for)


def _throttle_set(seconds: float) -> None:
    global _throttle_until
    with _throttle_lock:
        _throttle_until = max(_throttle_until, time.monotonic() + seconds)


# ---------------------------------------------------------------------------
# Translation helpers
# ---------------------------------------------------------------------------
def _is_retryable(exc: BaseException) -> bool:
    if isinstance(exc, requests.exceptions.HTTPError):
        resp = exc.response
        if resp is not None and resp.status_code in (429, 500, 502, 503, 504):
            return True
    return isinstance(exc, requests.exceptions.ConnectionError | requests.exceptions.Timeout)


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=0.5, min=1, max=10),
    retry=retry_if_exception(_is_retryable),
)
def _call_openrouter(
    api_key: str,
    system_prompt: str,
    user_content: str,
    timeout: float = DEFAULT_TIMEOUT,
    max_tokens: int = 600,
) -> tuple[str | None, float | None]:
    """Single LLM translation call → (translation_text, confidence)."""
    _throttle_wait()

    resp = requests.post(
        OPENROUTER_URL,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": TRANSLATION_MODEL,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content},
            ],
            "response_format": {"type": "json_object"},
            "max_tokens": max_tokens,
            "temperature": 0.1,
        },
        timeout=timeout,
    )

    if resp.status_code == 429:
        retry_after = resp.headers.get("Retry-After")
        backoff = 5.0
        if retry_after:
            try:
                backoff = max(1.0, float(retry_after))
            except ValueError:
                pass
        _throttle_set(min(backoff, 60.0))

    resp.raise_for_status()

    data = resp.json()
    choices = data.get("choices", [])
    if not choices:
        return None, None

    content = choices[0].get("message", {}).get("content", "")
    if not content:
        return None, None

    # Parse JSON response — prefer proper JSON parsing, fall back to regex
    sanitized = re.sub(r"[\x00-\x1f\x7f]", " ", content)

    # Strategy 1: Direct JSON parse (handles most cases including embedded quotes)
    translation = None
    confidence = None
    try:
        parsed = json.loads(sanitized)
        if isinstance(parsed, dict):
            translation = parsed.get("translation") or parsed.get("çeviri") or parsed.get("Translation")
            conf_val = parsed.get("confidence") or parsed.get("güven")
            if conf_val is not None:
                try:
                    confidence = max(0.0, min(1.0, float(conf_val)))
                except (ValueError, TypeError):
                    pass
    except json.JSONDecodeError:
        pass

    # Strategy 2: Regex fallback for malformed JSON
    if not translation:
        tr_match = _TRANSLATION_RE.search(sanitized)
        conf_match = _CONFIDENCE_RE.search(sanitized)

        if tr_match is None:
            return None, None

        raw = tr_match.group(1)
        try:
            translation = json.loads(f'"{raw}"')
        except json.JSONDecodeError:
            translation = raw.replace(r"\n", " ").replace(r"\t", " ").replace(r"\"", '"').strip()

        if conf_match and confidence is None:
            try:
                confidence = max(0.0, min(1.0, float(conf_match.group(1))))
            except ValueError:
                pass

    return (translation.strip() if translation else None), confidence


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> int:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S",
    )

    parser = argparse.ArgumentParser(description="Backfill missing Turkish translations")
    parser.add_argument("--workers", type=int, default=DEFAULT_WORKERS)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--limit", type=int, default=0, help="Max rows to translate (0=all)")
    args = parser.parse_args()

    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        logger.error("OPENROUTER_API_KEY not set — cannot translate")
        return 1

    engine = create_engine(DATABASE_URL, future=True)

    # Fetch rows missing Turkish translation
    with engine.connect() as conn:
        query = """
            SELECT id, root, root_buckwalter, definition_en, source, quran_frequency
            FROM qm_root_etymologies
            WHERE definition_tr IS NULL OR definition_tr = ''
            ORDER BY quran_frequency DESC
        """
        if args.limit > 0:
            query += f" LIMIT {args.limit}"
        rows = conn.execute(text(query)).fetchall()

    total = len(rows)
    if total == 0:
        logger.info("✅ No missing translations — nothing to do")
        return 0

    logger.info("Found %d rows missing Turkish translations", total)
    logger.info("Workers: %d, dry-run: %s", args.workers, args.dry_run)

    # Translate in parallel
    cancel_event = threading.Event()
    progress_lock = threading.Lock()
    done_count = 0
    success_count = 0
    fail_count = 0
    start_time = time.monotonic()

    def translate_row(row):
        nonlocal done_count, success_count, fail_count

        row_id = row[0]
        root = row[1]
        root_bw = row[2]
        def_en = row[3]
        freq = row[5]

        if cancel_event.is_set():
            return None

        try:
            if def_en and def_en.strip():
                if len(def_en) > LONG_DEFINITION_THRESHOLD:
                    prompt = LANE_LONG_SYSTEM_PROMPT
                    user_content = def_en[:6000]
                else:
                    prompt = LANE_SYSTEM_PROMPT
                    user_content = def_en
                translation, confidence = _call_openrouter(api_key, prompt, user_content, max_tokens=4096)
                tr_source = "llm_gemini"
            else:
                corpus_prompt = f"Arabic root: {root}, Quran frequency: {freq}"
                translation, confidence = _call_openrouter(api_key, CORPUS_SYSTEM_PROMPT, corpus_prompt)
                tr_source = "llm_generated"

            if translation:
                with progress_lock:
                    success_count += 1
                return (row_id, translation, confidence, tr_source)
            else:
                with progress_lock:
                    fail_count += 1
                return None

        except (requests.exceptions.HTTPError, RetryError) as exc:
            resp = getattr(exc, "response", None)
            if resp is not None and resp.status_code == 401:
                logger.error("API key rejected — aborting")
                cancel_event.set()
            logger.warning("Translation failed for %s (%s): %s", root, root_bw, exc)
            with progress_lock:
                fail_count += 1
            return None
        except CircuitBreakerError:
            logger.warning("Circuit breaker open — aborting")
            cancel_event.set()
            return None
        except Exception as exc:
            logger.warning("Unexpected error for %s: %s", root, exc)
            with progress_lock:
                fail_count += 1
            return None
        finally:
            with progress_lock:
                done_count += 1
                if done_count % 50 == 0 or done_count == total:
                    elapsed = time.monotonic() - start_time
                    rate = done_count / elapsed if elapsed > 0 else 0
                    remaining = total - done_count
                    eta = remaining / rate if rate > 0 else 0
                    logger.info(
                        "Progress: %d/%d (✅ %d ❌ %d) rate=%.1f/s elapsed=%.0fs eta=%.0fs",
                        done_count,
                        total,
                        success_count,
                        fail_count,
                        rate,
                        elapsed,
                        eta,
                    )

    # Execute
    updates: list[tuple] = []
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = {executor.submit(translate_row, row): row for row in rows}
        for future in as_completed(futures):
            result = future.result()
            if result is not None:
                updates.append(result)

    elapsed = time.monotonic() - start_time
    logger.info("")
    logger.info("═══ Backfill Complete ═══")
    logger.info("Total processed: %d", done_count)
    logger.info("Successful translations: %d", len(updates))
    logger.info("Failed: %d", fail_count)
    logger.info("Elapsed: %.0fs", elapsed)

    if args.dry_run:
        logger.info("[DRY RUN] Would update %d rows", len(updates))
        return 0

    if not updates:
        logger.warning("No translations produced — nothing to update")
        return 1

    # Batch UPDATE
    logger.info("Writing %d translations to database...", len(updates))
    batch_size = 100
    updated = 0
    with engine.begin() as conn:
        for i in range(0, len(updates), batch_size):
            batch = updates[i : i + batch_size]
            for row_id, translation, confidence, tr_source in batch:
                conn.execute(
                    text("""
                        UPDATE qm_root_etymologies
                        SET definition_tr = :tr,
                            tr_translation_confidence = :conf,
                            tr_translation_source = :src,
                            updated_at = NOW()
                        WHERE id = :id
                    """),
                    {"tr": translation, "conf": confidence, "src": tr_source, "id": row_id},
                )
                updated += 1

    logger.info("✅ Updated %d rows in qm_root_etymologies", updated)

    # Verify
    with engine.connect() as conn:
        still_missing = conn.execute(
            text("SELECT COUNT(*) FROM qm_root_etymologies WHERE definition_tr IS NULL OR definition_tr = ''")
        ).scalar()
        total_rows = conn.execute(text("SELECT COUNT(*) FROM qm_root_etymologies")).scalar()
        has_tr = (total_rows or 0) - (still_missing or 0)
        pct = has_tr / total_rows * 100 if total_rows else 0

    logger.info("Post-backfill: %d/%d rows have Turkish translation (%.1f%%)", has_tr, total_rows, pct)
    if still_missing:
        logger.info("Still missing: %d rows", still_missing)

    engine.dispose()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
