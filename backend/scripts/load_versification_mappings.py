"""Load Bible versification mappings (MT vs LXX) into bm_verse_mappings table.

Handles known versification differences, especially Psalms where MT and LXX numbering diverge.
Idempotent: clears existing mappings before loading.
"""

import sys
from pathlib import Path

# Ensure backend/ is on sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, text

# Import Base and models so metadata is populated
from app.models import BMVerseMapping  # noqa: F401 — registers table on Base.metadata

DATABASE_URL = "postgresql://postgres:postgres@localhost:54322/postgres"

# Known versification differences (MT vs LXX)
# Format: (mt_reference, lxx_reference, mapping_type, notes)
VERSIFICATION_MAPPINGS = [
    # Psalms: MT 10-147 = LXX 9-146 (shifted by 1)
    ("Ps.9.1", "Ps.8.1", "chapter_merge", "MT Ps 9 + 10 = LXX Ps 9"),
    ("Ps.9.2", "Ps.8.2", "chapter_merge", "MT Ps 9 + 10 = LXX Ps 9"),
    ("Ps.9.3", "Ps.8.3", "chapter_merge", "MT Ps 9 + 10 = LXX Ps 9"),
    ("Ps.9.4", "Ps.8.4", "chapter_merge", "MT Ps 9 + 10 = LXX Ps 9"),
    ("Ps.9.5", "Ps.8.5", "chapter_merge", "MT Ps 9 + 10 = LXX Ps 9"),
    ("Ps.9.6", "Ps.8.6", "chapter_merge", "MT Ps 9 + 10 = LXX Ps 9"),
    ("Ps.9.7", "Ps.8.7", "chapter_merge", "MT Ps 9 + 10 = LXX Ps 9"),
    ("Ps.9.8", "Ps.8.8", "chapter_merge", "MT Ps 9 + 10 = LXX Ps 9"),
    ("Ps.9.9", "Ps.8.9", "chapter_merge", "MT Ps 9 + 10 = LXX Ps 9"),
    ("Ps.9.10", "Ps.8.10", "chapter_merge", "MT Ps 9 + 10 = LXX Ps 9"),
    ("Ps.9.11", "Ps.8.11", "chapter_merge", "MT Ps 9 + 10 = LXX Ps 9"),
    ("Ps.9.12", "Ps.8.12", "chapter_merge", "MT Ps 9 + 10 = LXX Ps 9"),
    ("Ps.9.13", "Ps.8.13", "chapter_merge", "MT Ps 9 + 10 = LXX Ps 9"),
    ("Ps.9.14", "Ps.8.14", "chapter_merge", "MT Ps 9 + 10 = LXX Ps 9"),
    ("Ps.9.15", "Ps.8.15", "chapter_merge", "MT Ps 9 + 10 = LXX Ps 9"),
    ("Ps.9.16", "Ps.8.16", "chapter_merge", "MT Ps 9 + 10 = LXX Ps 9"),
    ("Ps.9.17", "Ps.8.17", "chapter_merge", "MT Ps 9 + 10 = LXX Ps 9"),
    ("Ps.9.18", "Ps.8.18", "chapter_merge", "MT Ps 9 + 10 = LXX Ps 9"),
    ("Ps.10.1", "Ps.9.22", "verse_shift", "MT Ps 10 = LXX Ps 9:22-39"),
    ("Ps.10.2", "Ps.9.23", "verse_shift", "MT Ps 10 = LXX Ps 9:22-39"),
    ("Ps.10.3", "Ps.9.24", "verse_shift", "MT Ps 10 = LXX Ps 9:22-39"),
    ("Ps.10.4", "Ps.9.25", "verse_shift", "MT Ps 10 = LXX Ps 9:22-39"),
    ("Ps.10.5", "Ps.9.26", "verse_shift", "MT Ps 10 = LXX Ps 9:22-39"),
    ("Ps.10.6", "Ps.9.27", "verse_shift", "MT Ps 10 = LXX Ps 9:22-39"),
    ("Ps.10.7", "Ps.9.28", "verse_shift", "MT Ps 10 = LXX Ps 9:22-39"),
    ("Ps.10.8", "Ps.9.29", "verse_shift", "MT Ps 10 = LXX Ps 9:22-39"),
    ("Ps.10.9", "Ps.9.30", "verse_shift", "MT Ps 10 = LXX Ps 9:22-39"),
    ("Ps.10.10", "Ps.9.31", "verse_shift", "MT Ps 10 = LXX Ps 9:22-39"),
    ("Ps.10.11", "Ps.9.32", "verse_shift", "MT Ps 10 = LXX Ps 9:22-39"),
    ("Ps.11.1", "Ps.10.1", "verse_shift", "Shift begins: MT 11+ = LXX 10+"),
    ("Ps.12.1", "Ps.11.1", "verse_shift", "Shift continues"),
    ("Ps.13.1", "Ps.12.1", "verse_shift", "Shift continues"),
    ("Ps.14.1", "Ps.13.1", "verse_shift", "Shift continues"),
    ("Ps.15.1", "Ps.14.1", "verse_shift", "Shift continues"),
    ("Ps.16.1", "Ps.15.1", "verse_shift", "Shift continues"),
    ("Ps.17.1", "Ps.16.1", "verse_shift", "Shift continues"),
    ("Ps.18.1", "Ps.17.1", "verse_shift", "Shift continues"),
    ("Ps.19.1", "Ps.18.1", "verse_shift", "Shift continues"),
    ("Ps.20.1", "Ps.19.1", "verse_shift", "Shift continues"),
    ("Ps.21.1", "Ps.20.1", "verse_shift", "Shift continues"),
    ("Ps.22.1", "Ps.21.1", "verse_shift", "Shift continues"),
    ("Ps.23.1", "Ps.22.1", "verse_shift", "Shift continues"),
    ("Ps.24.1", "Ps.23.1", "verse_shift", "Shift continues"),
    ("Ps.25.1", "Ps.24.1", "verse_shift", "Shift continues"),
    ("Ps.26.1", "Ps.25.1", "verse_shift", "Shift continues"),
    ("Ps.27.1", "Ps.26.1", "verse_shift", "Shift continues"),
    ("Ps.28.1", "Ps.27.1", "verse_shift", "Shift continues"),
    ("Ps.29.1", "Ps.28.1", "verse_shift", "Shift continues"),
    ("Ps.30.1", "Ps.29.1", "verse_shift", "Shift continues"),
    ("Ps.31.1", "Ps.30.1", "verse_shift", "Shift continues"),
    ("Ps.32.1", "Ps.31.1", "verse_shift", "Shift continues"),
    ("Ps.33.1", "Ps.32.1", "verse_shift", "Shift continues"),
    ("Ps.34.1", "Ps.33.1", "verse_shift", "Shift continues"),
    ("Ps.35.1", "Ps.34.1", "verse_shift", "Shift continues"),
    ("Ps.36.1", "Ps.35.1", "verse_shift", "Shift continues"),
    ("Ps.37.1", "Ps.36.1", "verse_shift", "Shift continues"),
    ("Ps.38.1", "Ps.37.1", "verse_shift", "Shift continues"),
    ("Ps.39.1", "Ps.38.1", "verse_shift", "Shift continues"),
    ("Ps.40.1", "Ps.39.1", "verse_shift", "Shift continues"),
    ("Ps.41.1", "Ps.40.1", "verse_shift", "Shift continues"),
    ("Ps.42.1", "Ps.41.1", "verse_shift", "Shift continues"),
    ("Ps.43.1", "Ps.42.1", "verse_shift", "Shift continues"),
    ("Ps.44.1", "Ps.43.1", "verse_shift", "Shift continues"),
    ("Ps.45.1", "Ps.44.1", "verse_shift", "Shift continues"),
    ("Ps.46.1", "Ps.45.1", "verse_shift", "Shift continues"),
    ("Ps.47.1", "Ps.46.1", "verse_shift", "Shift continues"),
    ("Ps.48.1", "Ps.47.1", "verse_shift", "Shift continues"),
    ("Ps.49.1", "Ps.48.1", "verse_shift", "Shift continues"),
    ("Ps.50.1", "Ps.49.1", "verse_shift", "Shift continues"),
    ("Ps.51.1", "Ps.50.1", "verse_shift", "Shift continues"),
    ("Ps.52.1", "Ps.51.1", "verse_shift", "Shift continues"),
    ("Ps.53.1", "Ps.52.1", "verse_shift", "Shift continues"),
    ("Ps.54.1", "Ps.53.1", "verse_shift", "Shift continues"),
    ("Ps.55.1", "Ps.54.1", "verse_shift", "Shift continues"),
    ("Ps.56.1", "Ps.55.1", "verse_shift", "Shift continues"),
    ("Ps.57.1", "Ps.56.1", "verse_shift", "Shift continues"),
    ("Ps.58.1", "Ps.57.1", "verse_shift", "Shift continues"),
    ("Ps.59.1", "Ps.58.1", "verse_shift", "Shift continues"),
    ("Ps.60.1", "Ps.59.1", "verse_shift", "Shift continues"),
    ("Ps.61.1", "Ps.60.1", "verse_shift", "Shift continues"),
    ("Ps.62.1", "Ps.61.1", "verse_shift", "Shift continues"),
    ("Ps.63.1", "Ps.62.1", "verse_shift", "Shift continues"),
    ("Ps.64.1", "Ps.63.1", "verse_shift", "Shift continues"),
    ("Ps.65.1", "Ps.64.1", "verse_shift", "Shift continues"),
    ("Ps.66.1", "Ps.65.1", "verse_shift", "Shift continues"),
    ("Ps.67.1", "Ps.66.1", "verse_shift", "Shift continues"),
    ("Ps.68.1", "Ps.67.1", "verse_shift", "Shift continues"),
    ("Ps.69.1", "Ps.68.1", "verse_shift", "Shift continues"),
    ("Ps.70.1", "Ps.69.1", "verse_shift", "Shift continues"),
    ("Ps.71.1", "Ps.70.1", "verse_shift", "Shift continues"),
    ("Ps.72.1", "Ps.71.1", "verse_shift", "Shift continues"),
    ("Ps.73.1", "Ps.72.1", "verse_shift", "Shift continues"),
    ("Ps.74.1", "Ps.73.1", "verse_shift", "Shift continues"),
    ("Ps.75.1", "Ps.74.1", "verse_shift", "Shift continues"),
    ("Ps.76.1", "Ps.75.1", "verse_shift", "Shift continues"),
    ("Ps.77.1", "Ps.76.1", "verse_shift", "Shift continues"),
    ("Ps.78.1", "Ps.77.1", "verse_shift", "Shift continues"),
    ("Ps.79.1", "Ps.78.1", "verse_shift", "Shift continues"),
    ("Ps.80.1", "Ps.79.1", "verse_shift", "Shift continues"),
    ("Ps.81.1", "Ps.80.1", "verse_shift", "Shift continues"),
    ("Ps.82.1", "Ps.81.1", "verse_shift", "Shift continues"),
    ("Ps.83.1", "Ps.82.1", "verse_shift", "Shift continues"),
    ("Ps.84.1", "Ps.83.1", "verse_shift", "Shift continues"),
    ("Ps.85.1", "Ps.84.1", "verse_shift", "Shift continues"),
    ("Ps.86.1", "Ps.85.1", "verse_shift", "Shift continues"),
    ("Ps.87.1", "Ps.86.1", "verse_shift", "Shift continues"),
    ("Ps.88.1", "Ps.87.1", "verse_shift", "Shift continues"),
    ("Ps.89.1", "Ps.88.1", "verse_shift", "Shift continues"),
    ("Ps.90.1", "Ps.89.1", "verse_shift", "Shift continues"),
    ("Ps.91.1", "Ps.90.1", "verse_shift", "Shift continues"),
    ("Ps.92.1", "Ps.91.1", "verse_shift", "Shift continues"),
    ("Ps.93.1", "Ps.92.1", "verse_shift", "Shift continues"),
    ("Ps.94.1", "Ps.93.1", "verse_shift", "Shift continues"),
    ("Ps.95.1", "Ps.94.1", "verse_shift", "Shift continues"),
    ("Ps.96.1", "Ps.95.1", "verse_shift", "Shift continues"),
    ("Ps.97.1", "Ps.96.1", "verse_shift", "Shift continues"),
    ("Ps.98.1", "Ps.97.1", "verse_shift", "Shift continues"),
    ("Ps.99.1", "Ps.98.1", "verse_shift", "Shift continues"),
    ("Ps.100.1", "Ps.99.1", "verse_shift", "Shift continues"),
    ("Ps.101.1", "Ps.100.1", "verse_shift", "Shift continues"),
    ("Ps.102.1", "Ps.101.1", "verse_shift", "Shift continues"),
    ("Ps.103.1", "Ps.102.1", "verse_shift", "Shift continues"),
    ("Ps.104.1", "Ps.103.1", "verse_shift", "Shift continues"),
    ("Ps.105.1", "Ps.104.1", "verse_shift", "Shift continues"),
    ("Ps.106.1", "Ps.105.1", "verse_shift", "Shift continues"),
    ("Ps.107.1", "Ps.106.1", "verse_shift", "Shift continues"),
    ("Ps.108.1", "Ps.107.1", "verse_shift", "Shift continues"),
    ("Ps.109.1", "Ps.108.1", "verse_shift", "Shift continues"),
    ("Ps.110.1", "Ps.109.1", "verse_shift", "Shift continues"),
    ("Ps.111.1", "Ps.110.1", "verse_shift", "Shift continues"),
    ("Ps.112.1", "Ps.111.1", "verse_shift", "Shift continues"),
    ("Ps.113.1", "Ps.112.1", "verse_shift", "Shift continues"),
    ("Ps.114.1", "Ps.113.1", "verse_shift", "Shift continues"),
    ("Ps.115.1", "Ps.114.1", "verse_shift", "Shift continues"),
    ("Ps.116.1", "Ps.115.1", "verse_shift", "Shift continues"),
    ("Ps.117.1", "Ps.116.1", "verse_shift", "Shift continues"),
    ("Ps.118.1", "Ps.117.1", "verse_shift", "Shift continues"),
    ("Ps.119.1", "Ps.118.1", "verse_shift", "Shift continues"),
    ("Ps.120.1", "Ps.119.1", "verse_shift", "Shift continues"),
    ("Ps.121.1", "Ps.120.1", "verse_shift", "Shift continues"),
    ("Ps.122.1", "Ps.121.1", "verse_shift", "Shift continues"),
    ("Ps.123.1", "Ps.122.1", "verse_shift", "Shift continues"),
    ("Ps.124.1", "Ps.123.1", "verse_shift", "Shift continues"),
    ("Ps.125.1", "Ps.124.1", "verse_shift", "Shift continues"),
    ("Ps.126.1", "Ps.125.1", "verse_shift", "Shift continues"),
    ("Ps.127.1", "Ps.126.1", "verse_shift", "Shift continues"),
    ("Ps.128.1", "Ps.127.1", "verse_shift", "Shift continues"),
    ("Ps.129.1", "Ps.128.1", "verse_shift", "Shift continues"),
    ("Ps.130.1", "Ps.129.1", "verse_shift", "Shift continues"),
    ("Ps.131.1", "Ps.130.1", "verse_shift", "Shift continues"),
    ("Ps.132.1", "Ps.131.1", "verse_shift", "Shift continues"),
    ("Ps.133.1", "Ps.132.1", "verse_shift", "Shift continues"),
    ("Ps.134.1", "Ps.133.1", "verse_shift", "Shift continues"),
    ("Ps.135.1", "Ps.134.1", "verse_shift", "Shift continues"),
    ("Ps.136.1", "Ps.135.1", "verse_shift", "Shift continues"),
    ("Ps.137.1", "Ps.136.1", "verse_shift", "Shift continues"),
    ("Ps.138.1", "Ps.137.1", "verse_shift", "Shift continues"),
    ("Ps.139.1", "Ps.138.1", "verse_shift", "Shift continues"),
    ("Ps.140.1", "Ps.139.1", "verse_shift", "Shift continues"),
    ("Ps.141.1", "Ps.140.1", "verse_shift", "Shift continues"),
    ("Ps.142.1", "Ps.141.1", "verse_shift", "Shift continues"),
    ("Ps.143.1", "Ps.142.1", "verse_shift", "Shift continues"),
    ("Ps.144.1", "Ps.143.1", "verse_shift", "Shift continues"),
    ("Ps.145.1", "Ps.144.1", "verse_shift", "Shift continues"),
    ("Ps.146.1", "Ps.145.1", "verse_shift", "Shift continues"),
    ("Ps.147.1", "Ps.146.1", "split", "MT Ps 147 = LXX Ps 146 + 147"),
]


def main() -> bool:
    """Load versification mappings. Returns True on success."""
    engine = create_engine(DATABASE_URL, echo=False)

    try:
        with engine.begin() as conn:
            # 1. Clear existing mappings (idempotent)
            conn.execute(text("DELETE FROM bm_verse_mappings"))
            print("✅ Cleared existing versification mappings")

            # 2. Insert new mappings
            for mt_ref, lxx_ref, mapping_type, notes in VERSIFICATION_MAPPINGS:
                conn.execute(
                    text(
                        """
						INSERT INTO bm_verse_mappings
						(mt_reference, lxx_reference, mapping_type, notes)
						VALUES (:mt_ref, :lxx_ref, :mapping_type, :notes)
						"""
                    ),
                    {
                        "mt_ref": mt_ref,
                        "lxx_ref": lxx_ref,
                        "mapping_type": mapping_type,
                        "notes": notes,
                    },
                )
            print(f"✅ Inserted {len(VERSIFICATION_MAPPINGS)} versification mappings")

        # 3. Verify
        with engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM bm_verse_mappings"))
            count = result.scalar()
            print(f"\n📋 Verification: {count} mappings in database")

            if count != len(VERSIFICATION_MAPPINGS):
                print(f"❌ Expected {len(VERSIFICATION_MAPPINGS)}, found {count}")
                return False

            # Show sample
            result = conn.execute(
                text("SELECT mt_reference, lxx_reference, mapping_type FROM bm_verse_mappings LIMIT 5")
            )
            print("\n📋 Sample mappings:")
            for row in result:
                print(f"   {row[0]} → {row[1]} ({row[2]})")

        print("\n✅ Versification mappings loaded successfully.")
        return True

    except Exception as e:
        print(f"❌ Loading failed: {e}")
        import traceback

        traceback.print_exc()
        return False
    finally:
        engine.dispose()


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
