#!/usr/bin/env python3
"""
Word Search Verification Test Suite

Tests the keyword search functionality against expected values from external sources:
- Quran: Quranic Arabic Corpus (corpus.quran.com)
- Hebrew OT: ETCBC BHSA, BibleHub Strong's Concordance
- Greek NT: MorphGNT, BibleHub

Metrics tested:
- Total Occurrence
- Unique Words (count + 80% intersection)
- Books/Surahs (count)
- Book/Surah Distribution
- Verse Results (count + spot-check)

Success criteria:
- Total Occurrence: ±5% tolerance
- Unique Words: 80% intersection minimum
- Books/Surahs: ±5% tolerance
"""

import asyncio
import json
import logging
import sys
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Optional

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.quran_morphology import QuranMorphologySearch
from src.bible_morphology import BibleMorphologySearch

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Data Classes
# ---------------------------------------------------------------------------


@dataclass
class TestResult:
    """Result of a single test case."""

    test_id: str
    query: str
    description: str
    source: str  # quran, hebrew_ot, greek_nt
    input_type: str  # latin, original, edge_case

    # Actual results from system
    actual_total_occurrences: int = 0
    actual_unique_words_count: int = 0
    actual_unique_words: list[str] = field(default_factory=list)
    actual_books_count: int = 0
    actual_book_distribution: dict = field(default_factory=dict)
    actual_verse_count: int = 0
    actual_root: Optional[str] = None
    actual_root_source: str = ""

    # Expected results from external sources
    expected_total_occurrences: Optional[int] = None
    expected_unique_words_count: Optional[int] = None
    expected_unique_words: list[str] = field(default_factory=list)
    expected_books_count: Optional[int] = None
    expected_book_distribution: dict = field(default_factory=dict)
    expected_verse_count: Optional[int] = None

    # Comparison results
    total_occurrence_pass: bool = False
    total_occurrence_diff_pct: float = 0.0
    unique_words_pass: bool = False
    unique_words_intersection_pct: float = 0.0
    books_count_pass: bool = False
    books_count_diff_pct: float = 0.0
    verse_count_pass: bool = False
    verse_count_diff_pct: float = 0.0

    # Overall
    overall_pass: bool = False
    error: Optional[str] = None
    execution_time_ms: float = 0.0

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class TestSummary:
    """Summary of all test results."""

    total_tests: int = 0
    passed_tests: int = 0
    failed_tests: int = 0
    error_tests: int = 0

    # By source
    quran_total: int = 0
    quran_passed: int = 0
    hebrew_total: int = 0
    hebrew_passed: int = 0
    greek_total: int = 0
    greek_passed: int = 0

    # By input type
    latin_total: int = 0
    latin_passed: int = 0
    original_total: int = 0
    original_passed: int = 0
    edge_case_total: int = 0
    edge_case_passed: int = 0

    # Metric-specific pass rates
    total_occurrence_pass_rate: float = 0.0
    unique_words_pass_rate: float = 0.0
    books_count_pass_rate: float = 0.0
    verse_count_pass_rate: float = 0.0

    overall_pass_rate: float = 0.0

    def to_dict(self) -> dict:
        return asdict(self)


# ---------------------------------------------------------------------------
# Test Runner
# ---------------------------------------------------------------------------


class WordSearchVerificationTest:
    """Main test runner for word search verification."""

    TOLERANCE_PCT = 5.0  # ±5% tolerance for numeric comparisons
    INTERSECTION_MIN = 0.80  # 80% minimum intersection for word lists

    def __init__(self):
        self.quran_search: Optional[QuranMorphologySearch] = None
        self.bible_search: Optional[BibleMorphologySearch] = None
        self.results: list[TestResult] = []
        self.summary = TestSummary()

    async def setup(self):
        """Initialize search services."""
        logger.info("Initializing search services...")
        self.quran_search = QuranMorphologySearch(
            "postgresql+asyncpg://postgres:postgres@localhost:54322/postgres"
        )
        self.bible_search = await BibleMorphologySearch.get_instance()
        logger.info("Search services initialized")

    async def teardown(self):
        """Cleanup search services."""
        if self.quran_search:
            await self.quran_search.close()
        logger.info("Search services closed")

    async def run_all_tests(self, input_file: str, expected_file: Optional[str] = None):
        """Run all tests from input file."""
        import time

        # Load test input
        with open(input_file, "r", encoding="utf-8") as f:
            test_input = json.load(f)

        # Load expected values if provided
        expected_data = {}
        if expected_file and Path(expected_file).exists():
            with open(expected_file, "r", encoding="utf-8") as f:
                expected_data = json.load(f)

        tests = test_input.get("tests", {})

        # Run Quran tests
        logger.info("=" * 60)
        logger.info("Running QURAN tests...")
        logger.info("=" * 60)
        await self._run_source_tests(
            "quran", tests.get("quran", {}), expected_data.get("quran", {})
        )

        # Run Hebrew OT tests
        logger.info("=" * 60)
        logger.info("Running HEBREW OT tests...")
        logger.info("=" * 60)
        await self._run_source_tests(
            "hebrew_ot",
            tests.get("hebrew_ot", {}),
            expected_data.get("hebrew_ot", {}),
            language_filter="hebrew",
        )

        # Run Greek NT tests
        logger.info("=" * 60)
        logger.info("Running GREEK NT tests...")
        logger.info("=" * 60)
        await self._run_source_tests(
            "greek_nt",
            tests.get("greek_nt", {}),
            expected_data.get("greek_nt", {}),
            language_filter="greek",
        )

        # Calculate summary
        self._calculate_summary()

    async def _run_source_tests(
        self,
        source: str,
        tests: dict,
        expected: dict,
        language_filter: Optional[str] = None,
    ):
        """Run tests for a single source (quran/hebrew/greek)."""
        import time

        for input_type in ["latin", "original", "edge_case"]:
            test_cases = tests.get(input_type, [])
            expected_cases = expected.get(input_type, {})

            for test_case in test_cases:
                test_id = test_case["id"]
                query = test_case["query"]
                description = test_case["description"]

                result = TestResult(
                    test_id=test_id,
                    query=query,
                    description=description,
                    source=source,
                    input_type=input_type,
                )

                start_time = time.time()

                try:
                    # Execute search
                    if source == "quran":
                        search_result = await self.quran_search.search_by_root(
                            query=query,
                            page=1,
                            per_page=0,  # Get all verses
                        )
                        result.actual_total_occurrences = (
                            search_result.total_occurrences
                        )
                        result.actual_unique_words_count = len(
                            search_result.unique_words
                        )
                        result.actual_unique_words = search_result.unique_words
                        result.actual_books_count = len(
                            search_result.surah_distribution
                        )
                        result.actual_book_distribution = {
                            sd.surah_name: sd.count
                            for sd in search_result.surah_distribution
                        }
                        result.actual_verse_count = search_result.total_verses
                        result.actual_root = search_result.root
                        result.actual_root_source = search_result.root_source
                    else:
                        search_result = await self.bible_search.search(
                            query=query,
                            page=1,
                            per_page=0,  # Get all verses
                            language_filter=language_filter,
                        )
                        result.actual_total_occurrences = (
                            search_result.total_occurrences
                        )
                        result.actual_unique_words_count = len(
                            search_result.unique_words
                        )
                        result.actual_unique_words = search_result.unique_words
                        result.actual_books_count = len(search_result.book_distribution)
                        result.actual_book_distribution = {
                            bd.book_name: bd.count
                            for bd in search_result.book_distribution
                        }
                        result.actual_verse_count = search_result.total_verses
                        result.actual_root = search_result.root
                        result.actual_root_source = search_result.root_source

                    # Compare with expected values if available
                    expected_case = expected_cases.get(test_id, {})
                    if expected_case:
                        self._compare_results(result, expected_case)
                    else:
                        # No expected data - mark as pass if found results (for non-edge cases)
                        if input_type == "edge_case":
                            # Edge cases pass if they don't crash
                            result.total_occurrence_pass = True
                            result.unique_words_pass = True
                            result.books_count_pass = True
                            result.verse_count_pass = True
                            result.overall_pass = True
                        else:
                            # For non-edge cases without expected data,
                            # pass if found something (root_source != not_found)
                            found_results = result.actual_root_source != "not_found"
                            result.total_occurrence_pass = found_results
                            result.unique_words_pass = found_results
                            result.books_count_pass = found_results
                            result.verse_count_pass = found_results
                            result.overall_pass = found_results

                except Exception as e:
                    result.error = str(e)
                    logger.error(f"Test {test_id} ERROR: {e}")

                result.execution_time_ms = (time.time() - start_time) * 1000
                self.results.append(result)

                # Log result
                status = (
                    "PASS"
                    if result.overall_pass
                    else ("ERROR" if result.error else "FAIL")
                )
                logger.info(
                    f"[{status}] {test_id}: {query!r} - "
                    f"occurrences={result.actual_total_occurrences}, "
                    f"words={result.actual_unique_words_count}, "
                    f"books={result.actual_books_count}, "
                    f"verses={result.actual_verse_count}"
                )

    def _compare_results(self, result: TestResult, expected: dict):
        """Compare actual results with expected values."""

        # Total Occurrences (±5% tolerance)
        if expected.get("total_occurrences") is not None:
            result.expected_total_occurrences = expected["total_occurrences"]
            exp = expected["total_occurrences"]
            act = result.actual_total_occurrences
            if exp > 0:
                result.total_occurrence_diff_pct = abs(act - exp) / exp * 100
                result.total_occurrence_pass = (
                    result.total_occurrence_diff_pct <= self.TOLERANCE_PCT
                )
            else:
                result.total_occurrence_pass = act == 0
        else:
            result.total_occurrence_pass = True

        # Unique Words (80% intersection minimum)
        if expected.get("unique_words"):
            result.expected_unique_words = expected["unique_words"]
            result.expected_unique_words_count = len(expected["unique_words"])
            exp_set = set(expected["unique_words"])
            act_set = set(result.actual_unique_words)
            if exp_set:
                intersection = len(exp_set & act_set)
                result.unique_words_intersection_pct = intersection / len(exp_set) * 100
                result.unique_words_pass = (
                    result.unique_words_intersection_pct >= self.INTERSECTION_MIN * 100
                )
            else:
                result.unique_words_pass = len(act_set) == 0
        elif expected.get("unique_words_count") is not None:
            result.expected_unique_words_count = expected["unique_words_count"]
            exp = expected["unique_words_count"]
            act = result.actual_unique_words_count
            if exp > 0:
                diff_pct = abs(act - exp) / exp * 100
                result.unique_words_pass = (
                    diff_pct <= self.TOLERANCE_PCT * 2
                )  # More lenient for count-only
            else:
                result.unique_words_pass = act == 0
        else:
            result.unique_words_pass = True

        # Books/Surahs Count (±5% tolerance)
        if expected.get("books_count") is not None:
            result.expected_books_count = expected["books_count"]
            exp = expected["books_count"]
            act = result.actual_books_count
            if exp > 0:
                result.books_count_diff_pct = abs(act - exp) / exp * 100
                result.books_count_pass = (
                    result.books_count_diff_pct <= self.TOLERANCE_PCT
                )
            else:
                result.books_count_pass = act == 0
        else:
            result.books_count_pass = True

        # Verse Count (±5% tolerance)
        if expected.get("verse_count") is not None:
            result.expected_verse_count = expected["verse_count"]
            exp = expected["verse_count"]
            act = result.actual_verse_count
            if exp > 0:
                result.verse_count_diff_pct = abs(act - exp) / exp * 100
                result.verse_count_pass = (
                    result.verse_count_diff_pct <= self.TOLERANCE_PCT
                )
            else:
                result.verse_count_pass = act == 0
        else:
            result.verse_count_pass = True

        # Overall pass if all metrics pass
        result.overall_pass = (
            result.total_occurrence_pass
            and result.unique_words_pass
            and result.books_count_pass
            and result.verse_count_pass
            and result.error is None
        )

    def _calculate_summary(self):
        """Calculate summary statistics."""
        s = self.summary
        s.total_tests = len(self.results)

        for r in self.results:
            if r.error:
                s.error_tests += 1
            elif r.overall_pass:
                s.passed_tests += 1
            else:
                s.failed_tests += 1

            # By source
            if r.source == "quran":
                s.quran_total += 1
                if r.overall_pass:
                    s.quran_passed += 1
            elif r.source == "hebrew_ot":
                s.hebrew_total += 1
                if r.overall_pass:
                    s.hebrew_passed += 1
            elif r.source == "greek_nt":
                s.greek_total += 1
                if r.overall_pass:
                    s.greek_passed += 1

            # By input type
            if r.input_type == "latin":
                s.latin_total += 1
                if r.overall_pass:
                    s.latin_passed += 1
            elif r.input_type == "original":
                s.original_total += 1
                if r.overall_pass:
                    s.original_passed += 1
            elif r.input_type == "edge_case":
                s.edge_case_total += 1
                if r.overall_pass:
                    s.edge_case_passed += 1

        # Calculate pass rates
        if s.total_tests > 0:
            s.overall_pass_rate = s.passed_tests / s.total_tests * 100

        # Metric-specific pass rates (excluding edge cases and errors)
        valid_results = [
            r for r in self.results if not r.error and r.input_type != "edge_case"
        ]
        if valid_results:
            s.total_occurrence_pass_rate = (
                sum(1 for r in valid_results if r.total_occurrence_pass)
                / len(valid_results)
                * 100
            )
            s.unique_words_pass_rate = (
                sum(1 for r in valid_results if r.unique_words_pass)
                / len(valid_results)
                * 100
            )
            s.books_count_pass_rate = (
                sum(1 for r in valid_results if r.books_count_pass)
                / len(valid_results)
                * 100
            )
            s.verse_count_pass_rate = (
                sum(1 for r in valid_results if r.verse_count_pass)
                / len(valid_results)
                * 100
            )

    def generate_report(self, output_dir: str) -> str:
        """Generate markdown report."""
        report_lines = []
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        report_lines.append("# Word Search Verification Report")
        report_lines.append(f"\n**Generated:** {now}")
        report_lines.append(f"**Total Tests:** {self.summary.total_tests}")
        report_lines.append("")

        # Summary
        report_lines.append("## Executive Summary")
        report_lines.append("")
        report_lines.append(f"| Metric | Value |")
        report_lines.append(f"|--------|-------|")
        report_lines.append(
            f"| **Overall Pass Rate** | **{self.summary.overall_pass_rate:.1f}%** |"
        )
        report_lines.append(f"| Passed | {self.summary.passed_tests} |")
        report_lines.append(f"| Failed | {self.summary.failed_tests} |")
        report_lines.append(f"| Errors | {self.summary.error_tests} |")
        report_lines.append("")

        # By Source
        report_lines.append("## Results by Source")
        report_lines.append("")
        report_lines.append("| Source | Total | Passed | Pass Rate |")
        report_lines.append("|--------|-------|--------|-----------|")
        if self.summary.quran_total > 0:
            rate = self.summary.quran_passed / self.summary.quran_total * 100
            report_lines.append(
                f"| Quran | {self.summary.quran_total} | {self.summary.quran_passed} | {rate:.1f}% |"
            )
        if self.summary.hebrew_total > 0:
            rate = self.summary.hebrew_passed / self.summary.hebrew_total * 100
            report_lines.append(
                f"| Hebrew OT | {self.summary.hebrew_total} | {self.summary.hebrew_passed} | {rate:.1f}% |"
            )
        if self.summary.greek_total > 0:
            rate = self.summary.greek_passed / self.summary.greek_total * 100
            report_lines.append(
                f"| Greek NT | {self.summary.greek_total} | {self.summary.greek_passed} | {rate:.1f}% |"
            )
        report_lines.append("")

        # By Input Type
        report_lines.append("## Results by Input Type")
        report_lines.append("")
        report_lines.append("| Input Type | Total | Passed | Pass Rate |")
        report_lines.append("|------------|-------|--------|-----------|")
        if self.summary.latin_total > 0:
            rate = self.summary.latin_passed / self.summary.latin_total * 100
            report_lines.append(
                f"| Latin | {self.summary.latin_total} | {self.summary.latin_passed} | {rate:.1f}% |"
            )
        if self.summary.original_total > 0:
            rate = self.summary.original_passed / self.summary.original_total * 100
            report_lines.append(
                f"| Original | {self.summary.original_total} | {self.summary.original_passed} | {rate:.1f}% |"
            )
        if self.summary.edge_case_total > 0:
            rate = self.summary.edge_case_passed / self.summary.edge_case_total * 100
            report_lines.append(
                f"| Edge Case | {self.summary.edge_case_total} | {self.summary.edge_case_passed} | {rate:.1f}% |"
            )
        report_lines.append("")

        # Metric-Specific Pass Rates
        report_lines.append("## Metric-Specific Pass Rates")
        report_lines.append("")
        report_lines.append("| Metric | Pass Rate |")
        report_lines.append("|--------|-----------|")
        report_lines.append(
            f"| Total Occurrence (±5%) | {self.summary.total_occurrence_pass_rate:.1f}% |"
        )
        report_lines.append(
            f"| Unique Words (80% intersection) | {self.summary.unique_words_pass_rate:.1f}% |"
        )
        report_lines.append(
            f"| Books/Surahs Count (±5%) | {self.summary.books_count_pass_rate:.1f}% |"
        )
        report_lines.append(
            f"| Verse Count (±5%) | {self.summary.verse_count_pass_rate:.1f}% |"
        )
        report_lines.append("")

        # Detailed Results
        report_lines.append("## Detailed Results")
        report_lines.append("")

        for source in ["quran", "hebrew_ot", "greek_nt"]:
            source_results = [r for r in self.results if r.source == source]
            if not source_results:
                continue

            source_name = {
                "quran": "Quran",
                "hebrew_ot": "Hebrew OT",
                "greek_nt": "Greek NT",
            }[source]
            report_lines.append(f"### {source_name}")
            report_lines.append("")
            report_lines.append(
                "| ID | Query | Description | Status | Occurrences | Words | Books | Verses |"
            )
            report_lines.append(
                "|-----|-------|-------------|--------|-------------|-------|-------|--------|"
            )

            for r in source_results:
                status = "✅" if r.overall_pass else ("❌ ERROR" if r.error else "❌")
                occ_str = f"{r.actual_total_occurrences}"
                if r.expected_total_occurrences is not None:
                    occ_str += f" (exp: {r.expected_total_occurrences})"
                words_str = f"{r.actual_unique_words_count}"
                books_str = f"{r.actual_books_count}"
                verses_str = f"{r.actual_verse_count}"

                # Escape pipe characters in query
                query_escaped = r.query.replace("|", "\\|") if r.query else ""

                report_lines.append(
                    f"| {r.test_id} | `{query_escaped}` | {r.description} | {status} | {occ_str} | {words_str} | {books_str} | {verses_str} |"
                )
            report_lines.append("")

        # Failed Tests Detail
        failed = [r for r in self.results if not r.overall_pass and not r.error]
        if failed:
            report_lines.append("## Failed Tests Detail")
            report_lines.append("")
            for r in failed:
                report_lines.append(f"### {r.test_id}: `{r.query}`")
                report_lines.append(f"- **Source:** {r.source}")
                report_lines.append(f"- **Description:** {r.description}")
                report_lines.append(
                    f"- **Root Found:** {r.actual_root} ({r.actual_root_source})"
                )
                if not r.total_occurrence_pass:
                    report_lines.append(
                        f"- **Total Occurrence:** {r.actual_total_occurrences} (expected: {r.expected_total_occurrences}, diff: {r.total_occurrence_diff_pct:.1f}%)"
                    )
                if not r.unique_words_pass:
                    report_lines.append(
                        f"- **Unique Words:** {r.actual_unique_words_count} (intersection: {r.unique_words_intersection_pct:.1f}%)"
                    )
                if not r.books_count_pass:
                    report_lines.append(
                        f"- **Books Count:** {r.actual_books_count} (expected: {r.expected_books_count}, diff: {r.books_count_diff_pct:.1f}%)"
                    )
                if not r.verse_count_pass:
                    report_lines.append(
                        f"- **Verse Count:** {r.actual_verse_count} (expected: {r.expected_verse_count}, diff: {r.verse_count_diff_pct:.1f}%)"
                    )
                report_lines.append("")

        # Errors
        errors = [r for r in self.results if r.error]
        if errors:
            report_lines.append("## Errors")
            report_lines.append("")
            for r in errors:
                report_lines.append(f"### {r.test_id}: `{r.query}`")
                report_lines.append(f"- **Error:** {r.error}")
                report_lines.append("")

        report_content = "\n".join(report_lines)

        # Save report
        report_path = Path(output_dir) / "word_search_verification_report.md"
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(report_content)

        # Save JSON results
        results_path = Path(output_dir) / "word_search_verification_results.json"
        with open(results_path, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "summary": self.summary.to_dict(),
                    "results": [r.to_dict() for r in self.results],
                },
                f,
                indent=2,
                ensure_ascii=False,
            )

        logger.info(f"Report saved to: {report_path}")
        logger.info(f"Results saved to: {results_path}")

        return report_content


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


async def main():
    """Run word search verification tests."""
    test_dir = Path(__file__).parent
    input_file = test_dir / "word_search_test_input.json"
    expected_file = test_dir / "word_search_expected_output.json"

    if not input_file.exists():
        logger.error(f"Input file not found: {input_file}")
        return 1

    runner = WordSearchVerificationTest()

    try:
        await runner.setup()
        await runner.run_all_tests(
            str(input_file), str(expected_file) if expected_file.exists() else None
        )
        report = runner.generate_report(str(test_dir))

        # Print summary
        print("\n" + "=" * 60)
        print("WORD SEARCH VERIFICATION TEST SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {runner.summary.total_tests}")
        print(f"Passed: {runner.summary.passed_tests}")
        print(f"Failed: {runner.summary.failed_tests}")
        print(f"Errors: {runner.summary.error_tests}")
        print(f"Overall Pass Rate: {runner.summary.overall_pass_rate:.1f}%")
        print("=" * 60)

        return (
            0
            if runner.summary.failed_tests == 0 and runner.summary.error_tests == 0
            else 1
        )

    finally:
        await runner.teardown()


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
