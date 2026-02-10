#!/usr/bin/env python3
# ruff: noqa: E402
# Test helper mutates sys.path before local imports.
"""
Unit tests for QueryTranslator module.

Tests cover:
- Native language queries (was_translated=False)
- Foreign language queries (was_translated=True)
- Heuristic pre-filter (Turkish chars skip LLM for quran)
- Heuristic pre-filter (Pure ASCII skip LLM for bible)
- Detect-only mode (corpus=None)
- Fallback on LLM failure (invalid JSON, connection error)
- Validation (empty query, invalid corpus)
- translate_response with citation preservation

Usage:
    cd backend && source ../venv/bin/activate
    set -a && source .env && set +a
    python tests/test_query_translator.py
"""

import json
import sys
from pathlib import Path
from unittest.mock import patch, Mock

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()

# Import after path setup
from src.query_translator import (
    QueryTranslator,
    TranslationError,
    TURKISH_CHARS,
    SUPPORTED_LANGUAGES,
    CORPUS_LANGUAGES,
)


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


def mock_llm_text_response(translated_text: str) -> Mock:
    """Create a mock requests.Response for text mode LLM calls."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.raise_for_status = Mock()
    mock_response.json.return_value = {
        "choices": [{"message": {"content": translated_text}}]
    }
    return mock_response


def mock_llm_invalid_json_response() -> Mock:
    """Create a mock response with invalid JSON content."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.raise_for_status = Mock()
    mock_response.json.return_value = {
        "choices": [{"message": {"content": "This is not valid JSON {broken"}}]
    }
    return mock_response


def mock_llm_empty_response() -> Mock:
    """Create a mock response with empty content."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.raise_for_status = Mock()
    mock_response.json.return_value = {"choices": [{"message": {"content": ""}}]}
    return mock_response


# ============================================================================
# TEST FUNCTIONS
# ============================================================================


def test_native_language_turkish_quran() -> bool:
    """Test Turkish query with quran corpus (heuristic: was_translated=False)."""
    console.print("\n[bold cyan]TEST: Native Language - Turkish + Quran[/bold cyan]")

    try:
        with patch("src.query_translator.llm_with_breaker") as mock_breaker:
            # Heuristic should skip LLM, so mock should NOT be called
            translator = QueryTranslator(api_key="test-key")
            result = translator.translate_query("sabır ve namaz", corpus="quran_tr")

            # Verify heuristic worked (LLM not called)
            assert not mock_breaker.called, (
                "LLM should NOT be called for Turkish + quran"
            )

            # Verify result
            assert result.detected_language == "tr", (
                f"Expected 'tr', got '{result.detected_language}'"
            )
            assert result.translated_query == "sabır ve namaz", (
                "Query should be unchanged"
            )
            assert result.was_translated is False, "was_translated should be False"

            console.print(
                "  [green]✅ PASS[/green] - Heuristic detected Turkish, skipped LLM"
            )
            return True

    except Exception as e:
        console.print(f"  [red]❌ FAIL[/red] - {e}")
        return False


def test_native_language_english_bible() -> bool:
    """Test English query with bible corpus (heuristic: was_translated=False)."""
    console.print("\n[bold cyan]TEST: Native Language - English + Bible[/bold cyan]")

    try:
        with patch("src.query_translator.llm_with_breaker") as mock_breaker:
            # Heuristic should skip LLM for pure ASCII + bible
            translator = QueryTranslator(api_key="test-key")
            result = translator.translate_query("love your neighbor", corpus="bible_ot")

            # Verify heuristic worked
            assert not mock_breaker.called, "LLM should NOT be called for ASCII + bible"

            # Verify result
            assert result.detected_language == "en", (
                f"Expected 'en', got '{result.detected_language}'"
            )
            assert result.translated_query == "love your neighbor", (
                "Query should be unchanged"
            )
            assert result.was_translated is False, "was_translated should be False"

            console.print(
                "  [green]✅ PASS[/green] - Heuristic detected English, skipped LLM"
            )
            return True

    except Exception as e:
        console.print(f"  [red]❌ FAIL[/red] - {e}")
        return False


def test_heuristic_turkish_chars_quran() -> bool:
    """Test heuristic pre-filter: Turkish chars + quran corpus skips LLM."""
    console.print("\n[bold cyan]TEST: Heuristic - Turkish chars + Quran[/bold cyan]")

    try:
        with patch("src.query_translator.llm_with_breaker") as mock_breaker:
            translator = QueryTranslator(api_key="test-key")
            result = translator.translate_query("şefaat nedir", corpus="quran")

            # Verify LLM was NOT called
            assert not mock_breaker.called, (
                "LLM should NOT be called (Turkish chars detected)"
            )

            # Verify result
            assert result.detected_language == "tr"
            assert result.translated_query == "şefaat nedir"
            assert result.was_translated is False

            console.print(
                "  [green]✅ PASS[/green] - Turkish chars detected, LLM skipped"
            )
            return True

    except Exception as e:
        console.print(f"  [red]❌ FAIL[/red] - {e}")
        return False


def test_heuristic_turkish_chars_bible_calls_llm() -> bool:
    """Test heuristic: Turkish chars + bible corpus DOES call LLM."""
    console.print(
        "\n[bold cyan]TEST: Heuristic - Turkish chars + Bible (calls LLM)[/bold cyan]"
    )

    try:
        with patch("src.query_translator.llm_with_breaker") as mock_breaker:
            # Mock LLM to return translation
            mock_breaker.return_value = mock_llm_json_response(
                detected_language="tr",
                translated_query="patience",
                was_translated=True,
            )

            translator = QueryTranslator(api_key="test-key")
            result = translator.translate_query("sabır", corpus="bible_ot")

            # Verify LLM WAS called (heuristic only for quran)
            assert mock_breaker.called, "LLM SHOULD be called for Turkish + bible"

            # Verify result
            assert result.detected_language == "tr"
            assert result.translated_query == "patience"
            assert result.was_translated is True

            console.print("  [green]✅ PASS[/green] - LLM called for Turkish + bible")
            return True

    except Exception as e:
        console.print(f"  [red]❌ FAIL[/red] - {e}")
        return False


def test_heuristic_pure_ascii_bible() -> bool:
    """Test heuristic: Pure ASCII + bible corpus skips LLM."""
    console.print("\n[bold cyan]TEST: Heuristic - Pure ASCII + Bible[/bold cyan]")

    try:
        with patch("src.query_translator.llm_with_breaker") as mock_breaker:
            translator = QueryTranslator(api_key="test-key")
            result = translator.translate_query("patience", corpus="bible_nt")

            # Verify LLM was NOT called
            assert not mock_breaker.called, (
                "LLM should NOT be called (pure ASCII + bible)"
            )

            # Verify result
            assert result.detected_language == "en"
            assert result.translated_query == "patience"
            assert result.was_translated is False

            console.print("  [green]✅ PASS[/green] - Pure ASCII detected, LLM skipped")
            return True

    except Exception as e:
        console.print(f"  [red]❌ FAIL[/red] - {e}")
        return False


def test_foreign_language_english_to_turkish() -> bool:
    """Test foreign language query: English -> Turkish for quran."""
    console.print(
        "\n[bold cyan]TEST: Foreign Language - English -> Turkish[/bold cyan]"
    )

    try:
        with patch("src.query_translator.llm_with_breaker") as mock_breaker:
            # Mock LLM to return translation
            mock_breaker.return_value = mock_llm_json_response(
                detected_language="en",
                translated_query="İslam'da sabır",
                was_translated=True,
            )

            translator = QueryTranslator(api_key="test-key")
            result = translator.translate_query("patience in Islam", corpus="quran_tr")

            # Verify LLM was called
            assert mock_breaker.called, "LLM should be called for English + quran"

            # Verify result
            assert result.detected_language == "en"
            assert result.translated_query == "İslam'da sabır"
            assert result.was_translated is True

            console.print("  [green]✅ PASS[/green] - English translated to Turkish")
            return True

    except Exception as e:
        console.print(f"  [red]❌ FAIL[/red] - {e}")
        return False


def test_foreign_language_spanish_to_english() -> bool:
    """Test foreign language query: Spanish -> English for bible."""
    console.print(
        "\n[bold cyan]TEST: Foreign Language - Spanish -> English[/bold cyan]"
    )

    try:
        with patch("src.query_translator.llm_with_breaker") as mock_breaker:
            # Mock LLM to return translation
            mock_breaker.return_value = mock_llm_json_response(
                detected_language="es",
                translated_query="love in the Bible",
                was_translated=True,
            )

            translator = QueryTranslator(api_key="test-key")
            # Use Spanish with non-ASCII chars to bypass heuristic
            result = translator.translate_query(
                "¿Qué dice la Biblia sobre el amor?", corpus="bible_ot"
            )

            # Verify result
            assert result.detected_language == "es", (
                f"Expected 'es', got '{result.detected_language}'"
            )
            assert result.translated_query == "love in the Bible", (
                f"Expected 'love in the Bible', got '{result.translated_query}'"
            )
            assert result.was_translated is True, (
                f"Expected was_translated=True, got {result.was_translated}"
            )

            console.print("  [green]✅ PASS[/green] - Spanish translated to English")
            return True

    except Exception as e:
        import traceback

        console.print(f"  [red]❌ FAIL[/red] - {e}")
        console.print(f"  [dim]{traceback.format_exc()}[/dim]")
        return False


def test_detect_only_mode() -> bool:
    """Test detect-only mode (corpus=None)."""
    console.print("\n[bold cyan]TEST: Detect-Only Mode (corpus=None)[/bold cyan]")

    try:
        with patch("src.query_translator.llm_with_breaker") as mock_breaker:
            # Mock LLM to return detection without translation
            mock_breaker.return_value = mock_llm_json_response(
                detected_language="es",
                translated_query="paciencia",
                was_translated=False,
            )

            translator = QueryTranslator(api_key="test-key")
            result = translator.translate_query("paciencia", corpus=None)

            # Verify result
            assert result.detected_language == "es"
            assert result.translated_query == "paciencia"
            assert result.was_translated is False

            console.print("  [green]✅ PASS[/green] - Detect-only mode works")
            return True

    except Exception as e:
        console.print(f"  [red]❌ FAIL[/red] - {e}")
        return False


def test_fallback_on_invalid_json() -> bool:
    """Test fallback when LLM returns invalid JSON."""
    console.print("\n[bold cyan]TEST: Fallback - Invalid JSON[/bold cyan]")

    try:
        with patch("src.query_translator.llm_with_breaker") as mock_breaker:
            # Mock LLM to return invalid JSON
            mock_breaker.return_value = mock_llm_invalid_json_response()

            translator = QueryTranslator(api_key="test-key")
            result = translator.translate_query("test query", corpus="quran_tr")

            # Verify fallback behavior
            assert result.detected_language == "tr", (
                "Should fallback to corpus language"
            )
            assert result.translated_query == "test query", (
                "Should return original query"
            )
            assert result.was_translated is False

            console.print("  [green]✅ PASS[/green] - Fallback on invalid JSON works")
            return True

    except Exception as e:
        console.print(f"  [red]❌ FAIL[/red] - {e}")
        return False


def test_fallback_on_connection_error() -> bool:
    """Test fallback when LLM connection fails after retries."""
    console.print("\n[bold cyan]TEST: Fallback - Connection Error[/bold cyan]")

    try:
        with patch("src.query_translator.llm_with_breaker") as mock_breaker:
            # Mock circuit breaker to raise CircuitBreakerError
            from pybreaker import CircuitBreakerError

            mock_breaker.side_effect = CircuitBreakerError("Circuit breaker OPEN")

            translator = QueryTranslator(api_key="test-key")

            # Should raise TranslationError
            try:
                translator.translate_query("test query", corpus="quran_tr")
                console.print(
                    "  [red]❌ FAIL[/red] - Should have raised TranslationError"
                )
                return False
            except TranslationError as e:
                assert "Circuit breaker OPEN" in str(e)
                console.print(
                    "  [green]✅ PASS[/green] - TranslationError raised on circuit breaker"
                )
                return True

    except Exception as e:
        console.print(f"  [red]❌ FAIL[/red] - {e}")
        return False


def test_validation_empty_query() -> bool:
    """Test validation: empty query raises ValueError."""
    console.print("\n[bold cyan]TEST: Validation - Empty Query[/bold cyan]")

    try:
        translator = QueryTranslator(api_key="test-key")

        # Test empty string
        try:
            translator.translate_query("", corpus="quran_tr")
            console.print(
                "  [red]❌ FAIL[/red] - Should have raised ValueError for empty query"
            )
            return False
        except ValueError as e:
            assert "must not be empty" in str(e).lower()

        # Test whitespace-only
        try:
            translator.translate_query("   ", corpus="quran_tr")
            console.print(
                "  [red]❌ FAIL[/red] - Should have raised ValueError for whitespace"
            )
            return False
        except ValueError as e:
            assert "must not be empty" in str(e).lower()

        console.print("  [green]✅ PASS[/green] - Empty query validation works")
        return True

    except Exception as e:
        console.print(f"  [red]❌ FAIL[/red] - {e}")
        return False


def test_validation_invalid_corpus() -> bool:
    """Test validation: invalid corpus raises ValueError."""
    console.print("\n[bold cyan]TEST: Validation - Invalid Corpus[/bold cyan]")

    try:
        translator = QueryTranslator(api_key="test-key")

        try:
            translator.translate_query("test query", corpus="invalid_corpus")
            console.print(
                "  [red]❌ FAIL[/red] - Should have raised ValueError for invalid corpus"
            )
            return False
        except ValueError as e:
            assert "invalid corpus" in str(e).lower()
            assert "invalid_corpus" in str(e)

        console.print("  [green]✅ PASS[/green] - Invalid corpus validation works")
        return True

    except Exception as e:
        console.print(f"  [red]❌ FAIL[/red] - {e}")
        return False


def test_translate_response_with_citations() -> bool:
    """Test translate_response preserves citations."""
    console.print(
        "\n[bold cyan]TEST: translate_response - Citation Preservation[/bold cyan]"
    )

    try:
        with patch("src.query_translator.llm_with_breaker") as mock_breaker:
            # Mock LLM to return translated text
            translated_text = "El concepto de paciencia es central en el Corán. En [Bakara:153], Allah ordena a los creyentes buscar ayuda."
            mock_breaker.return_value = mock_llm_text_response(translated_text)

            translator = QueryTranslator(api_key="test-key")

            original_text = "Sabır kavramı Kuran'da merkezi bir öneme sahiptir. [Bakara:153] ayetinde Allah, müminlere yardım dilemelerini emreder."
            result = translator.translate_response(
                text=original_text,
                target_lang="es",
                preserve_citations=True,
            )

            # Verify result
            assert "[Bakara:153]" in result, "Citation should be preserved"
            assert result == translated_text

            # Verify LLM was called with preserve_citations reminder
            # The lambda is called, so we can't directly inspect the prompt
            # But we can verify the function was called
            assert mock_breaker.called

            console.print(
                "  [green]✅ PASS[/green] - Citations preserved in translation"
            )
            return True

    except Exception as e:
        console.print(f"  [red]❌ FAIL[/red] - {e}")
        return False


def test_translate_response_empty_text() -> bool:
    """Test translate_response with empty text returns empty."""
    console.print("\n[bold cyan]TEST: translate_response - Empty Text[/bold cyan]")

    try:
        with patch("src.query_translator.llm_with_breaker") as mock_breaker:
            translator = QueryTranslator(api_key="test-key")

            # Empty string
            result = translator.translate_response("", target_lang="es")
            assert result == "", "Empty string should return empty"

            # Whitespace-only
            result = translator.translate_response("   ", target_lang="es")
            assert result == "   ", "Whitespace should return as-is"

            # Verify LLM was NOT called
            assert not mock_breaker.called, "LLM should NOT be called for empty text"

            console.print("  [green]✅ PASS[/green] - Empty text handled correctly")
            return True

    except Exception as e:
        console.print(f"  [red]❌ FAIL[/red] - {e}")
        return False


def test_constants_defined() -> bool:
    """Test that module constants are properly defined."""
    console.print("\n[bold cyan]TEST: Module Constants[/bold cyan]")

    try:
        # Verify TURKISH_CHARS
        assert isinstance(TURKISH_CHARS, str)
        assert "ğ" in TURKISH_CHARS
        assert "ş" in TURKISH_CHARS
        assert "ı" in TURKISH_CHARS

        # Verify SUPPORTED_LANGUAGES
        assert isinstance(SUPPORTED_LANGUAGES, set)
        assert "en" in SUPPORTED_LANGUAGES
        assert "tr" in SUPPORTED_LANGUAGES
        assert "es" in SUPPORTED_LANGUAGES

        # Verify CORPUS_LANGUAGES
        assert isinstance(CORPUS_LANGUAGES, dict)
        assert CORPUS_LANGUAGES["quran"] == "tr"
        assert CORPUS_LANGUAGES["quran_tr"] == "tr"
        assert CORPUS_LANGUAGES["bible"] == "en"
        assert CORPUS_LANGUAGES["bible_ot"] == "en"
        assert CORPUS_LANGUAGES["bible_nt"] == "en"
        assert CORPUS_LANGUAGES["bible_apocrypha"] == "en"

        console.print("  [green]✅ PASS[/green] - All constants defined correctly")
        return True

    except Exception as e:
        console.print(f"  [red]❌ FAIL[/red] - {e}")
        return False


# ============================================================================
# TEST RUNNER
# ============================================================================


def run_all_tests() -> None:
    """Run all tests and print summary."""
    console.print(
        Panel.fit(
            "[bold cyan]QueryTranslator Unit Tests[/bold cyan]\n"
            "[dim]Testing language detection, translation, and validation[/dim]",
            border_style="cyan",
        )
    )

    # Mock sentry_sdk to avoid initialization issues
    with patch("src.query_translator.sentry_sdk"):
        tests = [
            ("Constants", test_constants_defined),
            ("Native Language - Turkish + Quran", test_native_language_turkish_quran),
            ("Native Language - English + Bible", test_native_language_english_bible),
            ("Heuristic - Turkish chars + Quran", test_heuristic_turkish_chars_quran),
            (
                "Heuristic - Turkish chars + Bible (calls LLM)",
                test_heuristic_turkish_chars_bible_calls_llm,
            ),
            ("Heuristic - Pure ASCII + Bible", test_heuristic_pure_ascii_bible),
            (
                "Foreign Language - English -> Turkish",
                test_foreign_language_english_to_turkish,
            ),
            (
                "Foreign Language - Spanish -> English",
                test_foreign_language_spanish_to_english,
            ),
            ("Detect-Only Mode", test_detect_only_mode),
            ("Fallback - Invalid JSON", test_fallback_on_invalid_json),
            ("Fallback - Connection Error", test_fallback_on_connection_error),
            ("Validation - Empty Query", test_validation_empty_query),
            ("Validation - Invalid Corpus", test_validation_invalid_corpus),
            (
                "translate_response - Citation Preservation",
                test_translate_response_with_citations,
            ),
            ("translate_response - Empty Text", test_translate_response_empty_text),
        ]

        results = []
        for name, test_func in tests:
            passed = test_func()
            results.append((name, passed))

        # Print summary
        console.print("\n" + "=" * 80)
        console.print("[bold cyan]TEST SUMMARY[/bold cyan]")
        console.print("=" * 80 + "\n")

        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Test", width=50)
        table.add_column("Result", width=10)

        passed_count = 0
        failed_count = 0

        for name, passed in results:
            if passed:
                table.add_row(name, "[green]✅ PASS[/green]")
                passed_count += 1
            else:
                table.add_row(name, "[red]❌ FAIL[/red]")
                failed_count += 1

        console.print(table)

        console.print(f"\n[bold]Total:[/bold] {len(results)} tests")
        console.print(f"[bold green]Passed:[/bold green] {passed_count}")
        console.print(f"[bold red]Failed:[/bold red] {failed_count}")

        if failed_count == 0:
            console.print("\n[bold green]✅ ALL TESTS PASSED[/bold green]")
        else:
            console.print(f"\n[bold red]❌ {failed_count} TEST(S) FAILED[/bold red]")
            sys.exit(1)


if __name__ == "__main__":
    run_all_tests()
