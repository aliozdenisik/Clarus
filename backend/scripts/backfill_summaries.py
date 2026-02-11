#!/usr/bin/env python3
"""Backfill plain Turkish and English summaries in qm_root_etymologies.

Reads rows that lack summary_tr or summary_en, generates 2-4 sentence summaries
via OpenRouter LLM, and UPDATEs them in-place — without touching other columns.

Usage:
  uv run python scripts/backfill_summaries.py
  uv run python scripts/backfill_summaries.py --workers 10
  uv run python scripts/backfill_summaries.py --dry-run
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
SUMMARY_MODEL = "google/gemini-2.5-flash"
DEFAULT_WORKERS = 20
DEFAULT_TIMEOUT = 45.0
MAX_SUMMARY_LENGTH = 200

TURKISH_SYSTEM_PROMPT = (
    "Sen bir İslami etimoloji uzmanısın. Lane's Lexicon tanımlarını sade Türkçe özetlere "
    "dönüştür. Hedef kitle: Kur'an okuyucuları. 2-4 cümleyle özetle, 200 karakter veya altında tut. "
    "JSON formatında cevap ver."
)

TURKISH_USER_PROMPT_TEMPLATE = (
    "Bu kökün Lane's Lexicon tanımını 2-4 cümleyle Türkçe özetle. "
    "200 karakter veya altında tut.\n\n"
    "Kök: {root} ({bw})\n"
    "Tanım: {definition}\n\n"
    'JSON: {{"summary": "...", "confidence": 0.0-1.0}}'
)

TURKISH_CORPUS_USER_PROMPT_TEMPLATE = (
    "Bu Kur'an kökünün temel anlamını 2-4 cümleyle Türkçe özetle. "
    "200 karakter veya altında tut.\n\n"
    "Kök: {root} ({bw})\n"
    "Morfolojik formlar: {forms}\n\n"
    'JSON: {{"summary": "...", "confidence": 0.0-1.0}}'
)

ENGLISH_SYSTEM_PROMPT = (
    "You are a Quranic Arabic etymology expert. Summarize Lane's Lexicon definitions into "
    "plain English. Target: Quran readers. Summarize in 2-4 sentences, ≤200 chars. "
    "Respond in JSON."
)

ENGLISH_USER_PROMPT_TEMPLATE = (
    "Summarize in 2-4 sentences, ≤200 chars.\n\n"
    "Root: {root} ({bw})\n"
    "Definition: {definition}\n\n"
    'JSON: {{"summary": "...", "confidence": 0.0-1.0}}'
)

ENGLISH_CORPUS_USER_PROMPT_TEMPLATE = (
    "Summarize the primary meaning of this Quranic root in 2-4 sentences, ≤200 chars.\n\n"
    "Root: {root} ({bw})\n"
    "Morphological forms: {forms}\n\n"
    'JSON: {{"summary": "...", "confidence": 0.0-1.0}}'
)

_SUMMARY_RE = re.compile(r'"summary"\s*:\s*"((?:[^"\\]|\\.)*)"', re.DOTALL)
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
# Summary generation helpers
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
    max_tokens: int = 400,
) -> tuple[str | None, float | None]:
    """Single LLM summary call → (summary_text, confidence)."""
    _throttle_wait()

    resp = requests.post(
        OPENROUTER_URL,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": SUMMARY_MODEL,
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
    summary = None
    confidence = None
    try:
        parsed = json.loads(sanitized)
        if isinstance(parsed, dict):
            summary = parsed.get("summary") or parsed.get("özet") or parsed.get("Summary")
            conf_val = parsed.get("confidence") or parsed.get("güven")
            if conf_val is not None:
                try:
                    confidence = max(0.0, min(1.0, float(conf_val)))
                except (ValueError, TypeError):
                    pass
    except json.JSONDecodeError:
        pass

    # Strategy 2: Regex fallback for malformed JSON
    if not summary:
        sum_match = _SUMMARY_RE.search(sanitized)
        conf_match = _CONFIDENCE_RE.search(sanitized)

        if sum_match is None:
            return None, None

        raw = sum_match.group(1)
        try:
            summary = json.loads(f'"{raw}"')
        except json.JSONDecodeError:
            summary = raw.replace(r"\n", " ").replace(r"\t", " ").replace(r"\"", '"').strip()

        if conf_match and confidence is None:
            try:
                confidence = max(0.0, min(1.0, float(conf_match.group(1))))
            except ValueError:
                pass

    return (summary.strip() if summary else None), confidence


def _truncate_at_sentence(text: str, max_length: int) -> str:
    """Truncate text at last sentence boundary if it exceeds max_length."""
    if len(text) <= max_length:
        return text

    # Find last period, exclamation, or question mark before max_length
    truncated = text[:max_length]
    last_period = max(truncated.rfind("."), truncated.rfind("!"), truncated.rfind("?"))

    if last_period > 0:
        return text[: last_period + 1].strip()
    else:
        # No sentence boundary found, hard truncate
        return text[:max_length].strip() + "..."


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> int:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S",
    )

    parser = argparse.ArgumentParser(description="Backfill missing Turkish and English summaries")
    parser.add_argument("--workers", type=int, default=DEFAULT_WORKERS)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--limit", type=int, default=0, help="Max rows to process (0=all)")
    args = parser.parse_args()

    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        logger.error("OPENROUTER_API_KEY not set — cannot generate summaries")
        return 1

    engine = create_engine(DATABASE_URL, future=True)

    # Fetch rows missing summaries
    with engine.connect() as conn:
        query = """
            SELECT id, root, root_buckwalter, definition_en, morphological_forms
            FROM qm_root_etymologies
            WHERE summary_tr IS NULL OR summary_en IS NULL
            ORDER BY quran_frequency DESC
        """
        if args.limit > 0:
            query += f" LIMIT {args.limit}"
        rows = conn.execute(text(query)).fetchall()

    total = len(rows)
    if total == 0:
        logger.info("✅ No missing summaries — nothing to do")
        return 0

    logger.info("Found %d rows missing summaries", total)
    logger.info("Workers: %d, dry-run: %s", args.workers, args.dry_run)

    # Generate summaries in parallel
    cancel_event = threading.Event()
    progress_lock = threading.Lock()
    done_count = 0
    success_count = 0
    fail_count = 0
    start_time = time.monotonic()

    def process_row(row):
        nonlocal done_count, success_count, fail_count

        row_id = row[0]
        root = row[1]
        root_bw = row[2]
        def_en = row[3]
        morph_forms = row[4]

        if cancel_event.is_set():
            return None

        try:
            # Determine input for summarization
            if def_en and def_en.strip():
                # Use existing English definition
                tr_user_prompt = TURKISH_USER_PROMPT_TEMPLATE.format(root=root, bw=root_bw, definition=def_en[:6000])
                en_user_prompt = ENGLISH_USER_PROMPT_TEMPLATE.format(root=root, bw=root_bw, definition=def_en[:6000])
            else:
                # Use root + morphological forms
                if morph_forms and isinstance(morph_forms, list):
                    forms_text = (
                        ", ".join(
                            f.get("form_arabic", f.get("form_name", ""))
                            for f in morph_forms[:10]
                            if isinstance(f, dict)
                        )
                        or "N/A"
                    )
                else:
                    forms_text = str(morph_forms) if morph_forms else "N/A"
                tr_user_prompt = TURKISH_CORPUS_USER_PROMPT_TEMPLATE.format(root=root, bw=root_bw, forms=forms_text)
                en_user_prompt = ENGLISH_CORPUS_USER_PROMPT_TEMPLATE.format(root=root, bw=root_bw, forms=forms_text)

            # Generate Turkish summary
            summary_tr, _conf_tr = _call_openrouter(api_key, TURKISH_SYSTEM_PROMPT, tr_user_prompt)

            # Generate English summary
            summary_en, _conf_en = _call_openrouter(api_key, ENGLISH_SYSTEM_PROMPT, en_user_prompt)

            # Validate and truncate if needed
            if summary_tr:
                summary_tr = _truncate_at_sentence(summary_tr, MAX_SUMMARY_LENGTH)
            if summary_en:
                summary_en = _truncate_at_sentence(summary_en, MAX_SUMMARY_LENGTH)

            if summary_tr and summary_en:
                with progress_lock:
                    success_count += 1
                return (row_id, summary_tr, summary_en)
            else:
                with progress_lock:
                    fail_count += 1
                logger.warning("Incomplete summaries for %s (%s): TR=%s EN=%s", root, root_bw, summary_tr, summary_en)
                return None

        except (requests.exceptions.HTTPError, RetryError) as exc:
            resp = getattr(exc, "response", None)
            if resp is not None and resp.status_code == 401:
                logger.error("API key rejected — aborting")
                cancel_event.set()
            logger.warning("Summary generation failed for %s (%s): %s", root, root_bw, exc)
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
        futures = {executor.submit(process_row, row): row for row in rows}
        for future in as_completed(futures):
            result = future.result()
            if result is not None:
                updates.append(result)

    elapsed = time.monotonic() - start_time
    logger.info("")
    logger.info("═══ Backfill Complete ═══")
    logger.info("Total processed: %d", done_count)
    logger.info("Successful summaries: %d", len(updates))
    logger.info("Failed: %d", fail_count)
    logger.info("Elapsed: %.0fs", elapsed)

    if args.dry_run:
        logger.info("[DRY RUN] Would update %d rows", len(updates))
        return 0

    if not updates:
        logger.warning("No summaries produced — nothing to update")
        return 1

    # Batch UPDATE
    logger.info("Writing %d summaries to database...", len(updates))
    batch_size = 100
    updated = 0
    with engine.begin() as conn:
        for i in range(0, len(updates), batch_size):
            batch = updates[i : i + batch_size]
            for row_id, summary_tr, summary_en in batch:
                conn.execute(
                    text("""
                        UPDATE qm_root_etymologies
                        SET summary_tr = :summary_tr,
                            summary_en = :summary_en,
                            updated_at = NOW()
                        WHERE id = :id
                    """),
                    {
                        "summary_tr": summary_tr,
                        "summary_en": summary_en,
                        "id": row_id,
                    },
                )
                updated += 1

    logger.info("✅ Updated %d rows in qm_root_etymologies", updated)

    # Verify
    with engine.connect() as conn:
        still_missing = conn.execute(
            text("SELECT COUNT(*) FROM qm_root_etymologies WHERE summary_tr IS NULL OR summary_en IS NULL")
        ).scalar()
        total_rows = conn.execute(text("SELECT COUNT(*) FROM qm_root_etymologies")).scalar()
        has_summaries = (total_rows or 0) - (still_missing or 0)
        pct = has_summaries / total_rows * 100 if total_rows else 0

    logger.info("Post-backfill: %d/%d rows have summaries (%.1f%%)", has_summaries, total_rows, pct)
    if still_missing:
        logger.info("Still missing: %d rows", still_missing)

    # Show 10 random samples with character lengths
    logger.info("")
    logger.info("═══ Random Samples ═══")
    with engine.connect() as conn:
        samples = conn.execute(
            text("""
                SELECT root, root_buckwalter, summary_tr, summary_en
                FROM qm_root_etymologies
                WHERE summary_tr IS NOT NULL AND summary_en IS NOT NULL
                ORDER BY RANDOM()
                LIMIT 10
            """)
        ).fetchall()

        for idx, sample in enumerate(samples, 1):
            root, bw, tr_sum, en_sum = sample
            logger.info(
                "%d. Root: %s (%s) | TR: %d chars | EN: %d chars",
                idx,
                root,
                bw,
                len(tr_sum) if tr_sum else 0,
                len(en_sum) if en_sum else 0,
            )
            logger.info("   TR: %s", tr_sum[:80] if tr_sum else "N/A")
            logger.info("   EN: %s", en_sum[:80] if en_sum else "N/A")

    engine.dispose()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
