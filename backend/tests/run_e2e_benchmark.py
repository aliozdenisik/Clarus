#!/usr/bin/env python3
# ruff: noqa: E402
# Benchmark script mutates sys.path before local imports.
"""
E2E Benchmark: Retrieval + Generation
Tests real queries from test_data.json through the full ComparativeRAG pipeline.
"""

import json
import re
import sys
import time
from pathlib import Path

from dotenv import load_dotenv

# Load environment variables first
load_dotenv()

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from rich.console import Console
from rich.panel import Panel

console = Console()

from src.comparative_rag import ComparativeRAG

# ============================================================================
# UTILITIES REUSED FROM RETRIEVAL TEST
# ============================================================================


def parse_verse_reference(ref: str, source: str) -> set[str]:
    """Parse a verse reference into a set of individual verse identifiers."""
    verses = set()
    ref = ref.strip()

    if source == "quran":
        match = re.match(r"(\d+):(\d+)(?:-(\d+))?", ref)
        if match:
            surah = match.group(1)
            start_verse = int(match.group(2))
            end_verse = int(match.group(3)) if match.group(3) else start_verse
            for v in range(start_verse, end_verse + 1):
                verses.add(f"{surah}:{v}")
    else:
        # Bible format similar to retrieval test
        match = re.match(r"(.+?)\s+(\d+)(?::(\d+))?(?:-(\d+))?", ref)
        if match:
            book = match.group(1).lower()
            chapter = match.group(2)
            start_verse = int(match.group(3)) if match.group(3) else 1
            end_verse = int(match.group(4)) if match.group(4) else start_verse
            if match.group(3) is None:
                verses.add(f"{book} {chapter}:chapter")
            else:
                for v in range(start_verse, end_verse + 1):
                    verses.add(f"{book} {chapter}:{v}")
    return verses


def expand_expected_verses(expected: list[str], source: str) -> set[str]:
    all_verses = set()
    for ref in expected:
        all_verses.update(parse_verse_reference(ref, source))
    return all_verses


def extract_verse_from_result(result, source: str) -> str | None:
    """Extract verse reference from a search result object."""
    # Logic extracted from run_retrieval_accuracy_test.py
    if source == "quran":
        surah_id = getattr(result, "surah_id", None)
        verse_id = getattr(result, "verse_id", None)
        if verse_id is None:
            match = re.search(r"(\d+):(\d+)", getattr(result, "content", "") or "")
            if match:
                return f"{match.group(1)}:{match.group(2)}"

        # Fallback to payload or direct attributes
        if surah_id is None and hasattr(result, "payload"):
            payload = result.payload or {}
            surah_id = payload.get("surah_id")
            verse_id = payload.get("verse_id") or payload.get("start_verse")

        if surah_id and verse_id:
            return f"{surah_id}:{verse_id}"

    else:
        book_name = getattr(result, "book_name", None)
        chapter = getattr(result, "chapter", None)
        verse = getattr(result, "verse", None)

        if book_name is None and hasattr(result, "payload"):
            payload = result.payload or {}
            book_name = payload.get("book_name")
            chapter = payload.get("chapter") or payload.get("chapter_number")
            verse = payload.get("verse") or payload.get("verse_number")

        if book_name and chapter and verse:
            return f"{book_name.lower()} {chapter}:{verse}"

    return None


def calculate_metrics(expected: set[str], retrieved: set[str]) -> tuple[float, float, float]:
    if not retrieved:
        return (1.0, 0.0, 0.0) if expected else (1.0, 1.0, 1.0)
    if not expected:  # Hallucination test
        return (1.0, 1.0, 1.0) if not retrieved else (0.0, 1.0, 0.0)

    matches = set()
    for exp in expected:
        for ret in retrieved:
            if exp == ret:
                matches.add(exp)
                break
            # Partial match (book/surah level)
            exp_parts = exp.split(":")[0] if ":" in exp else exp.split()[0]
            ret_parts = ret.split(":")[0] if ":" in ret else ret.split()[0]
            if exp_parts == ret_parts:
                matches.add(exp)
                break

    precision = len(matches) / len(retrieved) if retrieved else 0.0
    recall = len(matches) / len(expected) if expected else 1.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
    return precision, recall, f1


# ============================================================================
# E2E BENCHMARK PIPELINE
# ============================================================================


def run_benchmark():
    console.print(Panel.fit("[bold cyan]E2E RAG Benchmark (Retrieval + Generation)[/bold cyan]"))

    # 1. Load Data
    test_data_path = Path(__file__).parent / "test_data.json"
    with open(test_data_path, encoding="utf-8") as f:
        data = json.load(f)
    tests = data["tests"]

    # 2. Initialize System
    console.print("[dim]Initializing ComparativeRAG...[/dim]")
    rag = ComparativeRAG(enable_multi_query=True, verbose=False)

    results = []

    # 3. Run Tests
    for i, test in enumerate(tests):
        console.print(f"\n[bold]Test {i + 1}/{len(tests)}: {test['id']}[/bold] - {test['question']}")

        start_time = time.time()

        # A. Search Stage
        try:
            search_result = rag.search_all(test["question"])

            # Combine all results for metric calculation
            # Note: test_data usually specifies source "quran" or "bible".
            # We will filter retrieved results based on expected source for fair metric comparison,
            # OR we check if the relevant verses are present in the massive pool.

            retrieved_verses = []

            # Helper to extract from list of objects
            def collect_verses(obj_list, src):
                for obj in obj_list:
                    v = extract_verse_from_result(obj, src)
                    if v:
                        retrieved_verses.append(v)

            if test["source"] == "quran":
                collect_verses(search_result.quran, "quran")
            else:
                collect_verses(search_result.ot, "bible")
                collect_verses(search_result.nt, "bible")
                collect_verses(search_result.apocrypha, "bible")

            # Calculate Retrieval Metrics
            expected_set = expand_expected_verses(test["expected_verses"], test["source"])
            retrieved_set = set(retrieved_verses)
            precision, recall, f1 = calculate_metrics(expected_set, retrieved_set)

            console.print(f"  [cyan]Retrieval:[/cyan] P={precision:.2f} R={recall:.2f} F1={f1:.2f}")

            # B. Generation Stage
            # Only generate if we retrieved something, or if it's a hallucination test?
            # Real user query -> Always generate.

            gen_start = time.time()
            answer = rag.multi_agent_generator.generate(
                query=test["question"],
                quran_verses=search_result.quran,
                ot_verses=search_result.ot,
                nt_verses=search_result.nt,
                apocrypha_verses=search_result.apocrypha,
            )
            gen_duration = time.time() - gen_start

            total_duration = time.time() - start_time

            # Capture Result
            result_entry = {
                "id": test["id"],
                "question": test["question"],
                "metrics": {"precision": precision, "recall": recall, "f1": f1},
                "timings": {"total": total_duration, "generation": gen_duration},
                "synthesis": answer.synthesis,
                "confidence": answer.confidence,
            }
            results.append(result_entry)

        except Exception as e:
            console.print(f"[red]Error:[/red] {e}")
            results.append({"id": test["id"], "question": test["question"], "error": str(e)})

    # 4. Generate Report
    generate_markdown_report(results)


def generate_markdown_report(results):
    report_path = Path(__file__).parent.parent / "e2e_test_report.md"

    md_lines = [
        "# E2E Comparative RAG Benchmark Report",
        "",
        f"Date: {time.strftime('%Y-%m-%d %H:%M:%S')}",
        "",
    ]

    # Summary Table
    md_lines.append("## Summary Metrics")
    md_lines.append("| ID | Question | Recall | F1 | Latency (s) | Confidence |")
    md_lines.append("|---|---|---|---|---|---|")

    avg_recall = 0
    avg_latency = 0
    valid_count = 0

    for r in results:
        if "error" in r:
            md_lines.append(f"| {r['id']} | {r['question']} | ERROR | - | - | - |")
            continue

        m = r["metrics"]
        t = r["timings"]
        md_lines.append(
            f"| {r['id']} | {r['question']} | {m['recall']:.2f} | {m['f1']:.2f} | {t['total']:.2f} | {r['confidence']:.2f} |"
        )

        avg_recall += m["recall"]
        avg_latency += t["total"]
        valid_count += 1

    if valid_count > 0:
        md_lines.append(f"\n**Average Recall:** {avg_recall / valid_count:.2f}")
        md_lines.append(f"**Average Latency:** {avg_latency / valid_count:.2f}s")

    # Detailed Outputs
    md_lines.append("\n## Detailed Responses")
    for r in results:
        if "error" in r:
            continue
        md_lines.append(f"### {r['id']}: {r['question']}")
        md_lines.append(f"**Confidence:** {r['confidence']:.0%}")
        md_lines.append("\n**Synthesis:**")
        md_lines.append(f"> {r['synthesis'].replace(chr(10), '  ' + chr(10))}")  # Blockquote
        md_lines.append("\n---")

    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))

    console.print(f"\n[green]Report generated at {report_path}[/green]")


if __name__ == "__main__":
    run_benchmark()
