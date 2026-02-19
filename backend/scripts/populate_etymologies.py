#!/usr/bin/env python3
"""ETL pipeline: Quranic Corpus + Lane's Lexicon -> qm_root_etymologies table.

Data Sources:
  - Quranic Arabic Corpus v0.4 (University of Leeds, GNU GPL)
    Citation: Dukes & Habash, "Morphological Annotation of Quranic Arabic", LREC 2010
  - Lane's Arabic-English Lexicon SQLite (Perseus/Tufts University, GPL-3.0)
    Original: Edward William Lane, 1863
  - Note: Derived etymology data is GPL-licensed due to source licenses

Usage:
  uv run python scripts/populate_etymologies.py
  uv run python scripts/populate_etymologies.py --dry-run
  uv run python scripts/populate_etymologies.py --corpus-only
"""

from __future__ import annotations

import argparse
import logging
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv

from src.etymology_pipeline import EtymologyPipeline

load_dotenv(Path(__file__).parent.parent / ".env")

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:54322/postgres",
)


def main() -> int:
    """Parse CLI arguments and run etymology ETL."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S",
    )

    parser = argparse.ArgumentParser(description="Populate qm_root_etymologies table")
    parser.add_argument(
        "--lane-db",
        type=Path,
        default=None,
        help="Path to Lane's Lexicon SQLite (fallback if PostgreSQL lane_entries is empty)",
    )
    parser.add_argument("--dry-run", action="store_true", help="Run without inserting")
    parser.add_argument("--corpus-only", action="store_true", help="Skip Lane matching")
    parser.add_argument(
        "--skip-translation", action="store_true", help="Skip Turkish translation (populate definition_en only)"
    )
    parser.add_argument(
        "--allow-translation-regression",
        action="store_true",
        help="Allow write even when Turkish translation/summary coverage would decrease",
    )
    parser.add_argument("--batch-size", type=int, default=100, help="Insert batch size")
    args = parser.parse_args()

    use_lane = not args.corpus_only
    lane_path = args.lane_db if use_lane else None
    api_key = os.environ.get("OPENROUTER_API_KEY") if use_lane else None

    pipeline = EtymologyPipeline(
        db_url=DATABASE_URL,
        lane_db_path=lane_path,
        openrouter_api_key=api_key,
        batch_size=args.batch_size,
        dry_run=args.dry_run,
        use_lane=use_lane,
        skip_translation=args.skip_translation,
        allow_translation_regression=args.allow_translation_regression,
    )
    result = pipeline.run()

    print("\n═══ Pipeline Summary ═══")
    print(f"Total roots: {result.total_roots}")
    print(f"Inserted rows: {result.inserted_rows}")
    print(f"Lane matches: {result.lane_matches}")
    print(f"Corpus-only: {result.corpus_only}")
    print(f"Turkish translations: {result.turkish_translations}")

    return 0 if result.success else 1


if __name__ == "__main__":
    raise SystemExit(main())
