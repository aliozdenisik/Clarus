"""Bible morphological root-based search service.

Provides async database-backed search for Hebrew/Aramaic roots in the Bible.
Supports Hebrew input (with nikud stripping and Strong's lookup),
Latin transliteration input (with fuzzy matching via pg_trgm),
and direct Strong's number input (H3789).

Usage:
    search = await BibleMorphologySearch.get_instance()
    result = await search.search("כתב")       # Hebrew input
    result = await search.search("H3789")      # Strong's number
    result = await search.search("ktb")        # Latin transliteration
    await search.close()
"""

import logging
import re
from dataclasses import dataclass, field, asdict
from typing import Optional

from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
)
from sqlalchemy import text as sa_text

from .hebrew_normalizer import (
    normalize_hebrew,
    transliterate_hebrew,
    detect_script,
    normalize_transliteration_for_lookup,
    normalize_user_hebrew_query,
)
from .greek_normalizer import (
    normalize_greek,
    normalize_greek_transliteration_for_lookup,
    normalize_user_greek_query,
)

logger = logging.getLogger(__name__)

DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:54322/postgres"

# Regex for Strong's number input: H or G followed by digits
STRONGS_PATTERN = re.compile(r"^[HGhg]\d{1,5}$")


# ---------------------------------------------------------------------------
# Hebrew Bet/Vet (ב) Variant Generation
# ---------------------------------------------------------------------------


def _generate_bet_vet_variant(text: str) -> str:
    """Generate the alternate b↔v variant for Hebrew transliteration.

    Hebrew letter ב (Bet/Vet) is transliterated as:
    - 'b' when it has dagesh (stop consonant) - ISO 259, SBL, ALA-LC
    - 'v' when it lacks dagesh (fricative) - ISO 259, SBL, ALA-LC

    Different databases and user inputs use different conventions:
    - Strong's: "da.var" (fricative convention)
    - User search: "dabar" (stop convention)

    This function swaps all b↔v to generate the alternate form,
    allowing dual-indexing for search compatibility.

    Academic References:
    - ISO 259:1984 Hebrew Romanization
    - ALA-LC Romanization Tables (Library of Congress)
    - SBL Handbook of Style, 2nd ed.

    Args:
        text: Normalized ASCII transliteration (e.g., "davar", "dabar")

    Returns:
        Alternate form with b↔v swapped (e.g., "dabar", "davar")

    Example:
        >>> _generate_bet_vet_variant("davar")
        'dabar'
        >>> _generate_bet_vet_variant("dabar")
        'davar'
        >>> _generate_bet_vet_variant("yehovah")
        'yehobah'
    """
    if not text:
        return text

    # Build translation table: b↔v swap
    # Using str.translate for efficiency
    trans_table = str.maketrans("bv", "vb")
    return text.translate(trans_table)


# ---------------------------------------------------------------------------
# Result Dataclasses
# ---------------------------------------------------------------------------


@dataclass
class BookCount:
    """Occurrence count of a root within a single book."""

    book_id: int
    book_name: str
    count: int


@dataclass
class BibleVerseMatch:
    """A single verse containing the searched root/word."""

    book_id: int
    book_name: str
    chapter: int
    verse: int
    text_original: Optional[str]
    text_english: Optional[str]
    matched_words: list[str] = field(default_factory=list)
    reference: str = ""


@dataclass
class BibleMorphologySearchResult:
    """Complete result of a Bible morphological search."""

    query: str
    root: Optional[str]
    root_source: (
        str  # exact_match | strongs_lookup | transliteration | fuzzy | not_found
    )
    strong_number: Optional[str] = None
    total_occurrences: int = 0
    unique_words: list[str] = field(default_factory=list)
    book_distribution: list[BookCount] = field(default_factory=list)
    verses: list[BibleVerseMatch] = field(default_factory=list)
    page: int = 1
    per_page: int = 50
    total_verses: int = 0
    transliteration: Optional[str] = None
    word_transliterations: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Serialize to plain dict for JSON responses."""
        return asdict(self)


# ---------------------------------------------------------------------------
# Main Search Service
# ---------------------------------------------------------------------------


class BibleMorphologySearch:
    """Root-based morphological search for the Bible (Hebrew/Aramaic).

    Creates its own async engine (independent of app.db) so it can be
    used from both CLI and API contexts. Uses singleton pattern with
    in-memory Strong's cache for fast lookups.
    """

    _instance: Optional["BibleMorphologySearch"] = None

    def __init__(self) -> None:
        self._engine = create_async_engine(DATABASE_URL, echo=False, pool_pre_ping=True)
        self._session_maker = async_sessionmaker(
            self._engine, class_=AsyncSession, expire_on_commit=False
        )
        # Forward map: strong_number → {original_word, transliteration, definition, language}
        self._strongs_cache: dict[str, dict] = {}
        # Reverse map: normalized_original_word (no nikud) → strong_number
        self._reverse_strongs: dict[str, list[str]] = {}
        # Transliteration map: strongs_transliteration → strong_number
        self._transliteration_map: dict[str, list[str]] = {}

    @classmethod
    async def get_instance(cls) -> "BibleMorphologySearch":
        """Get or create singleton instance with loaded cache."""
        if cls._instance is None:
            cls._instance = cls()
            await cls._instance._load_strongs_cache()
        return cls._instance

    async def _load_strongs_cache(self) -> None:
        """Load ALL bm_strongs into memory (~14K entries, ~2MB).

        Builds three lookup structures:
        - Forward: number → {original_word, transliteration, definition, language}
          (indexed by BOTH original key and zero-padded variant)
        - Reverse: normalized_hebrew → [numbers]
        - Transliteration: transliteration_lower → [numbers]
        """
        async with self._session_maker() as session:
            result = await session.execute(
                sa_text(
                    "SELECT number, original_word, transliteration, definition, language "
                    "FROM bm_strongs"
                )
            )
            rows = result.fetchall()

        for row in rows:
            number, original_word, translit, definition, language = row
            entry = {
                "original_word": original_word,
                "transliteration": translit,
                "definition": definition,
                "language": language,
            }
            self._strongs_cache[number] = entry

            # Also index by zero-padded variant (H430 → H0430)
            # bm_words uses H0430 format, bm_strongs uses H430
            prefix = number[0] if number else ""
            num_str = number[1:] if number else ""
            try:
                padded = f"{prefix}{int(num_str):04d}"
                if padded != number:
                    self._strongs_cache[padded] = entry
            except ValueError:
                pass

            # Build reverse map: normalized Hebrew → Strong's numbers
            if original_word:
                normalized = normalize_hebrew(original_word)
                if normalized not in self._reverse_strongs:
                    self._reverse_strongs[normalized] = []
                if number not in self._reverse_strongs[normalized]:
                    self._reverse_strongs[normalized].append(number)

            # Build transliteration map (original scholarly form)
            # Use zero-padded format (H0430) to match bm_words table format
            if translit:
                # Compute zero-padded Strong's number for bm_words compatibility
                padded_number = number
                if number and len(number) > 1:
                    prefix = number[0]
                    num_str = number[1:]
                    try:
                        padded_number = f"{prefix}{int(num_str):04d}"
                    except ValueError:
                        pass

                translit_lower = translit.lower().strip()
                if translit_lower not in self._transliteration_map:
                    self._transliteration_map[translit_lower] = []
                if padded_number not in self._transliteration_map[translit_lower]:
                    self._transliteration_map[translit_lower].append(padded_number)

                # Also add NORMALIZED ASCII key for user-friendly lookup
                # Use language-specific normalizer:
                # - Hebrew (H*): "ʼĕlôhîym" → "elohim", "chêçêd" → "hesed"
                # - Greek (G*): "zōḗ" → "zoe", "agápē" → "agape"
                is_greek = number.startswith("G") if number else False
                if is_greek:
                    normalized_ascii = normalize_greek_transliteration_for_lookup(
                        translit
                    )
                else:
                    normalized_ascii = normalize_transliteration_for_lookup(translit)

                if normalized_ascii and normalized_ascii != translit_lower:
                    if normalized_ascii not in self._transliteration_map:
                        self._transliteration_map[normalized_ascii] = []
                    if padded_number not in self._transliteration_map[normalized_ascii]:
                        self._transliteration_map[normalized_ascii].append(
                            padded_number
                        )

                # DUAL-INDEXING for Hebrew Bet/Vet (ב) variants
                # Academic basis: Hebrew ב is pronounced 'b' with dagesh (stop),
                # 'v' without dagesh (fricative). Different transliteration schemes
                # use different conventions (ISO 259 vs SBL vs ALA-LC).
                # Solution: Index BOTH b↔v variants pointing to the same Strong's.
                # Reference: ALA-LC Romanization Tables, Sefaria search implementation
                if not is_greek and normalized_ascii:
                    bet_vet_variant = _generate_bet_vet_variant(normalized_ascii)
                    if bet_vet_variant and bet_vet_variant != normalized_ascii:
                        if bet_vet_variant not in self._transliteration_map:
                            self._transliteration_map[bet_vet_variant] = []
                        if (
                            padded_number
                            not in self._transliteration_map[bet_vet_variant]
                        ):
                            self._transliteration_map[bet_vet_variant].append(
                                padded_number
                            )

        # OCCURRENCE-BASED PRIORITIZATION
        # When multiple Strong's numbers map to the same transliteration key
        # (e.g., "torah" → [H2960, H8451]), prioritize by occurrence count.
        # This ensures the most common word (H8451 "law" with 219 occurrences)
        # is returned before rare homographs (H2960 "burden" with 2 occurrences).
        # Reference: Standard IR practice for disambiguation
        await self._sort_maps_by_occurrence()

        logger.info(
            "Loaded Strong's cache: %d entries, %d reverse mappings, %d transliterations",
            len(self._strongs_cache),
            len(self._reverse_strongs),
            len(self._transliteration_map),
        )

    async def _sort_maps_by_occurrence(self) -> None:
        """Sort transliteration and reverse Strong's maps by occurrence count.

        When multiple Strong's numbers map to the same key (homographs),
        this ensures the most common word is returned first during lookup.

        Example: "torah" → [H2960, H8451]
        - H2960 (burden): 2 occurrences
        - H8451 (law): 219 occurrences
        After sorting: [H8451, H2960] (most common first)

        This is standard IR practice for disambiguation and improves
        search result relevance.
        """
        # Query occurrence counts for all Strong's numbers
        async with self._session_maker() as session:
            result = await session.execute(
                sa_text(
                    """
                    SELECT strong_number, COUNT(*) as cnt
                    FROM bm_words
                    WHERE strong_number IS NOT NULL
                    GROUP BY strong_number
                    """
                )
            )
            occurrence_counts = {row[0]: row[1] for row in result.fetchall()}

        # Sort transliteration_map lists by occurrence count (descending)
        for key in self._transliteration_map:
            self._transliteration_map[key].sort(
                key=lambda sn: occurrence_counts.get(sn, 0), reverse=True
            )

        # Sort reverse_strongs lists by occurrence count (descending)
        for key in self._reverse_strongs:
            self._reverse_strongs[key].sort(
                key=lambda sn: occurrence_counts.get(sn, 0), reverse=True
            )

        logger.debug(
            "Sorted maps by occurrence count (%d Strong's numbers)",
            len(occurrence_counts),
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def search(
        self,
        query: str,
        page: int = 1,
        per_page: int = 50,
        language_filter: Optional[str] = None,
        word_filter: Optional[str] = None,
        testament_filter: Optional[str] = None,
        category_filter: Optional[str] = None,
    ) -> BibleMorphologySearchResult:
        """Main entry point: detect input type, find root/strong, search database.

        Args:
            query: Hebrew text, Strong's number (H3789), or Latin transliteration
            page: Page number (1-based)
            per_page: Results per page (max 200)
            language_filter: Optional filter on bm_words.language ('hebrew', 'aramaic', or None)
            word_filter: Optional filter to search within specific word forms
            testament_filter: Optional filter on bm_books.testament ('ot', 'nt', 'apocrypha', or None)
            category_filter: Optional filter on bm_books.category ('ot', 'nt', 'apocrypha', 'pseudepigrapha', 'gnostic', 'apostolic_fathers', or None)
        """
        logger.info(
            "[BibleMorphology.search] START: query=%r, page=%d, per_page=%d, "
            "language_filter=%r, word_filter=%r, testament_filter=%r, category_filter=%r",
            query,
            page,
            per_page,
            language_filter,
            word_filter,
            testament_filter,
            category_filter,
        )
        try:
            query = query.replace("\x00", "").strip()
            if not query:
                logger.warning("[BibleMorphology.search] Empty query after strip")
                return BibleMorphologySearchResult(
                    query=query,
                    root=None,
                    root_source="not_found",
                    page=max(page, 1),
                    per_page=min(per_page, 200),
                )
            per_page = min(per_page, 200)
            page = max(page, 1)

            logger.debug(
                "[BibleMorphology.search] Finding root for query=%r, language_filter=%r",
                query,
                language_filter,
            )
            identifier, root_source = await self._find_root(
                query, language_filter=language_filter
            )
            logger.info(
                "[BibleMorphology.search] Root found: identifier=%r, root_source=%r",
                identifier,
                root_source,
            )
        except Exception as e:
            logger.exception(
                "[BibleMorphology.search] CRASH in _find_root: query=%r, error=%s",
                query,
                str(e),
            )
            raise

        if identifier is None:
            logger.info(
                "[BibleMorphology.search] No identifier found, returning not_found"
            )
            return BibleMorphologySearchResult(
                query=query,
                root=None,
                root_source=root_source,
                page=page,
                per_page=per_page,
            )

        # Greek returns lemma instead of Strong's number
        # Also handle Latin→Greek transliteration results and Greek Strong's → lemma translation
        if root_source in (
            "lemma_exact",
            "word_clean_exact",
            "latin_transliteration",
            "latin_transliteration_fuzzy",
            "strongs_to_lemma",
            "strongs_to_lemma_fuzzy",
            "greek_transliteration_normalized",  # Step L5a: zoe → G2222 → ζωή
        ) or (root_source == "fuzzy" and detect_script(query) == "greek"):
            logger.debug("[BibleMorphology.search] Routing to _search_by_lemma")

            # Preserve Strong's number when user explicitly searched for one
            # e.g., "G2316" → translated to lemma "θεός", but we want to return G2316
            greek_strongs: Optional[str] = None
            if root_source in ("strongs_to_lemma", "strongs_to_lemma_fuzzy"):
                if STRONGS_PATTERN.match(query):
                    # Normalize to standard format (uppercase, zero-padded)
                    prefix = query[0].upper()
                    num_part = query[1:]
                    try:
                        greek_strongs = f"{prefix}{int(num_part):04d}"
                    except ValueError:
                        greek_strongs = f"{prefix}{num_part}"

            try:
                result = await self._search_by_lemma(
                    query=query,
                    lemma=identifier,
                    root_source=root_source,
                    page=page,
                    per_page=per_page,
                    language_filter=language_filter or "greek",
                    word_filter=word_filter,
                    testament_filter=testament_filter,
                    category_filter=category_filter,
                    strong_number=greek_strongs,
                )
                logger.info(
                    "[BibleMorphology.search] _search_by_lemma completed: total_occurrences=%d",
                    result.total_occurrences,
                )
                return result
            except Exception as e:
                logger.exception(
                    "[BibleMorphology.search] CRASH in _search_by_lemma: query=%r, lemma=%r, error=%s",
                    query,
                    identifier,
                    str(e),
                )
                raise

        logger.debug("[BibleMorphology.search] Routing to _search_by_strong")
        try:
            result = await self._search_by_strong(
                query=query,
                strong_number=identifier,
                root_source=root_source,
                page=page,
                per_page=per_page,
                language_filter=language_filter,
                word_filter=word_filter,
                testament_filter=testament_filter,
                category_filter=category_filter,
            )
            logger.info(
                "[BibleMorphology.search] _search_by_strong completed: total_occurrences=%d",
                result.total_occurrences,
            )
            return result
        except Exception as e:
            logger.exception(
                "[BibleMorphology.search] CRASH in _search_by_strong: query=%r, strong_number=%r, error=%s",
                query,
                identifier,
                str(e),
            )
            raise

    async def list_roots(self, page: int = 1, per_page: int = 50) -> dict:
        """List all available roots with occurrence counts, paginated."""
        per_page = min(per_page, 200)
        offset = (page - 1) * per_page

        async with self._session_maker() as session:
            total_result = await session.execute(
                sa_text(
                    "SELECT COUNT(DISTINCT strong_number) FROM bm_words "
                    "WHERE strong_number IS NOT NULL"
                )
            )
            total = total_result.scalar()

            roots_result = await session.execute(
                sa_text(
                    """
                    SELECT w.strong_number, s.original_word, s.transliteration, COUNT(*) as cnt
                    FROM bm_words w
                    LEFT JOIN bm_strongs s ON w.strong_number = s.number
                    WHERE w.strong_number IS NOT NULL
                    GROUP BY w.strong_number, s.original_word, s.transliteration
                    ORDER BY cnt DESC
                    LIMIT :limit OFFSET :offset
                    """
                ),
                {"limit": per_page, "offset": offset},
            )
            roots = [
                {
                    "strong_number": r[0],
                    "original_word": r[1],
                    "transliteration": r[2],
                    "count": r[3],
                }
                for r in roots_result.fetchall()
            ]

        return {
            "roots": roots,
            "total": total,
            "page": page,
            "per_page": per_page,
        }

    async def get_stats(self) -> dict:
        """Get overall Bible keyword search statistics."""
        async with self._session_maker() as session:
            # Total words in database
            total_words_result = await session.execute(
                sa_text("SELECT COUNT(*) FROM bm_words")
            )
            total_words = total_words_result.scalar() or 0

            # Unique roots (Strong's numbers)
            unique_roots_result = await session.execute(
                sa_text(
                    "SELECT COUNT(DISTINCT strong_number) FROM bm_words "
                    "WHERE strong_number IS NOT NULL"
                )
            )
            unique_roots = unique_roots_result.scalar() or 0

            # Total books
            total_books_result = await session.execute(
                sa_text("SELECT COUNT(*) FROM bm_books")
            )
            total_books = total_books_result.scalar() or 0

            # Total verses
            total_verses_result = await session.execute(
                sa_text("SELECT COUNT(*) FROM bm_verses")
            )
            total_verses = total_verses_result.scalar() or 0

        return {
            "total_words": total_words,
            "unique_roots": unique_roots,
            "total_books": total_books,
            "total_verses": total_verses,
        }

    async def close(self) -> None:
        """Dispose engine and release connection pool."""
        await self._engine.dispose()

    # ------------------------------------------------------------------
    # Root / Strong's Finding (4-step cascade)
    # ------------------------------------------------------------------

    async def _find_root(
        self, query: str, language_filter: Optional[str] = None
    ) -> tuple[Optional[str], str]:
        """Find the Strong's number or lemma for a query.

        Pipeline:
        1. Script detection → route to Hebrew, Greek, or Latin path
        2. Hebrew: word_clean exact → Strong's reverse lookup → fuzzy
        3. Greek: lemma exact → word_clean → fuzzy (returns lemma, not Strong's)
        4. Latin: Strong's number check → transliteration → fuzzy
        5. Not found

        Args:
            query: Search term
            language_filter: Optional language constraint ('hebrew' or 'greek').
                When set, prevents fallback to other language searches.

        Returns:
            (identifier, source) where identifier is Strong's number (Hebrew) or lemma (Greek)
        """
        script = detect_script(query)
        logger.debug(
            "[BibleMorphology._find_root] query=%r, detected_script=%r, language_filter=%r",
            query,
            script,
            language_filter,
        )

        # Check for Strong's number input first (works for any script)
        if STRONGS_PATTERN.match(query):
            logger.debug(
                "[BibleMorphology._find_root] Matched Strong's pattern, routing to _find_by_strongs_number"
            )
            return await self._find_by_strongs_number(query)

        if script == "hebrew":
            logger.debug("[BibleMorphology._find_root] Routing to _find_root_hebrew")
            return await self._find_root_hebrew(query)
        elif script == "greek":
            logger.debug("[BibleMorphology._find_root] Routing to _find_root_greek")
            return await self._find_root_greek(query)
        logger.debug("[BibleMorphology._find_root] Routing to _find_root_latin")
        return await self._find_root_latin(query, language_filter=language_filter)

    async def _find_by_strongs_number(self, query: str) -> tuple[Optional[str], str]:
        """Direct Strong's number lookup (e.g., H3789, G2316).

        For Hebrew (H####): Returns Strong's number directly since bm_words has strong_number populated.
        For Greek (G####): Translates to lemma search since MorphGNT data lacks Strong's numbers.
        """
        # Normalize: uppercase prefix, zero-pad to 4 digits
        prefix = query[0].upper()
        num_part = query[1:]
        try:
            formatted = f"{prefix}{int(num_part):04d}"
        except ValueError:
            formatted = f"{prefix}{num_part}"

        # Also prepare unpadded variant
        unpadded = f"{prefix}{num_part}"

        # Check cache first
        if formatted in self._strongs_cache:
            # For Hebrew: check if words exist in DB with this Strong's number
            if prefix == "H":
                async with self._session_maker() as session:
                    result = await session.execute(
                        sa_text(
                            "SELECT strong_number FROM bm_words "
                            "WHERE strong_number = :sn LIMIT 1"
                        ),
                        {"sn": formatted},
                    )
                    row = result.fetchone()
                    if row:
                        return (formatted, "strongs_direct")
                    # Try unpadded
                    result = await session.execute(
                        sa_text(
                            "SELECT strong_number FROM bm_words "
                            "WHERE strong_number = :sn LIMIT 1"
                        ),
                        {"sn": unpadded},
                    )
                    row = result.fetchone()
                    if row:
                        return (unpadded, "strongs_direct")

            # For Greek (G####): MorphGNT doesn't have Strong's numbers in bm_words.
            # Instead, translate Strong's number → Greek word → search by lemma.
            elif prefix == "G":
                strongs_info = self._strongs_cache.get(
                    formatted
                ) or self._strongs_cache.get(unpadded)
                if strongs_info:
                    greek_word = strongs_info.get("original_word")
                    if greek_word:
                        logger.debug(
                            "[BibleMorphology._find_by_strongs_number] Greek Strong's %s → word '%s', searching by lemma",
                            formatted,
                            greek_word,
                        )
                        # Try to find this Greek word as a lemma in bm_words
                        async with self._session_maker() as session:
                            # First try exact lemma match
                            result = await session.execute(
                                sa_text(
                                    """
                                    SELECT lemma, COUNT(*) as cnt
                                    FROM bm_words
                                    WHERE lemma = :q AND language = 'greek'
                                    GROUP BY lemma
                                    ORDER BY cnt DESC
                                    LIMIT 1
                                    """
                                ),
                                {"q": greek_word},
                            )
                            row = result.fetchone()
                            if row:
                                return (row[0], "strongs_to_lemma")

                            # Try normalized (accent-stripped) match on word_clean
                            from src.greek_normalizer import normalize_greek

                            normalized_greek = normalize_greek(greek_word)
                            result = await session.execute(
                                sa_text(
                                    """
                                    SELECT lemma, COUNT(*) as cnt
                                    FROM bm_words
                                    WHERE word_clean = :q AND language = 'greek'
                                    GROUP BY lemma
                                    ORDER BY cnt DESC
                                    LIMIT 1
                                    """
                                ),
                                {"q": normalized_greek},
                            )
                            row = result.fetchone()
                            if row:
                                return (row[0], "strongs_to_lemma")

                            # Try fuzzy match as last resort
                            result = await session.execute(
                                sa_text(
                                    """
                                    SELECT lemma, word_clean,
                                           similarity(word_clean, :q) AS sim
                                    FROM bm_words
                                    WHERE word_clean % :q AND language = 'greek'
                                    ORDER BY sim DESC
                                    LIMIT 1
                                    """
                                ),
                                {"q": normalized_greek},
                            )
                            row = result.fetchone()
                            if row and row[0]:
                                return (row[0], "strongs_to_lemma_fuzzy")

                        logger.warning(
                            "[BibleMorphology._find_by_strongs_number] Greek Strong's %s word '%s' not found in bm_words",
                            formatted,
                            greek_word,
                        )
                return (None, "not_found")

        # Also try without zero-padding for cache check
        if unpadded in self._strongs_cache:
            # Recursively handle with the found variant
            return await self._find_by_strongs_number(unpadded)

        return (None, "not_found")

    async def _find_root_hebrew(self, query: str) -> tuple[Optional[str], str]:
        """Hebrew input path: normalize → exact match → Strong's reverse → fuzzy.

        The root column in bm_words stores Strong's original_word with nikud,
        which has non-standard Unicode combining character ordering. Direct
        string equality on root is unreliable. Instead, we search via:
        1. word_clean (nikud-stripped) → get strong_number
        2. Strong's reverse lookup (normalize query → match strongs.original_word)
        3. Fuzzy match on word_clean via pg_trgm
        """
        logger.debug("[BibleMorphology._find_root_hebrew] START: query=%r", query)
        try:
            normalized = normalize_hebrew(query)
            logger.debug(
                "[BibleMorphology._find_root_hebrew] normalized=%r", normalized
            )
        except Exception:
            logger.exception(
                "[BibleMorphology._find_root_hebrew] CRASH in normalize_hebrew: query=%r",
                query,
            )
            raise

        async with self._session_maker() as session:
            # Step 1: Exact match on word_clean → get most frequent strong_number
            result = await session.execute(
                sa_text(
                    """
                    SELECT strong_number, COUNT(*) as cnt
                    FROM bm_words
                    WHERE word_clean = :q AND strong_number IS NOT NULL
                    GROUP BY strong_number
                    ORDER BY cnt DESC
                    LIMIT 1
                    """
                ),
                {"q": normalized},
            )
            row = result.fetchone()
            if row:
                return (row[0], "exact_match")

            # Step 2: Strong's reverse lookup via in-memory cache
            # User typed Hebrew without nikud → find matching Strong's entry
            strongs_numbers = self._reverse_strongs.get(normalized)
            if strongs_numbers:
                # Verify the Strong's number exists in bm_words
                for sn in strongs_numbers:
                    result = await session.execute(
                        sa_text(
                            "SELECT strong_number FROM bm_words "
                            "WHERE strong_number = :sn LIMIT 1"
                        ),
                        {"sn": sn},
                    )
                    if result.fetchone():
                        return (sn, "strongs_lookup")

            # Step 3: Fuzzy match on word_clean via pg_trgm
            result = await session.execute(
                sa_text(
                    """
                    SELECT strong_number, word_clean,
                           similarity(word_clean, :q) AS sim
                    FROM bm_words
                    WHERE word_clean % :q AND strong_number IS NOT NULL
                    ORDER BY sim DESC
                    LIMIT 1
                    """
                ),
                {"q": normalized},
            )
            row = result.fetchone()
            if row:
                return (row[0], "fuzzy")

        return (None, "not_found")

    async def _find_root_latin(
        self, query: str, language_filter: Optional[str] = None
    ) -> tuple[Optional[str], str]:
        """Latin input path: transliteration exact → cache lookup → fuzzy.

        Handles SBL transliteration input (e.g., 'ktb', 'brʾšyt') and
        common romanizations.

        Args:
            query: Search term in Latin script
            language_filter: Optional language constraint ('hebrew' or 'greek').
                When 'hebrew', skips Greek fallback lookups (Step L5a/L5b).
        """
        logger.debug("[BibleMorphology._find_root_latin] START: query=%r", query)
        normalized = query.lower().strip()
        logger.debug("[BibleMorphology._find_root_latin] normalized=%r", normalized)

        async with self._session_maker() as session:
            # Step L1: Exact match on bm_words.transliteration
            result = await session.execute(
                sa_text(
                    """
                    SELECT strong_number, COUNT(*) as cnt
                    FROM bm_words
                    WHERE transliteration = :q AND strong_number IS NOT NULL
                    GROUP BY strong_number
                    ORDER BY cnt DESC
                    LIMIT 1
                    """
                ),
                {"q": normalized},
            )
            row = result.fetchone()
            if row:
                return (row[0], "transliteration")

            # Step L2: Strong's transliteration cache lookup
            # The bm_strongs.transliteration field uses a different format
            # (e.g., 'kâthab' for H3789), try matching
            strongs_numbers = self._transliteration_map.get(normalized)
            if strongs_numbers:
                for sn in strongs_numbers:
                    result = await session.execute(
                        sa_text(
                            "SELECT strong_number FROM bm_words "
                            "WHERE strong_number = :sn LIMIT 1"
                        ),
                        {"sn": sn},
                    )
                    if result.fetchone():
                        return (sn, "transliteration")

            # Step L2b: Try normalized ASCII lookup for user-friendly queries
            # e.g., "elohim" → matches normalized "ʼĕlôhîym" → H430
            normalized_ascii = normalize_user_hebrew_query(normalized)
            if normalized_ascii != normalized:
                logger.debug(
                    "[BibleMorphology._find_root_latin] Trying normalized ASCII: %r → %r",
                    normalized,
                    normalized_ascii,
                )
                strongs_numbers = self._transliteration_map.get(normalized_ascii)
                if strongs_numbers:
                    for sn in strongs_numbers:
                        result = await session.execute(
                            sa_text(
                                "SELECT strong_number FROM bm_words "
                                "WHERE strong_number = :sn LIMIT 1"
                            ),
                            {"sn": sn},
                        )
                        if result.fetchone():
                            return (sn, "transliteration_normalized")

            # Step L3: Try converting Latin to Hebrew via transliteration reverse
            # Build a simple reverse: strip diacritics from SBL transliteration
            # and match against bm_words.transliteration with LIKE
            # Strip common diacritics for broader matching
            stripped = _strip_transliteration_diacritics(normalized)
            if stripped != normalized:
                result = await session.execute(
                    sa_text(
                        """
                        SELECT strong_number, COUNT(*) as cnt
                        FROM bm_words
                        WHERE transliteration = :q AND strong_number IS NOT NULL
                        GROUP BY strong_number
                        ORDER BY cnt DESC
                        LIMIT 1
                        """
                    ),
                    {"q": stripped},
                )
                row = result.fetchone()
                if row:
                    return (row[0], "transliteration")

            # Step L4: Fuzzy match on transliteration via pg_trgm
            result = await session.execute(
                sa_text(
                    """
                    SELECT strong_number, transliteration,
                           similarity(transliteration, :q) AS sim
                    FROM bm_words
                    WHERE transliteration % :q AND strong_number IS NOT NULL
                    ORDER BY sim DESC
                    LIMIT 1
                    """
                ),
                {"q": normalized},
            )
            row = result.fetchone()
            if row:
                return (row[0], "fuzzy")

            # Also try fuzzy on stripped form
            if stripped != normalized:
                result = await session.execute(
                    sa_text(
                        """
                        SELECT strong_number, transliteration,
                               similarity(transliteration, :q) AS sim
                        FROM bm_words
                        WHERE transliteration % :q AND strong_number IS NOT NULL
                        ORDER BY sim DESC
                        LIMIT 1
                        """
                    ),
                    {"q": stripped},
                )
                row = result.fetchone()
                if row:
                    return (row[0], "fuzzy")

            # Step L5a: Try normalized Greek transliteration lookup (cache-based)
            # e.g., "zoe" → G2222 → ζωή (lemma), "eirene" → G1515 → εἰρήνη
            # This is more accurate than reverse_transliterate_greek() because
            # ASCII "zoe" maps to G2222 (ζωή) via Strong's transliteration "zōḗ"
            # NOTE: Greek bm_words doesn't have strong_number - it uses lemma only
            # So we look up Strong's → get original_word (lemma) → return lemma
            #
            # SKIP if language_filter="hebrew" - don't fall back to Greek
            if language_filter == "hebrew":
                logger.debug(
                    "[BibleMorphology._find_root_latin] Skipping Greek lookup (language_filter=hebrew)"
                )
                return (None, "not_found")

            normalized_greek = normalize_user_greek_query(normalized)
            if normalized_greek != normalized:
                logger.debug(
                    "[BibleMorphology._find_root_latin] Trying normalized Greek: %r → %r",
                    normalized,
                    normalized_greek,
                )
            # Also try the original normalized form (in case it's already ASCII)
            for lookup_key in [normalized_greek, normalized]:
                strongs_numbers = self._transliteration_map.get(lookup_key)
                if strongs_numbers:
                    for sn in strongs_numbers:
                        if sn.startswith("G"):  # Only Greek entries
                            # Greek words: get original_word (lemma) from bm_strongs
                            # bm_words for Greek doesn't have strong_number
                            entry = self._strongs_cache.get(sn)
                            if entry and entry.get("original_word"):
                                lemma = entry["original_word"]
                                # Verify lemma exists in bm_words
                                result = await session.execute(
                                    sa_text(
                                        "SELECT lemma FROM bm_words "
                                        "WHERE lemma = :lemma AND language = 'greek' "
                                        "LIMIT 1"
                                    ),
                                    {"lemma": lemma},
                                )
                                if result.fetchone():
                                    logger.debug(
                                        "[BibleMorphology._find_root_latin] Step L5a: "
                                        "Found Greek via cache: %r → %r → %r",
                                        lookup_key,
                                        sn,
                                        lemma,
                                    )
                                    return (lemma, "greek_transliteration_normalized")

            # Step L5b: Try Latin → Greek conversion for Greek word searches
            # (e.g., "logos" → "λογος", "theos" → "θεος")
            # Note: This is less accurate for words where ASCII can't distinguish
            # ε/η or ο/ω (e.g., "zoe" → "ζοε" instead of "ζωη")
            from src.greek_normalizer import reverse_transliterate_greek

            greek_query = reverse_transliterate_greek(normalized)
            logger.debug(
                "[BibleMorphology._find_root_latin] Latin→Greek conversion: %r → %r",
                normalized,
                greek_query,
            )

            # Try exact match on the converted Greek word_clean
            result = await session.execute(
                sa_text(
                    """
                    SELECT lemma, COUNT(*) as cnt
                    FROM bm_words
                    WHERE word_clean = :q AND language = 'greek'
                    GROUP BY lemma
                    ORDER BY cnt DESC
                    LIMIT 1
                    """
                ),
                {"q": greek_query},
            )
            row = result.fetchone()
            if row:
                return (row[0], "latin_transliteration")

            # Also try fuzzy match on converted Greek
            result = await session.execute(
                sa_text(
                    """
                    SELECT lemma, word_clean,
                           similarity(word_clean, :q) AS sim
                    FROM bm_words
                    WHERE word_clean % :q AND language = 'greek'
                    ORDER BY sim DESC
                    LIMIT 1
                    """
                ),
                {"q": greek_query},
            )
            row = result.fetchone()
            if row and row[0]:
                return (row[0], "latin_transliteration_fuzzy")

        return (None, "not_found")

    async def _find_root_greek(self, query: str) -> tuple[Optional[str], str]:
        """Greek input path: normalize → lemma exact → word_clean → fuzzy.

        Greek words in MorphGNT don't have Strong's numbers, so we search by lemma.
        Returns (lemma, source) instead of (strong_number, source).
        """
        logger.debug("[BibleMorphology._find_root_greek] START: query=%r", query)
        try:
            from src.greek_normalizer import normalize_greek

            normalized = normalize_greek(query)
            logger.debug("[BibleMorphology._find_root_greek] normalized=%r", normalized)
        except Exception:
            logger.exception(
                "[BibleMorphology._find_root_greek] CRASH in normalize_greek: query=%r",
                query,
            )
            raise

        async with self._session_maker() as session:
            # Step G1: Exact match on lemma
            result = await session.execute(
                sa_text(
                    """
                    SELECT lemma, COUNT(*) as cnt
                    FROM bm_words
                    WHERE lemma = :q AND language = 'greek'
                    GROUP BY lemma
                    ORDER BY cnt DESC
                    LIMIT 1
                    """
                ),
                {"q": query},  # Try original query first (with accents)
            )
            row = result.fetchone()
            if row:
                return (row[0], "lemma_exact")

            # Step G2: Exact match on normalized lemma (without accents)
            result = await session.execute(
                sa_text(
                    """
                    SELECT lemma, COUNT(*) as cnt
                    FROM bm_words
                    WHERE word_clean = :q AND language = 'greek'
                    GROUP BY lemma
                    ORDER BY cnt DESC
                    LIMIT 1
                    """
                ),
                {"q": normalized},
            )
            row = result.fetchone()
            if row:
                return (row[0], "word_clean_exact")

            # Step G3: Fuzzy match on word_clean via pg_trgm
            result = await session.execute(
                sa_text(
                    """
                    SELECT lemma, word_clean,
                           similarity(word_clean, :q) AS sim
                    FROM bm_words
                    WHERE word_clean % :q AND language = 'greek'
                    ORDER BY sim DESC
                    LIMIT 1
                    """
                ),
                {"q": normalized},
            )
            row = result.fetchone()
            if row and row[0]:
                return (row[0], "fuzzy")

        return (None, "not_found")

    async def _search_by_lemma(
        self,
        query: str,
        lemma: str,
        root_source: str,
        page: int,
        per_page: int,
        language_filter: Optional[str] = None,
        word_filter: Optional[str] = None,
        testament_filter: Optional[str] = None,
        category_filter: Optional[str] = None,
        strong_number: Optional[str] = None,
    ) -> BibleMorphologySearchResult:
        """Query all data for a given Greek lemma.

        Greek words in MorphGNT don't have Strong's numbers in bm_words,
        so we search by lemma. However, when user explicitly searched for
        a Strong's number (e.g., G2316), we preserve and return it.

        Args:
            query: Original user query
            lemma: Greek lemma to search for
            root_source: How the lemma was found
            page: Page number
            per_page: Results per page
            language_filter: Optional language filter
            word_filter: Optional word form filter
            testament_filter: Optional testament filter
            category_filter: Optional category filter
            strong_number: Optional Strong's number to include in result
                (preserved when user explicitly searched for G#### format)

        Fetches: total occurrences, unique words, book distribution,
        paginated verses with matched words.
        """
        # For Greek, set root directly from lemma (no Strong's cache lookup)
        root_word = lemma
        root_transliteration = None

        # If Strong's number provided, get transliteration from cache
        if strong_number:
            strongs_info = self._strongs_cache.get(strong_number, {})
            root_transliteration = strongs_info.get("transliteration")

        # Build WHERE clause fragments for language and word filters
        lang_clause = ""
        lang_params: dict[str, object] = {}
        if language_filter:
            lang_clause = " AND w.language = :lang"
            lang_params["lang"] = language_filter

        word_clause = ""
        word_params: dict[str, object] = {}
        if word_filter:
            word_clause = " AND w.word_clean = :word_filter"
            word_params["word_filter"] = word_filter

        # Build WHERE clause fragments for testament and category filters
        testament_clause = ""
        testament_params: dict[str, object] = {}
        if testament_filter:
            testament_clause = " AND b.testament = :testament"
            testament_params["testament"] = testament_filter

        category_clause = ""
        category_params: dict[str, object] = {}
        if category_filter:
            category_clause = " AND b.category = :category"
            category_params["category"] = category_filter

        async with self._session_maker() as session:
            base_params: dict[str, object] = {"lemma": lemma}
            all_params = {
                **base_params,
                **lang_params,
                **word_params,
                **testament_params,
                **category_params,
            }

            # Build book filter clause (for queries that already have bm_books joined as 'b')
            book_filter_clause = f"{testament_clause}{category_clause}"

            # 1. Total occurrences (needs JOIN to bm_books for testament/category filtering)
            if testament_filter or category_filter:
                total_result = await session.execute(
                    sa_text(
                        f"SELECT COUNT(*) FROM bm_words w "
                        f"JOIN bm_verses v ON w.verse_id = v.id "
                        f"JOIN bm_books b ON v.book_id = b.id "
                        f"WHERE w.lemma = :lemma AND w.language = 'greek'{lang_clause}{book_filter_clause}"
                    ),
                    {
                        **base_params,
                        **lang_params,
                        **testament_params,
                        **category_params,
                    },
                )
            else:
                total_result = await session.execute(
                    sa_text(
                        f"SELECT COUNT(*) FROM bm_words w "
                        f"WHERE w.lemma = :lemma AND w.language = 'greek'{lang_clause}"
                    ),
                    {**base_params, **lang_params},
                )
            total_occurrences = total_result.scalar() or 0

            # 2. Unique derived words (word_clean, deduplicated)
            if testament_filter or category_filter:
                words_result = await session.execute(
                    sa_text(
                        f"SELECT DISTINCT w.word_clean FROM bm_words w "
                        f"JOIN bm_verses v ON w.verse_id = v.id "
                        f"JOIN bm_books b ON v.book_id = b.id "
                        f"WHERE w.lemma = :lemma AND w.language = 'greek' AND w.word_clean IS NOT NULL{lang_clause}{book_filter_clause} "
                        f"ORDER BY w.word_clean"
                    ),
                    {
                        **base_params,
                        **lang_params,
                        **testament_params,
                        **category_params,
                    },
                )
            else:
                words_result = await session.execute(
                    sa_text(
                        f"SELECT DISTINCT w.word_clean FROM bm_words w "
                        f"WHERE w.lemma = :lemma AND w.language = 'greek' AND w.word_clean IS NOT NULL{lang_clause} "
                        f"ORDER BY w.word_clean"
                    ),
                    {**base_params, **lang_params},
                )
            unique_words = [row[0] for row in words_result.fetchall()]

            # For Greek, no transliterations needed (skip Hebrew transliteration logic)
            word_transliterations: dict[str, str] = {}

            # 3. Book distribution
            dist_result = await session.execute(
                sa_text(
                    f"""
                    SELECT b.id, b.name_english, COUNT(*) as cnt
                    FROM bm_words w
                    JOIN bm_verses v ON w.verse_id = v.id
                    JOIN bm_books b ON v.book_id = b.id
                    WHERE w.lemma = :lemma AND w.language = 'greek'{lang_clause}{book_filter_clause}
                    GROUP BY b.id, b.name_english
                    ORDER BY cnt DESC
                    """
                ),
                {**base_params, **lang_params, **testament_params, **category_params},
            )
            book_distribution = [
                BookCount(book_id=r[0], book_name=r[1], count=r[2])
                for r in dist_result.fetchall()
            ]

            # 4. Count total distinct verses
            count_sql = (
                f"SELECT COUNT(DISTINCT v.id) "
                f"FROM bm_words w "
                f"JOIN bm_verses v ON w.verse_id = v.id "
                f"JOIN bm_books b ON v.book_id = b.id "
                f"WHERE w.lemma = :lemma AND w.language = 'greek'{lang_clause}{word_clause}{book_filter_clause}"
            )
            total_verses_result = await session.execute(sa_text(count_sql), all_params)
            total_verses = total_verses_result.scalar() or 0

            # 5. Paginated verses (keyset pagination) or all verses when per_page=0
            # For page 1: start from v.id > 0
            # For page N: find the starting ID by skipping (N-1)*per_page rows
            # When per_page=0: return ALL verses (no pagination)
            start_id = 0
            if per_page > 0 and page > 1:
                skip_count = (page - 1) * per_page
                start_id_result = await session.execute(
                    sa_text(
                        f"""
                        SELECT v.id FROM (
                            SELECT DISTINCT v.id
                            FROM bm_words w
                            JOIN bm_verses v ON w.verse_id = v.id
                            JOIN bm_books b ON v.book_id = b.id
                            WHERE w.lemma = :lemma AND w.language = 'greek'{lang_clause}{word_clause}{book_filter_clause}
                            ORDER BY v.id
                            LIMIT :skip
                        ) sub
                        JOIN bm_verses v ON v.id = sub.id
                        ORDER BY v.id DESC
                        LIMIT 1
                        """
                    ),
                    {**all_params, "skip": skip_count},
                )
                row = start_id_result.fetchone()
                if row:
                    start_id = row[0]

            # Build verses query - conditionally add LIMIT clause
            verses_sql = f"""
                SELECT DISTINCT v.id, v.book_id, b.name_english,
                       v.chapter, v.verse, v.text_original, v.text_english,
                       v.reference
                FROM bm_words w
                JOIN bm_verses v ON w.verse_id = v.id
                JOIN bm_books b ON v.book_id = b.id
                WHERE w.lemma = :lemma AND w.language = 'greek' AND v.id > :start_id{lang_clause}{word_clause}{book_filter_clause}
                ORDER BY v.id
            """
            verses_params = {**all_params, "start_id": start_id}
            if per_page > 0:
                verses_sql += "\n                LIMIT :limit"
                verses_params["limit"] = per_page

            verses_result = await session.execute(sa_text(verses_sql), verses_params)
            verse_rows = verses_result.fetchall()

            # 6. Batch-fetch matched words for all verses
            verse_ids = [vr[0] for vr in verse_rows]
            matched_words_map: dict[int, list[str]] = {vid: [] for vid in verse_ids}
            if verse_ids:
                placeholders = ",".join(str(vid) for vid in verse_ids)
                batch_words_result = await session.execute(
                    sa_text(
                        f"SELECT DISTINCT verse_id, word_clean FROM bm_words "
                        f"WHERE verse_id IN ({placeholders}) AND lemma = :lemma AND language = 'greek' "
                        f"AND word_clean IS NOT NULL"
                    ),
                    {"lemma": lemma},
                )
                for row in batch_words_result.fetchall():
                    vid, token = row[0], row[1]
                    if token not in matched_words_map[vid]:
                        matched_words_map[vid].append(token)

            verses: list[BibleVerseMatch] = []
            for vr in verse_rows:
                verses.append(
                    BibleVerseMatch(
                        book_id=vr[1],
                        book_name=vr[2],
                        chapter=vr[3],
                        verse=vr[4],
                        text_original=vr[5],
                        text_english=vr[6],
                        matched_words=matched_words_map.get(vr[0], []),
                        reference=vr[7] or "",
                    )
                )

        return BibleMorphologySearchResult(
            query=query,
            root=root_word,
            root_source=root_source,
            strong_number=strong_number,  # Preserved when user searched G#### format
            total_occurrences=total_occurrences,
            unique_words=unique_words,
            book_distribution=book_distribution,
            verses=verses,
            page=page,
            per_page=per_page,
            total_verses=total_verses,
            transliteration=root_transliteration,
            word_transliterations=word_transliterations,
        )

    # ------------------------------------------------------------------
    # Database Search (after Strong's number is found)
    # ------------------------------------------------------------------

    async def _search_by_strong(
        self,
        query: str,
        strong_number: str,
        root_source: str,
        page: int,
        per_page: int,
        language_filter: Optional[str] = None,
        word_filter: Optional[str] = None,
        testament_filter: Optional[str] = None,
        category_filter: Optional[str] = None,
    ) -> BibleMorphologySearchResult:
        """Query all data for a given Strong's number.

        Fetches: total occurrences, unique words, book distribution,
        paginated verses with matched words.
        """
        # Get root info from Strong's cache
        strongs_info = self._strongs_cache.get(strong_number, {})
        root_word = strongs_info.get("original_word")
        root_transliteration = strongs_info.get("transliteration")

        # Build WHERE clause fragments for language and word filters
        lang_clause = ""
        lang_params: dict[str, object] = {}
        if language_filter:
            lang_clause = " AND w.language = :lang"
            lang_params["lang"] = language_filter

        word_clause = ""
        word_params: dict[str, object] = {}
        if word_filter:
            word_clause = " AND w.word_clean = :word_filter"
            word_params["word_filter"] = word_filter

        # Build WHERE clause fragments for testament and category filters
        testament_clause = ""
        testament_params: dict[str, object] = {}
        if testament_filter:
            testament_clause = " AND b.testament = :testament"
            testament_params["testament"] = testament_filter

        category_clause = ""
        category_params: dict[str, object] = {}
        if category_filter:
            category_clause = " AND b.category = :category"
            category_params["category"] = category_filter

        async with self._session_maker() as session:
            base_params: dict[str, object] = {"sn": strong_number}
            all_params = {
                **base_params,
                **lang_params,
                **word_params,
                **testament_params,
                **category_params,
            }

            # Build book filter clause (for queries that already have bm_books joined as 'b')
            book_filter_clause = f"{testament_clause}{category_clause}"

            # 1. Total occurrences (needs JOIN to bm_books for testament/category filtering)
            if testament_filter or category_filter:
                total_result = await session.execute(
                    sa_text(
                        f"SELECT COUNT(*) FROM bm_words w "
                        f"JOIN bm_verses v ON w.verse_id = v.id "
                        f"JOIN bm_books b ON v.book_id = b.id "
                        f"WHERE w.strong_number = :sn{lang_clause}{book_filter_clause}"
                    ),
                    {
                        **base_params,
                        **lang_params,
                        **testament_params,
                        **category_params,
                    },
                )
            else:
                total_result = await session.execute(
                    sa_text(
                        f"SELECT COUNT(*) FROM bm_words w "
                        f"WHERE w.strong_number = :sn{lang_clause}"
                    ),
                    {**base_params, **lang_params},
                )
            total_occurrences = total_result.scalar() or 0

            # 2. Unique derived words (word_clean, deduplicated)
            if testament_filter or category_filter:
                words_result = await session.execute(
                    sa_text(
                        f"SELECT DISTINCT w.word_clean FROM bm_words w "
                        f"JOIN bm_verses v ON w.verse_id = v.id "
                        f"JOIN bm_books b ON v.book_id = b.id "
                        f"WHERE w.strong_number = :sn AND w.word_clean IS NOT NULL{lang_clause}{book_filter_clause} "
                        f"ORDER BY w.word_clean"
                    ),
                    {
                        **base_params,
                        **lang_params,
                        **testament_params,
                        **category_params,
                    },
                )
            else:
                words_result = await session.execute(
                    sa_text(
                        f"SELECT DISTINCT w.word_clean FROM bm_words w "
                        f"WHERE w.strong_number = :sn AND w.word_clean IS NOT NULL{lang_clause} "
                        f"ORDER BY w.word_clean"
                    ),
                    {**base_params, **lang_params},
                )
            unique_words = [row[0] for row in words_result.fetchall()]

            # Compute transliterations for unique words
            word_transliterations: dict[str, str] = {}
            for word in unique_words:
                try:
                    word_transliterations[word] = transliterate_hebrew(word)
                except Exception:
                    word_transliterations[word] = word

            # 3. Book distribution
            dist_result = await session.execute(
                sa_text(
                    f"""
                    SELECT b.id, b.name_english, COUNT(*) as cnt
                    FROM bm_words w
                    JOIN bm_verses v ON w.verse_id = v.id
                    JOIN bm_books b ON v.book_id = b.id
                    WHERE w.strong_number = :sn{lang_clause}{book_filter_clause}
                    GROUP BY b.id, b.name_english
                    ORDER BY cnt DESC
                    """
                ),
                {**base_params, **lang_params, **testament_params, **category_params},
            )
            book_distribution = [
                BookCount(book_id=r[0], book_name=r[1], count=r[2])
                for r in dist_result.fetchall()
            ]

            # 4. Count total distinct verses
            count_sql = (
                f"SELECT COUNT(DISTINCT v.id) "
                f"FROM bm_words w "
                f"JOIN bm_verses v ON w.verse_id = v.id "
                f"JOIN bm_books b ON v.book_id = b.id "
                f"WHERE w.strong_number = :sn{lang_clause}{word_clause}{book_filter_clause}"
            )
            total_verses_result = await session.execute(sa_text(count_sql), all_params)
            total_verses = total_verses_result.scalar() or 0

            # 5. Paginated verses (keyset pagination) or all verses when per_page=0
            # For page 1: start from v.id > 0
            # For page N: find the starting ID by skipping (N-1)*per_page rows
            # When per_page=0: return ALL verses (no pagination)
            start_id = 0
            if per_page > 0 and page > 1:
                skip_count = (page - 1) * per_page
                start_id_result = await session.execute(
                    sa_text(
                        f"""
                        SELECT v.id FROM (
                            SELECT DISTINCT v.id
                            FROM bm_words w
                            JOIN bm_verses v ON w.verse_id = v.id
                            JOIN bm_books b ON v.book_id = b.id
                            WHERE w.strong_number = :sn{lang_clause}{word_clause}{book_filter_clause}
                            ORDER BY v.id
                            LIMIT :skip
                        ) sub
                        JOIN bm_verses v ON v.id = sub.id
                        ORDER BY v.id DESC
                        LIMIT 1
                        """
                    ),
                    {**all_params, "skip": skip_count},
                )
                row = start_id_result.fetchone()
                if row:
                    start_id = row[0]

            # Build verses query - conditionally add LIMIT clause
            verses_sql = f"""
                SELECT DISTINCT v.id, v.book_id, b.name_english,
                       v.chapter, v.verse, v.text_original, v.text_english,
                       v.reference
                FROM bm_words w
                JOIN bm_verses v ON w.verse_id = v.id
                JOIN bm_books b ON v.book_id = b.id
                WHERE w.strong_number = :sn AND v.id > :start_id{lang_clause}{word_clause}{book_filter_clause}
                ORDER BY v.id
            """
            verses_params = {**all_params, "start_id": start_id}
            if per_page > 0:
                verses_sql += "\n                LIMIT :limit"
                verses_params["limit"] = per_page

            verses_result = await session.execute(sa_text(verses_sql), verses_params)
            verse_rows = verses_result.fetchall()

            # 6. Batch-fetch matched words for all verses
            verse_ids = [vr[0] for vr in verse_rows]
            matched_words_map: dict[int, list[str]] = {vid: [] for vid in verse_ids}
            if verse_ids:
                placeholders = ",".join(str(vid) for vid in verse_ids)
                batch_words_result = await session.execute(
                    sa_text(
                        f"SELECT DISTINCT verse_id, word_clean FROM bm_words "
                        f"WHERE verse_id IN ({placeholders}) AND strong_number = :sn "
                        f"AND word_clean IS NOT NULL"
                    ),
                    {"sn": strong_number},
                )
                for row in batch_words_result.fetchall():
                    vid, token = row[0], row[1]
                    if token not in matched_words_map[vid]:
                        matched_words_map[vid].append(token)

            verses: list[BibleVerseMatch] = []
            for vr in verse_rows:
                verses.append(
                    BibleVerseMatch(
                        book_id=vr[1],
                        book_name=vr[2],
                        chapter=vr[3],
                        verse=vr[4],
                        text_original=vr[5],
                        text_english=vr[6],
                        matched_words=matched_words_map.get(vr[0], []),
                        reference=vr[7] or "",
                    )
                )

        return BibleMorphologySearchResult(
            query=query,
            root=root_word,
            root_source=root_source,
            strong_number=strong_number,
            total_occurrences=total_occurrences,
            unique_words=unique_words,
            book_distribution=book_distribution,
            verses=verses,
            page=page,
            per_page=per_page,
            total_verses=total_verses,
            transliteration=root_transliteration,
            word_transliterations=word_transliterations,
        )

    async def get_cross_reference(self, strongs_number: str) -> dict:
        """Get Hebrew↔Greek cross-reference for a Strong's number.

        Returns words from both Hebrew and Greek that share the same Strong's number.
        Includes word forms, transliterations, and occurrence counts.

        Args:
            strongs_number: Strong's number (H430, G26, etc.)

        Returns:
            dict with keys:
            - strongs_number: Normalized Strong's number
            - definition: Definition from bm_strongs
            - original_word: Original word from bm_strongs
            - transliteration: Transliteration from bm_strongs
            - hebrew_words: List of dicts {word, word_clean, transliteration, language, occurrence_count}
            - greek_words: List of dicts {word, word_clean, transliteration, language, occurrence_count}
            - total_occurrences: Sum of all occurrences
        """
        strongs_number = strongs_number.replace("\x00", "").strip().upper()
        if not strongs_number:
            return {
                "strongs_number": "",
                "definition": None,
                "original_word": None,
                "transliteration": None,
                "hebrew_words": [],
                "greek_words": [],
                "total_occurrences": 0,
            }

        # Normalize Strong's number format (H430 and H0430 are equivalent)
        prefix = strongs_number[0] if strongs_number else ""
        num_str = strongs_number[1:] if len(strongs_number) > 1 else ""
        try:
            normalized = f"{prefix}{int(num_str):04d}"
        except ValueError:
            normalized = strongs_number

        # Look up Strong's definition
        strongs_entry = self._strongs_cache.get(normalized) or self._strongs_cache.get(
            strongs_number
        )

        async with self._session_maker() as session:
            # Query bm_words for all words with this Strong's number
            result = await session.execute(
                sa_text(
                    """
                    SELECT word, word_clean, transliteration, language, COUNT(*) as occurrence_count
                    FROM bm_words
                    WHERE strong_number = :strong_number OR strong_number = :strong_number_padded
                    GROUP BY word, word_clean, transliteration, language
                    ORDER BY occurrence_count DESC
                    """
                ),
                {
                    "strong_number": strongs_number,
                    "strong_number_padded": normalized,
                },
            )
            rows = result.fetchall()

        hebrew_words = []
        greek_words = []
        total_occurrences = 0

        for row in rows:
            word, word_clean, transliteration, language, occurrence_count = row
            word_entry = {
                "word": word or "",
                "word_clean": word_clean or "",
                "transliteration": transliteration or "",
                "language": language or "unknown",
                "occurrence_count": occurrence_count or 0,
            }
            total_occurrences += occurrence_count or 0

            if language in ("hebrew", "aramaic"):
                hebrew_words.append(word_entry)
            elif language == "greek":
                greek_words.append(word_entry)

        return {
            "strongs_number": normalized,
            "definition": strongs_entry.get("definition") if strongs_entry else None,
            "original_word": strongs_entry.get("original_word")
            if strongs_entry
            else None,
            "transliteration": strongs_entry.get("transliteration")
            if strongs_entry
            else None,
            "hebrew_words": hebrew_words,
            "greek_words": greek_words,
            "total_occurrences": total_occurrences,
        }


# ---------------------------------------------------------------------------
# Utility Functions
# ---------------------------------------------------------------------------


def _strip_transliteration_diacritics(text: str) -> str:
    """Strip common diacritics from transliteration for broader matching.

    Converts scholarly transliteration characters to plain ASCII:
    - ʾ (alef) → removed
    - ʿ (ayin) → removed
    - ḥ → h, ṭ → t, ṣ → s
    - š → s, ś → s
    - â, ê, î, ô, û → a, e, i, o, u
    """
    replacements = {
        "ʾ": "",
        "ʿ": "",
        "\u1e25": "h",  # ḥ
        "\u1e6d": "t",  # ṭ
        "\u1e63": "s",  # ṣ
        "\u0161": "s",  # š
        "\u015b": "s",  # ś
        "\u00e2": "a",  # â
        "\u00ea": "e",  # ê
        "\u00ee": "i",  # î
        "\u00f4": "o",  # ô
        "\u00fb": "u",  # û
    }
    result = text
    for old, new in replacements.items():
        result = result.replace(old, new)
    return result


# ---------------------------------------------------------------------------
# Inline Test
# ---------------------------------------------------------------------------


if __name__ == "__main__":
    import asyncio
    import sys

    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    async def run_tests() -> None:
        print("=" * 60)
        print("BibleMorphologySearch — Inline Test")
        print("=" * 60)

        search = await BibleMorphologySearch.get_instance()
        print(
            f"\nStrong's cache loaded: {len(search._strongs_cache)} entries, "
            f"{len(search._reverse_strongs)} reverse mappings, "
            f"{len(search._transliteration_map)} transliterations"
        )

        test_cases = [
            ("כתב", "Hebrew input (ktb/write)"),
            ("H3789", "Strong's number (ktb/write)"),
            ("ktb", "Latin transliteration (ktb/write)"),
            ("אלהים", "Hebrew input (elohim/God)"),
            ("H0430", "Strong's number (elohim/God)"),
        ]

        all_passed = True
        for query, description in test_cases:
            print(f"\n{'─' * 60}")
            print(f"TEST: {description}")
            print(f"Query: {query}")

            try:
                result = await search.search(query, page=1, per_page=5)
                print(f"  Root: {result.root}")
                print(f"  Root source: {result.root_source}")
                print(f"  Strong's: {result.strong_number}")
                print(f"  Total occurrences: {result.total_occurrences}")
                print(f"  Unique words: {len(result.unique_words)}")
                if result.unique_words[:5]:
                    print(f"    Sample: {result.unique_words[:5]}")
                print(f"  Total verses: {result.total_verses}")
                print(f"  Books: {len(result.book_distribution)}")
                if result.book_distribution[:3]:
                    for bc in result.book_distribution[:3]:
                        print(f"    {bc.book_name}: {bc.count}")
                print(f"  Verses returned: {len(result.verses)}")
                if result.verses:
                    v = result.verses[0]
                    print(f"    First: {v.reference} — {v.matched_words}")
                print(f"  Transliteration: {result.transliteration}")

                if result.root_source == "not_found":
                    print("  ⚠ NOT FOUND")
                    all_passed = False
                else:
                    print("  ✓ PASS")
            except Exception as exc:
                print(f"  ✗ FAIL: {exc}")
                all_passed = False

        print(f"\n{'=' * 60}")
        if all_passed:
            print("ALL TESTS PASSED ✓")
        else:
            print("SOME TESTS FAILED ✗")
        print("=" * 60)

        await search.close()

    asyncio.run(run_tests())
