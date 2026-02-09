"""Test suite for verse reference parser.

Tests cover:
- Quran: numeric (2:183), Turkish (Bakara 183), ranges, multiple verses
- Bible: book chapter:verse format (Genesis 1:1), ranges
- Error handling: invalid formats, out-of-bounds, range limits
- Edge cases: whitespace, case-insensitivity, Turkish normalization
"""

import json
import sys
from pathlib import Path

import pytest

# Add backend to path for imports
sys.path.insert(0, "/home/freyja/qdrant/backend")

from src.verse_parser import (
    ParsedReference,
    ParseError,
    parse_verse_reference,
)

# Load test data
TEST_DATA_PATH = Path(__file__).parent / "verse_lookup_test_data.json"
with open(TEST_DATA_PATH, "r", encoding="utf-8") as f:
    TEST_DATA = json.load(f)


def get_test_cases(category: str) -> list[dict]:
    """Get test cases by category."""
    return [tc for tc in TEST_DATA["test_cases"] if tc["category"] == category]


class TestQuranSingleVerse:
    """Test Quran single verse parsing."""

    @pytest.mark.parametrize(
        "test_case",
        get_test_cases("quran_single"),
        ids=lambda tc: tc["id"],
    )
    def test_quran_single_verse(self, test_case):
        """Test single verse parsing for Quran."""
        result = parse_verse_reference(test_case["input"])
        expected = test_case["expected"]

        assert isinstance(result, ParsedReference)
        assert result.source == expected["source"]
        assert result.surah_id == expected["surah_id"]
        assert result.verses == expected["verses"]
        assert result.book_id is None
        assert result.chapter is None


class TestQuranRange:
    """Test Quran range parsing."""

    @pytest.mark.parametrize(
        "test_case",
        get_test_cases("quran_range"),
        ids=lambda tc: tc["id"],
    )
    def test_quran_range(self, test_case):
        """Test range parsing for Quran."""
        result = parse_verse_reference(test_case["input"])
        expected = test_case["expected"]

        assert isinstance(result, ParsedReference)
        assert result.source == expected["source"]
        assert result.surah_id == expected["surah_id"]
        assert result.verses == expected["verses"]


class TestQuranMultiple:
    """Test Quran multiple verse parsing."""

    @pytest.mark.parametrize(
        "test_case",
        get_test_cases("quran_multiple"),
        ids=lambda tc: tc["id"],
    )
    def test_quran_multiple(self, test_case):
        """Test multiple verse parsing for Quran."""
        result = parse_verse_reference(test_case["input"])
        expected = test_case["expected"]

        assert isinstance(result, ParsedReference)
        assert result.source == expected["source"]
        assert result.surah_id == expected["surah_id"]
        assert result.verses == expected["verses"]


class TestQuranErrors:
    """Test Quran error handling."""

    @pytest.mark.parametrize(
        "test_case",
        get_test_cases("quran_error"),
        ids=lambda tc: tc["id"],
    )
    def test_quran_errors(self, test_case):
        """Test error cases for Quran."""
        result = parse_verse_reference(test_case["input"])
        expected = test_case["expected"]

        assert isinstance(result, ParseError)
        assert result.code == expected["error"]
        assert result.input == test_case["input"]


class TestBibleSingleVerse:
    """Test Bible single verse parsing."""

    @pytest.mark.parametrize(
        "test_case",
        get_test_cases("bible_single"),
        ids=lambda tc: tc["id"],
    )
    def test_bible_single_verse(self, test_case):
        """Test single verse parsing for Bible."""
        result = parse_verse_reference(test_case["input"])
        expected = test_case["expected"]

        assert isinstance(result, ParsedReference)
        assert result.source == expected["source"]
        assert result.book_id == expected["book_id"]
        assert result.chapter == expected["chapter"]
        assert result.verses == expected["verses"]
        assert result.surah_id is None


class TestBibleRange:
    """Test Bible range parsing."""

    @pytest.mark.parametrize(
        "test_case",
        get_test_cases("bible_range"),
        ids=lambda tc: tc["id"],
    )
    def test_bible_range(self, test_case):
        """Test range parsing for Bible."""
        result = parse_verse_reference(test_case["input"])
        expected = test_case["expected"]

        assert isinstance(result, ParsedReference)
        assert result.source == expected["source"]
        assert result.book_id == expected["book_id"]
        assert result.chapter == expected["chapter"]
        assert result.verses == expected["verses"]


class TestBibleErrors:
    """Test Bible error handling."""

    @pytest.mark.parametrize(
        "test_case",
        get_test_cases("bible_error"),
        ids=lambda tc: tc["id"],
    )
    def test_bible_errors(self, test_case):
        """Test error cases for Bible."""
        result = parse_verse_reference(test_case["input"])
        expected = test_case["expected"]

        assert isinstance(result, ParseError)
        assert result.code == expected["error"]
        assert result.input == test_case["input"]


class TestEdgeCases:
    """Test edge cases: whitespace, case-insensitivity, normalization."""

    @pytest.mark.parametrize(
        "test_case",
        get_test_cases("edge_case"),
        ids=lambda tc: tc["id"],
    )
    def test_edge_cases(self, test_case):
        """Test edge cases."""
        result = parse_verse_reference(test_case["input"])
        expected = test_case["expected"]

        assert isinstance(result, ParsedReference)
        assert result.source == expected["source"]

        if result.source == "quran":
            assert result.surah_id == expected["surah_id"]
            assert result.verses == expected["verses"]
        else:  # bible
            assert result.book_id == expected["book_id"]
            assert result.chapter == expected["chapter"]
            assert result.verses == expected["verses"]


class TestParserReturnTypes:
    """Test that parser returns correct types."""

    def test_valid_input_returns_parsed_reference(self):
        """Valid input should return ParsedReference."""
        result = parse_verse_reference("Bakara 183")
        assert isinstance(result, ParsedReference)

    def test_invalid_input_returns_parse_error(self):
        """Invalid input should return ParseError."""
        result = parse_verse_reference("invalid format")
        assert isinstance(result, ParseError)

    def test_out_of_bounds_returns_parse_error(self):
        """Out of bounds input should return ParseError."""
        result = parse_verse_reference("Bakara 300")
        assert isinstance(result, ParseError)


class TestParsedReferenceFields:
    """Test ParsedReference field population."""

    def test_quran_reference_has_correct_fields(self):
        """Quran reference should populate surah fields."""
        result = parse_verse_reference("Bakara 183")
        assert result.source == "quran"
        assert result.surah_id == 2
        assert result.surah_name == "Bakara"
        assert result.verses == [183]
        # Bible fields should be None
        assert result.book_id is None
        assert result.book_name is None
        assert result.testament is None
        assert result.chapter is None

    def test_bible_reference_has_correct_fields(self):
        """Bible reference should populate book fields."""
        result = parse_verse_reference("Genesis 1:1")
        assert result.source == "bible"
        assert result.book_id == 1
        assert result.book_name == "Genesis"
        assert result.testament == "OT"
        assert result.chapter == 1
        assert result.verses == [1]
        # Quran fields should be None
        assert result.surah_id is None
        assert result.surah_name is None


class TestParseErrorFields:
    """Test ParseError field population."""

    def test_parse_error_has_required_fields(self):
        """ParseError should have code, message, and input."""
        result = parse_verse_reference("invalid format")
        assert isinstance(result, ParseError)
        assert result.code == "INVALID_FORMAT"
        assert isinstance(result.message, str)
        assert len(result.message) > 0
        assert result.input == "invalid format"

    def test_verse_out_of_bounds_error_message(self):
        """Out of bounds error should have descriptive message."""
        result = parse_verse_reference("Bakara 300")
        assert isinstance(result, ParseError)
        assert result.code == "VERSE_OUT_OF_BOUNDS"
        assert "286" in result.message  # Max verse count for Bakara
        assert "300" in result.message  # Requested verse


class TestRangeLimits:
    """Test range and multiple reference limits."""

    def test_range_exactly_10_verses_is_valid(self):
        """Range of exactly 10 verses should be valid."""
        result = parse_verse_reference("2:1-10")
        assert isinstance(result, ParsedReference)
        assert len(result.verses) == 10

    def test_range_11_verses_is_error(self):
        """Range of 11 verses should return error."""
        result = parse_verse_reference("2:1-11")
        assert isinstance(result, ParseError)
        assert result.code == "RANGE_TOO_LARGE"

    def test_exactly_5_multiple_refs_is_valid(self):
        """Exactly 5 multiple refs should be valid."""
        result = parse_verse_reference("2:1,2,3,4,5")
        assert isinstance(result, ParsedReference)
        assert len(result.verses) == 5

    def test_6_multiple_refs_is_error(self):
        """6 multiple refs should return error."""
        result = parse_verse_reference("2:1,2,3,4,5,6")
        assert isinstance(result, ParseError)
        assert result.code == "TOO_MANY_REFS"


class TestTurkishNormalization:
    """Test Turkish character normalization."""

    def test_turkish_chars_normalized(self):
        """Turkish special characters should be normalized."""
        # Fâtiha with circumflex should match Fatiha
        result1 = parse_verse_reference("Fâtiha 1")
        result2 = parse_verse_reference("Fatiha 1")
        assert result1.surah_id == result2.surah_id == 1

    def test_case_insensitive_turkish(self):
        """Turkish names should be case-insensitive."""
        result1 = parse_verse_reference("BAKARA 183")
        result2 = parse_verse_reference("bakara 183")
        result3 = parse_verse_reference("Bakara 183")
        assert result1.surah_id == result2.surah_id == result3.surah_id == 2


class TestBibleBookNames:
    """Test Bible book name parsing."""

    def test_numbered_books(self):
        """Books with numbers should parse correctly."""
        result = parse_verse_reference("1 Samuel 1:1")
        assert result.book_id == 9
        assert result.book_name == "1 Samuel"

    def test_multi_word_books(self):
        """Multi-word book names should parse correctly."""
        result = parse_verse_reference("Song of Solomon 1:1")
        assert result.book_id == 22
        assert result.book_name == "Song of Solomon"

    def test_revelation_full_name(self):
        """Revelation of John should parse correctly."""
        result = parse_verse_reference("Revelation of John 1:1")
        assert result.book_id == 66
        assert result.book_name == "Revelation of John"
