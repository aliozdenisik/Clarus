#!/usr/bin/env python3
"""Re-translate Turkish definitions that are missing Lane's section codes.

Splits English definition by section codes (-b2-, -A2-), translates each
section via LLM with JSON-structured I/O, and reassembles with codes intact.

Usage:
  uv run python scripts/retranslate_with_codes.py
  uv run python scripts/retranslate_with_codes.py --workers 15
  uv run python scripts/retranslate_with_codes.py --dry-run --limit 5
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import random
import re
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import requests
from sqlalchemy import create_engine, text
from tenacity import RetryError, retry, retry_if_exception, stop_after_attempt, wait_exponential

sys.path.insert(0, str(Path(__file__).parent.parent))
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:54322/postgres",
).replace("postgresql+asyncpg://", "postgresql://")

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
TRANSLATION_MODEL = "google/gemini-2.5-flash"
DEFAULT_WORKERS = 10
DEFAULT_TIMEOUT = 120.0

# Regex: splits on -b2- -b3- -A2- -A3- etc.
SECTION_SPLIT_RE = re.compile(r"(-[bA]\d+-)")

SYSTEM_PROMPT = (
    "You are a Quranic Arabic lexicography expert. "
    "You will receive a JSON object where each key is a Lane's Lexicon section code "
    "(like '1', '-b2-', '-A2-') and each value is the English definition for that section.\n\n"
    "Translate EACH section value to READABLE modern Turkish.\n\n"
    "RULES:\n"
    "1. EXPAND abbreviations inline:\n"
    "   S → Sihâh'a göre, K → Kámoos'a göre, TA → Tâcu'l-Arûs'a göre\n"
    "   Msb → Misbáh'a göre, Bd → Beyzâvî'ye göre, A → Esâsu'l-Belâga'ya göre\n"
    "   aor. → muzari fiil, inf. n. → mastar, pl. → çoğul, q. v. → bakınız\n"
    "   tropical → mecaz, assumed tropical → varsayılan mecaz\n"
    "2. Convert 19th-century English to clear modern Turkish\n"
    "3. Preserve ALL content — nothing removed, nothing added\n"
    "4. Use Islamic Turkish terminology (tövbe, salat, sadaka)\n"
    "5. Target: Quran readers with basic Islamic knowledge\n\n"
    "Return a JSON object with the SAME KEYS, Turkish translations as values.\n"
    'Example: {"1": "turkish...", "-b2-": "turkish...", "-A2-": "turkish..."}'
)

logger = logging.getLogger(__name__)

_throttle_lock = threading.Lock()
_throttle_until = 0.0


def _throttle_wait() -> None:
    global _throttle_until
    sleep_for = 0.0
    with _throttle_lock:
        now = time.monotonic()
        if now < _throttle_until:
            sleep_for = _throttle_until - now
    if sleep_for > 0:
        logger.info("Rate-limit backoff: sleeping %.1fs", sleep_for)
        time.sleep(sleep_for)
        jitter = random.uniform(0.1, 1.0)  # noqa: S311 — non-crypto jitter
        time.sleep(jitter)


def _throttle_set(seconds: float) -> None:
    global _throttle_until
    with _throttle_lock:
        _throttle_until = max(_throttle_until, time.monotonic() + seconds)


def split_lane_sections(definition_en: str) -> dict[str, str]:
    parts = SECTION_SPLIT_RE.split(definition_en)
    sections: dict[str, str] = {}
    current_key = "1"

    for part in parts:
        part = part.strip()
        if not part:
            continue
        if SECTION_SPLIT_RE.fullmatch(part):
            current_key = part
        else:
            if current_key in sections:
                sections[current_key] += " " + part
            else:
                sections[current_key] = part

    return sections


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
def translate_sections(
    api_key: str,
    sections: dict[str, str],
    timeout: float = DEFAULT_TIMEOUT,
) -> dict[str, str] | None:
    _throttle_wait()
    time.sleep(random.uniform(0.1, 0.5))  # noqa: S311 — non-crypto jitter

    user_content = json.dumps(sections, ensure_ascii=False)

    resp = requests.post(
        OPENROUTER_URL,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": TRANSLATION_MODEL,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_content},
            ],
            "response_format": {"type": "json_object"},
            "max_tokens": 8192,
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
        return None

    content = choices[0].get("message", {}).get("content", "")
    if not content:
        return None

    sanitized = re.sub(r"[\x00-\x1f\x7f]", " ", content)
    try:
        parsed = json.loads(sanitized)
        if isinstance(parsed, dict):
            return {k: str(v) for k, v in parsed.items()}
    except json.JSONDecodeError:
        pass

    return None


def reassemble_turkish(sections_tr: dict[str, str]) -> str:
    parts: list[str] = []
    for key, value in sections_tr.items():
        value = value.strip()
        if key == "1":
            parts.append(value)
        else:
            parts.append(f"\n\n{key} {value}")
    return "\n".join(parts)


def main() -> int:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S",
    )

    parser = argparse.ArgumentParser(description="Re-translate roots missing section codes")
    parser.add_argument("--workers", type=int, default=DEFAULT_WORKERS)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--limit", type=int, default=0)
    args = parser.parse_args()

    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        logger.error("OPENROUTER_API_KEY not set")
        return 1

    engine = create_engine(DATABASE_URL, future=True)

    with engine.connect() as conn:
        query = """
            SELECT id, root, root_buckwalter, definition_en, quran_frequency
            FROM qm_root_etymologies
            WHERE definition_en ~ '-[bA][0-9]+[-.]'
              AND definition_tr IS NOT NULL
              AND NOT definition_tr ~ '-[bA][0-9]+[-.]'
            ORDER BY quran_frequency DESC
        """
        if args.limit > 0:
            query += f" LIMIT {args.limit}"
        rows = conn.execute(text(query)).fetchall()

    total = len(rows)
    if total == 0:
        logger.info("All translations already have section codes")
        return 0

    logger.info("Found %d roots needing section-code retranslation", total)

    cancel_event = threading.Event()
    progress_lock = threading.Lock()
    done_count = 0
    success_count = 0
    fail_count = 0
    start_time = time.monotonic()

    def process_row(row):
        nonlocal done_count, success_count, fail_count
        row_id, root, root_bw, def_en, _freq = row

        if cancel_event.is_set():
            return None

        try:
            sections_en = split_lane_sections(def_en)
            if len(sections_en) < 2:
                with progress_lock:
                    fail_count += 1
                return None

            sections_tr = translate_sections(api_key, sections_en)
            if not sections_tr:
                with progress_lock:
                    fail_count += 1
                return None

            missing_keys = [k for k in sections_en if k not in sections_tr]
            if missing_keys:
                logger.warning("%s (%s): LLM dropped keys %s", root, root_bw, missing_keys)

            turkish = reassemble_turkish(sections_tr)

            if not turkish or len(turkish) < 50:
                logger.warning("%s (%s): translation too short (%d chars)", root, root_bw, len(turkish))
                with progress_lock:
                    fail_count += 1
                return None

            with progress_lock:
                success_count += 1
            return (row_id, turkish, root, root_bw, len(sections_en))

        except (requests.exceptions.HTTPError, RetryError) as exc:
            resp = getattr(exc, "response", None)
            if resp is not None and resp.status_code == 401:
                logger.error("API key rejected — aborting")
                cancel_event.set()
            logger.warning("Failed for %s (%s): %s", root, root_bw, exc)
            with progress_lock:
                fail_count += 1
            return None
        except Exception as exc:
            logger.warning("Unexpected error for %s (%s): %s", root, root_bw, exc)
            with progress_lock:
                fail_count += 1
            return None
        finally:
            with progress_lock:
                done_count += 1
                if done_count % 25 == 0 or done_count == total:
                    elapsed = time.monotonic() - start_time
                    rate = done_count / elapsed if elapsed > 0 else 0
                    eta = (total - done_count) / rate if rate > 0 else 0
                    logger.info(
                        "Progress: %d/%d (✅ %d ❌ %d) rate=%.1f/s eta=%.0fs",
                        done_count,
                        total,
                        success_count,
                        fail_count,
                        rate,
                        eta,
                    )

    updates: list[tuple] = []
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = {executor.submit(process_row, row): row for row in rows}
        for future in as_completed(futures):
            result = future.result()
            if result is not None:
                updates.append(result)

    elapsed = time.monotonic() - start_time
    logger.info("")
    logger.info("═══ Retranslation Complete ═══")
    logger.info("Total: %d | Success: %d | Failed: %d | Elapsed: %.0fs", total, len(updates), fail_count, elapsed)

    if args.dry_run:
        logger.info("[DRY RUN] Would update %d rows", len(updates))
        for row_id, turkish, root, root_bw, n_sections in updates[:3]:
            logger.info("  %s (%s): %d sections → %d chars", root, root_bw, n_sections, len(turkish))
            logger.info("  Preview: %s...", turkish[:200])
        return 0

    if not updates:
        logger.warning("No translations produced")
        return 1

    logger.info("Writing %d translations to database...", len(updates))
    with engine.begin() as conn:
        for row_id, turkish, root, root_bw, n_sections in updates:
            conn.execute(
                text("""
                    UPDATE qm_root_etymologies
                    SET definition_tr = :tr,
                        tr_translation_source = 'llm_gemini_v2',
                        updated_at = NOW()
                    WHERE id = :id
                """),
                {"tr": turkish, "id": row_id},
            )

    logger.info("✅ Updated %d rows", len(updates))

    with engine.connect() as conn:
        result = conn.execute(
            text("""
            SELECT
              COUNT(*) FILTER (WHERE definition_en ~ '-[bA][0-9]+[-.]') as en_with_codes,
              COUNT(*) FILTER (WHERE definition_tr ~ '-[bA][0-9]+[-.]') as tr_with_codes
            FROM qm_root_etymologies
            WHERE definition_en IS NOT NULL AND definition_tr IS NOT NULL
        """)
        ).fetchone()
        if result:
            logger.info("Post-update: EN with codes=%d, TR with codes=%d", result[0], result[1])

    engine.dispose()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
