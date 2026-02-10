#!/usr/bin/env python3
"""ETL pipeline: Tanzil XML + QAC morphology TSV → PostgreSQL qm_* tables.

Reads:
  - backend/data/tanzil/quran-data.xml      (surah metadata, downloaded if missing)
  - backend/data/tanzil/quran-uthmani.xml   (Uthmani verse text, pre-downloaded)
  - backend/data/tanzil/quran-simple-clean.xml (Simple Clean verse text, pre-downloaded)
  - backend/data/quranic-corpus-morphology-0.4-ar-processed.txt (morphology TSV)

Populates:
  - qm_surahs  (114 rows)
  - qm_ayahs   (6,236 rows)
  - qm_words   (~77,430 rows)

Idempotent: truncates all qm_* tables before inserting.
"""

import logging
import re
import sys
import unicodedata
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.request import urlretrieve

sys.path.insert(0, str(Path(__file__).parent.parent))

from pyarabic import araby
from pyarabic.trans import utf82latin as _arabic_to_buckwalter
from sqlalchemy import create_engine, text

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

DATABASE_URL = "postgresql://postgres:postgres@localhost:54322/postgres"

DATA_DIR = Path(__file__).parent.parent / "data"
TANZIL_DIR = DATA_DIR / "tanzil"
TSV_FILE = DATA_DIR / "quranic-corpus-morphology-0.4-ar-processed.txt"

QURAN_DATA_URL = "https://tanzil.net/res/text/metadata/quran-data.xml"
QURAN_DATA_FILE = TANZIL_DIR / "quran-data.xml"
UTHMANI_FILE = TANZIL_DIR / "quran-uthmani.xml"
SIMPLE_CLEAN_FILE = TANZIL_DIR / "quran-simple-clean.xml"

BATCH_SIZE = 2000

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Arabic normalization (inline — will be extracted to module in Task 4)
# ---------------------------------------------------------------------------


def normalize_arabic(text_input: str) -> str:
    """Normalize Arabic text for search indexing.

    Steps:
      1. Strip tashkeel (diacritics/harakat)
      2. Normalize hamza variants → bare alef/waw/ya
      3. Ta-marbuta → ha
      4. Alef-maksura → ya
      5. Strip tatweel
      6. NFC normalization
    """
    result = araby.strip_tashkeel(text_input)
    # Hamza normalization
    result = result.replace("\u0623", "\u0627")  # أ → ا
    result = result.replace("\u0625", "\u0627")  # إ → ا
    result = result.replace("\u0622", "\u0627")  # آ → ا
    result = result.replace("\u0624", "\u0648")  # ؤ → و
    result = result.replace("\u0626", "\u064a")  # ئ → ي
    # Ta-marbuta → ha
    result = result.replace("\u0629", "\u0647")  # ة → ه
    # Alef-maksura → ya
    result = result.replace("\u0649", "\u064a")  # ى → ي
    # Strip tatweel
    result = result.replace("\u0640", "")
    # NFC normalization
    result = unicodedata.normalize("NFC", result)
    return result


def arabic_to_buckwalter(arabic_text: str) -> str | None:
    """Convert Arabic text to Buckwalter transliteration."""
    if not arabic_text:
        return None
    try:
        return _arabic_to_buckwalter(arabic_text)
    except Exception:
        return None


# ---------------------------------------------------------------------------
# File verification
# ---------------------------------------------------------------------------


def verify_files() -> bool:
    """Verify all required data files exist. Returns True if all present."""
    missing = []
    for path, label in [
        (UTHMANI_FILE, "Uthmani XML"),
        (SIMPLE_CLEAN_FILE, "Simple Clean XML"),
        (TSV_FILE, "Morphology TSV"),
    ]:
        if not path.exists():
            missing.append(f"  - {label}: {path}")

    if missing:
        log.error("Missing required data files:\n%s", "\n".join(missing))
        log.error(
            "Download Tanzil XML files from https://tanzil.net/download/ and place them in %s",
            TANZIL_DIR,
        )
        return False
    return True


def download_quran_data() -> bool:
    """Download quran-data.xml from Tanzil if not cached."""
    if QURAN_DATA_FILE.exists():
        log.info("quran-data.xml already cached at %s", QURAN_DATA_FILE)
        return True

    log.info("Downloading quran-data.xml from %s ...", QURAN_DATA_URL)
    try:
        TANZIL_DIR.mkdir(parents=True, exist_ok=True)
        urlretrieve(QURAN_DATA_URL, QURAN_DATA_FILE)
        log.info("Downloaded quran-data.xml (%d bytes)", QURAN_DATA_FILE.stat().st_size)
        return True
    except Exception as exc:
        log.error("Failed to download quran-data.xml: %s", exc)
        return False


# ---------------------------------------------------------------------------
# Parsers
# ---------------------------------------------------------------------------


def parse_surah_metadata() -> list[dict]:
    """Parse quran-data.xml → list of surah dicts."""
    tree = ET.parse(QURAN_DATA_FILE)
    root = tree.getroot()

    surahs: list[dict] = []
    for sura_el in root.iter("sura"):
        surahs.append(
            {
                "id": int(sura_el.attrib["index"]),
                "name_arabic": sura_el.attrib["name"],
                "name_translit": sura_el.attrib["tname"],
                "name_english": sura_el.attrib["ename"],
                "revelation_type": sura_el.attrib["type"],
                "total_verses": int(sura_el.attrib["ayas"]),
            }
        )

    log.info("Parsed %d surahs from quran-data.xml", len(surahs))
    return surahs


def parse_xml_verses(xml_path: Path) -> dict[tuple[int, int], str]:
    """Parse a Tanzil verse XML → {(surah_index, ayah_index): text}."""
    tree = ET.parse(xml_path)
    root = tree.getroot()

    verses: dict[tuple[int, int], str] = {}
    for sura_el in root.iter("sura"):
        surah_idx = int(sura_el.attrib["index"])
        for aya_el in sura_el.iter("aya"):
            ayah_idx = int(aya_el.attrib["index"])
            verses[(surah_idx, ayah_idx)] = aya_el.attrib["text"]

    log.info("Parsed %d verses from %s", len(verses), xml_path.name)
    return verses


def parse_tsv_words() -> list[dict]:
    """Parse morphology TSV → list of word dicts (one per word position).

    Sub-parts (word_index > 1) are aggregated into a single word entry:
      - token: concatenation of all sub-part forms
      - root: taken from the sub-part that has a ROOT (stem, not prefix)
      - lemma: taken from the sub-part that has a LEM (non-prefix)
      - pos_tag: taken from the main morpheme (first non-prefix sub-part with ROOT)
      - features: all sub-part features joined with " || "
      - word_index: number of sub-parts in this word

    Returns ~77,430 aggregated word entries.
    """
    # Intermediate: collect sub-parts grouped by (surah, ayah, position)
    # Key: (surah, ayah, position) → list of sub-part dicts (ordered by word_index)
    word_parts: dict[tuple[int, int, int], list[dict]] = {}
    skipped = 0
    line_count = 0

    re_root = re.compile(r"ROOT:([^|]+)")
    re_lem = re.compile(r"LEM:([^|]+)")

    with open(TSV_FILE, encoding="utf-8") as fh:
        for line_num, raw_line in enumerate(fh, start=1):
            line = raw_line.rstrip("\n\r")

            # Skip comments
            if line.startswith("#"):
                continue

            # Skip header
            if line.startswith("LOCATION"):
                continue

            # Skip empty lines
            if not line.strip():
                continue

            line_count += 1
            parts = line.split("\t")
            if len(parts) < 4:
                log.warning(
                    "Line %d: expected 4 TSV columns, got %d: %r",
                    line_num,
                    len(parts),
                    line,
                )
                skipped += 1
                continue

            location_str, form, tag, features = parts[0], parts[1], parts[2], parts[3]

            # Parse location: surah:ayah:word:part
            loc_parts = location_str.split(":")
            if len(loc_parts) != 4:
                log.warning("Line %d: bad location format: %r", line_num, location_str)
                skipped += 1
                continue

            try:
                surah = int(loc_parts[0])
                ayah = int(loc_parts[1])
                position = int(loc_parts[2])
                word_index = int(loc_parts[3])
            except ValueError:
                log.warning("Line %d: non-integer in location: %r", line_num, location_str)
                skipped += 1
                continue

            # Extract ROOT from features
            root_match = re_root.search(features)
            root_val = root_match.group(1) if root_match else None

            # Extract LEM from features
            lem_match = re_lem.search(features)
            lemma_val = lem_match.group(1) if lem_match else None

            key = (surah, ayah, position)
            if key not in word_parts:
                word_parts[key] = []

            word_parts[key].append(
                {
                    "word_index": word_index,
                    "form": form,
                    "tag": tag,
                    "features": features,
                    "root": root_val,
                    "lemma": lemma_val,
                }
            )

    # Aggregate sub-parts into single word entries
    words: list[dict] = []
    for (surah, ayah, position), sub_parts in sorted(word_parts.items()):
        # Sort sub-parts by word_index
        sub_parts.sort(key=lambda p: p["word_index"])

        # Concatenate all forms to build the full token
        token = "".join(p["form"] for p in sub_parts)

        # Find root: take from first sub-part that has a ROOT
        root_val = None
        for p in sub_parts:
            if p["root"]:
                root_val = p["root"]
                break

        # Find lemma: take from first sub-part that has a LEM and is not a prefix
        lemma_val = None
        for p in sub_parts:
            if p["lemma"] and p["tag"] != "P":
                lemma_val = p["lemma"]
                break
        # Fallback: take any lemma if all parts are prefixes
        if lemma_val is None:
            for p in sub_parts:
                if p["lemma"]:
                    lemma_val = p["lemma"]
                    break

        # POS tag: take from the main morpheme (first non-prefix part with ROOT, or first non-P)
        pos_tag = sub_parts[0]["tag"]  # default to first
        for p in sub_parts:
            if p["root"] and p["tag"] != "P":
                pos_tag = p["tag"]
                break
        else:
            # If no root-bearing non-prefix found, use first non-P tag
            for p in sub_parts:
                if p["tag"] != "P":
                    pos_tag = p["tag"]
                    break

        # Combine all features
        all_features = " || ".join(p["features"] for p in sub_parts)

        # Buckwalter transliteration of root
        root_bw = arabic_to_buckwalter(root_val) if root_val else None

        # Normalize token for search
        token_clean = normalize_arabic(token) if token else None

        words.append(
            {
                "surah": surah,
                "ayah": ayah,
                "position": position,
                "word_index": len(sub_parts),  # number of sub-parts
                "token": token,
                "token_clean": token_clean,
                "root": root_val,
                "root_buckwalter": root_bw,
                "lemma": lemma_val,
                "pos_tag": pos_tag,
                "features": all_features,
            }
        )

    log.info(
        "Parsed %d words from TSV (%d data lines, %d positions, %d skipped)",
        len(words),
        line_count,
        len(word_parts),
        skipped,
    )
    return words


# ---------------------------------------------------------------------------
# Database operations
# ---------------------------------------------------------------------------


def truncate_tables(conn) -> None:
    """Truncate qm_* tables in correct order (children first)."""
    conn.execute(text("TRUNCATE TABLE qm_words CASCADE"))
    conn.execute(text("TRUNCATE TABLE qm_ayahs CASCADE"))
    conn.execute(text("TRUNCATE TABLE qm_surahs CASCADE"))
    log.info("Truncated qm_words, qm_ayahs, qm_surahs")


def insert_surahs(conn, surahs: list[dict]) -> None:
    """Batch insert surahs."""
    conn.execute(
        text(
            "INSERT INTO qm_surahs (id, name_arabic, name_translit, name_english, "
            "revelation_type, total_verses) "
            "VALUES (:id, :name_arabic, :name_translit, :name_english, "
            ":revelation_type, :total_verses)"
        ),
        surahs,
    )
    log.info("Inserted %d surahs", len(surahs))


def insert_ayahs(
    conn,
    uthmani_verses: dict[tuple[int, int], str],
    clean_verses: dict[tuple[int, int], str],
) -> dict[tuple[int, int], int]:
    """Insert ayahs from merged Uthmani + Simple Clean XML.

    Returns mapping: (surah_id, ayah_number) → ayah_db_id
    """
    ayah_rows: list[dict] = []

    # Build sorted list of all (surah, ayah) keys from Uthmani
    all_keys = sorted(uthmani_verses.keys())

    for surah_id, ayah_num in all_keys:
        text_uthmani = uthmani_verses.get((surah_id, ayah_num), "")
        text_clean = clean_verses.get((surah_id, ayah_num), "")

        if not text_uthmani:
            log.warning("Missing Uthmani text for %d:%d", surah_id, ayah_num)
        if not text_clean:
            log.warning("Missing Simple Clean text for %d:%d", surah_id, ayah_num)

        ayah_rows.append(
            {
                "surah_id": surah_id,
                "ayah_number": ayah_num,
                "text_uthmani": text_uthmani,
                "text_clean": text_clean,
            }
        )

    # Batch insert
    for i in range(0, len(ayah_rows), BATCH_SIZE):
        batch = ayah_rows[i : i + BATCH_SIZE]
        conn.execute(
            text(
                "INSERT INTO qm_ayahs (surah_id, ayah_number, text_uthmani, text_clean) "
                "VALUES (:surah_id, :ayah_number, :text_uthmani, :text_clean)"
            ),
            batch,
        )

    log.info("Inserted %d ayahs", len(ayah_rows))

    # Build mapping: (surah_id, ayah_number) → db id
    result = conn.execute(text("SELECT id, surah_id, ayah_number FROM qm_ayahs ORDER BY id"))
    ayah_id_map: dict[tuple[int, int], int] = {}
    for row in result:
        ayah_id_map[(row[1], row[2])] = row[0]

    return ayah_id_map


def insert_words(
    conn,
    words: list[dict],
    ayah_id_map: dict[tuple[int, int], int],
) -> int:
    """Insert words with FK resolution. Returns count of inserted words."""
    word_rows: list[dict] = []
    orphan_count = 0

    for w in words:
        key = (w["surah"], w["ayah"])
        ayah_db_id = ayah_id_map.get(key)
        if ayah_db_id is None:
            orphan_count += 1
            if orphan_count <= 5:
                log.warning(
                    "No ayah_id for %d:%d (word position %d:%d)",
                    w["surah"],
                    w["ayah"],
                    w["position"],
                    w["word_index"],
                )
            continue

        word_rows.append(
            {
                "ayah_id": ayah_db_id,
                "position": w["position"],
                "word_index": w["word_index"],
                "token": w["token"],
                "token_clean": w["token_clean"],
                "root": w["root"],
                "root_buckwalter": w["root_buckwalter"],
                "lemma": w["lemma"],
                "pos_tag": w["pos_tag"],
                "features": w["features"],
            }
        )

    if orphan_count > 0:
        log.warning("Skipped %d words with no matching ayah", orphan_count)

    # Batch insert
    inserted = 0
    for i in range(0, len(word_rows), BATCH_SIZE):
        batch = word_rows[i : i + BATCH_SIZE]
        conn.execute(
            text(
                "INSERT INTO qm_words "
                "(ayah_id, position, word_index, token, token_clean, "
                "root, root_buckwalter, lemma, pos_tag, features) "
                "VALUES (:ayah_id, :position, :word_index, :token, :token_clean, "
                ":root, :root_buckwalter, :lemma, :pos_tag, :features)"
            ),
            batch,
        )
        inserted += len(batch)

    log.info("Inserted %d words", inserted)
    return inserted


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------


def validate_counts(conn) -> bool:
    """Run data integrity checks. Returns True if all pass."""
    checks_passed = True

    # Surah count
    result = conn.execute(text("SELECT COUNT(*) FROM qm_surahs"))
    surah_count = result.scalar()
    if surah_count != 114:
        log.error("❌ Expected 114 surahs, got %d", surah_count)
        checks_passed = False
    else:
        log.info("✅ Surahs: %d", surah_count)

    # Ayah count
    result = conn.execute(text("SELECT COUNT(*) FROM qm_ayahs"))
    ayah_count = result.scalar()
    if ayah_count != 6236:
        log.error("❌ Expected 6236 ayahs, got %d", ayah_count)
        checks_passed = False
    else:
        log.info("✅ Ayahs: %d", ayah_count)

    # Word count
    result = conn.execute(text("SELECT COUNT(*) FROM qm_words"))
    word_count = result.scalar()
    if abs(word_count - 77430) > 500:
        log.error("❌ Expected ~77430 words (±500), got %d", word_count)
        checks_passed = False
    else:
        log.info("✅ Words: %d", word_count)

    # Unique roots
    result = conn.execute(text("SELECT COUNT(DISTINCT root) FROM qm_words WHERE root IS NOT NULL"))
    root_count = result.scalar()
    log.info("📊 Unique roots: %d", root_count)

    # Unique lemmas
    result = conn.execute(text("SELECT COUNT(DISTINCT lemma) FROM qm_words WHERE lemma IS NOT NULL"))
    lemma_count = result.scalar()
    log.info("📊 Unique lemmas: %d", lemma_count)

    # Orphan check
    result = conn.execute(
        text("SELECT COUNT(*) FROM qm_words w LEFT JOIN qm_ayahs a ON w.ayah_id = a.id WHERE a.id IS NULL")
    )
    orphan_count = result.scalar()
    if orphan_count != 0:
        log.error("❌ Found %d orphaned words", orphan_count)
        checks_passed = False
    else:
        log.info("✅ No orphaned words")

    # NULL token check
    result = conn.execute(text("SELECT COUNT(*) FROM qm_words WHERE token IS NULL"))
    null_tokens = result.scalar()
    if null_tokens > 0:
        log.warning("⚠️  %d words with NULL token", null_tokens)

    return checks_passed


def print_summary(conn) -> None:
    """Print final summary with counts and sample data."""
    result = conn.execute(text("SELECT COUNT(*) FROM qm_surahs"))
    surah_count = result.scalar()
    result = conn.execute(text("SELECT COUNT(*) FROM qm_ayahs"))
    ayah_count = result.scalar()
    result = conn.execute(text("SELECT COUNT(*) FROM qm_words"))
    word_count = result.scalar()
    result = conn.execute(text("SELECT COUNT(DISTINCT root) FROM qm_words WHERE root IS NOT NULL"))
    root_count = result.scalar()
    result = conn.execute(text("SELECT COUNT(DISTINCT lemma) FROM qm_words WHERE lemma IS NOT NULL"))
    lemma_count = result.scalar()

    print("\n" + "=" * 60)
    print("  QURAN MORPHOLOGY ETL — SUMMARY")
    print("=" * 60)
    print(f"  Surahs:       {surah_count:>8,}")
    print(f"  Ayahs:        {ayah_count:>8,}")
    print(f"  Words:        {word_count:>8,}")
    print(f"  Unique roots: {root_count:>8,}")
    print(f"  Unique lemmas:{lemma_count:>8,}")
    print("=" * 60)

    # Sample: first surah
    result = conn.execute(
        text("SELECT id, name_arabic, name_translit, name_english, revelation_type FROM qm_surahs WHERE id = 1")
    )
    row = result.fetchone()
    if row:
        print(f"\n  Sample surah: {row[0]} | {row[1]} | {row[2]} | {row[3]} | {row[4]}")

    # Sample: first ayah
    result = conn.execute(
        text(
            "SELECT surah_id, ayah_number, LEFT(text_uthmani, 60), LEFT(text_clean, 60) "
            "FROM qm_ayahs WHERE surah_id = 1 AND ayah_number = 1"
        )
    )
    row = result.fetchone()
    if row:
        print(f"  Sample ayah:  {row[0]}:{row[1]} | U: {row[2]} | C: {row[3]}")

    # Sample: root كتب
    result = conn.execute(
        text("SELECT COUNT(*) FROM qm_words WHERE root = :root"),
        {"root": "\u0643\u062a\u0628"},  # كتب
    )
    ktb_count = result.scalar()
    print(f"  Root كتب:     {ktb_count} occurrences")

    print("=" * 60 + "\n")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> bool:
    """Run the full ETL pipeline. Returns True on success."""
    log.info("Starting Quran Morphology ETL pipeline")

    # 1. Verify files
    if not verify_files():
        return False

    # 2. Download quran-data.xml if needed
    if not download_quran_data():
        return False

    # 3. Parse all data sources
    log.info("Parsing data sources...")
    surahs = parse_surah_metadata()
    uthmani_verses = parse_xml_verses(UTHMANI_FILE)
    clean_verses = parse_xml_verses(SIMPLE_CLEAN_FILE)
    words = parse_tsv_words()

    # 4. Connect and populate
    engine = create_engine(DATABASE_URL, echo=False)
    try:
        with engine.begin() as conn:
            # 4a. Truncate
            truncate_tables(conn)

            # 4b. Insert surahs
            insert_surahs(conn, surahs)

            # 4c. Insert ayahs (returns ID mapping)
            ayah_id_map = insert_ayahs(conn, uthmani_verses, clean_verses)

            # 4d. Insert words
            insert_words(conn, words, ayah_id_map)

        # 5. Validate (separate transaction for read)
        with engine.connect() as conn:
            valid = validate_counts(conn)
            print_summary(conn)

        if not valid:
            log.error("❌ Validation failed — check warnings above")
            return False

        log.info("✅ ETL pipeline completed successfully")
        return True

    except Exception as exc:
        log.error("❌ ETL pipeline failed: %s", exc)
        import traceback

        traceback.print_exc()
        return False
    finally:
        engine.dispose()


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
