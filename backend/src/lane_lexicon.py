"""Lane's Lexicon SQLite adapter.

This module provides a small adapter around the Lane's Arabic-English Lexicon
SQLite database published at https://github.com/laneslexicon/LexiconDatabase
(GPL-3.0). It resolves Quranic roots (Buckwalter or Arabic script) to an
English lexical definition extracted from Lane XML entries.
"""

from __future__ import annotations

import html
import logging
import re
import sqlite3
import unicodedata
from dataclasses import dataclass
from difflib import SequenceMatcher
from typing import TYPE_CHECKING

from src.arabic_normalizer import arabic_to_buckwalter, buckwalter_to_arabic, normalize_arabic

if TYPE_CHECKING:
    from pathlib import Path

logger = logging.getLogger(__name__)


_TAG_RE = re.compile(r"<[^>]+>")
_WS_RE = re.compile(r"\s+")


@dataclass
class LaneEntry:
    root_buckwalter: str
    root_arabic: str | None
    definition_en: str
    volume: int | None
    match_type: str  # "exact", "fuzzy"


@dataclass
class MatchStats:
    total: int
    matched: int
    unmatched: int
    exact_matches: int
    fuzzy_matches: int


class LaneLexiconAdapter:
    """Adapter for Lane's Lexicon SQLite root lookups.

    The constructor accepts either a SQLite file path or a directory containing
    a `.sqlite` / `.db` file.
    """

    def __init__(self, db_path: Path):
        """Open Lane's Lexicon SQLite database.

        Args:
            db_path: Path to a SQLite file or directory containing one.

        Raises:
            FileNotFoundError: If no Lane SQLite database is found.
        """
        self.db_file = self._discover_db_file(db_path)
        self.connection = sqlite3.connect(str(self.db_file))
        self.connection.row_factory = sqlite3.Row
        self._max_page = self._fetch_max_page()

    @staticmethod
    def _discover_db_file(db_path: Path) -> Path:
        if db_path.is_file() and db_path.suffix in {".sqlite", ".db"}:
            return db_path

        if db_path.is_dir():
            candidates = sorted(
                [*db_path.rglob("*.sqlite"), *db_path.rglob("*.db")],
                key=lambda item: (item.name != "lexicon.sqlite", len(str(item))),
            )
            if candidates:
                return candidates[0]

        raise FileNotFoundError(f"Lane lexicon database file not found under: {db_path}")

    def _fetch_max_page(self) -> int:
        row = self.connection.execute("SELECT MAX(page) AS max_page FROM entry").fetchone()
        if row is None or row["max_page"] is None:
            return 0
        return int(row["max_page"])

    @staticmethod
    def _clean_root_input(value: str | None) -> str:
        if value is None:
            return ""
        normalized = unicodedata.normalize("NFKC", value).strip()
        return normalized

    @staticmethod
    def _xml_to_text(xml_text: str) -> str:
        text = html.unescape(xml_text)
        text = _TAG_RE.sub(" ", text)
        text = _WS_RE.sub(" ", text).strip()
        return text

    def _build_entry(self, row: sqlite3.Row, match_type: str) -> LaneEntry:
        root_buckwalter = row["broot"] or ""
        root_arabic = row["root"]
        definition_en = self._xml_to_text(row["xml"] or "")
        volume = self._volume_from_page(row["page"])
        return LaneEntry(
            root_buckwalter=root_buckwalter,
            root_arabic=root_arabic,
            definition_en=definition_en,
            volume=volume,
            match_type=match_type,
        )

    def _volume_from_page(self, page: int | None) -> int | None:
        if page is None or self._max_page <= 0:
            return None
        page_int = int(page)
        if page_int <= 0:
            return None
        volume = ((page_int - 1) * 8) // self._max_page + 1
        return min(max(volume, 1), 8)

    def _query_exact_buckwalter(self, root_buckwalter: str) -> sqlite3.Row | None:
        return self.connection.execute(
            """
            SELECT root, broot, xml, page
            FROM entry
            WHERE broot = ?
            ORDER BY LENGTH(xml) DESC
            LIMIT 1
            """,
            (root_buckwalter,),
        ).fetchone()

    def _query_exact_arabic(self, root_arabic: str) -> sqlite3.Row | None:
        return self.connection.execute(
            """
            SELECT root, broot, xml, page
            FROM entry
            WHERE root = ?
            ORDER BY LENGTH(xml) DESC
            LIMIT 1
            """,
            (root_arabic,),
        ).fetchone()

    def _query_fuzzy(self, root_buckwalter: str) -> sqlite3.Row | None:
        prefix = f"{root_buckwalter}%"
        contains = f"%{root_buckwalter}%"
        candidates = self.connection.execute(
            """
            SELECT root, broot, xml, page
            FROM entry
            WHERE broot LIKE ? OR broot LIKE ?
            LIMIT 50
            """,
            (prefix, contains),
        ).fetchall()
        if not candidates:
            return None

        scored = [
            (
                SequenceMatcher(None, root_buckwalter, str(candidate["broot"]).strip()).ratio(),
                candidate,
            )
            for candidate in candidates
            if candidate["broot"]
        ]
        if not scored:
            return None

        scored.sort(key=lambda item: item[0], reverse=True)
        best_score, best_row = scored[0]
        if best_score < 0.60:
            return None
        return best_row

    def lookup_by_root(self, root_buckwalter: str) -> LaneEntry | None:
        """Look up a root in Lane's Lexicon by Buckwalter transliteration.

        Matching order: exact Buckwalter -> exact Arabic -> fuzzy -> None.
        """
        normalized = self._clean_root_input(root_buckwalter)
        if not normalized:
            return None

        row = self._query_exact_buckwalter(normalized)
        if row is not None:
            return self._build_entry(row, "exact")

        arabic_guess = self.lookup_by_arabic(buckwalter_to_arabic(normalized))
        if arabic_guess is not None:
            return LaneEntry(
                root_buckwalter=arabic_guess.root_buckwalter,
                root_arabic=arabic_guess.root_arabic,
                definition_en=arabic_guess.definition_en,
                volume=arabic_guess.volume,
                match_type="exact",
            )

        fuzzy_row = self._query_fuzzy(normalized)
        if fuzzy_row is not None:
            return self._build_entry(fuzzy_row, "fuzzy")

        return None

    def lookup_by_arabic(self, root_arabic: str) -> LaneEntry | None:
        """Look up by Arabic script root (converts to Buckwalter internally)."""
        normalized_arabic = self._clean_root_input(root_arabic)
        if not normalized_arabic:
            return None

        normalized_arabic = normalize_arabic(normalized_arabic)
        if not normalized_arabic:
            return None

        row = self._query_exact_arabic(normalized_arabic)
        if row is not None:
            return self._build_entry(row, "exact")

        buckwalter = self._clean_root_input(arabic_to_buckwalter(normalized_arabic))
        if not buckwalter:
            return None

        row = self._query_exact_buckwalter(buckwalter)
        if row is not None:
            return self._build_entry(row, "exact")

        fuzzy_row = self._query_fuzzy(buckwalter)
        if fuzzy_row is not None:
            return self._build_entry(fuzzy_row, "fuzzy")

        return None

    def get_volume(self, entry: LaneEntry) -> int | None:
        """Extract volume number for confidence classification."""
        return entry.volume

    def get_match_stats(self, roots: list[str]) -> MatchStats:
        """Batch match roots and return statistics."""
        total = len(roots)
        matched = 0
        exact_matches = 0
        fuzzy_matches = 0

        for root in roots:
            result = self.lookup_by_root(root)
            if result is None:
                continue
            matched += 1
            if result.match_type == "fuzzy":
                fuzzy_matches += 1
            else:
                exact_matches += 1

        unmatched = total - matched
        ratio = (matched / total * 100.0) if total else 0.0
        logger.info("Lane matches: %s/%s (%.1f%%)", matched, total, ratio)
        return MatchStats(
            total=total,
            matched=matched,
            unmatched=unmatched,
            exact_matches=exact_matches,
            fuzzy_matches=fuzzy_matches,
        )
