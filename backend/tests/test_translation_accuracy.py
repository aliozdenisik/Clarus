#!/usr/bin/env python3
"""
Translation Accuracy Test Suite — 40 Multilingual Query Pairs

Validates QueryTranslator output across 8 language categories using
mocked LLM responses. No real API calls are made.

Categories:
  1. Heuristic Pre-Filter (8 tests)  — Turkish chars + quran / ASCII + bible
  2. English → Turkish (8 tests)     — Quran corpus translations
  3. Spanish → Corpus Language (6)   — Mixed corpus translations
  4. French → Corpus Language (5)    — Mixed corpus translations
  5. Arabic → Corpus Language (5)    — Quran corpus translations
  6. German → Corpus Language (4)    — Mixed corpus translations
  7. Edge Cases (4 tests)            — Boundary conditions

Usage:
    cd backend && source ../venv/bin/activate
    set -a && source .env && set +a
    python tests/test_translation_accuracy.py
"""

import json
import sys
from pathlib import Path
from typing import List, Tuple
from unittest.mock import patch, Mock

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()

# Import after path setup
from src.query_translator import QueryTranslator, TranslationResult


# ============================================================================
# MOCK HELPERS
# ============================================================================


def mock_llm_json_response(
    detected_language: str,
    translated_query: str,
    was_translated: bool,
) -> Mock:
    """Create a mock requests.Response for JSON mode LLM calls."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.raise_for_status = Mock()
    mock_response.json.return_value = {
        "choices": [
            {
                "message": {
                    "content": json.dumps(
                        {
                            "detected_language": detected_language,
                            "translated_query": translated_query,
                            "was_translated": was_translated,
                        }
                    )
                }
            }
        ]
    }
    return mock_response


# ============================================================================
# TEST DATA DEFINITIONS
# ============================================================================

# Each tuple: (query, corpus, expected_lang, expected_query, expected_was_translated, needs_llm)
# needs_llm: False = heuristic should handle (mock NOT called), True = mock IS called

HEURISTIC_TESTS: List[Tuple[str, str, str, str, bool, bool]] = [
    # Category 1: Heuristic Pre-Filter (8 tests)
    # Turkish chars + quran → skip LLM
    ("sabır ve namaz", "quran_tr", "tr", "sabır ve namaz", False, False),
    ("şefaat nedir", "quran", "tr", "şefaat nedir", False, False),
    ("İslam'da tövbe", "quran_tr", "tr", "İslam'da tövbe", False, False),
    ("Kuran'daki güzel ahlak", "quran", "tr", "Kuran'daki güzel ahlak", False, False),
    # Pure ASCII + bible → skip LLM
    ("love your neighbor", "bible", "en", "love your neighbor", False, False),
    (
        "forgiveness in the Bible",
        "bible",
        "en",
        "forgiveness in the Bible",
        False,
        False,
    ),
    ("What is patience", "bible_ot", "en", "What is patience", False, False),
    ("grace and mercy", "bible_nt", "en", "grace and mercy", False, False),
]

EN_TO_TR_TESTS: List[Tuple[str, str, str, str, bool, bool]] = [
    # Category 2: English → Turkish Translation (8 tests)
    # ASCII + quran → no heuristic (quran heuristic checks Turkish chars, not ASCII)
    ("patience in Islam", "quran_tr", "en", "İslam'da sabır", True, True),
    ("prayer and worship", "quran_tr", "en", "namaz ve ibadet", True, True),
    ("creation of the universe", "quran_tr", "en", "evrenin yaratılışı", True, True),
    ("mercy and compassion", "quran_tr", "en", "merhamet ve şefkat", True, True),
    ("Day of Judgment", "quran_tr", "en", "kıyamet günü", True, True),
    (
        "prophets and messengers",
        "quran_tr",
        "en",
        "peygamberler ve elçiler",
        True,
        True,
    ),
    ("charity and almsgiving", "quran_tr", "en", "sadaka ve zekat", True, True),
    ("repentance and forgiveness", "quran_tr", "en", "tövbe ve bağışlama", True, True),
]

SPANISH_TESTS: List[Tuple[str, str, str, str, bool, bool]] = [
    # Category 3: Spanish → Corpus Language (6 tests)
    # Non-ASCII Spanish chars bypass heuristic
    (
        "¿Qué dice el Corán sobre la paciencia?",
        "quran",
        "es",
        "Kuran'da sabır hakkında ne söyleniyor?",
        True,
        True,
    ),
    # "amor en la Biblia" is pure ASCII + bible → heuristic fires → returns as-is
    ("amor en la Biblia", "bible", "en", "amor en la Biblia", False, False),
    # "la creación del mundo" has "ó" (non-ASCII) → LLM needed
    ("la creación del mundo", "quran", "es", "dünyanın yaratılışı", True, True),
    # "perdón" has "ó" (non-ASCII) → LLM needed even with bible corpus
    ("perdón y misericordia", "bible_ot", "es", "forgiveness and mercy", True, True),
    ("los profetas de Dios", "quran", "es", "Allah'ın peygamberleri", True, True),
    # "oración" has "ó" (non-ASCII) → LLM needed
    ("la oración en el Islam", "quran", "es", "İslam'da dua", True, True),
]

FRENCH_TESTS: List[Tuple[str, str, str, str, bool, bool]] = [
    # Category 4: French → Corpus Language (5 tests)
    # "patience dans l'Islam" is pure ASCII → quran → no Turkish chars → LLM needed
    ("patience dans l'Islam", "quran", "fr", "İslam'da sabır", True, True),
    # "l'amour dans la Bible" is pure ASCII + bible → heuristic fires → returns as-is
    ("l'amour dans la Bible", "bible", "en", "l'amour dans la Bible", False, False),
    # "création" has "é" (non-ASCII) → LLM needed
    ("la création du monde", "quran", "fr", "dünyanın yaratılışı", True, True),
    # "le pardon selon le Coran" is pure ASCII → quran → no Turkish chars → LLM needed
    ("le pardon selon le Coran", "quran", "fr", "Kuran'a göre bağışlama", True, True),
    # "prophètes" has "è" (non-ASCII) → LLM needed
    ("les prophètes bibliques", "bible_nt", "fr", "biblical prophets", True, True),
]

ARABIC_TESTS: List[Tuple[str, str, str, str, bool, bool]] = [
    # Category 5: Arabic → Corpus Language (5 tests)
    # Arabic chars are non-ASCII → LLM needed
    ("الصبر في الإسلام", "quran", "ar", "İslam'da sabır", True, True),
    ("المحبة في الكتاب المقدس", "bible", "ar", "love in the Holy Bible", True, True),
    ("يوم القيامة", "quran", "ar", "kıyamet günü", True, True),
    ("الرحمة والمغفرة", "quran", "ar", "merhamet ve mağfiret", True, True),
    ("الأنبياء والرسل", "quran", "ar", "peygamberler ve resuller", True, True),
]

GERMAN_TESTS: List[Tuple[str, str, str, str, bool, bool]] = [
    # Category 6: German → Corpus Language (4 tests)
    # "Geduld im Islam" is pure ASCII → quran → no Turkish chars → LLM needed
    ("Geduld im Islam", "quran", "de", "İslam'da sabır", True, True),
    # "Liebe in der Bibel" is pure ASCII + bible → heuristic fires → returns as-is
    ("Liebe in der Bibel", "bible", "en", "Liebe in der Bibel", False, False),
    # "Schöpfung" has "ö" which is in TURKISH_CHARS → quran heuristic fires → returns as-is
    ("Schöpfung der Welt", "quran", "tr", "Schöpfung der Welt", False, False),
    # "Vergebung und Barmherzigkeit" is pure ASCII + bible_ot → heuristic fires → returns as-is
    (
        "Vergebung und Barmherzigkeit",
        "bible_ot",
        "en",
        "Vergebung und Barmherzigkeit",
        False,
        False,
    ),
]

EDGE_CASE_TESTS: List[Tuple[str, str, str, str, bool, bool]] = [
    # Category 7: Edge Cases (4 tests)
    # "What does sabır mean?" has "ı" (non-ASCII) + bible → heuristic doesn't fire → LLM needed
    ("What does sabır mean?", "bible", "en", "What does sabır mean?", False, True),
    # Pure ASCII + bible_ot → heuristic fires
    (
        "Is Musa mentioned in the Torah?",
        "bible_ot",
        "en",
        "Is Musa mentioned in the Torah?",
        False,
        False,
    ),
    # "love" is pure ASCII + bible → heuristic fires
    ("love", "bible", "en", "love", False, False),
    # "patience" is pure ASCII + quran → no Turkish chars → heuristic doesn't fire → LLM needed
    ("patience", "quran", "en", "sabır", True, True),
]


# ============================================================================
# TEST RUNNER PER CATEGORY
# ============================================================================


def run_category_tests(
    category_name: str,
    tests: List[Tuple[str, str, str, str, bool, bool]],
) -> List[bool]:
    """Run a category of tests and return list of pass/fail booleans."""
    console.print(f"\n[bold cyan]{category_name}[/bold cyan]")
    results: List[bool] = []

    for (
        query,
        corpus,
        expected_lang,
        expected_query,
        expected_was_translated,
        needs_llm,
    ) in tests:
        passed = _run_single_test(
            query=query,
            corpus=corpus,
            expected_lang=expected_lang,
            expected_query=expected_query,
            expected_was_translated=expected_was_translated,
            needs_llm=needs_llm,
        )
        results.append(passed)

    return results


def _run_single_test(
    query: str,
    corpus: str,
    expected_lang: str,
    expected_query: str,
    expected_was_translated: bool,
    needs_llm: bool,
) -> bool:
    """Run a single translation test. Returns True if passed."""
    try:
        with patch("src.query_translator.llm_with_breaker") as mock_breaker:
            # Configure mock if LLM is expected to be called
            if needs_llm:
                mock_breaker.return_value = mock_llm_json_response(
                    detected_language=expected_lang,
                    translated_query=expected_query,
                    was_translated=expected_was_translated,
                )

            translator = QueryTranslator(api_key="test-key")
            result = translator.translate_query(query, corpus=corpus)

            # Verify LLM call expectation
            if needs_llm:
                assert mock_breaker.called, (
                    f"LLM should have been called for '{query}' + {corpus}"
                )
            else:
                assert not mock_breaker.called, (
                    f"LLM should NOT have been called for '{query}' + {corpus}"
                )

            # Verify result fields
            assert result.detected_language == expected_lang, (
                f"Language: expected '{expected_lang}', got '{result.detected_language}'"
            )
            assert result.translated_query == expected_query, (
                f"Query: expected '{expected_query}', got '{result.translated_query}'"
            )
            assert result.was_translated is expected_was_translated, (
                f"was_translated: expected {expected_was_translated}, got {result.was_translated}"
            )

            # Format output
            if expected_was_translated:
                console.print(
                    f'  [green]✅ PASS[/green]: "{query}" + {corpus} → "{expected_query}"'
                )
            else:
                console.print(
                    f'  [green]✅ PASS[/green]: "{query}" + {corpus} → {expected_lang}, no translation'
                )
            return True

    except Exception as e:
        console.print(f'  [red]❌ FAIL[/red]: "{query}" + {corpus} — {e}')
        return False


# ============================================================================
# MAIN RUNNER
# ============================================================================


def run_all_tests() -> None:
    """Run all 40 translation accuracy tests and print summary."""
    console.print(
        Panel.fit(
            "[bold cyan]Translation Accuracy Test Suite (40 pairs)[/bold cyan]\n"
            "[dim]Validating QueryTranslator with mocked LLM responses[/dim]",
            border_style="cyan",
        )
    )

    # Mock sentry_sdk to avoid initialization issues
    with patch("src.query_translator.sentry_sdk"):
        category_results: List[Tuple[str, List[bool]]] = []

        # Category 1: Heuristic Pre-Filter (8 tests)
        results = run_category_tests(
            "Category 1: Heuristic Pre-Filter (8 tests)", HEURISTIC_TESTS
        )
        category_results.append(("Turkish (heuristic)", results[:4]))
        category_results.append(("English (heuristic)", results[4:]))

        # Category 2: English → Turkish (8 tests)
        results = run_category_tests(
            "Category 2: English → Turkish (8 tests)", EN_TO_TR_TESTS
        )
        category_results.append(("English → Turkish", results))

        # Category 3: Spanish (6 tests)
        results = run_category_tests(
            "Category 3: Spanish → Corpus Language (6 tests)", SPANISH_TESTS
        )
        category_results.append(("Spanish", results))

        # Category 4: French (5 tests)
        results = run_category_tests(
            "Category 4: French → Corpus Language (5 tests)", FRENCH_TESTS
        )
        category_results.append(("French", results))

        # Category 5: Arabic (5 tests)
        results = run_category_tests(
            "Category 5: Arabic → Corpus Language (5 tests)", ARABIC_TESTS
        )
        category_results.append(("Arabic", results))

        # Category 6: German (4 tests)
        results = run_category_tests(
            "Category 6: German → Corpus Language (4 tests)", GERMAN_TESTS
        )
        category_results.append(("German", results))

        # Category 7: Edge Cases (4 tests)
        results = run_category_tests(
            "Category 7: Edge Cases (4 tests)", EDGE_CASE_TESTS
        )
        category_results.append(("Edge Cases", results))

    # ── Summary ──────────────────────────────────────────────────────────
    total_passed = sum(sum(r) for _, r in category_results)
    total_tests = sum(len(r) for _, r in category_results)

    console.print("\n" + "═" * 60)
    console.print(
        f"[bold cyan]SUMMARY: {total_passed}/{total_tests} passed "
        f"({total_passed * 100 // total_tests}%)[/bold cyan]"
    )
    console.print("═" * 60)

    # Per-language breakdown table
    console.print("\n[bold]Per-Language Breakdown:[/bold]")
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Category", width=25)
    table.add_column("Passed", width=10)
    table.add_column("Status", width=8)

    for name, results in category_results:
        passed = sum(results)
        total = len(results)
        status = "[green]✅[/green]" if passed == total else "[red]❌[/red]"
        table.add_row(name, f"{passed}/{total}", status)

    console.print(table)

    if total_passed == total_tests:
        console.print(f"\n[bold green]✅ ALL {total_tests} TESTS PASSED[/bold green]")
    else:
        failed = total_tests - total_passed
        console.print(f"\n[bold red]❌ {failed} TEST(S) FAILED[/bold red]")
        sys.exit(1)


if __name__ == "__main__":
    run_all_tests()
