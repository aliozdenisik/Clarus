#!/usr/bin/env python3
"""Import Lane's Lexicon data from SQLite into PostgreSQL."""

from __future__ import annotations

import argparse
import os
import sqlite3
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv(Path(__file__).parent.parent / ".env")

DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://postgres:postgres@localhost:54322/postgres")


def normalize_sqlalchemy_dsn(db_url: str) -> str:
    return db_url.replace("postgresql+asyncpg://", "postgresql://")


def import_lane_data(sqlite_path: Path, db_url: str, batch_size: int) -> tuple[int, int]:
    if not sqlite_path.exists():
        raise FileNotFoundError(f"SQLite file not found: {sqlite_path}")

    sqlite_conn = sqlite3.connect(str(sqlite_path))
    sqlite_conn.row_factory = sqlite3.Row

    engine = create_engine(normalize_sqlalchemy_dsn(db_url), future=True)

    entry_insert = text(
        """
        INSERT INTO lane_entries (id, root, broot, word, bword, xml, page, headword, itype)
        VALUES (:id, :root, :broot, :word, :bword, :xml, :page, :headword, :itype)
        """
    )
    root_insert = text(
        """
        INSERT INTO lane_roots (id, word, bword, letter, bletter, page)
        VALUES (:id, :word, :bword, :letter, :bletter, :page)
        """
    )

    entry_count = 0
    root_count = 0

    try:
        with engine.begin() as conn:
            conn.execute(text("TRUNCATE TABLE lane_entries, lane_roots"))

            entry_cursor = sqlite_conn.execute(
                """
                SELECT id, root, broot, word, bword, xml, page, headword, itype
                FROM entry
                ORDER BY id
                """
            )
            while True:
                rows = entry_cursor.fetchmany(batch_size)
                if not rows:
                    break

                payload = [
                    {
                        "id": row["id"],
                        "root": row["root"],
                        "broot": row["broot"],
                        "word": row["word"],
                        "bword": row["bword"],
                        "xml": row["xml"],
                        "page": row["page"],
                        "headword": row["headword"],
                        "itype": row["itype"],
                    }
                    for row in rows
                ]
                conn.execute(entry_insert, payload)
                entry_count += len(payload)

            root_cursor = sqlite_conn.execute(
                """
                SELECT id, word, bword, letter, bletter, page
                FROM root
                ORDER BY id
                """
            )
            while True:
                rows = root_cursor.fetchmany(batch_size)
                if not rows:
                    break

                payload = [
                    {
                        "id": row["id"],
                        "word": row["word"],
                        "bword": row["bword"],
                        "letter": row["letter"],
                        "bletter": row["bletter"],
                        "page": row["page"],
                    }
                    for row in rows
                ]
                conn.execute(root_insert, payload)
                root_count += len(payload)
    finally:
        sqlite_conn.close()
        engine.dispose()

    return entry_count, root_count


def main() -> int:
    parser = argparse.ArgumentParser(description="Import Lane Lexicon SQLite data into PostgreSQL")
    parser.add_argument(
        "--sqlite-path",
        type=Path,
        default=Path("data/lane_lexicon/lexicon.sqlite"),
        help="Path to lane SQLite file",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=2000,
        help="Batch size for insert operations",
    )
    args = parser.parse_args()

    entries, roots = import_lane_data(args.sqlite_path, DATABASE_URL, args.batch_size)
    print("Lane import complete")
    print(f"  lane_entries inserted: {entries}")
    print(f"  lane_roots inserted:   {roots}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
