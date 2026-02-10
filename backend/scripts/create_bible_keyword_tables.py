"""Create Bible morphology tables (bm_books, bm_verses, bm_words, bm_strongs) with indexes.

Idempotent: drops existing bm_* tables and recreates them.
Uses synchronous psycopg2 connection (one-shot migration script).
"""

import sys
from pathlib import Path

# Ensure backend/ is on sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, text

# Import Base and models so metadata is populated
from app.db import Base
from app.models import (  # noqa: F401 — registers tables on Base.metadata
    BMBook,
    BMStrongs,
    BMVerse,
    BMVerseMapping,
    BMWord,
)

DATABASE_URL = "postgresql://postgres:postgres@localhost:54322/postgres"

BM_TABLES = [
    "bm_verse_mappings",
    "bm_words",
    "bm_verses",
    "bm_books",
    "bm_strongs",
]  # drop order (children first)

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
    "CREATE INDEX IF NOT EXISTS ix_bm_verse_mappings_mt ON bm_verse_mappings(mt_reference);",
    "CREATE INDEX IF NOT EXISTS ix_bm_verse_mappings_lxx ON bm_verse_mappings(lxx_reference);",
]


def main() -> bool:
    """Create Bible morphology tables and indexes. Returns True on success."""
    engine = create_engine(DATABASE_URL, echo=False)

    try:
        with engine.begin() as conn:
            # 1. Enable pg_trgm extension
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS pg_trgm"))
            print("✅ pg_trgm extension ensured")

            # 2. Drop existing bm_* tables (CASCADE) for idempotency
            for table_name in BM_TABLES:
                conn.execute(text(f"DROP TABLE IF EXISTS {table_name} CASCADE"))
            print("✅ Dropped existing bm_* tables (if any)")

        # 3. Create tables via SQLAlchemy metadata (filtered to bm_* only)
        bm_table_objects = [table for table in Base.metadata.sorted_tables if table.name.startswith("bm_")]
        Base.metadata.create_all(engine, tables=bm_table_objects)
        print("✅ Created bm_books, bm_verses, bm_words, bm_strongs, bm_verse_mappings tables")

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
                    "SELECT table_name FROM information_schema.tables WHERE table_name LIKE 'bm_%' ORDER BY table_name"
                )
            )
            tables = [row[0] for row in result]
            print(f"\n📋 Tables found: {tables}")

            if len(tables) != 5:
                print(f"❌ Expected 5 tables, found {len(tables)}")
                return False

            # Check indexes
            result = conn.execute(
                text("SELECT indexname FROM pg_indexes WHERE tablename LIKE 'bm_%' ORDER BY indexname")
            )
            indexes = [row[0] for row in result]
            print(f"📋 Indexes found ({len(indexes)}): {indexes}")

            if len(indexes) < 11:
                print(f"❌ Expected at least 11 indexes, found {len(indexes)}")
                return False

            # Verify GIN trigram indexes specifically
            result = conn.execute(
                text(
                    "SELECT indexname, indexdef FROM pg_indexes "
                    "WHERE indexdef LIKE '%gin_trgm_ops%' AND tablename LIKE 'bm_%'"
                )
            )
            gin_indexes = [(row[0], row[1]) for row in result]
            print(f"📋 GIN trigram indexes ({len(gin_indexes)}):")
            for name, _defn in gin_indexes:
                print(f"   - {name}")

        print("\n✅ Migration complete. All 5 bm_* tables and 11+ indexes created successfully.")
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
