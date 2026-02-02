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
    buckwalter_to_arabic,
    strip_buckwalter_vowels,
    arabic_to_buckwalter,
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
    root_buckwalter: Optional[str] = None
    word_transliterations: dict[str, str] = field(default_factory=dict)

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

    # Well-known terms whose roots can't be reliably derived algorithmically.
    # Maps normalized forms (Arabic or lowercase Latin) → (root, source).
    # Checked FIRST in _find_root, before any DB or algorithmic lookup.
    SPECIAL_TERMS: dict[str, tuple[str, str]] = {
        # Arabic forms — normalize_arabic() will strip diacritics/hamza
        "الله": ("أله", "exact_match"),
        "لله": ("أله", "exact_match"),
        "بالله": ("أله", "exact_match"),
        "والله": ("أله", "exact_match"),
        "فالله": ("أله", "exact_match"),
        "تالله": ("أله", "exact_match"),
        "اللهم": ("أله", "exact_match"),
        "اله": ("أله", "exact_match"),
        "الاله": ("أله", "exact_match"),
        "القران": ("قرأ", "exact_match"),
        "قران": ("قرأ", "exact_match"),
        "بالقران": ("قرأ", "exact_match"),
        "والقران": ("قرأ", "exact_match"),
        "قرانا": ("قرأ", "exact_match"),
        # Latin forms — normalize_latin_query() will lowercase
        "quran": ("قرأ", "buckwalter_exact"),
        "kuran": ("قرأ", "buckwalter_exact"),
        "quraan": ("قرأ", "buckwalter_exact"),
        "allah": ("أله", "buckwalter_exact"),
    }

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
        self,
        query: str,
        page: int = 1,
        per_page: int = 50,
        word_filter: str | None = None,
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

        return await self._search_root_in_db(
            query, root, source, page, per_page, word_filter=word_filter
        )

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
        """Hybrid root extraction: special terms -> DB lookup -> prefix strip -> algorithmic (Arabic) or Buckwalter (Latin)."""
        # Step 0: Check well-known terms before any other processing.
        # Normalise the lookup key the same way each path would.
        if is_arabic(query):
            lookup_key = normalize_arabic(query)
        else:
            lookup_key = normalize_latin_query(query)
        special = self.SPECIAL_TERMS.get(lookup_key)
        if special:
            return special

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
        """Latin path: exact → vowel-strip → Arabic convert → fuzzy fallback.

        Handles both strict Buckwalter input ('ktb') and common romanizations
        ('kitab') by stripping short-vowel diacritics and converting to Arabic.
        Fuzzy matching is the last resort to avoid false positives.
        """
        normalized = normalize_latin_query(query)

        async with self._session_maker() as session:
            # Step L1: Buckwalter match on root (case-insensitive)
            # normalize_latin_query() lowercases input, but Buckwalter is
            # case-sensitive (H=ح vs h=ه, S=ص vs s=س).  Use LOWER() to
            # match regardless and pick the most frequent root when
            # multiple case variants exist (e.g. hmd→Hmd/حمد over hmd/همد).
            result = await session.execute(
                sa_text(
                    """
                    SELECT root, COUNT(*) as cnt
                    FROM qm_words
                    WHERE LOWER(root_buckwalter) = :q AND root IS NOT NULL
                    GROUP BY root
                    ORDER BY cnt DESC
                    LIMIT 1
                    """
                ),
                {"q": normalized},
            )
            row = result.fetchone()
            if row:
                return (row[0], "buckwalter_exact")

            # Step L2: Strip Buckwalter vowels and retry as root
            # Handles romanized input: 'kitab' → 'ktb', 'salaam' → 'slm'
            vowel_stripped = strip_buckwalter_vowels(normalized)
            if vowel_stripped and vowel_stripped != normalized:
                # L2a: Exact match with vowel-stripped form
                result = await session.execute(
                    sa_text(
                        "SELECT DISTINCT root FROM qm_words "
                        "WHERE root_buckwalter = :q AND root IS NOT NULL LIMIT 1"
                    ),
                    {"q": vowel_stripped},
                )
                row = result.fetchone()
                if row:
                    return (row[0], "buckwalter_vowel_stripped")

                # L2b: Case-insensitive match (catches 'rahim'→'rhm' vs DB 'rHm')
                # Pick the most frequent root when multiple case variants exist
                result = await session.execute(
                    sa_text(
                        """
                        SELECT root, COUNT(*) as cnt
                        FROM qm_words
                        WHERE LOWER(root_buckwalter) = :q AND root IS NOT NULL
                        GROUP BY root
                        ORDER BY cnt DESC
                        LIMIT 1
                        """
                    ),
                    {"q": vowel_stripped},
                )
                row = result.fetchone()
                if row:
                    return (row[0], "buckwalter_vowel_stripped")

                # L2c: Triliteral fallback — most Arabic roots are 3 consonants.
                # If vowel-stripped form is 4+ chars (e.g. 'rhmn' from 'rahman'),
                # try the first 3 chars as a root candidate.
                if len(vowel_stripped) >= 4:
                    triliteral = vowel_stripped[:3]
                    result = await session.execute(
                        sa_text(
                            """
                            SELECT root, COUNT(*) as cnt
                            FROM qm_words
                            WHERE LOWER(root_buckwalter) = :q AND root IS NOT NULL
                            GROUP BY root
                            ORDER BY cnt DESC
                            LIMIT 1
                            """
                        ),
                        {"q": triliteral},
                    )
                    row = result.fetchone()
                    if row:
                        return (row[0], "buckwalter_vowel_stripped")

        # Step L3: Convert Latin to Arabic via reverse Buckwalter, then use Arabic path
        # 'kitab' → tim2utf8 → 'كِتَب' → normalize → 'كتب' → Arabic root lookup
        try:
            arabic_text = buckwalter_to_arabic(normalized)
            if arabic_text:
                arabic_normalized = normalize_arabic(arabic_text)
                if arabic_normalized and is_arabic(arabic_normalized):
                    root, source = await self._find_root_arabic(arabic_normalized)
                    if root:
                        return (root, "buckwalter_converted")
        except Exception as exc:
            logger.warning("Buckwalter→Arabic conversion failed: %s", exc)

        # Step L4: Fuzzy match as last resort via pg_trgm
        async with self._session_maker() as session:
            # L4a: Fuzzy on original normalized input
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

            # L4b: Fuzzy on vowel-stripped form
            if vowel_stripped and vowel_stripped != normalized:
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
                    {"q": vowel_stripped},
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
        word_filter: str | None = None,
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

            # Compute Buckwalter transliterations
            root_buckwalter = arabic_to_buckwalter(root) if root else None
            word_transliterations: dict[str, str] = {}
            for word in unique_words:
                try:
                    word_transliterations[word] = arabic_to_buckwalter(word)
                except Exception:
                    word_transliterations[word] = word  # fallback to Arabic

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
            # When word_filter is set, only count verses that contain the specific word form
            count_sql = """
                    SELECT COUNT(DISTINCT a.id)
                    FROM qm_words w JOIN qm_ayahs a ON w.ayah_id = a.id
                    WHERE w.root = :root
                    """
            count_params: dict[str, object] = {"root": root}
            if word_filter:
                count_sql += " AND w.token_clean = :word_filter"
                count_params["word_filter"] = word_filter
            total_verses_result = await session.execute(
                sa_text(count_sql), count_params
            )
            total_verses = total_verses_result.scalar()

            # 5. Verse results (paginated or all when per_page=0)
            verses_sql = """
                    SELECT DISTINCT a.id, s.id as surah_id, s.name_arabic,
                           a.ayah_number, a.text_uthmani, a.text_clean
                    FROM qm_words w
                    JOIN qm_ayahs a ON w.ayah_id = a.id
                    JOIN qm_surahs s ON a.surah_id = s.id
                    WHERE w.root = :root
                    """
            verses_params: dict[str, object] = {"root": root}
            if word_filter:
                verses_sql += " AND w.token_clean = :word_filter"
                verses_params["word_filter"] = word_filter
            verses_sql += "\n                    ORDER BY s.id, a.ayah_number"
            if per_page > 0:
                offset = (page - 1) * per_page
                verses_sql += "\n                    LIMIT :limit OFFSET :offset"
                verses_params["limit"] = per_page
                verses_params["offset"] = offset
            verses_result = await session.execute(sa_text(verses_sql), verses_params)
            verse_rows = verses_result.fetchall()

            # 6. Batch-fetch matched words for all verses in one query
            ayah_ids = [vr[0] for vr in verse_rows]
            matched_words_map: dict[int, list[str]] = {aid: [] for aid in ayah_ids}
            if ayah_ids:
                # Fetch all matched words for all verses at once
                placeholders = ",".join(str(aid) for aid in ayah_ids)
                batch_words_result = await session.execute(
                    sa_text(
                        f"SELECT DISTINCT ayah_id, token_clean FROM qm_words "
                        f"WHERE ayah_id IN ({placeholders}) AND root = :root "
                        f"AND token_clean IS NOT NULL"
                    ),
                    {"root": root},
                )
                for row in batch_words_result.fetchall():
                    aid, token = row[0], row[1]
                    if token not in matched_words_map[aid]:
                        matched_words_map[aid].append(token)

            verses: list[VerseMatch] = []
            for vr in verse_rows:
                verses.append(
                    VerseMatch(
                        surah_id=vr[1],
                        surah_name=vr[2],
                        ayah_number=vr[3],
                        text_uthmani=vr[4],
                        text_clean=vr[5],
                        matched_words=matched_words_map.get(vr[0], []),
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
            root_buckwalter=root_buckwalter,
            word_transliterations=word_transliterations,
        )
