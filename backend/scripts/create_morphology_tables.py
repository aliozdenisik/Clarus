"""Create Quran morphology tables (qm_surahs, qm_ayahs, qm_words) with indexes.

Idempotent: drops existing qm_* tables and recreates them.
Uses synchronous psycopg2 connection (one-shot migration script).
"""

import sys
from pathlib import Path

# Ensure backend/ is on sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, text

# Import Base and models so metadata is populated
from app.db import Base
from app.models import QMAyah, QMSurah, QMWord  # noqa: F401 — registers tables on Base.metadata

DATABASE_URL = "postgresql://postgres:postgres@localhost:54322/postgres"

QM_TABLES = ["qm_words", "qm_ayahs", "qm_surahs"]  # drop order (children first)

INDEXES_SQL = [
    "CREATE INDEX IF NOT EXISTS ix_qm_words_root ON qm_words(root);",
    "CREATE INDEX IF NOT EXISTS ix_qm_words_root_bw ON qm_words(root_buckwalter);",
    "CREATE INDEX IF NOT EXISTS ix_qm_words_root_bw_trgm ON qm_words USING gin(root_buckwalter gin_trgm_ops);",
    "CREATE INDEX IF NOT EXISTS ix_qm_words_lemma ON qm_words(lemma);",
    "CREATE INDEX IF NOT EXISTS ix_qm_words_token_clean_trgm ON qm_words USING gin(token_clean gin_trgm_ops);",
    "CREATE INDEX IF NOT EXISTS ix_qm_words_ayah_id ON qm_words(ayah_id);",
    "CREATE INDEX IF NOT EXISTS ix_qm_ayahs_surah_id ON qm_ayahs(surah_id);",
]


def main() -> bool:
    """Create morphology tables and indexes. Returns True on success."""
    engine = create_engine(DATABASE_URL, echo=False)

    try:
        with engine.begin() as conn:
            # 1. Enable pg_trgm extension
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS pg_trgm"))
            print("✅ pg_trgm extension ensured")

            # 2. Drop existing qm_* tables (CASCADE) for idempotency
            for table_name in QM_TABLES:
                conn.execute(text(f"DROP TABLE IF EXISTS {table_name} CASCADE"))
            print("✅ Dropped existing qm_* tables (if any)")

        # 3. Create tables via SQLAlchemy metadata (filtered to qm_* only)
        qm_table_objects = [table for table in Base.metadata.sorted_tables if table.name.startswith("qm_")]
        Base.metadata.create_all(engine, tables=qm_table_objects)
        print("✅ Created qm_surahs, qm_ayahs, qm_words tables")

        # 4. Create indexes explicitly
        with engine.begin() as conn:
            for idx_sql in INDEXES_SQL:
                conn.execute(text(idx_sql))
            print(f"✅ Created {len(INDEXES_SQL)} indexes (B-tree + GIN trigram)")

        # 5. Validate
        with engine.connect() as conn:
            # Check tables exist
            result = conn.execute(
                text(
                    "SELECT table_name FROM information_schema.tables WHERE table_name LIKE 'qm_%' ORDER BY table_name"
                )
            )
            tables = [row[0] for row in result]
            print(f"\n📋 Tables found: {tables}")

            if len(tables) != 3:
                print(f"❌ Expected 3 tables, found {len(tables)}")
                return False

            # Check indexes
            result = conn.execute(
                text("SELECT indexname FROM pg_indexes WHERE tablename LIKE 'qm_%' ORDER BY indexname")
            )
            indexes = [row[0] for row in result]
            print(f"📋 Indexes found ({len(indexes)}): {indexes}")

            # Verify GIN trigram indexes specifically
            result = conn.execute(
                text(
                    "SELECT indexname, indexdef FROM pg_indexes "
                    "WHERE indexdef LIKE '%gin_trgm_ops%' AND tablename LIKE 'qm_%'"
                )
            )
            gin_indexes = [(row[0], row[1]) for row in result]
            print(f"📋 GIN trigram indexes ({len(gin_indexes)}):")
            for name, _defn in gin_indexes:
                print(f"   - {name}")

        print("\n✅ Migration complete. All 3 qm_* tables and indexes created successfully.")
        return True

    except Exception as e:
        print(f"❌ Migration failed: {e}")
        import traceback

        traceback.print_exc()
        return False
    finally:
        engine.dispose()


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
