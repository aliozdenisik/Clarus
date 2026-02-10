"""Etymology pipeline helpers for Quranic morphology extraction.

This module extracts morphological form statistics from ``qm_words`` records
and provides root-frequency snapshots for etymology table generation.
"""

from __future__ import annotations

import asyncio
import logging
from collections import Counter
from collections.abc import Mapping, Sequence
from dataclasses import dataclass

import asyncpg  # pyright: ignore[reportMissingImports]

logger = logging.getLogger(__name__)

DATABASE_DSN = "postgresql://postgres:postgres@localhost:54322/postgres"


@dataclass
class RootInfo:
    """Normalized root metadata extracted from ``qm_words``."""

    root: str
    root_buckwalter: str | None
    frequency: int


# Arabic grammatical form patterns (awzan)
FORM_PATTERNS: dict[str, dict[str, str]] = {
    # Verb forms (10 canonical patterns)
    "form_I": {"arabic": "فَعَلَ", "name": "fa'ala", "type": "فعل ثلاثي مجرد"},  # noqa: RUF001, RUF100
    "form_II": {"arabic": "فَعَّلَ", "name": "fa''ala", "type": "فعل ثلاثي مزيد"},  # noqa: RUF001, RUF100
    "form_III": {"arabic": "فَاعَلَ", "name": "faa'ala", "type": "فعل ثلاثي مزيد"},  # noqa: RUF001, RUF100
    "form_IV": {"arabic": "أَفْعَلَ", "name": "af'ala", "type": "فعل ثلاثي مزيد"},  # noqa: RUF001, RUF100
    "form_V": {"arabic": "تَفَعَّلَ", "name": "tafa''ala", "type": "فعل ثلاثي مزيد"},  # noqa: RUF001, RUF100
    "form_VI": {"arabic": "تَفَاعَلَ", "name": "tafaa'ala", "type": "فعل ثلاثي مزيد"},  # noqa: RUF001, RUF100
    "form_VII": {"arabic": "اِنْفَعَلَ", "name": "infa'ala", "type": "فعل ثلاثي مزيد"},  # noqa: RUF001, RUF100
    "form_VIII": {"arabic": "اِفْتَعَلَ", "name": "ifta'ala", "type": "فعل ثلاثي مزيد"},  # noqa: RUF001, RUF100
    "form_IX": {"arabic": "اِفْعَلَّ", "name": "if'alla", "type": "فعل ثلاثي مزيد"},  # noqa: RUF001, RUF100
    "form_X": {"arabic": "اِسْتَفْعَلَ", "name": "istaf'ala", "type": "فعل ثلاثي مزيد"},  # noqa: RUF001, RUF100
    # Nominal / derived patterns
    "active_participle": {"arabic": "فَاعِل", "name": "faa'il", "type": "اسم فاعل"},  # noqa: RUF001, RUF100
    "passive_participle": {"arabic": "مَفْعُول", "name": "maf'ul", "type": "اسم مفعول"},  # noqa: RUF001, RUF100
    "verbal_noun_I": {"arabic": "فَعْل", "name": "fa'l", "type": "مصدر"},  # noqa: RUF001, RUF100
    "verbal_noun_II": {"arabic": "تَفْعِيل", "name": "taf'il", "type": "مصدر"},  # noqa: RUF001, RUF100
    "intensive": {"arabic": "فَعَّال", "name": "fa''aal", "type": "صيغة مبالغة"},  # noqa: RUF001, RUF100
    "qualitative_adj": {"arabic": "فَعِيل", "name": "fa'il", "type": "صفة مشبهة"},  # noqa: RUF001, RUF100
    "instrument": {"arabic": "مِفْعَال", "name": "mif'aal", "type": "اسم آلة"},  # noqa: RUF001, RUF100
    "place_noun": {"arabic": "مَفْعِل", "name": "maf'il", "type": "اسم مكان"},  # noqa: RUF001, RUF100
    "diminutive": {"arabic": "فُعَيْل", "name": "fu'ayl", "type": "تصغير"},  # noqa: RUF001, RUF100
    "collective": {"arabic": "فُعُول", "name": "fu'uul", "type": "جمع تكسير"},  # noqa: RUF001, RUF100
    # Practical fallbacks from corpus tagging
    "nominal_generic": {"arabic": "اِسْم", "name": "generic_noun", "type": "اسم"},  # noqa: RUF001, RUF100
    "verb_generic": {"arabic": "فِعْل", "name": "generic_verb", "type": "فعل"},  # noqa: RUF001, RUF100
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
    try:
        value = row[key]  # type: ignore[index]
        return "" if value is None else str(value)
    except Exception:
        pass

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
    """Extract aggregated morphological forms for one Arabic root.

    Args:
        root: Arabic triliteral (or quadriliteral) root string.
        words: ``qm_words`` rows as tuples or mappings in the shape
            ``(token, token_clean, pos_tag, features)``.

    Returns:
        List of form dictionaries with category metadata and occurrence counts.
    """
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


async def _fetch_root_frequency_rows() -> list[RootInfo]:
    conn = await asyncpg.connect(DATABASE_DSN)
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


def extract_all_roots_with_frequency() -> list[RootInfo]:
    """Return all unique roots from ``qm_words`` with occurrence frequency."""
    try:
        return asyncio.run(_fetch_root_frequency_rows())
    except RuntimeError as exc:
        if "asyncio.run() cannot be called from a running event loop" not in str(exc):
            raise

        logger.debug("Running loop detected; falling back to dedicated event loop")
        loop = asyncio.new_event_loop()
        try:
            return loop.run_until_complete(_fetch_root_frequency_rows())
        finally:
            loop.close()
