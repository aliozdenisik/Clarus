#!/usr/bin/env python3
"""ETL pipeline: MorphGNT + KJVA JSON -> PostgreSQL bm_books, bm_verses, bm_words.

Reads:
  - backend/data/morphgnt/*.txt   (27 NT books, MorphGNT SBLGNT)
  - backend/data/bible_kjva.json  (KJVA English text for verse matching)

Populates:
  - bm_books   (27 NT books, book_id 40-66)
  - bm_verses  (~7,957 verses with Greek text_original + English text_english)
  - bm_words   (~140,000 words with morphological data)

Does NOT modify existing OT/Apocrypha data (book_id 1-39, 100+).

Usage:
  python backend/scripts/setup_greek_nt.py              # All 27 NT books
  python backend/scripts/setup_greek_nt.py --book Matt  # Single book
  python backend/scripts/setup_greek_nt.py --skip-indexes
"""

import argparse
import json
import logging
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
MORPHGNT_DIR = DATA_DIR / "morphgnt"
KJVA_FILE = DATA_DIR / "bible_kjva.json"

BATCH_SIZE = 2000

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# NT Book metadata: MorphGNT file number -> canonical order, names
# ---------------------------------------------------------------------------

# (book_id, morphgnt_file_num, morphgnt_abbrev, english_name, greek_name, kjva_name)
# book_id: 40-66 (continuing from OT 1-39)
# morphgnt_file_num: 61-87 (MorphGNT file naming)
# morphgnt_bcv_book: 01-27 (MorphGNT bcv column book number)
NT_BOOKS: list[tuple[int, int, int, str, str, str, str]] = [
    (40, 61, 1, "Matt", "Matthew", "Κατὰ Ματθαῖον", "Matthew"),
    (41, 62, 2, "Mark", "Mark", "Κατὰ Μᾶρκον", "Mark"),
    (42, 63, 3, "Luke", "Luke", "Κατὰ Λουκᾶν", "Luke"),
    (43, 64, 4, "John", "John", "Κατὰ Ἰωάννην", "John"),
    (44, 65, 5, "Acts", "Acts", "Πράξεις Ἀποστόλων", "Acts"),
    (45, 66, 6, "Rom", "Romans", "Πρὸς Ῥωμαίους", "Romans"),
    (46, 67, 7, "1Cor", "1 Corinthians", "Πρὸς Κορινθίους Αʹ", "1 Corinthians"),
    (47, 68, 8, "2Cor", "2 Corinthians", "Πρὸς Κορινθίους Βʹ", "2 Corinthians"),
    (48, 69, 9, "Gal", "Galatians", "Πρὸς Γαλάτας", "Galatians"),
    (49, 70, 10, "Eph", "Ephesians", "Πρὸς Ἐφεσίους", "Ephesians"),
    (50, 71, 11, "Phil", "Philippians", "Πρὸς Φιλιππησίους", "Philippians"),
    (51, 72, 12, "Col", "Colossians", "Πρὸς Κολοσσαεῖς", "Colossians"),
    (
        52,
        73,
        13,
        "1Thess",
        "1 Thessalonians",
        "Πρὸς Θεσσαλονικεῖς Αʹ",
        "1 Thessalonians",
    ),
    (
        53,
        74,
        14,
        "2Thess",
        "2 Thessalonians",
        "Πρὸς Θεσσαλονικεῖς Βʹ",
        "2 Thessalonians",
    ),
    (54, 75, 15, "1Tim", "1 Timothy", "Πρὸς Τιμόθεον Αʹ", "1 Timothy"),
    (55, 76, 16, "2Tim", "2 Timothy", "Πρὸς Τιμόθεον Βʹ", "2 Timothy"),
    (56, 77, 17, "Titus", "Titus", "Πρὸς Τίτον", "Titus"),
    (57, 78, 18, "Phlm", "Philemon", "Πρὸς Φιλήμονα", "Philemon"),
    (58, 79, 19, "Heb", "Hebrews", "Πρὸς Ἑβραίους", "Hebrews"),
    (59, 80, 20, "Jas", "James", "Ἰακώβου", "James"),
    (60, 81, 21, "1Pet", "1 Peter", "Πέτρου Αʹ", "1 Peter"),
    (61, 82, 22, "2Pet", "2 Peter", "Πέτρου Βʹ", "2 Peter"),
    (62, 83, 23, "1John", "1 John", "Ἰωάννου Αʹ", "1 John"),
    (63, 84, 24, "2John", "2 John", "Ἰωάννου Βʹ", "2 John"),
    (64, 85, 25, "3John", "3 John", "Ἰωάννου Γʹ", "3 John"),
    (65, 86, 26, "Jude", "Jude", "Ἰούδα", "Jude"),
    (66, 87, 27, "Rev", "Revelation", "Ἀποκάλυψις Ἰωάννου", "Revelation of John"),
]

# Quick lookup dicts
ABBREV_TO_BOOK_ID = {b[3]: b[0] for b in NT_BOOKS}
ABBREV_TO_ENGLISH = {b[3]: b[4] for b in NT_BOOKS}
ABBREV_TO_GREEK = {b[3]: b[5] for b in NT_BOOKS}
ABBREV_TO_KJVA = {b[3]: b[6] for b in NT_BOOKS}
FILE_NUM_TO_ABBREV = {b[1]: b[3] for b in NT_BOOKS}
BCV_BOOK_TO_BOOK_ID = {b[2]: b[0] for b in NT_BOOKS}

# MorphGNT file name patterns
MORPHGNT_FILE_PATTERNS = {
    61: "61-Mt-morphgnt.txt",
    62: "62-Mk-morphgnt.txt",
    63: "63-Lk-morphgnt.txt",
    64: "64-Jn-morphgnt.txt",
    65: "65-Ac-morphgnt.txt",
    66: "66-Ro-morphgnt.txt",
    67: "67-1Co-morphgnt.txt",
    68: "68-2Co-morphgnt.txt",
    69: "69-Ga-morphgnt.txt",
    70: "70-Eph-morphgnt.txt",
    71: "71-Php-morphgnt.txt",
    72: "72-Col-morphgnt.txt",
    73: "73-1Th-morphgnt.txt",
    74: "74-2Th-morphgnt.txt",
    75: "75-1Ti-morphgnt.txt",
    76: "76-2Ti-morphgnt.txt",
    77: "77-Tit-morphgnt.txt",
    78: "78-Phm-morphgnt.txt",
    79: "79-Heb-morphgnt.txt",
    80: "80-Jas-morphgnt.txt",
    81: "81-1Pe-morphgnt.txt",
    82: "82-2Pe-morphgnt.txt",
    83: "83-1Jn-morphgnt.txt",
    84: "84-2Jn-morphgnt.txt",
    85: "85-3Jn-morphgnt.txt",
    86: "86-Jud-morphgnt.txt",
    87: "87-Re-morphgnt.txt",
}

# POS tag mapping from MorphGNT
POS_MAP = {
    "A-": "Adjective",
    "C-": "Conjunction",
    "D-": "Adverb",
    "I-": "Interjection",
    "N-": "Noun",
    "P-": "Preposition",
    "RA": "Article",
    "RD": "Demonstrative",
    "RI": "Interrogative",
    "RP": "Personal",
    "RR": "Relative",
    "V-": "Verb",
    "X-": "Particle",
}


# ---------------------------------------------------------------------------
# KJVA English text loader
# ---------------------------------------------------------------------------


def load_kjva_nt_english() -> dict[tuple[str, int, int], str]:
    """Load KJVA English text for NT books, keyed by (kjva_book_name, chapter, verse).

    Returns:
        Dict mapping (book_name, chapter, verse) -> English text
    """
    if not KJVA_FILE.exists():
        log.warning("KJVA file not found: %s — English text will be empty", KJVA_FILE)
        return {}

    with open(KJVA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    kjva_map: dict[tuple[str, int, int], str] = {}
    books = data.get("books", [])

    # NT books are at indices 53-79 in KJVA (Matthew to Revelation)
    for book in books[53:80]:
        book_name = book["name"]
        for chapter in book.get("chapters", []):
            ch_num = chapter["chapter"]
            for verse in chapter.get("verses", []):
                v_num = verse["verse"]
                kjva_map[(book_name, ch_num, v_num)] = verse["text"]

    log.info("Loaded %d KJVA English verses (27 NT books)", len(kjva_map))
    return kjva_map


# ---------------------------------------------------------------------------
# MorphGNT parsing
# ---------------------------------------------------------------------------


def extract_pos_tag(pos_code: str) -> str | None:
    """Extract POS tag from MorphGNT POS code.

    MorphGNT POS codes are 2 characters (e.g., "N-", "V-", "RA").

    Args:
        pos_code: MorphGNT POS code

    Returns:
        Single POS letter or None
    """
    if not pos_code or len(pos_code) < 2:
        return None

    # Return first character as POS tag
    return pos_code[0]


def parse_morphgnt_book(
    txt_path: Path,
    book_id: int,
    abbrev: str,
) -> tuple[list[dict], list[dict]]:
    """Parse a single MorphGNT text file into verse and word records.

    MorphGNT format (space-separated, 7 columns):
      bcv     pos  parse     text      word      normalized  lemma
      010101  N-   ----NSF-  Βίβλος    Βίβλος    βίβλος      βίβλος

    Args:
        txt_path: Path to the MorphGNT text file
        book_id: Canonical book ID (40-66)
        abbrev: Book abbreviation (e.g., "Matt")

    Returns:
        Tuple of (verse_rows, word_rows)
    """
    verse_rows: list[dict] = []
    word_rows: list[dict] = []

    # Track verses to build text_original
    verse_words: dict[tuple[int, int], list[str]] = {}  # (chapter, verse) -> words
    verse_positions: dict[
        tuple[int, int], int
    ] = {}  # (chapter, verse) -> position counter

    with open(txt_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            parts = line.split()
            if len(parts) != 7:
                log.warning(
                    "Unexpected line format in %s: %s", txt_path.name, line[:50]
                )
                continue

            bcv, pos, parse, text_col, word_col, normalized, lemma = parts

            # Parse bcv (BBCCVV format)
            # BB = book (01-27), CC = chapter, VV = verse
            if len(bcv) != 6:
                log.warning("Invalid bcv format: %s", bcv)
                continue

            int(bcv[0:2])
            chapter = int(bcv[2:4])
            verse = int(bcv[4:6])

            # Initialize verse tracking
            verse_key = (chapter, verse)
            if verse_key not in verse_words:
                verse_words[verse_key] = []
                verse_positions[verse_key] = 0

            # Increment position
            verse_positions[verse_key] += 1
            position = verse_positions[verse_key]

            # Clean word (remove punctuation from text column)
            word_text = text_col.rstrip(".,;:!?·")
            verse_words[verse_key].append(word_text)

            # Normalize word
            word_clean = normalize_greek(normalized) if normalized else None

            # Transliteration
            transliteration = transliterate_greek(word_clean) if word_clean else None

            # POS tag
            pos_tag = extract_pos_tag(pos)

            word_rows.append(
                {
                    "book_id": book_id,
                    "chapter": chapter,
                    "verse": verse,
                    "position": position,
                    "word": word_col,  # word column (with accents)
                    "word_clean": word_clean,  # normalized column (no accents)
                    "lemma": lemma,  # lemma column
                    "root": lemma,  # Greek uses lemma as root
                    "strong_number": None,  # MorphGNT doesn't include Strong's
                    "morph_tag": parse if parse else None,
                    "pos_tag": pos_tag,
                    "transliteration": transliteration,
                    "language": "greek",
                    "original_lemma": lemma,
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


def delete_nt_data(conn) -> None:
    """Delete existing NT data (book_id 40-66) without affecting OT/Apocrypha."""
    log.info("Deleting existing NT data (book_id 40-66)...")
    conn.execute(
        text(
            "DELETE FROM bm_words WHERE verse_id IN (SELECT id FROM bm_verses WHERE book_id BETWEEN 40 AND 66)"
        )
    )
    conn.execute(text("DELETE FROM bm_verses WHERE book_id BETWEEN 40 AND 66"))
    conn.execute(text("DELETE FROM bm_books WHERE id BETWEEN 40 AND 66"))
    log.info("Deleted existing NT entries")


def insert_nt_books(conn, books_to_insert: list[tuple]) -> None:
    """Insert NT book records into bm_books.

    Args:
        conn: SQLAlchemy connection
        books_to_insert: List of (book_id, abbrev) tuples for books to insert
    """
    rows: list[dict] = []
    for book_id, abbrev in books_to_insert:
        english_name = ABBREV_TO_ENGLISH[abbrev]
        greek_name = ABBREV_TO_GREEK[abbrev]

        rows.append(
            {
                "id": book_id,
                "name": abbrev,
                "name_hebrew": greek_name,  # Using name_hebrew for Greek name
                "name_english": english_name,
                "testament": "nt",
                "category": "nt",
                "total_chapters": 0,  # Updated after verse insert
                "total_verses": 0,  # Updated after verse insert
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
    log.info("Inserted %d NT books", len(rows))


def update_nt_book_counts(conn) -> None:
    """Update total_chapters and total_verses in bm_books for NT books."""
    conn.execute(
        text(
            "UPDATE bm_books b SET "
            "total_chapters = sub.ch_count, "
            "total_verses = sub.v_count "
            "FROM ("
            "  SELECT book_id, COUNT(DISTINCT chapter) AS ch_count, COUNT(*) AS v_count "
            "  FROM bm_verses WHERE book_id BETWEEN 40 AND 66 GROUP BY book_id"
            ") sub "
            "WHERE b.id = sub.book_id"
        )
    )
    log.info("Updated NT book chapter/verse counts")


def insert_nt_verses(
    conn,
    all_verse_rows: list[dict],
    kjva_map: dict[tuple[str, int, int], str],
) -> dict[tuple[int, int, int], int]:
    """Insert NT verses into bm_verses with English text matching.

    Args:
        conn: SQLAlchemy connection
        all_verse_rows: List of verse dicts from parsing
        kjva_map: KJVA English text lookup

    Returns:
        Mapping of (book_id, chapter, verse) -> verse_db_id
    """
    rows_to_insert: list[dict] = []
    english_matched = 0
    english_missing = 0

    for vr in all_verse_rows:
        book_id = vr["book_id"]
        ch = vr["chapter"]
        v = vr["verse"]

        # Look up KJVA English text
        abbrev = None
        for b in NT_BOOKS:
            if b[0] == book_id:
                abbrev = b[3]
                break

        kjva_name = ABBREV_TO_KJVA.get(abbrev, "") if abbrev else ""
        text_english = kjva_map.get((kjva_name, ch, v))

        if text_english:
            english_matched += 1
        else:
            english_missing += 1

        rows_to_insert.append(
            {
                "book_id": book_id,
                "chapter": ch,
                "verse": v,
                "text_original": vr["text_original"],
                "text_english": text_english,
                "reference": vr["reference"],
            }
        )

    # Batch insert
    inserted = 0
    for i in range(0, len(rows_to_insert), BATCH_SIZE):
        batch = rows_to_insert[i : i + BATCH_SIZE]
        conn.execute(
            text(
                "INSERT INTO bm_verses "
                "(book_id, chapter, verse, text_original, text_english, reference) "
                "VALUES (:book_id, :chapter, :verse, :text_original, :text_english, :reference)"
            ),
            batch,
        )
        inserted += len(batch)

    log.info(
        "Inserted %d NT verses (English matched: %d, missing: %d)",
        inserted,
        english_matched,
        english_missing,
    )
    return _build_nt_verse_id_map(conn)


def _build_nt_verse_id_map(conn) -> dict[tuple[int, int, int], int]:
    """Build mapping of (book_id, chapter, verse) -> verse_db_id for NT."""
    result = conn.execute(
        text(
            "SELECT id, book_id, chapter, verse FROM bm_verses WHERE book_id BETWEEN 40 AND 66 ORDER BY id"
        )
    )
    verse_map: dict[tuple[int, int, int], int] = {}
    for row in result:
        verse_map[(row[1], row[2], row[3])] = row[0]
    return verse_map


def insert_nt_words(
    conn,
    all_word_rows: list[dict],
    verse_id_map: dict[tuple[int, int, int], int],
) -> int:
    """Insert NT words into bm_words with FK resolution.

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

    log.info("Inserted %d Greek NT words total", inserted)
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

    # NT Book counts
    result = conn.execute(text("SELECT COUNT(*) FROM bm_books WHERE testament = 'nt'"))
    nt_book_count = result.scalar()
    log.info("Books (NT): %d", nt_book_count)

    # NT Verse count
    result = conn.execute(
        text("SELECT COUNT(*) FROM bm_verses WHERE book_id BETWEEN 40 AND 66")
    )
    nt_verse_count = result.scalar()
    log.info("Verses (NT): %d", nt_verse_count)

    # Greek word count
    result = conn.execute(
        text("SELECT COUNT(*) FROM bm_words WHERE language = 'greek'")
    )
    greek_word_count = result.scalar()
    log.info("Words (Greek): %d", greek_word_count)

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

    # Top 10 most common Greek lemmas
    result = conn.execute(
        text(
            "SELECT lemma, COUNT(*) AS cnt FROM bm_words "
            "WHERE language = 'greek' AND lemma IS NOT NULL "
            "GROUP BY lemma ORDER BY cnt DESC LIMIT 10"
        )
    )
    top_lemmas = [(row[0], row[1]) for row in result]

    # English text coverage for NT
    result = conn.execute(
        text(
            "SELECT COUNT(*) FROM bm_verses WHERE book_id BETWEEN 40 AND 66 AND text_english IS NOT NULL"
        )
    )
    english_count = result.scalar()
    result = conn.execute(
        text(
            "SELECT COUNT(*) FROM bm_verses WHERE book_id BETWEEN 40 AND 66 AND text_english IS NULL"
        )
    )
    no_english = result.scalar()

    # Print summary
    print("\n" + "=" * 60)
    print("  GREEK NT ETL — SUMMARY")
    print("=" * 60)
    print(f"  Books (NT):        {nt_book_count:>8,}")
    print(f"  Verses (NT):       {nt_verse_count:>8,}")
    print(f"  Words (Greek):     {greek_word_count:>8,}")
    print(f"  Words (Total):     {total_word_count:>8,}")
    for lang, cnt in sorted(lang_counts.items()):
        print(f"    {lang:>12}:    {cnt:>8,}")
    print(f"  Unique lemmas:     {unique_lemmas:>8,}")
    print(f"  English matched:   {english_count:>8,}")
    print(f"  English missing:   {no_english:>8,}")
    print()
    if top_lemmas:
        print("  Top 10 most common Greek lemmas:")
        for i, (lemma, cnt) in enumerate(top_lemmas, 1):
            print(f"    {i:>2}. {lemma:<20} {cnt:>6,} occurrences")
    print("=" * 60)

    # Sample verification - Matthew 1:1
    result = conn.execute(
        text(
            "SELECT b.name_english, v.chapter, v.verse, "
            "LEFT(v.text_original, 50), LEFT(v.text_english, 50) "
            "FROM bm_verses v JOIN bm_books b ON v.book_id = b.id "
            "WHERE v.reference = 'Matt 1:1'"
        )
    )
    row = result.fetchone()
    if row:
        print("\n  Sample Matt 1:1:")
        print(f"    Book: {row[0]}")
        print(f"    Greek: {row[3]}")
        print(f"    English: {row[4]}")
    else:
        log.error("Matt 1:1 not found in bm_verses")
        checks_passed = False

    # Sample word
    result = conn.execute(
        text(
            "SELECT w.word, w.word_clean, w.lemma, w.root, "
            "w.morph_tag, w.pos_tag, w.transliteration, w.language "
            "FROM bm_words w JOIN bm_verses v ON w.verse_id = v.id "
            "WHERE v.reference = 'Matt 1:1' ORDER BY w.position LIMIT 3"
        )
    )
    rows = result.fetchall()
    if rows:
        print("\n  Sample words from Matt 1:1:")
        for r in rows:
            print(
                f"    {r[0]} | clean={r[1]} | lemma={r[2]} | root={r[3]} | "
                f"morph={r[4]} | pos={r[5]} | xlit={r[6]} | lang={r[7]}"
            )

    print("=" * 60 + "\n")
    return checks_passed


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> bool:
    """Run the Greek NT ETL pipeline. Returns True on success."""
    parser = argparse.ArgumentParser(
        description="ETL: MorphGNT + KJVA JSON -> bm_books, bm_verses, bm_words (NT)"
    )
    parser.add_argument(
        "--book",
        type=str,
        default=None,
        help="Parse single NT book only (e.g., --book Matt)",
    )
    parser.add_argument(
        "--skip-indexes",
        action="store_true",
        help="Skip index creation after ETL",
    )
    args = parser.parse_args()

    start_time = time.time()

    log.info("Starting Greek NT ETL pipeline (MorphGNT)")

    # Determine which NT books to process
    if args.book:
        if args.book not in ABBREV_TO_BOOK_ID:
            log.error(
                "Unknown book abbreviation: %s. Valid: %s",
                args.book,
                ", ".join(sorted(ABBREV_TO_BOOK_ID.keys())),
            )
            return False
        books_to_process = [(ABBREV_TO_BOOK_ID[args.book], args.book)]
        log.info("Single book mode: %s", args.book)
    else:
        books_to_process = [(b[0], b[3]) for b in NT_BOOKS]
        log.info("Processing all %d NT books", len(books_to_process))

    # Connect to database
    engine = create_engine(DATABASE_URL, echo=False)

    try:
        # 1. Verify MorphGNT files exist
        missing_files = []
        for book_id, abbrev in books_to_process:
            # Find file number for this book
            found_file_num: int | None = None
            for b in NT_BOOKS:
                if b[0] == book_id:
                    found_file_num = b[1]
                    break
            if found_file_num is None:
                missing_files.append(f"Unknown book_id: {book_id}")
                continue

            filename = MORPHGNT_FILE_PATTERNS.get(found_file_num)
            if filename is None:
                missing_files.append(f"Unknown file_num: {found_file_num}")
                continue

            txt_path = MORPHGNT_DIR / filename
            if not txt_path.exists():
                missing_files.append(str(txt_path))

        if missing_files:
            log.error("Missing MorphGNT files:\n  %s", "\n  ".join(missing_files))
            return False

        # 2. Load KJVA English text
        kjva_map = load_kjva_nt_english()

        # 3. Parse all MorphGNT files
        all_verse_rows: list[dict] = []
        all_word_rows: list[dict] = []

        log.info("Parsing MorphGNT files...")
        for book_id, abbrev in books_to_process:
            # Find file number for this book
            file_num: int = 61  # Default to Matthew
            for b in NT_BOOKS:
                if b[0] == book_id:
                    file_num = b[1]
                    break

            filename = MORPHGNT_FILE_PATTERNS[file_num]
            txt_path = MORPHGNT_DIR / filename

            verse_rows, word_rows = parse_morphgnt_book(txt_path, book_id, abbrev)
            all_verse_rows.extend(verse_rows)
            all_word_rows.extend(word_rows)

        log.info(
            "Parsing complete: %d verses, %d words from %d books",
            len(all_verse_rows),
            len(all_word_rows),
            len(books_to_process),
        )

        # 4. Populate database
        with engine.begin() as conn:
            # 4a. Delete existing NT data (idempotent)
            delete_nt_data(conn)

            # 4b. Insert NT books
            insert_nt_books(conn, books_to_process)

            # 4c. Insert verses (with English text matching)
            verse_id_map = insert_nt_verses(conn, all_verse_rows, kjva_map)

            # 4d. Update book chapter/verse counts
            update_nt_book_counts(conn)

            # 4e. Insert words
            insert_nt_words(conn, all_word_rows, verse_id_map)

            # 4f. Create indexes (unless skipped)
            if not args.skip_indexes:
                create_indexes(conn)
            else:
                log.info("Skipping index creation (--skip-indexes)")

        # 5. Validate (separate read transaction)
        with engine.connect() as conn:
            valid = validate_and_summarize(conn)

        elapsed = time.time() - start_time
        log.info("ETL completed in %.1f seconds", elapsed)

        if valid:
            log.info("Greek NT ETL pipeline completed successfully")
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
