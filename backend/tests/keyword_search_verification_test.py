#!/usr/bin/env python3
"""
Keyword Search Verification Test Suite

This test verifies the keyword search functionality against authoritative external sources:
- Hebrew OT: BibleHub Strong's Concordance (biblehub.com)
- Greek NT: Blue Letter Bible Strong's Concordance (blueletterbible.org)
- Arabic Quran: Quranic Arabic Corpus (corpus.quran.com)

Test Data Sources:
- Hebrew: BibleHub Hebrew Lexicon (https://biblehub.com/hebrew/)
- Greek: Blue Letter Bible Greek Lexicon (https://www.blueletterbible.org/)
- Arabic: Quranic Arabic Corpus (https://corpus.quran.com)

Author: Automated Test Suite
Date: 2026-02-03
"""

import asyncio
import os
import sys
from dataclasses import dataclass
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.bible_morphology import BibleMorphologySearch
from src.quran_morphology import QuranMorphologySearch

# Database URL (same as in app/config.py)
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:54322/postgres")


@dataclass
class HebrewTestCase:
    """Hebrew OT test case with expected values from BibleHub Strong's Concordance"""

    strong_number: str
    hebrew_word: str
    transliteration: str
    meaning: str
    expected_occurrences: int
    tolerance_percent: float = 15.0  # Allow 15% variance due to manuscript differences


@dataclass
class GreekTestCase:
    """Greek NT test case with expected values from Blue Letter Bible"""

    strong_number: str
    greek_word: str
    transliteration: str
    meaning: str
    expected_occurrences: int
    tolerance_percent: float = 15.0


@dataclass
class ArabicTestCase:
    """Arabic Quran test case with expected values from corpus.quran.com"""

    root: str
    buckwalter: str
    meaning: str
    expected_occurrences: int
    tolerance_percent: float = 20.0  # Higher tolerance for root-based counting variations


# =============================================================================
# HEBREW OLD TESTAMENT TEST DATA
# Source: BibleHub Strong's Hebrew Lexicon (https://biblehub.com/hebrew/)
# =============================================================================
HEBREW_TEST_CASES = [
    HebrewTestCase("H3789", "כָּתַב", "kathab", "to write", 227),
    HebrewTestCase("H1696", "דָּבַר", "dabar", "to speak/word", 1089),
    HebrewTestCase("H559", "אָמַר", "amar", "to say", 5316),
    HebrewTestCase("H5414", "נָתַן", "nathan", "to give", 2060),
    HebrewTestCase("H7200", "רָאָה", "raah", "to see", 1311),
    HebrewTestCase("H8085", "שָׁמַע", "shama", "to hear", 1165),
    HebrewTestCase("H3045", "יָדַע", "yada", "to know", 947),
    HebrewTestCase("H1980", "הָלַךְ", "halak", "to walk/go", 1554),
    HebrewTestCase("H935", "בּוֹא", "bo", "to come", 2595),
    HebrewTestCase("H6213", "עָשָׂה", "asah", "to do/make", 2632),
    HebrewTestCase("H430", "אֱלֹהִים", "elohim", "God", 2602),
    HebrewTestCase("H3068", "יְהוָה", "YHWH", "LORD", 6828),
    HebrewTestCase("H776", "אֶרֶץ", "erets", "earth/land", 2505),
    HebrewTestCase("H8064", "שָׁמַיִם", "shamayim", "heaven", 421),
    HebrewTestCase("H4325", "מַיִם", "mayim", "water", 582),
    HebrewTestCase("H1121", "בֵּן", "ben", "son", 4941),
    HebrewTestCase("H3117", "יוֹם", "yom", "day", 2301),
]


# =============================================================================
# GREEK NEW TESTAMENT TEST DATA
# Source: Blue Letter Bible Strong's Greek Lexicon (https://www.blueletterbible.org/)
# =============================================================================
GREEK_TEST_CASES = [
    GreekTestCase("G3056", "λόγος", "logos", "word", 330),
    GreekTestCase("G2316", "θεός", "theos", "God", 1318),
    GreekTestCase("G2424", "Ἰησοῦς", "Iesous", "Jesus", 917),
    GreekTestCase("G5547", "Χριστός", "Christos", "Christ", 529),
    GreekTestCase("G4102", "πίστις", "pistis", "faith", 243),
    GreekTestCase("G26", "ἀγάπη", "agape", "love", 116),
    GreekTestCase("G4151", "πνεῦμα", "pneuma", "spirit", 379),
    GreekTestCase("G2222", "ζωή", "zoe", "life", 135),
    GreekTestCase("G225", "ἀλήθεια", "aletheia", "truth", 109),
    GreekTestCase("G1680", "ἐλπίς", "elpis", "hope", 53),
    GreekTestCase("G5485", "χάρις", "charis", "grace", 155),
    GreekTestCase("G1411", "δύναμις", "dunamis", "power", 120),
    GreekTestCase("G1343", "δικαιοσύνη", "dikaiosyne", "righteousness", 92),
    GreekTestCase("G932", "βασιλεία", "basileia", "kingdom", 163),
    GreekTestCase("G2889", "κόσμος", "kosmos", "world", 186),
    GreekTestCase("G3772", "οὐρανός", "ouranos", "heaven", 278),
    GreekTestCase("G2288", "θάνατος", "thanatos", "death", 120),
]


# =============================================================================
# ARABIC QURAN TEST DATA
# Source: Quranic Arabic Corpus (https://corpus.quran.com)
# =============================================================================
ARABIC_TEST_CASES = [
    ArabicTestCase("ك ت ب", "ktb", "to write", 319),
    ArabicTestCase("ق و ل", "qwl", "to say", 1618),
    ArabicTestCase("ع ل م", "Elm", "to know", 854),
    ArabicTestCase("أ م ن", "Amn", "to believe", 879),
    ArabicTestCase("ص ل و", "Slw", "to pray", 45),
    ArabicTestCase("ر ح م", "rHm", "mercy", 339),
    ArabicTestCase("ع ب د", "Ebd", "to worship", 275),
    ArabicTestCase("ه د ي", "hdy", "to guide", 316),
    ArabicTestCase("س ب ح", "sbH", "to glorify", 92),
    ArabicTestCase("ش ك ر", "$kr", "to thank", 75),
    ArabicTestCase("ص ب ر", "Sbr", "patience", 103),
    ArabicTestCase("ت و ب", "twb", "repentance", 87),
    ArabicTestCase("ذ ك ر", "*kr", "to remember", 292),
    ArabicTestCase("ن ز ل", "nzl", "to reveal", 293),
    ArabicTestCase("خ ل ق", "xlq", "to create", 261),
    ArabicTestCase("ج ع ل", "jEl", "to make", 346),
    ArabicTestCase("ر ب ب", "rbb", "Lord", 975),
]


class TestResult:
    """Test result container"""

    def __init__(
        self,
        test_name: str,
        query: str,
        expected: int,
        actual: int,
        tolerance_percent: float,
        passed: bool,
        details: dict | None = None,
    ):
        self.test_name = test_name
        self.query = query
        self.expected = expected
        self.actual = actual
        self.tolerance_percent = tolerance_percent
        self.passed = passed
        self.details = details or {}
        self.variance_percent = abs(actual - expected) / expected * 100 if expected > 0 else 0

    def __str__(self):
        status = "✅ PASS" if self.passed else "❌ FAIL"
        return (
            f"{status} | {self.test_name} | Query: {self.query} | "
            f"Expected: {self.expected} | Actual: {self.actual} | "
            f"Variance: {self.variance_percent:.1f}%"
        )


def is_within_tolerance(expected: int, actual: int, tolerance_percent: float) -> bool:
    """Check if actual value is within tolerance of expected value"""
    if expected == 0:
        return actual == 0
    variance = abs(actual - expected) / expected * 100
    return variance <= tolerance_percent


async def test_hebrew_keyword_search() -> list[TestResult]:
    """Test Hebrew OT keyword search against BibleHub Strong's Concordance data"""
    print("\n" + "=" * 80)
    print("HEBREW OLD TESTAMENT KEYWORD SEARCH VERIFICATION")
    print("Source: BibleHub Strong's Concordance (biblehub.com)")
    print("=" * 80)

    results = []
    service = await BibleMorphologySearch.get_instance()

    for tc in HEBREW_TEST_CASES:
        try:
            # Search using Strong's number with OT testament filter
            search_result = await service.search(
                query=tc.strong_number,
                per_page=0,  # Get all results
                testament_filter="ot",  # Old Testament only
            )

            actual_occurrences = search_result.total_occurrences
            unique_words = len(search_result.unique_words)
            books_count = len(search_result.book_distribution)

            passed = is_within_tolerance(tc.expected_occurrences, actual_occurrences, tc.tolerance_percent)

            result = TestResult(
                test_name=f"Hebrew {tc.strong_number}",
                query=f"{tc.hebrew_word} ({tc.transliteration})",
                expected=tc.expected_occurrences,
                actual=actual_occurrences,
                tolerance_percent=tc.tolerance_percent,
                passed=passed,
                details={
                    "meaning": tc.meaning,
                    "unique_words": unique_words,
                    "books_count": books_count,
                    "root": search_result.root or "",
                    "transliteration": search_result.transliteration or "",
                },
            )
            results.append(result)
            print(result)

        except Exception as e:
            result = TestResult(
                test_name=f"Hebrew {tc.strong_number}",
                query=f"{tc.hebrew_word} ({tc.transliteration})",
                expected=tc.expected_occurrences,
                actual=0,
                tolerance_percent=tc.tolerance_percent,
                passed=False,
                details={"error": str(e)},
            )
            results.append(result)
            print(f"❌ ERROR | Hebrew {tc.strong_number} | {e}")

    return results


async def test_greek_keyword_search() -> list[TestResult]:
    """Test Greek NT keyword search against Blue Letter Bible data"""
    print("\n" + "=" * 80)
    print("GREEK NEW TESTAMENT KEYWORD SEARCH VERIFICATION")
    print("Source: Blue Letter Bible Strong's Concordance (blueletterbible.org)")
    print("=" * 80)

    results = []
    service = await BibleMorphologySearch.get_instance()

    for tc in GREEK_TEST_CASES:
        try:
            # Search using Strong's number with NT testament filter
            search_result = await service.search(
                query=tc.strong_number,
                per_page=0,
                testament_filter="nt",  # New Testament only
            )

            actual_occurrences = search_result.total_occurrences
            unique_words = len(search_result.unique_words)
            books_count = len(search_result.book_distribution)

            passed = is_within_tolerance(tc.expected_occurrences, actual_occurrences, tc.tolerance_percent)

            result = TestResult(
                test_name=f"Greek {tc.strong_number}",
                query=f"{tc.greek_word} ({tc.transliteration})",
                expected=tc.expected_occurrences,
                actual=actual_occurrences,
                tolerance_percent=tc.tolerance_percent,
                passed=passed,
                details={
                    "meaning": tc.meaning,
                    "unique_words": unique_words,
                    "books_count": books_count,
                    "root": search_result.root or "",
                },
            )
            results.append(result)
            print(result)

        except Exception as e:
            result = TestResult(
                test_name=f"Greek {tc.strong_number}",
                query=f"{tc.greek_word} ({tc.transliteration})",
                expected=tc.expected_occurrences,
                actual=0,
                tolerance_percent=tc.tolerance_percent,
                passed=False,
                details={"error": str(e)},
            )
            results.append(result)
            print(f"❌ ERROR | Greek {tc.strong_number} | {e}")

    return results


async def test_arabic_keyword_search() -> list[TestResult]:
    """Test Arabic Quran keyword search against corpus.quran.com data"""
    print("\n" + "=" * 80)
    print("ARABIC QURAN KEYWORD SEARCH VERIFICATION")
    print("Source: Quranic Arabic Corpus (corpus.quran.com)")
    print("=" * 80)

    results = []
    service = QuranMorphologySearch(DATABASE_URL)

    try:
        for tc in ARABIC_TEST_CASES:
            try:
                # Search using Buckwalter transliteration
                search_result = await service.search_by_root(query=tc.buckwalter, per_page=0)

                actual_occurrences = search_result.total_occurrences
                unique_words = len(search_result.unique_words)
                surahs_count = len(search_result.surah_distribution)

                passed = is_within_tolerance(tc.expected_occurrences, actual_occurrences, tc.tolerance_percent)

                result = TestResult(
                    test_name=f"Arabic {tc.buckwalter}",
                    query=f"{tc.root} ({tc.buckwalter})",
                    expected=tc.expected_occurrences,
                    actual=actual_occurrences,
                    tolerance_percent=tc.tolerance_percent,
                    passed=passed,
                    details={
                        "meaning": tc.meaning,
                        "unique_words": unique_words,
                        "surahs_count": surahs_count,
                        "root": search_result.root or "",
                    },
                )
                results.append(result)
                print(result)

            except Exception as e:
                result = TestResult(
                    test_name=f"Arabic {tc.buckwalter}",
                    query=f"{tc.root} ({tc.buckwalter})",
                    expected=tc.expected_occurrences,
                    actual=0,
                    tolerance_percent=tc.tolerance_percent,
                    passed=False,
                    details={"error": str(e)},
                )
                results.append(result)
                print(f"❌ ERROR | Arabic {tc.buckwalter} | {e}")
    finally:
        await service.close()

    return results


def generate_report(
    hebrew_results: list[TestResult],
    greek_results: list[TestResult],
    arabic_results: list[TestResult],
) -> str:
    """Generate comprehensive test report"""
    all_results = hebrew_results + greek_results + arabic_results
    passed = sum(1 for r in all_results if r.passed)
    failed = sum(1 for r in all_results if not r.passed)
    total = len(all_results)

    report = []
    report.append("\n" + "=" * 80)
    report.append("KEYWORD SEARCH VERIFICATION TEST REPORT")
    report.append("=" * 80)
    report.append(f"\nTotal Tests: {total}")
    report.append(f"Passed: {passed} ({passed / total * 100:.1f}%)" if total > 0 else "Passed: 0")
    report.append(f"Failed: {failed} ({failed / total * 100:.1f}%)" if total > 0 else "Failed: 0")

    # Hebrew summary
    hebrew_passed = sum(1 for r in hebrew_results if r.passed)
    report.append(f"\nHebrew OT: {hebrew_passed}/{len(hebrew_results)} passed")

    # Greek summary
    greek_passed = sum(1 for r in greek_results if r.passed)
    report.append(f"Greek NT: {greek_passed}/{len(greek_results)} passed")

    # Arabic summary
    arabic_passed = sum(1 for r in arabic_results if r.passed)
    report.append(f"Arabic Quran: {arabic_passed}/{len(arabic_results)} passed")

    # Failed tests detail
    failed_tests = [r for r in all_results if not r.passed]
    if failed_tests:
        report.append("\n" + "-" * 40)
        report.append("FAILED TESTS DETAIL:")
        report.append("-" * 40)
        for r in failed_tests:
            report.append(f"\n{r.test_name}")
            report.append(f"  Query: {r.query}")
            report.append(f"  Expected: {r.expected}")
            report.append(f"  Actual: {r.actual}")
            report.append(f"  Variance: {r.variance_percent:.1f}%")
            report.append(f"  Tolerance: {r.tolerance_percent}%")
            if "error" in r.details:
                report.append(f"  Error: {r.details['error']}")

    report.append("\n" + "=" * 80)
    report.append("DATA SOURCES:")
    report.append("- Hebrew OT: BibleHub Strong's Concordance (https://biblehub.com/hebrew/)")
    report.append("- Greek NT: Blue Letter Bible (https://www.blueletterbible.org/)")
    report.append("- Arabic Quran: Quranic Arabic Corpus (https://corpus.quran.com)")
    report.append("=" * 80)

    return "\n".join(report)


async def main():
    """Run all keyword search verification tests"""
    print("\n" + "=" * 80)
    print("KEYWORD SEARCH VERIFICATION TEST SUITE")
    print("Testing against authoritative concordance sources")
    print("=" * 80)

    # Run all tests
    hebrew_results = await test_hebrew_keyword_search()
    greek_results = await test_greek_keyword_search()
    arabic_results = await test_arabic_keyword_search()

    # Generate and print report
    report = generate_report(hebrew_results, greek_results, arabic_results)
    print(report)

    # Save report to file
    report_path = Path(__file__).parent / "keyword_search_verification_report.txt"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"\nReport saved to: {report_path}")

    # Return exit code based on results
    all_results = hebrew_results + greek_results + arabic_results
    failed = sum(1 for r in all_results if not r.passed)
    return 1 if failed > 0 else 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
