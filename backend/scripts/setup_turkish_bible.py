#!/usr/bin/env python3
"""ETL pipeline: Turkish Bible OSIS XML -> bm_verses.text_turkish.

Reads:
  - backend/data/turkish_bible/tur-turkish.osis.xml (1941 Turkish translation)

Updates:
  - bm_verses.text_turkish column for matching verses

Requires:
  - bm_verses already populated (via setup_bible_keyword.py)

Reference format mapping:
  - OSIS: "Gen.1.1" -> bm_verses.reference: "Gen 1:1"

Usage:
  python backend/scripts/setup_turkish_bible.py
  python backend/scripts/setup_turkish_bible.py --dry-run  # Preview without updating
"""

import argparse
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from lxml import etree
from sqlalchemy import create_engine, text

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

DATABASE_URL = "postgresql://postgres:postgres@localhost:54322/postgres"

DATA_DIR = Path(__file__).parent.parent / "data"
TURKISH_BIBLE_FILE = DATA_DIR / "turkish_bible" / "tur-turkish.osis.xml"

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
# OSIS reference to bm_verses reference mapping
# ---------------------------------------------------------------------------

# OSIS book abbreviations -> bm_verses abbreviations
# Most are the same, but some differ
OSIS_TO_BM_BOOK = {
    "Gen": "Gen",
    "Exod": "Exod",
    "Lev": "Lev",
    "Num": "Num",
    "Deut": "Deut",
    "Josh": "Josh",
    "Judg": "Judg",
    "Ruth": "Ruth",
    "1Sam": "1Sam",
    "2Sam": "2Sam",
    "1Kgs": "1Kgs",
    "2Kgs": "2Kgs",
    "1Chr": "1Chr",
    "2Chr": "2Chr",
    "Ezra": "Ezra",
    "Neh": "Neh",
    "Esth": "Esth",
    "Job": "Job",
    "Ps": "Ps",
    "Prov": "Prov",
    "Eccl": "Eccl",
    "Song": "Song",
    "Isa": "Isa",
    "Jer": "Jer",
    "Lam": "Lam",
    "Ezek": "Ezek",
    "Dan": "Dan",
    "Hos": "Hos",
    "Joel": "Joel",
    "Amos": "Amos",
    "Obad": "Obad",
    "Jonah": "Jonah",
    "Mic": "Mic",
    "Nah": "Nah",
    "Hab": "Hab",
    "Zeph": "Zeph",
    "Hag": "Hag",
    "Zech": "Zech",
    "Mal": "Mal",
    # NT books
    "Matt": "Matt",
    "Mark": "Mark",
    "Luke": "Luke",
    "John": "John",
    "Acts": "Acts",
    "Rom": "Rom",
    "1Cor": "1Cor",
    "2Cor": "2Cor",
    "Gal": "Gal",
    "Eph": "Eph",
    "Phil": "Phil",
    "Col": "Col",
    "1Thess": "1Thess",
    "2Thess": "2Thess",
    "1Tim": "1Tim",
    "2Tim": "2Tim",
    "Titus": "Titus",
    "Phlm": "Phlm",
    "Heb": "Heb",
    "Jas": "Jas",
    "1Pet": "1Pet",
    "2Pet": "2Pet",
    "1John": "1John",
    "2John": "2John",
    "3John": "3John",
    "Jude": "Jude",
    "Rev": "Rev",
}


def osis_to_bm_reference(osis_id: str) -> str | None:
    """Convert OSIS reference to bm_verses reference format.

    Args:
        osis_id: OSIS reference like "Gen.1.1"

    Returns:
        bm_verses reference like "Gen 1:1" or None if invalid
    """
    parts = osis_id.split(".")
    if len(parts) < 3:
        return None

    book = parts[0]
    chapter = parts[1]
    verse = parts[2]

    # Map book abbreviation
    bm_book = OSIS_TO_BM_BOOK.get(book, book)

    return f"{bm_book} {chapter}:{verse}"


# ---------------------------------------------------------------------------
# OSIS XML parsing
# ---------------------------------------------------------------------------


def parse_turkish_bible(xml_path: Path) -> dict[str, str]:
    """Parse Turkish Bible OSIS XML into reference -> text mapping.

    Args:
        xml_path: Path to the OSIS XML file

    Returns:
        Dict mapping bm_verses reference -> Turkish text
    """
    if not xml_path.exists():
        log.error("Turkish Bible file not found: %s", xml_path)
        return {}

    log.info("Parsing Turkish Bible from %s", xml_path)

    tree = etree.parse(str(xml_path))
    root = tree.getroot()

    verses: dict[str, str] = {}
    book_count = 0
    verse_count = 0

    # Find all book divs
    for book_div in root.findall(".//osis:div[@type='book']", NS):
        book_div.get("osisID", "")
        book_count += 1

        # Find all verses in this book
        for verse_el in book_div.findall(".//osis:verse", NS):
            osis_id = verse_el.get("osisID", "")
            if not osis_id:
                continue

            # Get verse text
            text = verse_el.text or ""
            text = text.strip()

            if not text:
                continue

            # Convert to bm_verses reference format
            bm_ref = osis_to_bm_reference(osis_id)
            if bm_ref:
                verses[bm_ref] = text
                verse_count += 1

    log.info("Parsed %d books, %d verses from Turkish Bible", book_count, verse_count)
    return verses


# ---------------------------------------------------------------------------
# Database operations
# ---------------------------------------------------------------------------


def update_turkish_text(
    conn, turkish_verses: dict[str, str], dry_run: bool = False
) -> tuple[int, int]:
    """Update bm_verses.text_turkish for matching verses.

    Args:
        conn: SQLAlchemy connection
        turkish_verses: Dict mapping reference -> Turkish text
        dry_run: If True, don't actually update

    Returns:
        Tuple of (matched_count, not_found_count)
    """
    if not turkish_verses:
        log.warning("No Turkish verses to update")
        return 0, 0

    # Get all existing references from bm_verses
    result = conn.execute(text("SELECT reference FROM bm_verses"))
    existing_refs = {row[0] for row in result}
    log.info("Found %d existing verses in bm_verses", len(existing_refs))

    # Prepare updates
    updates: list[dict] = []
    not_found: list[str] = []

    for ref, turkish_text in turkish_verses.items():
        if ref in existing_refs:
            updates.append({"reference": ref, "text_turkish": turkish_text})
        else:
            not_found.append(ref)

    log.info(
        "Matched %d verses, %d not found in bm_verses", len(updates), len(not_found)
    )

    if not_found and len(not_found) <= 20:
        log.info("Not found references: %s", not_found[:20])

    if dry_run:
        log.info("DRY RUN: Would update %d verses", len(updates))
        return len(updates), len(not_found)

    # Batch update
    updated = 0
    for i in range(0, len(updates), BATCH_SIZE):
        batch = updates[i : i + BATCH_SIZE]
        for row in batch:
            conn.execute(
                text(
                    "UPDATE bm_verses SET text_turkish = :text_turkish "
                    "WHERE reference = :reference"
                ),
                row,
            )
        updated += len(batch)
        if updated % 5000 == 0:
            log.info("Updated %d verses...", updated)

    conn.commit()
    log.info("Updated %d verses with Turkish text", updated)

    return len(updates), len(not_found)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser(
        description="Load Turkish Bible text into bm_verses.text_turkish"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview without updating database",
    )
    args = parser.parse_args()

    log.info("=" * 60)
    log.info("Turkish Bible ETL Pipeline")
    log.info("=" * 60)

    # Parse Turkish Bible
    turkish_verses = parse_turkish_bible(TURKISH_BIBLE_FILE)

    if not turkish_verses:
        log.error("No verses parsed from Turkish Bible")
        sys.exit(1)

    # Connect to database
    engine = create_engine(DATABASE_URL)

    with engine.connect() as conn:
        # Check if bm_verses has data
        result = conn.execute(text("SELECT COUNT(*) FROM bm_verses"))
        verse_count = result.scalar()

        if verse_count == 0:
            log.error("bm_verses is empty. Run setup_bible_keyword.py first.")
            sys.exit(1)

        log.info("bm_verses has %d verses", verse_count)

        # Update Turkish text
        matched, not_found = update_turkish_text(conn, turkish_verses, args.dry_run)

    # Summary
    log.info("=" * 60)
    log.info("Turkish Bible ETL — SUMMARY")
    log.info("=" * 60)
    log.info("  Turkish verses parsed: %d", len(turkish_verses))
    log.info("  Matched in bm_verses:  %d", matched)
    log.info("  Not found:             %d", not_found)
    log.info("=" * 60)

    if not args.dry_run:
        # Verify
        with engine.connect() as conn:
            result = conn.execute(
                text("SELECT COUNT(*) FROM bm_verses WHERE text_turkish IS NOT NULL")
            )
            turkish_count = result.scalar()
            log.info("Verification: %d verses now have Turkish text", turkish_count)


if __name__ == "__main__":
    main()
