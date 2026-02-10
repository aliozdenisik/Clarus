"""Etymology pipeline helpers and ETL workflow for Quranic roots.

This module provides:
- morphology extraction helpers from ``qm_words``
- root frequency extraction utilities
- ``EtymologyPipeline`` for loading ``qm_root_etymologies``
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import random
import re
from collections import Counter
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

import asyncpg
import requests
from pybreaker import CircuitBreakerError
from sqlalchemy import create_engine, text
from tenacity import RetryError, retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from src.arabic_normalizer import arabic_to_buckwalter
from src.circuit_breaker import llm_with_breaker
from src.lane_lexicon import LaneLexiconAdapter

if TYPE_CHECKING:
    from sqlalchemy.engine import Connection

    from src.lane_lexicon import LaneEntry

logger = logging.getLogger(__name__)

DATABASE_DSN = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:54322/postgres")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
TRANSLATION_MODEL = "google/gemini-2.5-flash"
TRANSLATION_SYSTEM_PROMPT = (
    "You are an Arabic-English-Turkish lexicography expert. "
    "Translate the following Arabic root definition from English to Turkish. "
    "Preserve academic terminology. Return JSON: "
    '{"translation": "...", "confidence": 0.0-1.0}'
)
CORPUS_DEFINITION_PROMPT = (
    "You are a Quranic Arabic lexicography expert. "
    "Given an Arabic root and its Quran frequency, provide a concise Turkish definition "
    "of the root's primary meaning in Quranic context. Return JSON: "
    '{"translation": "...", "confidence": 0.0-1.0}'
)
_TRANSLATION_RE = re.compile(r'"translation"\s*:\s*"((?:[^"\\]|\\.)*)"', re.DOTALL)
_CONFIDENCE_RE = re.compile(r'"confidence"\s*:\s*([\d.]+)')
ETYMOLOGY_EXPORT_DIR = Path(__file__).resolve().parent.parent / "data" / "etymology"


@dataclass
class RootInfo:
    """Normalized root metadata extracted from ``qm_words``."""

    root: str
    root_buckwalter: str | None
    frequency: int


@dataclass
class PipelineResult:
    """Summary of ETL execution."""

    success: bool
    total_roots: int
    inserted_rows: int
    lane_matches: int
    lane_high_confidence: int
    lane_medium_confidence: int
    corpus_only: int
    forms_available: int
    turkish_translations: int
    low_confidence_translations: int


# Arabic grammatical form patterns (awzan)
FORM_PATTERNS: dict[str, dict[str, str]] = {
    # Verb forms (10 canonical patterns)
    "form_I": {"arabic": "فَعَلَ", "name": "fa'ala", "type": "فعل ثلاثي مجرد"},
    "form_II": {"arabic": "فَعَّلَ", "name": "fa''ala", "type": "فعل ثلاثي مزيد"},
    "form_III": {"arabic": "فَاعَلَ", "name": "faa'ala", "type": "فعل ثلاثي مزيد"},
    "form_IV": {"arabic": "أَفْعَلَ", "name": "af'ala", "type": "فعل ثلاثي مزيد"},
    "form_V": {"arabic": "تَفَعَّلَ", "name": "tafa''ala", "type": "فعل ثلاثي مزيد"},
    "form_VI": {"arabic": "تَفَاعَلَ", "name": "tafaa'ala", "type": "فعل ثلاثي مزيد"},
    "form_VII": {"arabic": "اِنْفَعَلَ", "name": "infa'ala", "type": "فعل ثلاثي مزيد"},
    "form_VIII": {"arabic": "اِفْتَعَلَ", "name": "ifta'ala", "type": "فعل ثلاثي مزيد"},
    "form_IX": {"arabic": "اِفْعَلَّ", "name": "if'alla", "type": "فعل ثلاثي مزيد"},
    "form_X": {"arabic": "اِسْتَفْعَلَ", "name": "istaf'ala", "type": "فعل ثلاثي مزيد"},
    # Nominal / derived patterns
    "active_participle": {"arabic": "فَاعِل", "name": "faa'il", "type": "اسم فاعل"},
    "passive_participle": {"arabic": "مَفْعُول", "name": "maf'ul", "type": "اسم مفعول"},
    "verbal_noun_I": {"arabic": "فَعْل", "name": "fa'l", "type": "مصدر"},
    "verbal_noun_II": {"arabic": "تَفْعِيل", "name": "taf'il", "type": "مصدر"},
    "intensive": {"arabic": "فَعَّال", "name": "fa''aal", "type": "صيغة مبالغة"},
    "qualitative_adj": {"arabic": "فَعِيل", "name": "fa'il", "type": "صفة مشبهة"},
    "instrument": {"arabic": "مِفْعَال", "name": "mif'aal", "type": "اسم آلة"},
    "place_noun": {"arabic": "مَفْعِل", "name": "maf'il", "type": "اسم مكان"},
    "diminutive": {"arabic": "فُعَيْل", "name": "fu'ayl", "type": "تصغير"},
    "collective": {"arabic": "فُعُول", "name": "fu'uul", "type": "جمع تكسير"},
    # Practical fallbacks from corpus tagging
    "nominal_generic": {"arabic": "اِسْم", "name": "generic_noun", "type": "اسم"},
    "verb_generic": {"arabic": "فِعْل", "name": "generic_verb", "type": "فعل"},
}

_VF_TO_FORM: dict[str, str] = {
    "1": "form_I",
    "2": "form_II",
    "3": "form_III",
    "4": "form_IV",
    "5": "form_V",
    "6": "form_VI",
    "7": "form_VII",
    "8": "form_VIII",
    "9": "form_IX",
    "10": "form_X",
}


def _row_value(row: object, index: int, key: str) -> str:
    if isinstance(row, Mapping):
        value = row.get(key)
        return "" if value is None else str(value)

    if isinstance(row, Sequence) and not isinstance(row, str | bytes | bytearray):
        if len(row) <= index:
            return ""
        value = row[index]
        return "" if value is None else str(value)

    value = getattr(row, key, None)
    return "" if value is None else str(value)


def _parse_feature_segment(segment: str) -> tuple[set[str], dict[str, str]]:
    tokens = {part.strip() for part in segment.split("|") if part.strip()}
    key_values: dict[str, str] = {}
    for token in tokens:
        if ":" not in token:
            continue
        key, value = token.split(":", 1)
        key_values[key.strip()] = value.strip()
    return tokens, key_values


def _detect_form_pattern(pos_tag: str, tags: set[str], features: Mapping[str, str]) -> str | None:
    vf = features.get("VF")
    if vf and vf in _VF_TO_FORM:
        return _VF_TO_FORM[vf]

    if "ACT_PCPL" in tags:
        return "active_participle"
    if "PASS_PCPL" in tags:
        return "passive_participle"

    if pos_tag == "V":
        return "verb_generic"
    if pos_tag in {"N", "PN", "ADJ"}:
        return "nominal_generic"

    return None


def extract_morphological_forms(root: str, words: list[object]) -> list[dict[str, object]]:
    """Extract aggregated morphological forms for one Arabic root."""
    normalized_root = root.strip()
    if not normalized_root:
        return []

    occurrences: Counter[str] = Counter()
    examples: dict[str, str] = {}

    for row in words:
        token = _row_value(row, 0, "token")
        pos_tag = _row_value(row, 2, "pos_tag")
        features = _row_value(row, 3, "features")
        if not features:
            continue

        segments = [segment.strip() for segment in features.split("||") if segment.strip()]
        for segment in segments:
            tags, kv = _parse_feature_segment(segment)
            segment_root = kv.get("ROOT")
            if segment_root and segment_root != normalized_root:
                continue

            pattern_key = _detect_form_pattern(pos_tag, tags, kv)
            if not pattern_key or pattern_key not in FORM_PATTERNS:
                continue

            occurrences[pattern_key] += 1
            if pattern_key not in examples and token:
                examples[pattern_key] = token

    result: list[dict[str, object]] = []
    for pattern_key, count in sorted(
        occurrences.items(),
        key=lambda item: (-item[1], item[0]),
    ):
        pattern_meta = FORM_PATTERNS[pattern_key]
        result.append(
            {
                "form_pattern": pattern_key,
                "form_arabic": pattern_meta["arabic"],
                "form_name": pattern_meta["name"],
                "form_category": pattern_meta["type"],
                "example_word": examples.get(pattern_key, ""),
                "occurrences": count,
            }
        )

    return result


async def _fetch_root_frequency_rows(database_dsn: str) -> list[RootInfo]:
    normalized_dsn = database_dsn.replace("postgresql+asyncpg://", "postgresql://")
    conn = await asyncpg.connect(normalized_dsn)
    try:
        rows = await conn.fetch(
            """
            SELECT root, root_buckwalter, COUNT(*) AS frequency
            FROM qm_words
            WHERE root IS NOT NULL AND root <> ''
            GROUP BY root, root_buckwalter
            ORDER BY frequency DESC, root ASC
            """
        )
        return [
            RootInfo(
                root=str(row["root"]),
                root_buckwalter=(str(row["root_buckwalter"]) if row["root_buckwalter"] else None),
                frequency=int(row["frequency"]),
            )
            for row in rows
        ]
    finally:
        await conn.close()


def extract_all_roots_with_frequency(database_dsn: str = DATABASE_DSN) -> list[RootInfo]:
    """Return all unique roots from ``qm_words`` with occurrence frequency."""
    try:
        return asyncio.run(_fetch_root_frequency_rows(database_dsn))
    except RuntimeError as exc:
        if "asyncio.run() cannot be called from a running event loop" not in str(exc):
            raise

        logger.debug("Running loop detected; falling back to dedicated event loop")
        loop = asyncio.new_event_loop()
        try:
            return loop.run_until_complete(_fetch_root_frequency_rows(database_dsn))
        finally:
            loop.close()


class EtymologyPipeline:
    """ETL pipeline: qm_words + Lane's Lexicon -> qm_root_etymologies.

    Sources:
      - Quranic Arabic Corpus v0.4 (University of Leeds, GNU GPL)
      - Lane's Arabic-English Lexicon SQLite (GPL-3.0)
    """

    def __init__(
        self,
        db_url: str = DATABASE_DSN,
        lane_db_path: Path | None = None,
        openrouter_api_key: str | None = None,
        batch_size: int = 100,
        dry_run: bool = False,
        *,
        use_lane: bool = True,
    ):
        """Initialize pipeline."""
        self.db_url = db_url
        self._asyncpg_dsn = self._normalize_asyncpg_dsn(db_url)
        self._sqlalchemy_dsn = self._normalize_sqlalchemy_dsn(db_url)
        self._engine = create_engine(self._sqlalchemy_dsn, future=True)
        self.batch_size = batch_size
        self.dry_run = dry_run
        self.openrouter_api_key = openrouter_api_key
        self.export_dir = ETYMOLOGY_EXPORT_DIR
        self._forms_connection: Connection | None = None

        self.lane_adapter: LaneLexiconAdapter | None = None
        if use_lane:
            try:
                self.lane_adapter = LaneLexiconAdapter(db_url=self._sqlalchemy_dsn)
                logger.info("Using Lane lexicon from PostgreSQL lane_entries")
            except Exception as exc:
                logger.warning("Lane PostgreSQL unavailable (%s)", exc)
                if lane_db_path is not None:
                    try:
                        self.lane_adapter = LaneLexiconAdapter(db_path=lane_db_path)
                        logger.info("Using Lane lexicon from SQLite at %s", lane_db_path)
                    except FileNotFoundError:
                        logger.warning("Lane database missing at %s, running corpus-only mode", lane_db_path)

        self._truncate_done = False

    @staticmethod
    def _normalize_asyncpg_dsn(db_url: str) -> str:
        return db_url.replace("postgresql+asyncpg://", "postgresql://")

    @staticmethod
    def _normalize_sqlalchemy_dsn(db_url: str) -> str:
        return db_url.replace("postgresql+asyncpg://", "postgresql://")

    def run(self) -> PipelineResult:
        """Run full ETL pipeline (synchronous)."""
        try:
            roots = self._extract_roots()
            processed_rows: list[dict[str, object]] = []

            with self._engine.connect() as forms_connection:
                self._forms_connection = forms_connection

                for root in roots:
                    lane_entry = self._match_lane(root)
                    forms = self._extract_forms(root.root)
                    confidence = self._assign_confidence(lane_entry)

                    root_buckwalter = root.root_buckwalter or arabic_to_buckwalter(root.root)
                    row: dict[str, object] = {
                        "root": root.root,
                        "root_buckwalter": root_buckwalter,
                        "definition_en": lane_entry.definition_en if lane_entry else None,
                        "definition_tr": None,
                        "semantic_field": None,
                        "morphological_forms": forms if forms else None,
                        "related_roots": None,
                        "quran_frequency": root.frequency,
                        "source": "lane" if lane_entry else "corpus_only",
                        "lane_match_type": lane_entry.match_type if lane_entry else None,
                        "lane_volume": lane_entry.volume if lane_entry else None,
                        "confidence": confidence,
                        "tr_translation_source": None,
                        "tr_translation_confidence": None,
                    }
                    processed_rows.append(row)

            self._forms_connection = None

            final_rows = self._translate_batch(processed_rows)

            inserted_rows = 0
            if not self.dry_run:
                inserted_rows = self._insert_batch(final_rows)
            else:
                inserted_rows = len(final_rows)

            self._export_validation(final_rows)

            lane_matches = sum(1 for row in final_rows if row["source"] == "lane")
            high_count = sum(1 for row in final_rows if row["confidence"] == "high")
            medium_count = sum(1 for row in final_rows if row["confidence"] == "medium")
            corpus_only_count = sum(1 for row in final_rows if row["source"] == "corpus_only")
            forms_available = sum(1 for row in final_rows if row["morphological_forms"] is not None)
            turkish_translations = sum(1 for row in final_rows if row["definition_tr"] is not None)
            low_conf_translations = sum(
                1
                for row in final_rows
                if isinstance(row["tr_translation_confidence"], float) and row["tr_translation_confidence"] < 0.80
            )

            total_roots = len(final_rows)
            lane_pct = (lane_matches / total_roots * 100.0) if total_roots else 0.0
            corpus_pct = (corpus_only_count / total_roots * 100.0) if total_roots else 0.0
            forms_pct = (forms_available / total_roots * 100.0) if total_roots else 0.0
            tr_pct = (turkish_translations / total_roots * 100.0) if total_roots else 0.0
            low_conf_pct = (low_conf_translations / turkish_translations * 100.0) if turkish_translations else 0.0

            logger.info("═══ Etymology Pipeline Complete ═══")
            logger.info("Total roots: %s", total_roots)
            logger.info(
                "Lane matches: %s (%.1f%%) — high: %s, medium: %s",
                lane_matches,
                lane_pct,
                high_count,
                medium_count,
            )
            logger.info("Corpus-only: %s (%.1f%%)", corpus_only_count, corpus_pct)
            logger.info("Morphological forms: %s roots (%.1f%%)", forms_available, forms_pct)
            logger.info("Turkish translations: %s (%.1f%% of all roots)", turkish_translations, tr_pct)
            logger.info("Low-confidence translations: %s (%.1f%%)", low_conf_translations, low_conf_pct)

            return PipelineResult(
                success=True,
                total_roots=total_roots,
                inserted_rows=inserted_rows,
                lane_matches=lane_matches,
                lane_high_confidence=high_count,
                lane_medium_confidence=medium_count,
                corpus_only=corpus_only_count,
                forms_available=forms_available,
                turkish_translations=turkish_translations,
                low_confidence_translations=low_conf_translations,
            )
        finally:
            self._forms_connection = None
            self.close()

    def close(self) -> None:
        """Dispose shared SQLAlchemy engine."""
        self._engine.dispose()

    def _extract_roots(self) -> list[RootInfo]:
        """Get all unique roots with frequency from qm_words."""
        return extract_all_roots_with_frequency(self._asyncpg_dsn)

    def _match_lane(self, root: RootInfo) -> LaneEntry | None:
        """Match root against Lane's Lexicon."""
        if self.lane_adapter is None:
            return None

        if root.root_buckwalter:
            match = self.lane_adapter.lookup_by_root(root.root_buckwalter)
            if match is not None:
                return match

        return self.lane_adapter.lookup_by_arabic(root.root)

    def _extract_forms(self, root: str) -> list[dict[str, object]]:
        """Extract morphological forms for a root."""
        if self._forms_connection is not None:
            rows = (
                self._forms_connection.execute(
                    text(
                        """
                        SELECT token, token_clean, pos_tag, features
                        FROM qm_words
                        WHERE root = :root
                        """
                    ),
                    {"root": root},
                )
                .mappings()
                .all()
            )
            return extract_morphological_forms(root, list(rows))

        with self._engine.connect() as conn:
            rows = (
                conn.execute(
                    text(
                        """
                        SELECT token, token_clean, pos_tag, features
                        FROM qm_words
                        WHERE root = :root
                        """
                    ),
                    {"root": root},
                )
                .mappings()
                .all()
            )
        return extract_morphological_forms(root, list(rows))

    def _parse_translation_response(self, content: str) -> tuple[str | None, float | None]:
        payload: dict[str, object] | None = None

        try:
            candidate = json.loads(content)
            if isinstance(candidate, dict):
                payload = candidate
        except json.JSONDecodeError:
            payload = None

        if payload is None:
            sanitized_content = re.sub(r"[\x00-\x1f\x7f]", " ", content)
            try:
                candidate = json.loads(sanitized_content)
                if isinstance(candidate, dict):
                    payload = candidate
            except json.JSONDecodeError:
                payload = None

        translation: str | None = None
        confidence: float | None = None
        if payload is not None:
            translation_raw = payload.get("translation")
            confidence_raw = payload.get("confidence")
            translation = str(translation_raw).strip() if translation_raw else None
            if isinstance(confidence_raw, int | float):
                confidence = max(0.0, min(1.0, float(confidence_raw)))
            return translation, confidence

        sanitized_content = re.sub(r"[\x00-\x1f\x7f]", " ", content)
        translation_match = _TRANSLATION_RE.search(sanitized_content)
        confidence_match = _CONFIDENCE_RE.search(sanitized_content)
        if translation_match is None:
            return None, None

        raw_translation = translation_match.group(1)
        try:
            translation = json.loads(f'"{raw_translation}"')
        except json.JSONDecodeError:
            translation = raw_translation.replace(r"\n", " ").replace(r"\t", " ").replace(r"\"", '"').strip()

        if confidence_match is not None:
            try:
                confidence = max(0.0, min(1.0, float(confidence_match.group(1))))
            except ValueError:
                confidence = None

        return (translation.strip() if translation else None), confidence

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=20),
        retry=retry_if_exception_type((requests.exceptions.ConnectionError, requests.exceptions.Timeout)),
        before_sleep=lambda rs: logger.info("Retrying translation request, attempt %d/3", rs.attempt_number),
    )
    def _translate_definition(
        self,
        definition_en: str,
        *,
        system_prompt: str = TRANSLATION_SYSTEM_PROMPT,
    ) -> tuple[str | None, float | None]:
        if not self.openrouter_api_key:
            return None, None

        headers = {
            "Authorization": f"Bearer {self.openrouter_api_key}",
            "Content-Type": "application/json",
        }
        messages = [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": definition_en,
            },
        ]

        response = llm_with_breaker(
            lambda: requests.post(
                OPENROUTER_URL,
                headers=headers,
                json={
                    "model": TRANSLATION_MODEL,
                    "messages": messages,
                    "response_format": {"type": "json_object"},
                    "max_tokens": 600,
                    "temperature": 0.1,
                },
                timeout=45,
            )
        )
        response.raise_for_status()

        response_json = response.json()
        choices = response_json.get("choices", [])
        if not choices:
            return None, None

        content = choices[0].get("message", {}).get("content", "")
        if not content:
            return None, None

        return self._parse_translation_response(content)

    def _translate_batch(self, entries: list[dict[str, object]]) -> list[dict[str, object]]:
        """Translate English definitions to Turkish via OpenRouter LLM."""
        if not entries:
            return []

        translated_entries: list[dict[str, object]] = []
        for start in range(0, len(entries), 10):
            chunk = entries[start : start + 10]
            for entry in chunk:
                definition_en = entry.get("definition_en")
                if not isinstance(definition_en, str) or not definition_en.strip():
                    root = str(entry.get("root", ""))
                    freq = entry.get("quran_frequency", 0)
                    if root and self.openrouter_api_key:
                        prompt_text = f"Arabic root: {root}, Quran frequency: {freq}"
                        translation, confidence = self._translate_definition(
                            prompt_text,
                            system_prompt=CORPUS_DEFINITION_PROMPT,
                        )
                        entry["definition_tr"] = translation
                        entry["tr_translation_confidence"] = confidence
                        entry["tr_translation_source"] = "llm_generated"
                    else:
                        entry["definition_tr"] = None
                        entry["tr_translation_confidence"] = None
                        entry["tr_translation_source"] = None
                    translated_entries.append(entry)
                    continue

                if not self.openrouter_api_key:
                    entry["definition_tr"] = None
                    entry["tr_translation_confidence"] = None
                    entry["tr_translation_source"] = None
                    translated_entries.append(entry)
                    continue

                try:
                    translation, confidence = self._translate_definition(definition_en)
                    entry["definition_tr"] = translation
                    entry["tr_translation_confidence"] = confidence
                    entry["tr_translation_source"] = "llm_gemini"
                except requests.exceptions.HTTPError as exc:
                    status_code = exc.response.status_code if exc.response is not None else None
                    logger.warning("Translation HTTP error for root %s: %s", entry.get("root"), exc)
                    entry["definition_tr"] = None
                    entry["tr_translation_confidence"] = None
                    entry["tr_translation_source"] = None
                    if status_code == 401:
                        logger.warning("OpenRouter API key rejected; disabling translation for remaining entries")
                        self.openrouter_api_key = None
                except CircuitBreakerError:
                    logger.warning("Translation skipped due to open LLM circuit breaker")
                    entry["definition_tr"] = None
                    entry["tr_translation_confidence"] = None
                    entry["tr_translation_source"] = None
                except (RetryError, requests.exceptions.RequestException, json.JSONDecodeError) as exc:
                    logger.warning("Translation failed for root %s: %s", entry.get("root"), exc)
                    entry["definition_tr"] = None
                    entry["tr_translation_confidence"] = None
                    entry["tr_translation_source"] = None

                translated_entries.append(entry)

        return translated_entries

    def _assign_confidence(self, lane_entry: LaneEntry | None) -> str:
        """Assign confidence level based on Lane volume."""
        if lane_entry is None:
            return "low"
        if lane_entry.volume is None:
            return "low"
        if 1 <= lane_entry.volume <= 5:
            return "high"
        if 6 <= lane_entry.volume <= 8:
            return "medium"
        return "low"

    def _insert_batch(self, rows: list[dict[str, object]]) -> int:
        """Batch insert into qm_root_etymologies. Returns count."""
        if not rows:
            return 0

        inserted = 0
        with self._engine.begin() as conn:
            conn.execute(text("TRUNCATE TABLE qm_root_etymologies RESTART IDENTITY"))

            for start in range(0, len(rows), self.batch_size):
                batch = rows[start : start + self.batch_size]
                prepared_batch: list[dict[str, object]] = []
                for row in batch:
                    prepared_row = dict(row)
                    morph_forms = prepared_row.get("morphological_forms")
                    related_roots = prepared_row.get("related_roots")
                    prepared_row["morphological_forms"] = (
                        json.dumps(morph_forms, ensure_ascii=False) if morph_forms is not None else None
                    )
                    prepared_row["related_roots"] = (
                        json.dumps(related_roots, ensure_ascii=False) if related_roots is not None else None
                    )
                    prepared_batch.append(prepared_row)

                conn.execute(
                    text(
                        """
                        INSERT INTO qm_root_etymologies (
                            root,
                            root_buckwalter,
                            definition_en,
                            definition_tr,
                            semantic_field,
                            morphological_forms,
                            related_roots,
                            quran_frequency,
                            source,
                            lane_match_type,
                            lane_volume,
                            confidence,
                            tr_translation_source,
                            tr_translation_confidence
                        ) VALUES (
                            :root,
                            :root_buckwalter,
                            :definition_en,
                            :definition_tr,
                            :semantic_field,
                            CAST(:morphological_forms AS JSON),
                            CAST(:related_roots AS JSON),
                            :quran_frequency,
                            :source,
                            :lane_match_type,
                            :lane_volume,
                            :confidence,
                            :tr_translation_source,
                            :tr_translation_confidence
                        )
                        """
                    ),
                    prepared_batch,
                )
                inserted += len(batch)
        return inserted

    def _export_validation(self, results: list[dict[str, object]]) -> None:
        """Export validation JSON files to backend/data/etymology/."""
        self.export_dir.mkdir(parents=True, exist_ok=True)

        unmatched_roots = [
            {
                "root": row["root"],
                "root_buckwalter": row["root_buckwalter"],
                "quran_frequency": row["quran_frequency"],
            }
            for row in results
            if row["source"] != "lane"
        ]

        low_conf_translations = [
            {
                "root": row["root"],
                "definition_en": row["definition_en"],
                "definition_tr": row["definition_tr"],
                "tr_translation_confidence": row["tr_translation_confidence"],
            }
            for row in results
            if isinstance(row["tr_translation_confidence"], float) and row["tr_translation_confidence"] < 0.80
        ]

        sample_size = min(50, len(results))
        rng = random.Random(42)  # noqa: S311
        spot_check_sample = rng.sample(results, sample_size) if sample_size > 0 else []

        (self.export_dir / "lane_unmatched_roots.json").write_text(
            json.dumps(unmatched_roots, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        (self.export_dir / "tr_low_confidence_translations.json").write_text(
            json.dumps(low_conf_translations, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        (self.export_dir / "spot_check_sample.json").write_text(
            json.dumps(spot_check_sample, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
