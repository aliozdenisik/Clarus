#!/usr/bin/env python3
"""Export qm_root_etymologies table to JSON and XML formats.

Usage:
  uv run python scripts/export_etymologies.py
  uv run python scripts/export_etymologies.py --format json
  uv run python scripts/export_etymologies.py --format xml
  uv run python scripts/export_etymologies.py --format both
"""

import argparse
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

from sqlalchemy import create_engine, text

sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:54322/postgres",
).replace("postgresql+asyncpg://", "postgresql://")

logger = logging.getLogger(__name__)


def export_to_json(data: list[dict[str, Any]], output_path: Path) -> None:
    """Export etymology data to JSON format."""
    export_data = {
        "metadata": {
            "export_date": datetime.now().isoformat(),
            "total_roots": len(data),
            "version": "1.0",
            "source": "qm_root_etymologies",
            "statistics": {
                "has_definition_en": sum(1 for r in data if r.get("definition_en")),
                "has_definition_tr": sum(1 for r in data if r.get("definition_tr")),
                "has_summary_tr": sum(1 for r in data if r.get("summary_tr")),
                "has_summary_en": sum(1 for r in data if r.get("summary_en")),
                "lane_matches": sum(1 for r in data if r.get("source") == "lane"),
                "corpus_only": sum(1 for r in data if r.get("source") == "corpus_only"),
            },
        },
        "roots": data,
    }

    with output_path.open("w", encoding="utf-8") as f:
        json.dump(export_data, f, ensure_ascii=False, indent=2)

    logger.info(f"✅ JSON export complete: {output_path} ({output_path.stat().st_size / 1024 / 1024:.2f} MB)")


def export_to_xml(data: list[dict[str, Any]], output_path: Path) -> None:
    """Export etymology data to XML format."""
    from xml.dom import minidom
    from xml.etree import ElementTree as ET

    Element = ET.Element
    SubElement = ET.SubElement

    root = Element("etymology_database")

    metadata = SubElement(root, "metadata")
    SubElement(metadata, "export_date").text = datetime.now().isoformat()
    SubElement(metadata, "total_roots").text = str(len(data))
    SubElement(metadata, "version").text = "1.0"
    SubElement(metadata, "source").text = "qm_root_etymologies"

    statistics = SubElement(metadata, "statistics")
    SubElement(statistics, "has_definition_en").text = str(sum(1 for r in data if r.get("definition_en")))
    SubElement(statistics, "has_definition_tr").text = str(sum(1 for r in data if r.get("definition_tr")))
    SubElement(statistics, "has_summary_tr").text = str(sum(1 for r in data if r.get("summary_tr")))
    SubElement(statistics, "has_summary_en").text = str(sum(1 for r in data if r.get("summary_en")))
    SubElement(statistics, "lane_matches").text = str(sum(1 for r in data if r.get("source") == "lane"))
    SubElement(statistics, "corpus_only").text = str(sum(1 for r in data if r.get("source") == "corpus_only"))

    roots_elem = SubElement(root, "roots")

    for root_data in data:
        root_elem = SubElement(roots_elem, "root")
        SubElement(root_elem, "id").text = str(root_data.get("id", ""))

        SubElement(root_elem, "root_arabic").text = root_data.get("root", "")
        SubElement(root_elem, "root_buckwalter").text = root_data.get("root_buckwalter", "")

        SubElement(root_elem, "definition_en").text = root_data.get("definition_en") or ""
        SubElement(root_elem, "definition_tr").text = root_data.get("definition_tr") or ""

        SubElement(root_elem, "summary_tr").text = root_data.get("summary_tr") or ""
        SubElement(root_elem, "summary_en").text = root_data.get("summary_en") or ""

        SubElement(root_elem, "semantic_field").text = root_data.get("semantic_field") or ""
        SubElement(root_elem, "quran_frequency").text = str(root_data.get("quran_frequency", 0))

        SubElement(root_elem, "source").text = root_data.get("source", "")
        SubElement(root_elem, "lane_match_type").text = root_data.get("lane_match_type") or ""
        SubElement(root_elem, "lane_volume").text = str(root_data.get("lane_volume") or "")
        SubElement(root_elem, "confidence").text = root_data.get("confidence") or ""

        SubElement(root_elem, "tr_translation_source").text = root_data.get("tr_translation_source") or ""
        SubElement(root_elem, "tr_translation_confidence").text = str(root_data.get("tr_translation_confidence") or "")

        if root_data.get("morphological_forms"):
            forms_elem = SubElement(root_elem, "morphological_forms")
            for form in root_data["morphological_forms"]:
                form_elem = SubElement(forms_elem, "form")
                SubElement(form_elem, "pattern").text = form.get("form_pattern", "")
                SubElement(form_elem, "arabic").text = form.get("form_arabic", "")
                SubElement(form_elem, "name").text = form.get("form_name", "")
                SubElement(form_elem, "category").text = form.get("form_category", "")
                SubElement(form_elem, "example").text = form.get("example_word", "")
                SubElement(form_elem, "occurrences").text = str(form.get("occurrences", 0))

        SubElement(root_elem, "created_at").text = str(root_data.get("created_at", ""))
        SubElement(root_elem, "updated_at").text = str(root_data.get("updated_at", ""))

    xml_str = minidom.parseString(ET.tostring(root, encoding="utf-8")).toprettyxml(indent="  ")  # noqa: S318 — self-generated XML, not untrusted input

    with output_path.open("w", encoding="utf-8") as f:
        f.write(xml_str)

    logger.info(f"✅ XML export complete: {output_path} ({output_path.stat().st_size / 1024 / 1024:.2f} MB)")


def main() -> int:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S",
    )

    parser = argparse.ArgumentParser(description="Export etymology database to JSON/XML")
    parser.add_argument(
        "--format",
        choices=["json", "xml", "both"],
        default="both",
        help="Export format (default: both)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(__file__).parent.parent / "data" / "exports",
        help="Output directory",
    )
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)

    engine = create_engine(DATABASE_URL, future=True)

    logger.info("Fetching etymology data from database...")
    with engine.connect() as conn:
        result = conn.execute(
            text("""
                SELECT
                    id, root, root_buckwalter, definition_en, definition_tr,
                    summary_tr, summary_en, semantic_field, morphological_forms,
                    related_roots, quran_frequency, source, lane_match_type,
                    lane_volume, confidence, tr_translation_source,
                    tr_translation_confidence, created_at, updated_at
                FROM qm_root_etymologies
                ORDER BY quran_frequency DESC, root
            """)
        )
        rows = result.fetchall()

    data = []
    for row in rows:
        row_dict = dict(row._mapping)
        for key in ["created_at", "updated_at"]:
            if row_dict.get(key):
                row_dict[key] = row_dict[key].isoformat()
        data.append(row_dict)

    logger.info(f"Fetched {len(data)} roots from database")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    if args.format in ("json", "both"):
        json_path = args.output_dir / f"qm_root_etymologies_{timestamp}.json"
        export_to_json(data, json_path)

    if args.format in ("xml", "both"):
        xml_path = args.output_dir / f"qm_root_etymologies_{timestamp}.xml"
        export_to_xml(data, xml_path)

    logger.info("")
    logger.info("═══ Export Complete ═══")
    logger.info(f"Output directory: {args.output_dir}")
    logger.info(f"Total roots exported: {len(data)}")

    engine.dispose()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
