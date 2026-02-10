"""
Shared helpers and models for compare and stream endpoints.

Eliminates DRY violations in verse detail extraction (Issue #10)
and paragraph building (Issue #11).

This module contains:
- VerseDetail and ParagraphData Pydantic models (shared by compare.py and stream.py)
- build_verse_details() helper function
- build_paragraphs() helper function
"""

import logging
import re
from typing import Union, cast

from pydantic import BaseModel

from src.multi_agent_answer_generator import MultiAgentAnswer
from src.search import BibleSearchResult, SearchResult

logger = logging.getLogger(__name__)


# =============================================================================
# Text Post-Processing Helpers
# =============================================================================


def strip_markdown_headers(text: str) -> str:
    """Strip markdown headers and horizontal rules from translated text.

    Defense-in-depth against LLM translation output that injects
    ## Headers or --- dividers into translated paragraph content.

    Args:
        text: Translated text that may contain injected markdown formatting.

    Returns:
        Cleaned text with headers and rules removed, multiple newlines collapsed.
    """
    if not text:
        return text
    text = re.sub(r"^#{1,6}\s+.*$", "", text, flags=re.MULTILINE)
    text = re.sub(r"^-{3,}\s*$", "", text, flags=re.MULTILINE)
    text = re.sub(r"^\*{3,}\s*$", "", text, flags=re.MULTILINE)
    text = re.sub(r"\n{3,}", "\n\n", text)  # Collapse multiple newlines
    return text.strip()


# =============================================================================
# Pydantic Models (moved here to avoid circular imports)
# =============================================================================


class ParagraphData(BaseModel):
    """Individual paragraph with metadata."""

    title: str
    content: str
    citations: list[str]


class VerseDetail(BaseModel):
    """Full verse metadata for rich reference display."""

    model_config = {"ser_json_timedelta": "iso8601"}

    text: str  # Full verse text (max ~400 chars)
    book_name: str  # "Genesis", "Bakara", etc.
    chapter: int  # Chapter/Surah number
    verse: int  # Verse number
    source: str  # Collection: 'quran_tr', 'bible_ot', 'bible_nt', 'bible_apocrypha'
    translation: str  # "Diyanet Isleri Baskanligi" or "King James Version with Apocrypha"
    book_nr: int | None = None  # Bible book number (None for Quran)


# =============================================================================
# Private Helper Functions
# =============================================================================


def _extract_quran_verse_detail(result: SearchResult) -> tuple[str, VerseDetail]:
    """Extract citation reference and verse detail from Quran SearchResult.

    Args:
        result: Quran search result from ComparativeRAG.search_all()

    Returns:
        Tuple of (citation_reference, verse_detail)
        Example: ("Bakara:153", VerseDetail(...))
    """
    reference = f"{result.surah_name}:{result.verse_id}"

    return reference, VerseDetail(
        text=result.translation[:400],
        book_name=result.surah_name,
        chapter=result.surah_id,
        verse=result.verse_id,
        source="quran_tr",  # Generic marker for all Quran translators
        translation="Diyanet Isleri Baskanligi",
    )


def _extract_bible_verse_detail(result: BibleSearchResult, source: str) -> tuple[str, VerseDetail]:
    """Extract citation reference and verse detail from Bible BibleSearchResult.

    Args:
        result: Bible search result
        source: Collection name ('bible_ot', 'bible_nt', 'bible_apocrypha')

    Returns:
        Tuple of (citation_reference, verse_detail)
        Example: ("Genesis 1:1", VerseDetail(...))
    """
    reference = f"{result.book_name} {result.chapter}:{result.verse}"

    return reference, VerseDetail(
        text=result.text[:400],
        book_name=result.book_name,
        chapter=result.chapter,
        verse=result.verse,
        source=source,
        translation="King James Version with Apocrypha",
        book_nr=result.book_id,
    )


# =============================================================================
# Public Helper Functions
# =============================================================================


def build_verse_details(
    quran_results: list[SearchResult],
    ot_results: list[BibleSearchResult],
    nt_results: list[BibleSearchResult],
    apocrypha_results: list[BibleSearchResult],
    *,
    as_dict: bool = False,
) -> dict[str, Union[VerseDetail, dict]]:
    """
    Build verse details dictionary from search results.

    Extracts citation reference + metadata for each verse, deduplicates
    by reference key. Used by both batch and streaming compare endpoints.

    Args:
        quran_results: Quran search results from ComparativeRAG.search_all()
        ot_results: Old Testament search results
        nt_results: New Testament search results
        apocrypha_results: Apocrypha search results
        as_dict: If True, returns dict values; if False, returns VerseDetail objects

    Returns:
        Dictionary mapping citation references to verse metadata:
        - Keys: "Bakara:153", "Genesis 1:1", etc. (NO BRACKETS)
        - Values: VerseDetail objects or dicts (depending on as_dict)

    Examples:
        >>> # Batch endpoint (compare.py)
        >>> verse_details = build_verse_details(q, ot, nt, ap, as_dict=False)
        >>> verse_details["Bakara:153"]  # VerseDetail(text="...", ...)

        >>> # Streaming endpoint (stream.py)
        >>> verse_details = build_verse_details(q, ot, nt, ap, as_dict=True)
        >>> verse_details["Bakara:153"]  # {"text": "...", ...}
    """
    verse_details: dict[str, VerseDetail] = {}

    # Extract Quran verses
    for result in quran_results:
        ref, detail = _extract_quran_verse_detail(result)
        if ref not in verse_details:
            verse_details[ref] = detail

    # Extract Old Testament verses
    for result in ot_results:
        ref, detail = _extract_bible_verse_detail(result, "bible_ot")
        if ref not in verse_details:
            verse_details[ref] = detail

    # Extract New Testament verses
    for result in nt_results:
        ref, detail = _extract_bible_verse_detail(result, "bible_nt")
        if ref not in verse_details:
            verse_details[ref] = detail

    # Extract Apocrypha verses
    for result in apocrypha_results:
        ref, detail = _extract_bible_verse_detail(result, "bible_apocrypha")
        if ref not in verse_details:
            verse_details[ref] = detail

    logger.info(f"Built verse_details with {len(verse_details)} references")

    # Convert to dict if requested (for SSE serialization)
    if as_dict:
        return {ref: detail.model_dump() for ref, detail in verse_details.items()}

    return cast("dict[str, Union[VerseDetail, dict]]", verse_details)


def build_paragraphs(
    result: MultiAgentAnswer,
    *,
    as_dict: bool = False,
) -> list[Union[ParagraphData, dict]]:
    """
    Build structured paragraphs from MultiAgentAnswer.

    Transforms 5-agent commentaries into ordered paragraph list with
    titles and citations. Used by both batch and streaming endpoints.

    Args:
        result: MultiAgentAnswer from multi_agent_generator.generate()
        as_dict: If True, returns list of dicts; if False, returns ParagraphData objects

    Returns:
        List of up to 5 paragraphs (OT, NT, Apocrypha, Quran, Synthesis) in order.
        Each paragraph includes title, content, and citations.

    Examples:
        >>> # Batch endpoint (compare.py)
        >>> paragraphs = build_paragraphs(result, as_dict=False)
        >>> paragraphs[0]  # ParagraphData(title="Eski Ahit", ...)

        >>> # Streaming endpoint (stream.py)
        >>> paragraphs = build_paragraphs(result, as_dict=True)
        >>> paragraphs[0]  # {"title": "Eski Ahit", ...}
    """
    paragraphs: list[Union[ParagraphData, dict]] = []

    # Paragraph 1: Old Testament
    if result.old_testament_commentary:
        para = ParagraphData(
            title="Eski Ahit (Old Testament)",
            content=result.old_testament_commentary,
            citations=result.citations.get("old_testament", []),
        )
        paragraphs.append(para.model_dump() if as_dict else para)

    # Paragraph 2: New Testament
    if result.new_testament_commentary:
        para = ParagraphData(
            title="Yeni Ahit (New Testament)",
            content=result.new_testament_commentary,
            citations=result.citations.get("new_testament", []),
        )
        paragraphs.append(para.model_dump() if as_dict else para)

    # Paragraph 3: Apocrypha
    if result.apocrypha_commentary:
        para = ParagraphData(
            title="Apokrifa (Apocrypha)",
            content=result.apocrypha_commentary,
            citations=result.citations.get("apocrypha", []),
        )
        paragraphs.append(para.model_dump() if as_dict else para)

    # Paragraph 4: Quran
    if result.quran_commentary:
        para = ParagraphData(
            title="Kuran-ı Kerim",
            content=result.quran_commentary,
            citations=result.citations.get("quran", []),
        )
        paragraphs.append(para.model_dump() if as_dict else para)

    # Paragraph 5: Synthesis
    if result.synthesis:
        para = ParagraphData(
            title="Karşılaştırmalı Değerlendirme",
            content=result.synthesis,
            citations=[],
        )
        paragraphs.append(para.model_dump() if as_dict else para)

    logger.info(f"Built {len(paragraphs)} paragraphs from MultiAgentAnswer")
    return paragraphs
