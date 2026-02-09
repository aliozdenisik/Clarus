#!/usr/bin/env python3
"""ETL pipeline: CCAT LXX Morphological Data -> PostgreSQL bm_books, bm_verses, bm_words.

Reads:
  - backend/data/lxx/*.mlxx   (64 LXX files, CCAT morphological data)

Populates:
  - bm_books   (LXX books with book_id 67-99 for deuterocanonical, reuses 1-39 for canonical OT)
  - bm_verses  (LXX verses with Greek text_original)
  - bm_words   (LXX words with morphological data, language='greek')

Does NOT modify existing NT data (book_id 40-66) or Scrollmapper (100+).

Usage:
  python backend/scripts/setup_lxx.py              # All LXX books
  python backend/scripts/setup_lxx.py --book Gen   # Single book
  python backend/scripts/setup_lxx.py --skip-indexes
  python backend/scripts/setup_lxx.py --deuterocanonical-only  # Only apocryphal books
"""

import argparse
import logging
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, text

from src.greek_normalizer import normalize_greek, transliterate_greek

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

DATABASE_URL = "postgresql://postgres:postgres@localhost:54322/postgres"

DATA_DIR = Path(__file__).parent.parent / "data"
LXX_DIR = DATA_DIR / "lxx"

BATCH_SIZE = 2000

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Beta Code to Unicode conversion
# ---------------------------------------------------------------------------

# Beta Code mapping for Greek letters (CCAT standard)
BETA_TO_UNICODE = {
    # Lowercase letters
    "A": "α",
    "B": "β",
    "G": "γ",
    "D": "δ",
    "E": "ε",
    "Z": "ζ",
    "H": "η",
    "Q": "θ",
    "I": "ι",
    "K": "κ",
    "L": "λ",
    "M": "μ",
    "N": "ν",
    "C": "ξ",
    "O": "ο",
    "P": "π",
    "R": "ρ",
    "S": "σ",
    "J": "ς",  # J = final sigma
    "T": "τ",
    "U": "υ",
    "F": "φ",
    "X": "χ",
    "Y": "ψ",
    "W": "ω",
    # Uppercase (preceded by *)
    "*A": "Α",
    "*B": "Β",
    "*G": "Γ",
    "*D": "Δ",
    "*E": "Ε",
    "*Z": "Ζ",
    "*H": "Η",
    "*Q": "Θ",
    "*I": "Ι",
    "*K": "Κ",
    "*L": "Λ",
    "*M": "Μ",
    "*N": "Ν",
    "*C": "Ξ",
    "*O": "Ο",
    "*P": "Π",
    "*R": "Ρ",
    "*S": "Σ",
    "*T": "Τ",
    "*U": "Υ",
    "*F": "Φ",
    "*X": "Χ",
    "*Y": "Ψ",
    "*W": "Ω",
}

# Diacritical marks (applied after base letter)
BETA_DIACRITICS = {
    ")": "\u0313",  # smooth breathing (psili)
    "(": "\u0314",  # rough breathing (dasia)
    "/": "\u0301",  # acute accent (oxia)
    "\\": "\u0300",  # grave accent (varia)
    "=": "\u0342",  # circumflex (perispomeni)
    "+": "\u0308",  # diaeresis
    "|": "\u0345",  # iota subscript (ypogegrammeni)
}


def beta_to_unicode(beta_text: str) -> str:
    """Convert Beta Code text to Unicode Greek.

    Beta Code format (CCAT):
    - Uppercase letters represent lowercase Greek
    - * prefix indicates uppercase Greek
    - Diacritics follow the letter: ) smooth, ( rough, / acute, \\ grave, = circumflex
    - | is iota subscript
    - J is final sigma

    Args:
        beta_text: Text in Beta Code format

    Returns:
        Unicode Greek text
    """
    result = []
    i = 0

    while i < len(beta_text):
        # Check for uppercase marker
        if beta_text[i] == "*" and i + 1 < len(beta_text):
            key = "*" + beta_text[i + 1]
            if key in BETA_TO_UNICODE:
                result.append(BETA_TO_UNICODE[key])
                i += 2
                # Collect diacritics
                while i < len(beta_text) and beta_text[i] in BETA_DIACRITICS:
                    result.append(BETA_DIACRITICS[beta_text[i]])
                    i += 1
                continue
            else:
                # Unknown uppercase, skip *
                i += 1
                continue

        # Check for regular letter
        char = beta_text[i]
        if char in BETA_TO_UNICODE:
            result.append(BETA_TO_UNICODE[char])
            i += 1
            # Collect diacritics
            while i < len(beta_text) and beta_text[i] in BETA_DIACRITICS:
                result.append(BETA_DIACRITICS[beta_text[i]])
                i += 1
            continue

        # Check for diacritic without letter (shouldn't happen but handle it)
        if char in BETA_DIACRITICS:
            result.append(BETA_DIACRITICS[char])
            i += 1
            continue

        # Pass through other characters (punctuation, spaces, etc.)
        result.append(char)
        i += 1

    return "".join(result)


# ---------------------------------------------------------------------------
# LXX Book metadata
# ---------------------------------------------------------------------------

# LXX books: (file_num, file_name, book_id, abbrev, english_name, is_deuterocanonical)
# book_id: 1-39 for canonical OT (same as Hebrew), 67-99 for deuterocanonical
# Each text version gets a unique book_id to avoid conflicts
LXX_BOOKS: list[tuple[int, str, int, str, str, bool]] = [
    # Pentateuch (canonical OT - skip, already have Hebrew)
    # Historical Books (canonical OT - skip, already have Hebrew)
    # Deuterocanonical Historical
    (18, "18.1Esdras.mlxx", 67, "1Esd", "1 Esdras", True),
    (21, "21.Judith.mlxx", 68, "Jdt", "Judith", True),
    (22, "22.TobitBA.mlxx", 69, "TobBA", "Tobit (BA text)", True),
    (23, "23.TobitS.mlxx", 82, "TobS", "Tobit (S text)", True),  # Unique ID
    (24, "24.1Macc.mlxx", 70, "1Mac", "1 Maccabees", True),
    (25, "25.2Macc.mlxx", 71, "2Mac", "2 Maccabees", True),
    (26, "26.3Macc.mlxx", 72, "3Mac", "3 Maccabees", True),
    (27, "27.4Macc.mlxx", 73, "4Mac", "4 Maccabees", True),
    # Poetry (deuterocanonical)
    (30, "30.Odes.mlxx", 74, "Odes", "Odes", True),
    (35, "35.Wisdom.mlxx", 75, "Wis", "Wisdom of Solomon", True),
    (36, "36.Sirach.mlxx", 76, "Sir", "Sirach (Ecclesiasticus)", True),
    (37, "37.PsSol.mlxx", 77, "PsSol", "Psalms of Solomon", True),
    # Prophetic additions (deuterocanonical)
    (54, "54.Baruch.mlxx", 78, "Bar", "Baruch", True),
    (55, "55.EpJer.mlxx", 79, "EpJer", "Epistle of Jeremiah", True),
    # Daniel additions (deuterocanonical)
    (59, "59.BelOG.mlxx", 80, "BelOG", "Bel and the Dragon (OG)", True),
    (60, "60.BelTh.mlxx", 83, "BelTh", "Bel and the Dragon (Th)", True),  # Unique ID
    (63, "63.SusOG.mlxx", 81, "SusOG", "Susanna (OG)", True),
    (64, "64.SusTh.mlxx", 84, "SusTh", "Susanna (Th)", True),  # Unique ID
]

# Quick lookup dicts
FILE_TO_BOOK = {b[1]: b for b in LXX_BOOKS}
ABBREV_TO_BOOK = {b[3]: b for b in LXX_BOOKS}

# Deuterocanonical book IDs (67-99)
DEUTEROCANONICAL_IDS = {b[2] for b in LXX_BOOKS if b[5]}

# POS tag mapping from CCAT morphology codes
POS_MAP = {
    "N": "Noun",
    "V": "Verb",
    "A": "Adjective",
    "R": "Pronoun",
    "C": "Conjunction",
    "P": "Preposition",
    "D": "Adverb",
    "X": "Particle",
    "I": "Interjection",
    "M": "Number",
}


# ---------------------------------------------------------------------------
# LXX parsing
# ---------------------------------------------------------------------------


def parse_verse_header(line: str) -> tuple[str, int, int] | None:
    """Parse a verse header line like 'Gen 1:1'.

    Args:
        line: Line that might be a verse header

    Returns:
        Tuple of (book_abbrev, chapter, verse) or None if not a header
    """
    # Match patterns like "Gen 1:1", "1Sam 2:3", "Ps 119:1"
    match = re.match(r"^([A-Za-z0-9]+)\s+(\d+):(\d+)\s*$", line)
    if match:
        return (match.group(1), int(match.group(2)), int(match.group(3)))
    return None


def parse_word_line(line: str) -> dict | None:
    """Parse a word line from CCAT LXX format.

    Format: WORD_BETA    TYPE  PARSE  LEMMA_BETA  [PREFIX]

    Example:
        E)N                      P          E)N
        A)RXH=|                  N1  DSF    A)RXH/
        E)POI/HSEN               VAI AAI3S  POIE/W

    Args:
        line: Word line from CCAT file

    Returns:
        Dict with word data or None if not a word line
    """
    # Skip empty lines and verse headers
    line = line.rstrip()
    if not line or parse_verse_header(line):
        return None

    # Split by whitespace (variable spacing)
    parts = line.split()
    if len(parts) < 3:
        return None

    word_beta = parts[0]
    type_code = parts[1]

    # Parse code is usually at position 2, lemma at position 3
    # But some lines have different formats
    if len(parts) >= 4:
        parse_code = parts[2]
        lemma_beta = parts[3]
        prefix = parts[4] if len(parts) > 4 else None
    else:
        parse_code = parts[2] if len(parts) > 2 else None
        lemma_beta = parts[2] if len(parts) == 3 else None
        prefix = None

    # Convert Beta Code to Unicode
    word_unicode = beta_to_unicode(word_beta)
    lemma_unicode = beta_to_unicode(lemma_beta) if lemma_beta else None

    # Extract POS from type code (first character)
    pos_tag = type_code[0] if type_code else None

    return {
        "word_beta": word_beta,
        "word": word_unicode,
        "type_code": type_code,
        "parse_code": parse_code,
        "lemma_beta": lemma_beta,
        "lemma": lemma_unicode,
        "prefix": prefix,
        "pos_tag": pos_tag,
    }


def parse_lxx_file(
    file_path: Path,
    book_id: int,
    abbrev: str,
) -> tuple[list[dict], list[dict]]:
    """Parse a single CCAT LXX file into verse and word records.

    Args:
        file_path: Path to the .mlxx file
        book_id: Canonical book ID
        abbrev: Book abbreviation

    Returns:
        Tuple of (verse_rows, word_rows)
    """
    verse_rows: list[dict] = []
    word_rows: list[dict] = []

    current_verse: tuple[str, int, int] | None = None
    verse_words: dict[tuple[int, int], list[str]] = {}
    verse_positions: dict[tuple[int, int], int] = {}

    with open(file_path, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.rstrip()
            if not line:
                continue

            # Check for verse header
            header = parse_verse_header(line)
            if header:
                current_verse = header
                verse_key = (header[1], header[2])
                if verse_key not in verse_words:
                    verse_words[verse_key] = []
                    verse_positions[verse_key] = 0
                continue

            # Parse word line
            if current_verse is None:
                continue

            word_data = parse_word_line(line)
            if word_data is None:
                continue

            chapter, verse = current_verse[1], current_verse[2]
            verse_key = (chapter, verse)

            # Increment position
            verse_positions[verse_key] += 1
            position = verse_positions[verse_key]

            # Add word to verse text
            verse_words[verse_key].append(word_data["word"])

            # Normalize word
            word_clean = (
                normalize_greek(word_data["word"]) if word_data["word"] else None
            )

            # Transliteration
            transliteration = transliterate_greek(word_clean) if word_clean else None

            word_rows.append(
                {
                    "book_id": book_id,
                    "chapter": chapter,
                    "verse": verse,
                    "position": position,
                    "word": word_data["word"],
                    "word_clean": word_clean,
                    "lemma": word_data["lemma"],
                    "root": word_data["lemma"],  # Greek uses lemma as root
                    "strong_number": None,  # CCAT doesn't include Strong's
                    "morph_tag": word_data["parse_code"],
                    "pos_tag": word_data["pos_tag"],
                    "transliteration": transliteration,
                    "language": "greek",
                    "original_lemma": word_data["lemma_beta"],
                }
            )

    # Build verse records
    for (chapter, verse), words in sorted(verse_words.items()):
        text_original = " ".join(words) if words else None
        reference = f"{abbrev} {chapter}:{verse}"

        verse_rows.append(
            {
                "book_id": book_id,
                "chapter": chapter,
                "verse": verse,
                "text_original": text_original,
                "text_english": None,  # LXX doesn't have English translation
                "reference": reference,
            }
        )

    log.info(
        "  %s: parsed %d verses, %d words",
        abbrev,
        len(verse_rows),
        len(word_rows),
    )
    return verse_rows, word_rows


# ---------------------------------------------------------------------------
# Database operations
# ---------------------------------------------------------------------------


def delete_lxx_data(conn, deuterocanonical_only: bool = False) -> None:
    """Delete existing LXX data.

    Args:
        conn: SQLAlchemy connection
        deuterocanonical_only: If True, only delete deuterocanonical books (67-99)
    """
    if deuterocanonical_only:
        log.info("Deleting existing LXX deuterocanonical data (book_id 67-99)...")
        conn.execute(
            text(
                "DELETE FROM bm_words WHERE verse_id IN "
                "(SELECT id FROM bm_verses WHERE book_id BETWEEN 67 AND 99)"
            )
        )
        conn.execute(text("DELETE FROM bm_verses WHERE book_id BETWEEN 67 AND 99"))
        conn.execute(text("DELETE FROM bm_books WHERE id BETWEEN 67 AND 99"))
    else:
        # Delete all LXX data (canonical OT Greek + deuterocanonical)
        # Note: This will delete Greek words for canonical OT books
        log.info("Deleting existing LXX Greek data...")
        # Delete Greek words from canonical OT (1-39)
        conn.execute(
            text(
                "DELETE FROM bm_words WHERE language = 'greek' AND verse_id IN "
                "(SELECT id FROM bm_verses WHERE book_id BETWEEN 1 AND 39)"
            )
        )
        # Delete deuterocanonical books entirely
        conn.execute(
            text(
                "DELETE FROM bm_words WHERE verse_id IN "
                "(SELECT id FROM bm_verses WHERE book_id BETWEEN 67 AND 99)"
            )
        )
        conn.execute(text("DELETE FROM bm_verses WHERE book_id BETWEEN 67 AND 99"))
        conn.execute(text("DELETE FROM bm_books WHERE id BETWEEN 67 AND 99"))

    log.info("Deleted existing LXX entries")


def insert_lxx_books(conn, books_to_insert: list[tuple]) -> None:
    """Insert LXX book records into bm_books.

    Only inserts deuterocanonical books (67-99). Canonical OT books (1-39)
    should already exist from Hebrew ETL.

    Args:
        conn: SQLAlchemy connection
        books_to_insert: List of book tuples to insert
    """
    rows: list[dict] = []

    for book_tuple in books_to_insert:
        file_num, filename, book_id, abbrev, english_name, is_deut = book_tuple

        # Only insert deuterocanonical books (canonical OT should exist)
        if book_id < 67:
            continue

        # Check if book already exists
        result = conn.execute(
            text("SELECT id FROM bm_books WHERE id = :id"), {"id": book_id}
        )
        if result.fetchone():
            continue

        rows.append(
            {
                "id": book_id,
                "name": abbrev,
                "name_hebrew": None,  # LXX books don't have Hebrew names
                "name_english": english_name,
                "testament": "apocrypha",
                "category": "lxx_deuterocanonical",
                "total_chapters": 0,
                "total_verses": 0,
                "book_order": book_id,
            }
        )

    if rows:
        conn.execute(
            text(
                "INSERT INTO bm_books "
                "(id, name, name_hebrew, name_english, testament, category, "
                "total_chapters, total_verses, book_order) "
                "VALUES (:id, :name, :name_hebrew, :name_english, :testament, "
                ":category, :total_chapters, :total_verses, :book_order)"
            ),
            rows,
        )
    log.info("Inserted %d LXX deuterocanonical books", len(rows))


def update_lxx_book_counts(conn) -> None:
    """Update total_chapters and total_verses in bm_books for LXX books."""
    conn.execute(
        text(
            "UPDATE bm_books b SET "
            "total_chapters = sub.ch_count, "
            "total_verses = sub.v_count "
            "FROM ("
            "  SELECT book_id, COUNT(DISTINCT chapter) AS ch_count, COUNT(*) AS v_count "
            "  FROM bm_verses WHERE book_id BETWEEN 67 AND 99 GROUP BY book_id"
            ") sub "
            "WHERE b.id = sub.book_id"
        )
    )
    log.info("Updated LXX book chapter/verse counts")


def insert_lxx_verses(
    conn,
    all_verse_rows: list[dict],
) -> dict[tuple[int, int, int], int]:
    """Insert LXX verses into bm_verses.

    Args:
        conn: SQLAlchemy connection
        all_verse_rows: List of verse dicts from parsing

    Returns:
        Mapping of (book_id, chapter, verse) -> verse_db_id
    """
    # Group verses by book_id to handle canonical vs deuterocanonical
    deut_verses = [v for v in all_verse_rows if v["book_id"] >= 67]

    # Insert deuterocanonical verses
    if deut_verses:
        for i in range(0, len(deut_verses), BATCH_SIZE):
            batch = deut_verses[i : i + BATCH_SIZE]
            conn.execute(
                text(
                    "INSERT INTO bm_verses "
                    "(book_id, chapter, verse, text_original, text_english, reference) "
                    "VALUES (:book_id, :chapter, :verse, :text_original, :text_english, :reference)"
                ),
                batch,
            )

    log.info("Inserted %d LXX verses", len(deut_verses))

    # Build verse ID map for all LXX books
    return _build_lxx_verse_id_map(conn)


def _build_lxx_verse_id_map(conn) -> dict[tuple[int, int, int], int]:
    """Build mapping of (book_id, chapter, verse) -> verse_db_id for LXX."""
    # Get all verses for LXX books (canonical OT + deuterocanonical)
    result = conn.execute(
        text(
            "SELECT id, book_id, chapter, verse FROM bm_verses "
            "WHERE book_id BETWEEN 1 AND 39 OR book_id BETWEEN 67 AND 99 "
            "ORDER BY id"
        )
    )
    verse_map: dict[tuple[int, int, int], int] = {}
    for row in result:
        verse_map[(row[1], row[2], row[3])] = row[0]
    return verse_map


def insert_lxx_words(
    conn,
    all_word_rows: list[dict],
    verse_id_map: dict[tuple[int, int, int], int],
) -> int:
    """Insert LXX words into bm_words with FK resolution.

    Args:
        conn: SQLAlchemy connection
        all_word_rows: List of word dicts from parsing
        verse_id_map: (book_id, chapter, verse) -> verse_db_id

    Returns:
        Count of inserted words
    """
    rows_to_insert: list[dict] = []
    orphan_count = 0

    for w in all_word_rows:
        key = (w["book_id"], w["chapter"], w["verse"])
        verse_db_id = verse_id_map.get(key)
        if verse_db_id is None:
            orphan_count += 1
            if orphan_count <= 5:
                log.warning(
                    "No verse_id for book=%d ch=%d v=%d pos=%d",
                    w["book_id"],
                    w["chapter"],
                    w["verse"],
                    w["position"],
                )
            continue

        rows_to_insert.append(
            {
                "verse_id": verse_db_id,
                "position": w["position"],
                "word": w["word"],
                "word_clean": w["word_clean"],
                "lemma": w["lemma"],
                "root": w["root"],
                "strong_number": w["strong_number"],
                "morph_tag": w["morph_tag"],
                "pos_tag": w["pos_tag"],
                "transliteration": w["transliteration"],
                "language": w["language"],
                "original_lemma": w["original_lemma"],
            }
        )

    if orphan_count > 0:
        log.warning("Skipped %d words with no matching verse", orphan_count)

    # Batch insert
    inserted = 0
    for i in range(0, len(rows_to_insert), BATCH_SIZE):
        batch = rows_to_insert[i : i + BATCH_SIZE]
        conn.execute(
            text(
                "INSERT INTO bm_words "
                "(verse_id, position, word, word_clean, lemma, root, strong_number, "
                "morph_tag, pos_tag, transliteration, language, original_lemma) "
                "VALUES (:verse_id, :position, :word, :word_clean, :lemma, :root, "
                ":strong_number, :morph_tag, :pos_tag, :transliteration, :language, "
                ":original_lemma)"
            ),
            batch,
        )
        inserted += len(batch)
        if (i // BATCH_SIZE) % 25 == 0 and i > 0:
            log.info("  Words inserted so far: %d / %d", inserted, len(rows_to_insert))

    log.info("Inserted %d LXX Greek words total", inserted)
    return inserted


# ---------------------------------------------------------------------------
# Index creation
# ---------------------------------------------------------------------------


INDEXES_SQL = [
    "CREATE INDEX IF NOT EXISTS ix_bm_words_root ON bm_words(root);",
    "CREATE INDEX IF NOT EXISTS ix_bm_words_lemma ON bm_words(lemma);",
    "CREATE INDEX IF NOT EXISTS ix_bm_words_strong ON bm_words(strong_number);",
    "CREATE INDEX IF NOT EXISTS ix_bm_words_word_clean ON bm_words(word_clean);",
    "CREATE INDEX IF NOT EXISTS ix_bm_words_word_clean_trgm ON bm_words USING gin(word_clean gin_trgm_ops);",
    "CREATE INDEX IF NOT EXISTS ix_bm_words_verse_id ON bm_words(verse_id);",
    "CREATE INDEX IF NOT EXISTS ix_bm_words_language ON bm_words(language);",
    "CREATE INDEX IF NOT EXISTS ix_bm_verses_book_id ON bm_verses(book_id);",
    "CREATE UNIQUE INDEX IF NOT EXISTS ix_bm_verses_reference ON bm_verses(reference);",
]


def create_indexes(conn) -> None:
    """Create indexes on bm_* tables."""
    for idx_sql in INDEXES_SQL:
        conn.execute(text(idx_sql))
    log.info("Created/verified %d indexes", len(INDEXES_SQL))


# ---------------------------------------------------------------------------
# Validation & summary
# ---------------------------------------------------------------------------


def validate_and_summarize(conn) -> bool:
    """Run validation checks and print summary. Returns True if all pass."""
    checks_passed = True

    # LXX Book counts
    result = conn.execute(
        text("SELECT COUNT(*) FROM bm_books WHERE category = 'lxx_deuterocanonical'")
    )
    lxx_book_count = result.scalar()
    log.info("Books (LXX Deuterocanonical): %d", lxx_book_count)

    # LXX Verse count
    result = conn.execute(
        text("SELECT COUNT(*) FROM bm_verses WHERE book_id BETWEEN 67 AND 99")
    )
    lxx_verse_count = result.scalar()
    log.info("Verses (LXX Deuterocanonical): %d", lxx_verse_count)

    # Greek word count (all)
    result = conn.execute(
        text("SELECT COUNT(*) FROM bm_words WHERE language = 'greek'")
    )
    greek_word_count = result.scalar()
    log.info("Words (Greek total): %d", greek_word_count)

    # Total word count
    result = conn.execute(text("SELECT COUNT(*) FROM bm_words"))
    total_word_count = result.scalar()
    log.info("Words (Total): %d", total_word_count)

    # Language breakdown
    result = conn.execute(
        text(
            "SELECT language, COUNT(*) FROM bm_words GROUP BY language ORDER BY language"
        )
    )
    lang_counts = {row[0]: row[1] for row in result}
    for lang, cnt in lang_counts.items():
        log.info("  %s words: %d", lang, cnt)

    # Unique Greek lemmas
    result = conn.execute(
        text(
            "SELECT COUNT(DISTINCT lemma) FROM bm_words WHERE language = 'greek' AND lemma IS NOT NULL"
        )
    )
    unique_lemmas = result.scalar()
    log.info("Unique Greek lemmas: %d", unique_lemmas)

    # Print summary
    print("\n" + "=" * 60)
    print("  LXX ETL — SUMMARY")
    print("=" * 60)
    print(f"  Books (LXX Deut):  {lxx_book_count:>8,}")
    print(f"  Verses (LXX Deut): {lxx_verse_count:>8,}")
    print(f"  Words (Greek):     {greek_word_count:>8,}")
    print(f"  Words (Total):     {total_word_count:>8,}")
    for lang, cnt in sorted(lang_counts.items()):
        print(f"    {lang:>12}:    {cnt:>8,}")
    print(f"  Unique lemmas:     {unique_lemmas:>8,}")
    print("=" * 60)

    # Sample verification - Wisdom 1:1
    result = conn.execute(
        text(
            "SELECT b.name_english, v.chapter, v.verse, "
            "LEFT(v.text_original, 50) "
            "FROM bm_verses v JOIN bm_books b ON v.book_id = b.id "
            "WHERE v.reference LIKE 'Wis 1:1%' LIMIT 1"
        )
    )
    row = result.fetchone()
    if row:
        print("\n  Sample Wisdom 1:1:")
        print(f"    Book: {row[0]}")
        print(f"    Greek: {row[3]}")
    else:
        log.warning("Wisdom 1:1 not found in bm_verses (may not be loaded)")

    print("=" * 60 + "\n")
    return checks_passed


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> bool:
    """Run the LXX ETL pipeline. Returns True on success."""
    parser = argparse.ArgumentParser(
        description="ETL: CCAT LXX -> bm_books, bm_verses, bm_words"
    )
    parser.add_argument(
        "--book",
        type=str,
        default=None,
        help="Parse single LXX book only (e.g., --book Wis)",
    )
    parser.add_argument(
        "--skip-indexes",
        action="store_true",
        help="Skip index creation after ETL",
    )
    parser.add_argument(
        "--deuterocanonical-only",
        action="store_true",
        help="Only process deuterocanonical books (67-99)",
    )
    args = parser.parse_args()

    start_time = time.time()

    log.info("Starting LXX ETL pipeline (CCAT morphological data)")

    # Determine which books to process
    if args.book:
        if args.book not in ABBREV_TO_BOOK:
            log.error(
                "Unknown book abbreviation: %s. Valid: %s",
                args.book,
                ", ".join(sorted(ABBREV_TO_BOOK.keys())),
            )
            return False
        books_to_process = [ABBREV_TO_BOOK[args.book]]
        log.info("Single book mode: %s", args.book)
    elif args.deuterocanonical_only:
        books_to_process = [b for b in LXX_BOOKS if b[5]]  # is_deuterocanonical
        log.info("Deuterocanonical-only mode: %d books", len(books_to_process))
    else:
        books_to_process = LXX_BOOKS
        log.info("Processing all %d LXX files", len(books_to_process))

    # Connect to database
    engine = create_engine(DATABASE_URL, echo=False)

    try:
        # 1. Verify LXX files exist
        missing_files = []
        for book_tuple in books_to_process:
            file_path = LXX_DIR / book_tuple[1]
            if not file_path.exists():
                missing_files.append(str(file_path))

        if missing_files:
            log.error("Missing LXX files:\n  %s", "\n  ".join(missing_files))
            return False

        # 2. Parse all LXX files
        all_verse_rows: list[dict] = []
        all_word_rows: list[dict] = []

        log.info("Parsing LXX files...")
        for book_tuple in books_to_process:
            file_num, filename, book_id, abbrev, english_name, is_deut = book_tuple
            file_path = LXX_DIR / filename

            verse_rows, word_rows = parse_lxx_file(file_path, book_id, abbrev)
            all_verse_rows.extend(verse_rows)
            all_word_rows.extend(word_rows)

        log.info(
            "Parsing complete: %d verses, %d words from %d files",
            len(all_verse_rows),
            len(all_word_rows),
            len(books_to_process),
        )

        # 3. Populate database
        with engine.begin() as conn:
            # 3a. Delete existing LXX data (idempotent)
            delete_lxx_data(conn, args.deuterocanonical_only)

            # 3b. Insert LXX books (deuterocanonical only)
            insert_lxx_books(conn, books_to_process)

            # 3c. Insert verses
            verse_id_map = insert_lxx_verses(conn, all_verse_rows)

            # 3d. Update book chapter/verse counts
            update_lxx_book_counts(conn)

            # 3e. Insert words
            insert_lxx_words(conn, all_word_rows, verse_id_map)

            # 3f. Create indexes (unless skipped)
            if not args.skip_indexes:
                create_indexes(conn)
            else:
                log.info("Skipping index creation (--skip-indexes)")

        # 4. Validate (separate read transaction)
        with engine.connect() as conn:
            valid = validate_and_summarize(conn)

        elapsed = time.time() - start_time
        log.info("ETL completed in %.1f seconds", elapsed)

        if valid:
            log.info("LXX ETL pipeline completed successfully")
            return True
        else:
            log.error("Validation failed — check warnings above")
            return False

    except Exception as exc:
        log.error("ETL pipeline failed: %s", exc)
        import traceback

        traceback.print_exc()
        return False
    finally:
        engine.dispose()


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
