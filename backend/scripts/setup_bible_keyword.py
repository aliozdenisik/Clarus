#!/usr/bin/env python3
"""ETL pipeline: OSHB XML + KJVA JSON -> PostgreSQL bm_books, bm_verses, bm_words.

Reads:
  - backend/data/oshb/wlc/*.xml   (39 OT books, OSHB morphological Hebrew Bible)
  - backend/data/bible_kjva.json   (KJVA English text for verse matching)

Populates:
  - bm_books   (39 OT books)
  - bm_verses  (~23,145 verses with Hebrew text_original + English text_english)
  - bm_words   (~306,000 words with morphological data)

Requires:
  - bm_strongs already loaded (13,950 entries via load_strongs.py)

Idempotent: truncates bm_words, bm_verses, bm_books before inserting.
Does NOT truncate bm_strongs.

Usage:
  python backend/scripts/setup_bible_keyword.py              # All 39 books
  python backend/scripts/setup_bible_keyword.py --book Gen   # Single book
  python backend/scripts/setup_bible_keyword.py --skip-indexes
"""

import argparse
import importlib
import json
import logging
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, text

try:
    etree = importlib.import_module("lxml.etree")
except ModuleNotFoundError:
    import xml.etree.ElementTree as etree

from src.hebrew_normalizer import (
    normalize_hebrew,
    parse_oshb_lemma,
    transliterate_hebrew,
)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

DATABASE_URL = "postgresql://postgres:postgres@localhost:54322/postgres"

DATA_DIR = Path(__file__).parent.parent / "data"
OSHB_DIR = DATA_DIR / "oshb" / "wlc"
KJVA_FILE = DATA_DIR / "bible_kjva.json"
SCROLLMAPPER_DIR = DATA_DIR / "scrollmapper"

OSIS_NS = "http://www.bibletechnologies.net/2003/OSIS/namespace"
NS = {"osis": OSIS_NS}

BATCH_SIZE = 2000

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Book metadata: OSHB filename -> canonical order, names
# ---------------------------------------------------------------------------

# (order, oshb_abbrev, english_name, hebrew_name, kjva_name)
OT_BOOKS: list[tuple[int, str, str, str, str]] = [
    (1, "Gen", "Genesis", "\u05d1\u05e8\u05d0\u05e9\u05d9\u05ea", "Genesis"),
    (2, "Exod", "Exodus", "\u05e9\u05de\u05d5\u05ea", "Exodus"),
    (3, "Lev", "Leviticus", "\u05d5\u05d9\u05e7\u05e8\u05d0", "Leviticus"),
    (4, "Num", "Numbers", "\u05d1\u05de\u05d3\u05d1\u05e8", "Numbers"),
    (5, "Deut", "Deuteronomy", "\u05d3\u05d1\u05e8\u05d9\u05dd", "Deuteronomy"),
    (6, "Josh", "Joshua", "\u05d9\u05d4\u05d5\u05e9\u05e2", "Joshua"),
    (7, "Judg", "Judges", "\u05e9\u05d5\u05e4\u05d8\u05d9\u05dd", "Judges"),
    (8, "Ruth", "Ruth", "\u05e8\u05d5\u05ea", "Ruth"),
    (9, "1Sam", "1 Samuel", "\u05e9\u05de\u05d5\u05d0\u05dc \u05d0", "1 Samuel"),
    (10, "2Sam", "2 Samuel", "\u05e9\u05de\u05d5\u05d0\u05dc \u05d1", "2 Samuel"),
    (11, "1Kgs", "1 Kings", "\u05de\u05dc\u05db\u05d9\u05dd \u05d0", "1 Kings"),
    (12, "2Kgs", "2 Kings", "\u05de\u05dc\u05db\u05d9\u05dd \u05d1", "2 Kings"),
    (
        13,
        "1Chr",
        "1 Chronicles",
        "\u05d3\u05d1\u05e8\u05d9 \u05d4\u05d9\u05de\u05d9\u05dd \u05d0",
        "1 Chronicles",
    ),
    (
        14,
        "2Chr",
        "2 Chronicles",
        "\u05d3\u05d1\u05e8\u05d9 \u05d4\u05d9\u05de\u05d9\u05dd \u05d1",
        "2 Chronicles",
    ),
    (15, "Ezra", "Ezra", "\u05e2\u05d6\u05e8\u05d0", "Ezra"),
    (16, "Neh", "Nehemiah", "\u05e0\u05d7\u05de\u05d9\u05d4", "Nehemiah"),
    (17, "Esth", "Esther", "\u05d0\u05e1\u05ea\u05e8", "Esther"),
    (18, "Job", "Job", "\u05d0\u05d9\u05d5\u05d1", "Job"),
    (19, "Ps", "Psalms", "\u05ea\u05d4\u05dc\u05d9\u05dd", "Psalms"),
    (20, "Prov", "Proverbs", "\u05de\u05e9\u05dc\u05d9", "Proverbs"),
    (21, "Eccl", "Ecclesiastes", "\u05e7\u05d4\u05dc\u05ea", "Ecclesiastes"),
    (
        22,
        "Song",
        "Song of Solomon",
        "\u05e9\u05d9\u05e8 \u05d4\u05e9\u05d9\u05e8\u05d9\u05dd",
        "Song of Solomon",
    ),
    (23, "Isa", "Isaiah", "\u05d9\u05e9\u05e2\u05d9\u05d4\u05d5", "Isaiah"),
    (24, "Jer", "Jeremiah", "\u05d9\u05e8\u05de\u05d9\u05d4\u05d5", "Jeremiah"),
    (25, "Lam", "Lamentations", "\u05d0\u05d9\u05db\u05d4", "Lamentations"),
    (26, "Ezek", "Ezekiel", "\u05d9\u05d7\u05d6\u05e7\u05d0\u05dc", "Ezekiel"),
    (27, "Dan", "Daniel", "\u05d3\u05e0\u05d9\u05d0\u05dc", "Daniel"),
    (28, "Hos", "Hosea", "\u05d4\u05d5\u05e9\u05e2", "Hosea"),
    (29, "Joel", "Joel", "\u05d9\u05d5\u05d0\u05dc", "Joel"),
    (30, "Amos", "Amos", "\u05e2\u05de\u05d5\u05e1", "Amos"),
    (31, "Obad", "Obadiah", "\u05e2\u05d1\u05d3\u05d9\u05d4", "Obadiah"),
    (32, "Jonah", "Jonah", "\u05d9\u05d5\u05e0\u05d4", "Jonah"),
    (33, "Mic", "Micah", "\u05de\u05d9\u05db\u05d4", "Micah"),
    (34, "Nah", "Nahum", "\u05e0\u05d7\u05d5\u05dd", "Nahum"),
    (35, "Hab", "Habakkuk", "\u05d7\u05d1\u05e7\u05d5\u05e7", "Habakkuk"),
    (36, "Zeph", "Zephaniah", "\u05e6\u05e4\u05e0\u05d9\u05d4", "Zephaniah"),
    (37, "Hag", "Haggai", "\u05d7\u05d2\u05d9", "Haggai"),
    (38, "Zech", "Zechariah", "\u05d6\u05db\u05e8\u05d9\u05d4", "Zechariah"),
    (39, "Mal", "Malachi", "\u05de\u05dc\u05d0\u05db\u05d9", "Malachi"),
]

# Quick lookup dicts
ABBREV_TO_ORDER = {b[1]: b[0] for b in OT_BOOKS}
ABBREV_TO_ENGLISH = {b[1]: b[2] for b in OT_BOOKS}
ABBREV_TO_HEBREW = {b[1]: b[3] for b in OT_BOOKS}
ABBREV_TO_KJVA = {b[1]: b[4] for b in OT_BOOKS}

# POS tag extraction from OSHB morph codes
POS_MAP = {
    "A": "Adjective",
    "C": "Conjunction",
    "D": "Adverb",
    "N": "Noun",
    "P": "Pronoun",
    "R": "Preposition",
    "S": "Suffix",
    "T": "Particle",
    "V": "Verb",
}


# ---------------------------------------------------------------------------
# KJVA English text loader
# ---------------------------------------------------------------------------


def load_kjva_english() -> dict[tuple[str, int, int], str]:
    """Load KJVA English text, keyed by (kjva_book_name, chapter, verse).

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

    # Only process first 39 books (OT)
    for book in books[:39]:
        book_name = book["name"]
        for chapter in book.get("chapters", []):
            ch_num = chapter["chapter"]
            for verse in chapter.get("verses", []):
                v_num = verse["verse"]
                kjva_map[(book_name, ch_num, v_num)] = verse["text"]

    log.info("Loaded %d KJVA English verses (39 OT books)", len(kjva_map))
    return kjva_map


# ---------------------------------------------------------------------------
# Scrollmapper category mapping
# ---------------------------------------------------------------------------


def get_scrollmapper_category(filename: str) -> str:
    """Map Scrollmapper filename to category.

    Categories:
    - 'apocrypha': Standard apocryphal texts (Tobit, Judith, Wisdom, Sirach, etc.)
    - 'pseudepigrapha': Jewish pseudepigraphal texts (Enoch, Jubilees, Testaments, etc.)
    - 'gnostic': Gnostic texts (Gospel of Thomas, Gospel of Philip, etc.)
    - 'apostolic_fathers': Early Christian writings (Didache, Hermas, Clement, etc.)

    Args:
        filename: Scrollmapper JSON filename (without .json extension)

    Returns:
        Category string
    """
    # Normalize filename for matching
    fn = filename.lower()

    # Apostolic Fathers
    if any(
        x in fn
        for x in ["didache", "hermas", "clement", "barnabas", "polycarp", "ignatius"]
    ):
        return "apostolic_fathers"

    # Gnostic texts
    if any(
        x in fn
        for x in [
            "gospel-of-thomas",
            "gospel-of-philip",
            "gospel-of-judas",
            "gospel-of-mary",
            "gospel-of-truth",
            "pistis-sophia",
            "apocryphon-of-john",
            "hypostasis-of-the-archons",
        ]
    ):
        return "gnostic"

    # Pseudepigrapha (Jewish)
    if any(
        x in fn
        for x in [
            "enoch",
            "jubilees",
            "testament-of-",
            "psalms-of-solomon",
            "odes-of-solomon",
            "assumption-of-moses",
            "apocalypse-of-abraham",
            "apocalypse-of-elijah",
            "apocalypse-of-peter",
            "apocalypse-of-sedrach",
            "apocryphon-of-joshua",
            "ascension-of-isaiah",
            "baruch",
            "esdras",
            "adam-and-eve",
            "genesis-apocryphon",
            "ladder-of-jacob",
            "joseph-and-asenath",
            "lives-of-the-prophets",
            "book-of-giants",
            "book-of-jasher",
            "book-of-jubilees",
            "book-of-nathan",
            "gad-the-seer",
            "jannes-and-jambres",
            "visions-of-amram",
            "wisdom-of-ahikar",
            "history-of-the-rechabites",
            "songs-of-the-sabbath",
            "five-psalms-of-david",
            "prayer-of-manasseh",
        ]
    ):
        return "pseudepigrapha"

    # Standard Apocrypha (deuterocanonical)
    if any(
        x in fn
        for x in [
            "tobit",
            "judith",
            "wisdom-of-solomon",
            "sirach",
            "maccabees",
            "baruch",
            "susanna",
            "bel-and-the-dragon",
            "greek-esther",
        ]
    ):
        return "apocrypha"

    # Default to pseudepigrapha for unknown texts
    return "pseudepigrapha"


# ---------------------------------------------------------------------------
# Scrollmapper JSON loader
# ---------------------------------------------------------------------------


def load_scrollmapper(conn, data_dir: Path) -> None:
    """Load Scrollmapper JSON texts into bm_books and bm_verses.

    Scrollmapper texts have NO morphological data, so NO bm_words entries are created.

    Args:
        conn: SQLAlchemy connection
        data_dir: Path to scrollmapper directory
    """
    if not data_dir.exists():
        log.error("Scrollmapper directory not found: %s", data_dir)
        return

    # Get all JSON files
    json_files = sorted(data_dir.glob("*.json"))
    if not json_files:
        log.warning("No JSON files found in %s", data_dir)
        return

    log.info("Loading %d Scrollmapper texts from %s", len(json_files), data_dir)

    # 1. Delete existing Scrollmapper data (idempotent)
    log.info("Cleaning up existing Scrollmapper data (book_id >= 100)...")
    conn.execute(
        text(
            "DELETE FROM bm_words WHERE verse_id IN (SELECT id FROM bm_verses WHERE book_id >= 100)"
        )
    )
    conn.execute(text("DELETE FROM bm_verses WHERE book_id >= 100"))
    conn.execute(text("DELETE FROM bm_books WHERE id >= 100"))
    log.info("Cleaned up existing Scrollmapper entries")

    # 2. Parse all Scrollmapper files
    all_books: list[dict] = []
    all_verses: list[dict] = []
    book_id = 100  # Start from 100 to avoid collision with OT books 1-39

    for json_file in json_files:
        try:
            with open(json_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            books = data.get("books", [])
            if not books:
                log.warning("No books found in %s", json_file.name)
                continue

            # Each JSON file typically has 1 book
            for book in books:
                book_name = book.get("name", "")
                if not book_name:
                    log.warning("Book without name in %s", json_file.name)
                    continue

                # Get category from filename
                filename_stem = json_file.stem  # Remove .json
                category = get_scrollmapper_category(filename_stem)

                # Count chapters and verses
                chapters = book.get("chapters", [])
                total_chapters = len(chapters)
                total_verses = sum(len(ch.get("verses", [])) for ch in chapters)

                # Add book record
                all_books.append(
                    {
                        "id": book_id,
                        "name": book_name,
                        "name_hebrew": None,
                        "name_english": book_name,
                        "testament": "apocrypha",
                        "category": category,
                        "total_chapters": total_chapters,
                        "total_verses": total_verses,
                        "book_order": book_id,
                    }
                )

                # Parse verses (deduplicate by chapter:verse)
                verses_seen = set()
                for chapter in chapters:
                    ch_num = chapter.get("chapter", 0)
                    verses = chapter.get("verses", [])

                    for verse in verses:
                        v_num = verse.get("verse", 0)
                        v_name = verse.get("name", "")
                        v_text = verse.get("text", "")

                        # Skip duplicate verses (same chapter:verse)
                        verse_key = (ch_num, v_num)
                        if verse_key in verses_seen:
                            continue
                        verses_seen.add(verse_key)

                        all_verses.append(
                            {
                                "book_id": book_id,
                                "chapter": ch_num,
                                "verse": v_num,
                                "text_original": None,  # No original language text
                                "text_english": v_text if v_text else None,
                                "reference": v_name
                                if v_name
                                else f"{book_name} {ch_num}:{v_num}",
                            }
                        )

                log.info(
                    "  %s: %d chapters, %d verses (category: %s)",
                    book_name,
                    total_chapters,
                    total_verses,
                    category,
                )

                book_id += 1

        except Exception as e:
            log.error("Error parsing %s: %s", json_file.name, e)
            continue

    log.info("Parsed %d Scrollmapper books, %d verses", len(all_books), len(all_verses))

    # 3. Insert books
    if all_books:
        conn.execute(
            text(
                "INSERT INTO bm_books "
                "(id, name, name_hebrew, name_english, testament, category, "
                "total_chapters, total_verses, book_order) "
                "VALUES (:id, :name, :name_hebrew, :name_english, :testament, "
                ":category, :total_chapters, :total_verses, :book_order)"
            ),
            all_books,
        )
        log.info("Inserted %d Scrollmapper books", len(all_books))

    # 4. Insert verses (batch)
    if all_verses:
        inserted = 0
        for i in range(0, len(all_verses), BATCH_SIZE):
            batch = all_verses[i : i + BATCH_SIZE]
            conn.execute(
                text(
                    "INSERT INTO bm_verses "
                    "(book_id, chapter, verse, text_original, text_english, reference) "
                    "VALUES (:book_id, :chapter, :verse, :text_original, :text_english, :reference)"
                ),
                batch,
            )
            inserted += len(batch)

        log.info("Inserted %d Scrollmapper verses", inserted)

    log.info(
        "Scrollmapper ETL complete: %d books, %d verses",
        len(all_books),
        len(all_verses),
    )


# ---------------------------------------------------------------------------
# Strong's lookup cache
# ---------------------------------------------------------------------------


def load_strongs_cache(conn) -> dict[str, str]:
    """Load bm_strongs into memory for fast root/lemma lookup.

    Returns:
        Dict mapping Strong's number (e.g., "H7225") -> original_word (Hebrew lemma)
    """
    result = conn.execute(
        text("SELECT number, original_word FROM bm_strongs WHERE language = 'hebrew'")
    )
    cache: dict[str, str] = {}
    for row in result:
        if row[1]:  # original_word not null
            cache[row[0]] = row[1]

    log.info("Loaded %d Hebrew Strong's entries for lookup", len(cache))
    return cache


# ---------------------------------------------------------------------------
# OSHB XML parsing
# ---------------------------------------------------------------------------


def extract_pos_tag(morph_tag: str) -> str | None:
    """Extract POS tag from OSHB morph code.

    Morph format: [H|A][prefix_indicators/]POS[details]
    - Skip language prefix (H or A)
    - Skip prefix indicators before '/'
    - Take first POS letter after the last '/'

    Examples:
        "HR/Ncfsa"  -> "N" (Noun)
        "HVqp3ms"   -> "V" (Verb)
        "HNcmpa"    -> "N" (Noun)
        "HC/To"     -> "T" (Particle)
        "HTd/Ncbsa" -> "N" (Noun) — 'd' is article prefix, N is the POS
        "AVqp3ms"   -> "V" (Verb, Aramaic)

    Args:
        morph_tag: OSHB morphology tag

    Returns:
        Single POS letter or None
    """
    if not morph_tag:
        return None

    # Remove language prefix (H or A)
    tag = morph_tag
    if tag and tag[0] in ("H", "A"):
        tag = tag[1:]

    # Split by '/' — the POS is in the last segment
    segments = tag.split("/")
    last_segment = segments[-1]

    if not last_segment:
        return None

    # First character of last segment is the POS
    pos_char = last_segment[0]
    return pos_char if pos_char in POS_MAP else None


def parse_oshb_book(
    xml_path: Path,
    book_order: int,
    abbrev: str,
    strongs_cache: dict[str, str],
) -> tuple[list[dict], list[dict]]:
    """Parse a single OSHB XML file into verse and word records.

    Args:
        xml_path: Path to the OSHB XML file
        book_order: Canonical book order (1-39)
        abbrev: OSHB book abbreviation (e.g., "Gen")
        strongs_cache: Strong's number -> original_word lookup

    Returns:
        Tuple of (verse_rows, word_rows)
    """
    tree = etree.parse(str(xml_path))
    root = tree.getroot()

    verse_rows: list[dict] = []
    word_rows: list[dict] = []
    unmapped_count = 0

    # Find the book div
    book_div = root.find(".//osis:div[@type='book']", NS)
    if book_div is None:
        log.error("No book div found in %s", xml_path.name)
        return [], []

    # Iterate chapters
    for chapter_el in book_div.findall(".//osis:chapter", NS):
        ch_osis_id = chapter_el.get("osisID", "")
        # osisID format: "Gen.1"
        parts = ch_osis_id.split(".")
        if len(parts) < 2:
            continue
        ch_num = int(parts[1])

        # Iterate verses within this chapter
        for verse_el in chapter_el.findall(".//osis:verse", NS):
            v_osis_id = verse_el.get("osisID", "")
            # osisID format: "Gen.1.1"
            v_parts = v_osis_id.split(".")
            if len(v_parts) < 3:
                continue
            v_num = int(v_parts[2])

            # Collect Hebrew text from all <w> elements in this verse
            hebrew_words: list[str] = []
            position = 0

            for child in verse_el:
                if isinstance(child.tag, str):
                    tag = child.tag.rsplit("}", 1)[-1]
                else:
                    tag = ""

                if tag == "w":
                    position += 1
                    word_text = "".join(child.itertext()).strip()

                    # Handle '/' separator in word text (e.g., "בְּ/רֵאשִׁ֖ית")
                    word_joined = word_text.replace("/", "")

                    hebrew_words.append(word_joined)

                    # Process word attributes
                    lemma_attr = child.get("lemma", "")
                    morph_attr = child.get("morph", "")

                    # Normalize word
                    word_clean = normalize_hebrew(word_joined) if word_joined else None

                    # Parse lemma to get Strong's number
                    strong_number = None
                    lemma_word = None
                    root_word = None

                    if lemma_attr:
                        parsed = parse_oshb_lemma(lemma_attr)
                        strong_number = parsed.get("strongs")

                        # Look up Strong's for root and lemma
                        if strong_number and strong_number in strongs_cache:
                            lemma_word = strongs_cache[strong_number]
                            root_word = lemma_word  # Use Strong's original_word as root
                        elif strong_number:
                            # Try without zero-padding variations
                            # e.g., H0430 might be stored as H430
                            alt_key = (
                                "H" + str(int(strong_number[1:]))
                                if strong_number.startswith("H")
                                else None
                            )
                            if alt_key and alt_key in strongs_cache:
                                lemma_word = strongs_cache[alt_key]
                                root_word = lemma_word
                            else:
                                unmapped_count += 1
                                # Fallback: use word_clean as root
                                root_word = word_clean

                    # If no Strong's at all (bare prefix), use word_clean
                    if root_word is None and word_clean:
                        root_word = word_clean

                    # Transliteration
                    transliteration = (
                        transliterate_hebrew(word_clean) if word_clean else None
                    )

                    # Language detection from morph tag
                    language = "aramaic" if morph_attr.startswith("A") else "hebrew"

                    # POS tag
                    pos_tag = extract_pos_tag(morph_attr)

                    word_rows.append(
                        {
                            "book_id": book_order,
                            "chapter": ch_num,
                            "verse": v_num,
                            "position": position,
                            "word": word_joined,
                            "word_clean": word_clean,
                            "lemma": lemma_word,
                            "root": root_word,
                            "strong_number": strong_number,
                            "morph_tag": morph_attr if morph_attr else None,
                            "pos_tag": pos_tag,
                            "transliteration": transliteration,
                            "language": language,
                            "original_lemma": lemma_attr if lemma_attr else None,
                        }
                    )

                # Skip <seg> elements (punctuation) — they are NOT words

            # Build verse Hebrew text
            text_original = " ".join(hebrew_words) if hebrew_words else None

            # Reference format: "Gen 1:1"
            reference = f"{abbrev} {ch_num}:{v_num}"

            verse_rows.append(
                {
                    "book_id": book_order,
                    "chapter": ch_num,
                    "verse": v_num,
                    "text_original": text_original,
                    "reference": reference,
                }
            )

    if unmapped_count > 0:
        log.info(
            "  %s: %d words with Strong's number not found in bm_strongs",
            abbrev,
            unmapped_count,
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


def truncate_tables(conn) -> None:
    """Truncate bm_words, bm_verses, bm_books (children first). NOT bm_strongs."""
    conn.execute(text("TRUNCATE TABLE bm_words CASCADE"))
    conn.execute(text("TRUNCATE TABLE bm_verses CASCADE"))
    conn.execute(text("TRUNCATE TABLE bm_books CASCADE"))
    log.info("Truncated bm_words, bm_verses, bm_books (bm_strongs preserved)")


def insert_books(conn, books_to_insert: list[tuple]) -> None:
    """Insert book records into bm_books.

    Args:
        conn: SQLAlchemy connection
        books_to_insert: List of (order, abbrev) tuples for books to insert
    """
    rows: list[dict] = []
    for order, abbrev in books_to_insert:
        english_name = ABBREV_TO_ENGLISH[abbrev]
        hebrew_name = ABBREV_TO_HEBREW[abbrev]

        # Count chapters and verses from parsed data (will be updated later)
        rows.append(
            {
                "id": order,
                "name": abbrev,
                "name_hebrew": hebrew_name,
                "name_english": english_name,
                "testament": "ot",
                "category": "ot",
                "total_chapters": 0,  # Updated after verse insert
                "total_verses": 0,  # Updated after verse insert
                "book_order": order,
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
    log.info("Inserted %d books", len(rows))


def update_book_counts(conn) -> None:
    """Update total_chapters and total_verses in bm_books from actual verse data."""
    conn.execute(
        text(
            "UPDATE bm_books b SET "
            "total_chapters = sub.ch_count, "
            "total_verses = sub.v_count "
            "FROM ("
            "  SELECT book_id, COUNT(DISTINCT chapter) AS ch_count, COUNT(*) AS v_count "
            "  FROM bm_verses GROUP BY book_id"
            ") sub "
            "WHERE b.id = sub.book_id"
        )
    )
    log.info("Updated book chapter/verse counts")


def insert_verses(
    conn,
    all_verse_rows: list[dict],
    kjva_map: dict[tuple[str, int, int], str],
) -> dict[tuple[int, int, int], int]:
    """Insert verses into bm_verses with English text matching.

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
        for order, ab in ABBREV_TO_ORDER.items():
            if ab == book_id:
                abbrev = order
                break
        # Reverse lookup: book_id -> abbrev
        for b in OT_BOOKS:
            if b[0] == book_id:
                abbrev = b[1]
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
        "Inserted %d verses (English matched: %d, missing: %d)",
        inserted,
        english_matched,
        english_missing,
    )
    return _build_verse_id_map(conn)


def _build_verse_id_map(conn) -> dict[tuple[int, int, int], int]:
    """Build mapping of (book_id, chapter, verse) -> verse_db_id."""
    result = conn.execute(
        text("SELECT id, book_id, chapter, verse FROM bm_verses ORDER BY id")
    )
    verse_map: dict[tuple[int, int, int], int] = {}
    for row in result:
        verse_map[(row[1], row[2], row[3])] = row[0]
    return verse_map


def insert_words(
    conn,
    all_word_rows: list[dict],
    verse_id_map: dict[tuple[int, int, int], int],
) -> int:
    """Insert words into bm_words with FK resolution.

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

    log.info("Inserted %d words total", inserted)
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

    # Book counts
    result = conn.execute(text("SELECT COUNT(*) FROM bm_books WHERE testament = 'ot'"))
    ot_book_count = result.scalar()
    log.info("Books (OT): %d", ot_book_count)

    result = conn.execute(
        text("SELECT COUNT(*) FROM bm_books WHERE testament = 'apocrypha'")
    )
    apocrypha_book_count = result.scalar()
    log.info("Books (Apocrypha/Scrollmapper): %d", apocrypha_book_count)

    # Verse count
    result = conn.execute(text("SELECT COUNT(*) FROM bm_verses"))
    verse_count = result.scalar()
    log.info("Verses: %d", verse_count)

    # Word count
    result = conn.execute(text("SELECT COUNT(*) FROM bm_words"))
    word_count = result.scalar()
    log.info("Words: %d", word_count)

    # Hebrew vs Aramaic
    result = conn.execute(
        text(
            "SELECT language, COUNT(*) FROM bm_words GROUP BY language ORDER BY language"
        )
    )
    lang_counts = {row[0]: row[1] for row in result}
    for lang, cnt in lang_counts.items():
        log.info("  %s words: %d", lang, cnt)

    # Words with/without Strong's
    result = conn.execute(
        text("SELECT COUNT(*) FROM bm_words WHERE strong_number IS NOT NULL")
    )
    with_strongs = result.scalar()
    result = conn.execute(
        text("SELECT COUNT(*) FROM bm_words WHERE strong_number IS NULL")
    )
    without_strongs = result.scalar()
    log.info("Words with Strong's: %d, without: %d", with_strongs, without_strongs)

    # Unique roots
    result = conn.execute(
        text("SELECT COUNT(DISTINCT root) FROM bm_words WHERE root IS NOT NULL")
    )
    unique_roots = result.scalar()
    log.info("Unique roots: %d", unique_roots)

    # Top 10 most common roots
    result = conn.execute(
        text(
            "SELECT root, COUNT(*) AS cnt FROM bm_words "
            "WHERE root IS NOT NULL "
            "GROUP BY root ORDER BY cnt DESC LIMIT 10"
        )
    )
    top_roots = [(row[0], row[1]) for row in result]

    # English text coverage
    result = conn.execute(
        text("SELECT COUNT(*) FROM bm_verses WHERE text_english IS NOT NULL")
    )
    english_count = result.scalar()
    result = conn.execute(
        text("SELECT COUNT(*) FROM bm_verses WHERE text_english IS NULL")
    )
    no_english = result.scalar()

    # Print summary
    print("\n" + "=" * 60)
    print("  BIBLE KEYWORD ETL — SUMMARY")
    print("=" * 60)
    print(f"  Books (OT):        {ot_book_count:>8,}")
    print(f"  Books (Apocrypha): {apocrypha_book_count:>8,}")
    print(f"  Total Books:       {ot_book_count + apocrypha_book_count:>8,}")
    print(f"  Verses:            {verse_count:>8,}")
    print(f"  Words:             {word_count:>8,}")
    for lang, cnt in sorted(lang_counts.items()):
        print(f"    {lang:>12}:    {cnt:>8,}")
    print(f"  With Strong's:     {with_strongs:>8,}")
    print(f"  Without Strong's:  {without_strongs:>8,}")
    print(f"  Unique roots:      {unique_roots:>8,}")
    print(f"  English matched:   {english_count:>8,}")
    print(f"  English missing:   {no_english:>8,}")
    print()
    if top_roots:
        print("  Top 10 most common roots:")
        for i, (root, cnt) in enumerate(top_roots, 1):
            print(f"    {i:>2}. {root:<20} {cnt:>6,} occurrences")
    print("=" * 60)

    # Sample verification
    result = conn.execute(
        text(
            "SELECT b.name_english, v.chapter, v.verse, "
            "LEFT(v.text_original, 50), LEFT(v.text_english, 50) "
            "FROM bm_verses v JOIN bm_books b ON v.book_id = b.id "
            "WHERE v.reference = 'Gen 1:1'"
        )
    )
    row = result.fetchone()
    if row:
        print("\n  Sample Gen 1:1:")
        print(f"    Book: {row[0]}")
        print(f"    Hebrew: {row[3]}")
        print(f"    English: {row[4]}")
    else:
        log.error("Gen 1:1 not found in bm_verses")
        checks_passed = False

    # Sample word
    result = conn.execute(
        text(
            "SELECT w.word, w.word_clean, w.strong_number, w.root, w.lemma, "
            "w.morph_tag, w.pos_tag, w.transliteration, w.language "
            "FROM bm_words w JOIN bm_verses v ON w.verse_id = v.id "
            "WHERE v.reference = 'Gen 1:1' ORDER BY w.position LIMIT 3"
        )
    )
    rows = result.fetchall()
    if rows:
        print("\n  Sample words from Gen 1:1:")
        for r in rows:
            print(
                f"    {r[0]} | clean={r[1]} | strong={r[2]} | root={r[3]} | "
                f"lemma={r[4]} | morph={r[5]} | pos={r[6]} | xlit={r[7]} | lang={r[8]}"
            )

    print("=" * 60 + "\n")
    return checks_passed


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> bool:
    """Run the Bible keyword ETL pipeline. Returns True on success."""
    parser = argparse.ArgumentParser(
        description="ETL: OSHB XML + KJVA JSON + Scrollmapper -> bm_books, bm_verses, bm_words"
    )
    parser.add_argument(
        "--book",
        type=str,
        default=None,
        help="Parse single OT book only (e.g., --book Gen)",
    )
    parser.add_argument(
        "--scrollmapper-only",
        action="store_true",
        help="Load ONLY Scrollmapper texts (skip OSHB OT)",
    )
    parser.add_argument(
        "--skip-indexes",
        action="store_true",
        help="Skip index creation after ETL",
    )
    args = parser.parse_args()

    start_time = time.time()

    # Determine ETL mode
    if args.scrollmapper_only:
        log.info("Starting Scrollmapper-only ETL pipeline")
        scrollmapper_mode = True
        books_to_process = []
    else:
        log.info("Starting Bible Keyword ETL pipeline (OSHB + Scrollmapper)")
        scrollmapper_mode = False

        # Determine which OT books to process
        if args.book:
            if args.book not in ABBREV_TO_ORDER:
                log.error(
                    "Unknown book abbreviation: %s. Valid: %s",
                    args.book,
                    ", ".join(sorted(ABBREV_TO_ORDER.keys())),
                )
                return False
            books_to_process = [(ABBREV_TO_ORDER[args.book], args.book)]
            log.info("Single book mode: %s", args.book)
        else:
            books_to_process = [(b[0], b[1]) for b in OT_BOOKS]
            log.info("Processing all %d OT books", len(books_to_process))

    # Connect to database
    engine = create_engine(DATABASE_URL, echo=False)

    try:
        if scrollmapper_mode:
            # Scrollmapper-only mode: load Scrollmapper texts
            log.info("Scrollmapper-only mode: loading 69 texts")

            with engine.begin() as conn:
                # Load Scrollmapper data (handles its own cleanup)
                load_scrollmapper(conn, SCROLLMAPPER_DIR)

                # Create indexes (unless skipped)
                if not args.skip_indexes:
                    create_indexes(conn)
                else:
                    log.info("Skipping index creation (--skip-indexes)")

        else:
            # OSHB mode (with optional Scrollmapper)
            # 1. Verify OSHB files exist
            missing_files = []
            for order, abbrev in books_to_process:
                xml_path = OSHB_DIR / f"{abbrev}.xml"
                if not xml_path.exists():
                    missing_files.append(str(xml_path))
            if missing_files:
                log.error("Missing OSHB XML files:\n  %s", "\n  ".join(missing_files))
                return False

            # 2. Load KJVA English text
            kjva_map = load_kjva_english()

            # 3a. Load Strong's cache (read-only, separate connection)
            with engine.connect() as conn:
                strongs_cache = load_strongs_cache(conn)

            # 4. Parse all OSHB XML files
            all_verse_rows: list[dict] = []
            all_word_rows: list[dict] = []

            log.info("Parsing OSHB XML files...")
            for order, abbrev in books_to_process:
                xml_path = OSHB_DIR / f"{abbrev}.xml"
                verse_rows, word_rows = parse_oshb_book(
                    xml_path, order, abbrev, strongs_cache
                )
                all_verse_rows.extend(verse_rows)
                all_word_rows.extend(word_rows)

            log.info(
                "Parsing complete: %d verses, %d words from %d books",
                len(all_verse_rows),
                len(all_word_rows),
                len(books_to_process),
            )

            # 5. Populate database
            with engine.begin() as conn:
                # 5a. Truncate (idempotent) — only for OSHB mode
                truncate_tables(conn)

                # 5b. Insert books
                insert_books(conn, books_to_process)

                # 5c. Insert verses (with English text matching)
                verse_id_map = insert_verses(conn, all_verse_rows, kjva_map)

                # 5d. Update book chapter/verse counts
                update_book_counts(conn)

                # 5e. Insert words
                insert_words(conn, all_word_rows, verse_id_map)

                # 5f. Load Scrollmapper texts (append to existing data)
                log.info("Loading Scrollmapper texts...")
                load_scrollmapper(conn, SCROLLMAPPER_DIR)

                # 5g. Create indexes (unless skipped)
                if not args.skip_indexes:
                    create_indexes(conn)
                else:
                    log.info("Skipping index creation (--skip-indexes)")

        # 6. Validate (separate read transaction)
        with engine.connect() as conn:
            valid = validate_and_summarize(conn)

        elapsed = time.time() - start_time
        log.info("ETL completed in %.1f seconds", elapsed)

        if valid:
            log.info("ETL pipeline completed successfully")
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
