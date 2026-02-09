"""Load Strong's Concordance data from JSON files into PostgreSQL bm_strongs table.

Reads:
  - backend/data/strongs/strongs_hebrew.json  (8,427 entries)
  - backend/data/strongs/strongs_greek.json   (5,523 entries)

Populates:
  - bm_strongs (13,950 rows total)

Idempotent: truncates bm_strongs before inserting.
"""

import json
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, text

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

DATABASE_URL = "postgresql://postgres:postgres@localhost:54322/postgres"

DATA_DIR = Path(__file__).parent.parent / "data"
STRONGS_DIR = DATA_DIR / "strongs"
HEBREW_FILE = STRONGS_DIR / "strongs_hebrew.json"
GREEK_FILE = STRONGS_DIR / "strongs_greek.json"

BATCH_SIZE = 1000

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------


def load_strongs_data() -> list[dict]:
    """Load Strong's Hebrew and Greek concordance data from JSON files.

    Returns list of dicts with keys:
      - number (PK): "H1", "H8674", "G1", "G5523", etc.
      - original_word: lemma from JSON
      - transliteration: xlit (Hebrew) or translit (Greek)
      - definition: strongs_def from JSON
      - language: "hebrew" or "greek"
    """
    entries: list[dict] = []

    # Load Hebrew
    log.info("Loading Hebrew Strong's data...")
    with open(HEBREW_FILE, "r", encoding="utf-8") as f:
        hebrew_data = json.load(f)

    for number, entry in hebrew_data.items():
        entries.append(
            {
                "number": number,
                "original_word": entry.get("lemma", ""),
                "transliteration": entry.get("xlit", ""),
                "definition": entry.get("strongs_def", ""),
                "language": "hebrew",
            }
        )

    log.info("Loaded %d Hebrew entries", len(hebrew_data))

    # Load Greek
    log.info("Loading Greek Strong's data...")
    with open(GREEK_FILE, "r", encoding="utf-8") as f:
        greek_data = json.load(f)

    for number, entry in greek_data.items():
        entries.append(
            {
                "number": number,
                "original_word": entry.get("lemma", ""),
                "transliteration": entry.get("translit", ""),  # Note: Greek uses "translit"
                "definition": entry.get("strongs_def", ""),
                "language": "greek",
            }
        )

    log.info("Loaded %d Greek entries", len(greek_data))
    log.info("Total entries: %d", len(entries))

    return entries


# ---------------------------------------------------------------------------
# Database operations
# ---------------------------------------------------------------------------


def truncate_table(conn) -> None:
    """Truncate bm_strongs table."""
    conn.execute(text("TRUNCATE TABLE bm_strongs"))
    log.info("Truncated bm_strongs")


def insert_strongs(conn, entries: list[dict]) -> int:
    """Batch insert Strong's entries. Returns count of inserted rows."""
    inserted = 0

    for i in range(0, len(entries), BATCH_SIZE):
        batch = entries[i : i + BATCH_SIZE]
        conn.execute(
            text(
                "INSERT INTO bm_strongs "
                "(number, original_word, transliteration, definition, language) "
                "VALUES (:number, :original_word, :transliteration, :definition, :language)"
            ),
            batch,
        )
        inserted += len(batch)
        log.info("  Inserted batch: %d-%d (total: %d)", i, i + len(batch), inserted)

    log.info("Inserted %d Strong's entries total", inserted)
    return inserted


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------


def validate_counts(conn) -> bool:
    """Run data integrity checks. Returns True if all pass."""
    checks_passed = True

    # Total count (actual data: 8,427 Hebrew + 5,523 Greek = 13,950)
    result = conn.execute(text("SELECT COUNT(*) FROM bm_strongs"))
    total_count = result.scalar()
    if total_count != 13950:
        log.error("❌ Expected 13,950 entries, got %d", total_count)
        checks_passed = False
    else:
        log.info("✅ Total entries: %d", total_count)

    # Hebrew count
    result = conn.execute(text("SELECT COUNT(*) FROM bm_strongs WHERE language = 'hebrew'"))
    hebrew_count = result.scalar()
    if hebrew_count != 8427:
        log.error("❌ Expected 8,427 Hebrew entries, got %d", hebrew_count)
        checks_passed = False
    else:
        log.info("✅ Hebrew entries: %d", hebrew_count)

    # Greek count
    result = conn.execute(text("SELECT COUNT(*) FROM bm_strongs WHERE language = 'greek'"))
    greek_count = result.scalar()
    if greek_count != 5523:
        log.error("❌ Expected 5,523 Greek entries, got %d", greek_count)
        checks_passed = False
    else:
        log.info("✅ Greek entries: %d", greek_count)

    # Sample: H7225 (Reshith - "beginning")
    result = conn.execute(
        text(
            "SELECT number, original_word, transliteration, definition, language "
            "FROM bm_strongs WHERE number = 'H7225'"
        )
    )
    row = result.fetchone()
    if row:
        log.info(
            "✅ Sample H7225: %s | %s | %s | %s | %s",
            row[0],
            row[1],
            row[2],
            row[3][:50],
            row[4],
        )
    else:
        log.error("❌ H7225 not found in bm_strongs")
        checks_passed = False

    # Sample: G26 (Agape - "love")
    result = conn.execute(
        text(
            "SELECT number, original_word, transliteration, definition, language "
            "FROM bm_strongs WHERE number = 'G26'"
        )
    )
    row = result.fetchone()
    if row:
        log.info(
            "✅ Sample G26: %s | %s | %s | %s | %s",
            row[0],
            row[1],
            row[2],
            row[3][:50],
            row[4],
        )
    else:
        log.warning("⚠️  G26 not found in bm_strongs (may not exist in data)")

    log.info("=" * 60)
    return checks_passed


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> bool:
    """Run the Strong's Concordance loader. Returns True on success."""
    log.info("Starting Strong's Concordance loader")

    # 1. Load data
    entries = load_strongs_data()

    # 2. Connect and populate
    engine = create_engine(DATABASE_URL, echo=False)
    try:
        with engine.begin() as conn:
            # 2a. Truncate
            truncate_table(conn)

            # 2b. Insert
            insert_strongs(conn, entries)

        # 3. Validate (separate transaction for read)
        with engine.connect() as conn:
            valid = validate_counts(conn)

        if valid:
            log.info("✅ Strong's Concordance loader completed successfully")
            return True
        else:
            log.error("❌ Validation failed")
            return False

    except Exception as e:
        log.error("❌ Error: %s", e, exc_info=True)
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
