"""Quran morphological root-based search service.

Provides async database-backed search for Arabic roots in the Quran.
Supports Arabic input (with prefix stripping and algorithmic fallback)
and Latin/Buckwalter transliteration input (with fuzzy matching via pg_trgm).

Usage:
    search = QuranMorphologySearch("postgresql+asyncpg://...")
    result = await search.search_by_root("كتب")
    result = await search.search_by_root("ktb")  # Buckwalter Latin
    await search.close()
"""

import logging
from dataclasses import dataclass, field, asdict
from typing import Optional

from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
)
from sqlalchemy import text as sa_text

from .arabic_normalizer import (
    normalize_arabic,
    is_arabic,
    normalize_latin_query,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Result Dataclasses
# ---------------------------------------------------------------------------


@dataclass
class SurahCount:
    """Occurrence count of a root within a single surah."""

    surah_id: int
    surah_name: str
    count: int


@dataclass
class VerseMatch:
    """A single verse containing the searched root."""

    surah_id: int
    surah_name: str
    ayah_number: int
    text_uthmani: str
    text_clean: str
    matched_words: list[str] = field(default_factory=list)


@dataclass
class MorphologySearchResult:
    """Complete result of a morphological root search."""

    query: str
    root: Optional[str]
    root_source: str  # exact_match | prefix_stripped | algorithmic | buckwalter_exact | buckwalter_fuzzy | not_found
    total_occurrences: int = 0
    unique_words: list[str] = field(default_factory=list)
    surah_distribution: list[SurahCount] = field(default_factory=list)
    verses: list[VerseMatch] = field(default_factory=list)
    page: int = 1
    per_page: int = 50
    total_verses: int = 0

    def to_dict(self) -> dict:
        """Serialize to plain dict for JSON responses."""
        return asdict(self)


# ---------------------------------------------------------------------------
# Main Search Service
# ---------------------------------------------------------------------------


class QuranMorphologySearch:
    """Root-based morphological search for the Quran.

    Creates its own async engine (independent of app.db) so it can be
    used from both CLI and API contexts.
    """

    # Prefix strip order: longest first to avoid partial matches
    PREFIXES = [
        "\u0648\u0644\u0644",  # ولل
        "\u0648\u0627\u0644",  # وال
        "\u0641\u0627\u0644",  # فال
        "\u0644\u0644",  # لل
        "\u0627\u0644",  # ال
        "\u0648\u0644",  # ول
        "\u0641\u0644",  # فل
        "\u0648",  # و
        "\u0641",  # ف
        "\u0644",  # ل
        "\u0628",  # ب
        "\u0643",  # ك
    ]

    def __init__(self, db_url: str) -> None:
        self._engine = create_async_engine(db_url, echo=False, pool_pre_ping=True)
        self._session_maker = async_sessionmaker(
            self._engine, class_=AsyncSession, expire_on_commit=False
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def search_by_root(
        self, query: str, page: int = 1, per_page: int = 50
    ) -> MorphologySearchResult:
        """Main entry point: detect language, find root, search database."""
        # Sanitize: strip null bytes and control chars that PostgreSQL rejects
        query = query.replace("\x00", "").strip()
        if not query:
            return MorphologySearchResult(
                query=query,
                root=None,
                root_source="not_found",
                page=max(page, 1),
                per_page=min(per_page, 200),
            )
        per_page = min(per_page, 200)
        page = max(page, 1)

        root, source = await self._find_root(query)

        if root is None:
            return MorphologySearchResult(
                query=query,
                root=None,
                root_source=source,
                page=page,
                per_page=per_page,
            )

        return await self._search_root_in_db(query, root, source, page, per_page)

    async def list_roots(self, page: int = 1, per_page: int = 50) -> dict:
        """List all available roots with occurrence counts, paginated."""
        per_page = min(per_page, 200)
        offset = (page - 1) * per_page

        async with self._session_maker() as session:
            total_result = await session.execute(
                sa_text(
                    "SELECT COUNT(DISTINCT root) FROM qm_words WHERE root IS NOT NULL"
                )
            )
            total = total_result.scalar()

            roots_result = await session.execute(
                sa_text(
                    """
                    SELECT root, COUNT(*) as cnt
                    FROM qm_words
                    WHERE root IS NOT NULL
                    GROUP BY root
                    ORDER BY cnt DESC
                    LIMIT :limit OFFSET :offset
                    """
                ),
                {"limit": per_page, "offset": offset},
            )
            roots = [{"root": r[0], "count": r[1]} for r in roots_result.fetchall()]

        return {
            "roots": roots,
            "total": total,
            "page": page,
            "per_page": per_page,
        }

    async def close(self) -> None:
        """Dispose engine and release connection pool."""
        await self._engine.dispose()

    # ------------------------------------------------------------------
    # Root Finding
    # ------------------------------------------------------------------

    async def _find_root(self, query: str) -> tuple[Optional[str], str]:
        """Hybrid root extraction: DB lookup -> prefix strip -> algorithmic (Arabic) or Buckwalter (Latin)."""
        if is_arabic(query):
            return await self._find_root_arabic(query)
        return await self._find_root_latin(query)

    async def _find_root_arabic(self, query: str) -> tuple[Optional[str], str]:
        """Arabic path: normalize -> exact match -> prefix strip -> Tashaphyne."""
        normalized = normalize_arabic(query)

        async with self._session_maker() as session:
            # Step 1: Exact match on token_clean
            result = await session.execute(
                sa_text(
                    "SELECT root FROM qm_words "
                    "WHERE token_clean = :q AND root IS NOT NULL LIMIT 1"
                ),
                {"q": normalized},
            )
            row = result.fetchone()
            if row:
                return (row[0], "exact_match")

            # Step 2: Prefix stripping — try longest prefixes first
            for prefix in self.PREFIXES:
                if normalized.startswith(prefix) and len(normalized) > len(prefix):
                    remainder = normalized[len(prefix) :]
                    result = await session.execute(
                        sa_text(
                            "SELECT root FROM qm_words "
                            "WHERE token_clean = :q AND root IS NOT NULL LIMIT 1"
                        ),
                        {"q": remainder},
                    )
                    row = result.fetchone()
                    if row:
                        return (row[0], "prefix_stripped")

            # Step 3: Check if input itself IS a root
            # Normalize both sides: user input is already normalized, but DB roots may contain hamza
            # Use SQL REPLACE to normalize hamza variants (أ, إ, آ) to plain alef (ا)
            result = await session.execute(
                sa_text(
                    """
                    SELECT DISTINCT root FROM qm_words 
                    WHERE REPLACE(REPLACE(REPLACE(root, 'أ', 'ا'), 'إ', 'ا'), 'آ', 'ا') = :q 
                    AND root IS NOT NULL 
                    LIMIT 1
                    """
                ),
                {"q": normalized},
            )
            row = result.fetchone()
            if row:
                return (row[0], "exact_match")

        # Step 4: Tashaphyne algorithmic fallback
        try:
            from tashaphyne.stemming import ArabicLightStemmer

            stemmer = ArabicLightStemmer()
            stemmer.light_stem(query)
            algo_root = stemmer.get_root()
            if algo_root:
                # Verify this root exists in DB
                async with self._session_maker() as session:
                    result = await session.execute(
                        sa_text(
                            "SELECT DISTINCT root FROM qm_words WHERE root = :q LIMIT 1"
                        ),
                        {"q": algo_root},
                    )
                    row = result.fetchone()
                    if row:
                        return (algo_root, "algorithmic")
                return (algo_root, "algorithmic")
        except Exception as exc:
            logger.warning("Tashaphyne fallback failed: %s", exc)

        return (None, "not_found")

    async def _find_root_latin(self, query: str) -> tuple[Optional[str], str]:
        """Latin path: normalize -> Buckwalter exact -> Buckwalter fuzzy (pg_trgm)."""
        normalized = normalize_latin_query(query)

        async with self._session_maker() as session:
            # Step L1: Buckwalter exact match
            result = await session.execute(
                sa_text(
                    "SELECT DISTINCT root FROM qm_words "
                    "WHERE root_buckwalter = :q AND root IS NOT NULL LIMIT 1"
                ),
                {"q": normalized},
            )
            row = result.fetchone()
            if row:
                return (row[0], "buckwalter_exact")

            # Step L2: Buckwalter fuzzy match via pg_trgm
            # NOTE: Use literal_binds=False to avoid parameter escaping issues with %
            result = await session.execute(
                sa_text(
                    """
                    SELECT DISTINCT root, root_buckwalter,
                           similarity(root_buckwalter, :q) AS sim
                    FROM qm_words
                    WHERE root_buckwalter % :q AND root IS NOT NULL
                    ORDER BY sim DESC
                    LIMIT 5
                    """
                ),
                {"q": normalized},
            )
            rows = result.fetchall()
            if rows:
                return (rows[0][0], "buckwalter_fuzzy")

        return (None, "not_found")

    # ------------------------------------------------------------------
    # Database Search
    # ------------------------------------------------------------------

    async def _search_root_in_db(
        self,
        query: str,
        root: str,
        source: str,
        page: int,
        per_page: int,
    ) -> MorphologySearchResult:
        """Query all data for a given root: count, unique words, surah distribution, paginated verses."""
        async with self._session_maker() as session:
            # 1. Total occurrences
            total_result = await session.execute(
                sa_text("SELECT COUNT(*) FROM qm_words WHERE root = :root"),
                {"root": root},
            )
            total_occurrences = total_result.scalar()

            # 2. Unique derived words (token_clean, deduplicated)
            words_result = await session.execute(
                sa_text(
                    "SELECT DISTINCT token_clean FROM qm_words "
                    "WHERE root = :root AND token_clean IS NOT NULL "
                    "ORDER BY token_clean"
                ),
                {"root": root},
            )
            unique_words = [row[0] for row in words_result.fetchall()]

            # 3. Surah distribution
            dist_result = await session.execute(
                sa_text(
                    """
                    SELECT s.id, s.name_arabic, COUNT(*) as cnt
                    FROM qm_words w
                    JOIN qm_ayahs a ON w.ayah_id = a.id
                    JOIN qm_surahs s ON a.surah_id = s.id
                    WHERE w.root = :root
                    GROUP BY s.id, s.name_arabic
                    ORDER BY cnt DESC
                    """
                ),
                {"root": root},
            )
            surah_distribution = [
                SurahCount(surah_id=r[0], surah_name=r[1], count=r[2])
                for r in dist_result.fetchall()
            ]

            # 4. Count total distinct verses containing this root
            total_verses_result = await session.execute(
                sa_text(
                    """
                    SELECT COUNT(DISTINCT a.id)
                    FROM qm_words w JOIN qm_ayahs a ON w.ayah_id = a.id
                    WHERE w.root = :root
                    """
                ),
                {"root": root},
            )
            total_verses = total_verses_result.scalar()

            # 5. Paginated verse results
            offset = (page - 1) * per_page
            verses_result = await session.execute(
                sa_text(
                    """
                    SELECT DISTINCT a.id, s.id as surah_id, s.name_arabic,
                           a.ayah_number, a.text_uthmani, a.text_clean
                    FROM qm_words w
                    JOIN qm_ayahs a ON w.ayah_id = a.id
                    JOIN qm_surahs s ON a.surah_id = s.id
                    WHERE w.root = :root
                    ORDER BY s.id, a.ayah_number
                    LIMIT :limit OFFSET :offset
                    """
                ),
                {"root": root, "limit": per_page, "offset": offset},
            )
            verse_rows = verses_result.fetchall()

            # 6. For each verse, get matched words
            verses: list[VerseMatch] = []
            for vr in verse_rows:
                ayah_db_id = vr[0]
                surah_id = vr[1]
                surah_name = vr[2]
                ayah_number = vr[3]
                text_uthmani = vr[4]
                text_clean = vr[5]

                words_in_verse = await session.execute(
                    sa_text(
                        "SELECT DISTINCT token FROM qm_words "
                        "WHERE ayah_id = :aid AND root = :root "
                        "AND token IS NOT NULL"
                    ),
                    {"aid": ayah_db_id, "root": root},
                )
                matched = [w[0] for w in words_in_verse.fetchall()]

                verses.append(
                    VerseMatch(
                        surah_id=surah_id,
                        surah_name=surah_name,
                        ayah_number=ayah_number,
                        text_uthmani=text_uthmani,
                        text_clean=text_clean,
                        matched_words=matched,
                    )
                )

        return MorphologySearchResult(
            query=query,
            root=root,
            root_source=source,
            total_occurrences=total_occurrences,
            unique_words=unique_words,
            surah_distribution=surah_distribution,
            verses=verses,
            page=page,
            per_page=per_page,
            total_verses=total_verses,
        )
