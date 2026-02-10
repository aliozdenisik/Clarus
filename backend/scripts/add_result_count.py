"""Add result_count column to search_history table."""

# ruff: noqa: E402
# This migration script adjusts sys.path before importing project modules.

import asyncio
import os
import sys
from pathlib import Path

# Ensure backend/ is on sys.path (project convention from compare.py:22-24)
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv

load_dotenv(os.path.join(Path(__file__).parent.parent, ".env"))

from sqlalchemy import text

from app.db import engine


async def migrate() -> bool:
    """Returns True on success, False on failure."""
    async with engine.begin() as conn:
        # 1. Verify table exists
        table_check = await conn.execute(
            text("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name='search_history')")
        )
        if not table_check.scalar():
            print("❌ ERROR: search_history table does not exist. Run init_db() first.")
            return False

        # 2. Check if column already exists (idempotent)
        result = await conn.execute(
            text(
                "SELECT column_name FROM information_schema.columns "
                "WHERE table_name='search_history' AND column_name='result_count'"
            )
        )
        if result.fetchone() is not None:
            print("ℹ️  result_count column already exists, skipping")
            return True

        # 3. Add column
        try:
            await conn.execute(text("ALTER TABLE search_history ADD COLUMN result_count INTEGER"))
            print("✅ Added result_count column to search_history")
            return True
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            return False


if __name__ == "__main__":
    success = asyncio.run(migrate())
    sys.exit(0 if success else 1)
