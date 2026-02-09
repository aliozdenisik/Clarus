"""
Unit tests for QueryEnhancer.extract_keywords() method.

Tests the hybrid rule-based + LLM keyword extraction with mocked LLM calls.
Covers rule-based splitting, LLM extraction, deduplication, blacklist filtering,
and selection limits.
"""

from unittest.mock import patch

import pytest

from src.query_enhancer import EnhanceResponse, KeywordSuggestion, QueryEnhancer


@pytest.fixture
def enhancer():
    """Create QueryEnhancer with mocked API key."""
    with patch.dict("os.environ", {"OPENROUTER_API_KEY": "test-key"}):
        return QueryEnhancer()


class TestRuleBasedExtraction:
    """Test rule-based keyword extraction (conjunctions and commas)."""

    def test_rule_based_conjunction_split(self, enhancer):
        """Test Turkish 've' conjunction splits into 2+ keywords."""
        result = enhancer.extract_keywords("sabır ve namaz", corpus="quran")
        assert len(result) >= 2
        assert any(kw.text == "sabır" for kw in result)
        assert any(kw.text == "namaz" for kw in result)
        assert all(kw.source == "rule_based" for kw in result)
        assert all(kw.language == "tr" for kw in result)

    def test_rule_based_english_conjunction(self, enhancer):
        """Test English 'and' conjunction splits into 2+ keywords."""
        result = enhancer.extract_keywords("patience and prayer", corpus="bible")
        assert len(result) >= 2
        assert any(kw.text == "patience" for kw in result)
        assert any(kw.text == "prayer" for kw in result)
        assert all(kw.source == "rule_based" for kw in result)
        assert all(kw.language == "en" for kw in result)

    def test_rule_based_comma_split(self, enhancer):
        """Test comma-separated query splits into 3 keywords."""
        result = enhancer.extract_keywords("sabır, namaz, oruç", corpus="quran")
        assert len(result) >= 3
        assert any(kw.text == "sabır" for kw in result)
        assert any(kw.text == "namaz" for kw in result)
        assert any(kw.text == "oruç" for kw in result)
        assert all(kw.source == "rule_based" for kw in result)

    def test_rule_based_with_conjunction(self, enhancer):
        """Test 'with' conjunction in English."""
        result = enhancer.extract_keywords("faith with works", corpus="bible")
        assert len(result) >= 2
        assert any(kw.text == "faith" for kw in result)
        assert any(kw.text == "works" for kw in result)

    def test_rule_based_or_conjunction(self, enhancer):
        """Test 'or' conjunction in English."""
        result = enhancer.extract_keywords("sin or righteousness", corpus="bible")
        assert len(result) >= 2
        assert any(kw.text == "sin" for kw in result)
        assert any(kw.text == "righteousness" for kw in result)


class TestLLMExtraction:
    """Test LLM-based keyword extraction for single-word and complex queries."""

    @patch.object(QueryEnhancer, "_call_llm_json")
    def test_single_word_returns_keyword(self, mock_llm, enhancer):
        """Test single word triggers LLM extraction."""
        mock_llm.return_value = {
            "original_language": "tr",
            "translated_query": "sabır",
            "expanded_terms": ["sebat", "direnç", "tahammül"],
            "final_search_query": "sabır sebat direnç tahammül",
        }
        result = enhancer.extract_keywords("sabır", corpus="quran")
        assert len(result) >= 1
        assert all(isinstance(kw, KeywordSuggestion) for kw in result)
        assert all(kw.source == "llm" for kw in result)

    @patch.object(QueryEnhancer, "_call_llm_json")
    def test_llm_extraction_bible_mode(self, mock_llm, enhancer):
        """Test LLM extraction in Bible mode returns English keywords."""
        mock_llm.return_value = {
            "original_language": "en",
            "translated_query": "love",
            "expanded_terms": ["charity", "affection", "devotion"],
            "final_search_query": "love charity affection devotion",
        }
        result = enhancer.extract_keywords("love", corpus="bible")
        assert len(result) >= 1
        assert all(kw.language == "en" for kw in result)
        assert all(kw.source == "llm" for kw in result)

    @patch.object(QueryEnhancer, "_call_llm_json")
    def test_llm_extraction_includes_translated_query(self, mock_llm, enhancer):
        """Test that translated query is included as keyword if different."""
        mock_llm.return_value = {
            "original_language": "tr",
            "translated_query": "merhamet",
            "expanded_terms": ["şefkat", "acıma"],
            "final_search_query": "merhamet şefkat acıma",
        }
        result = enhancer.extract_keywords("mercy", corpus="quran")
        # Should include translated_query as a keyword
        assert any(kw.text == "merhamet" for kw in result)


class TestEmptyAndWhitespace:
    """Test handling of empty and whitespace-only queries."""

    def test_empty_query_returns_empty(self, enhancer):
        """Test empty string returns empty list."""
        result = enhancer.extract_keywords("", corpus="quran")
        assert result == []

    def test_whitespace_query_returns_empty(self, enhancer):
        """Test whitespace-only query returns empty list."""
        result = enhancer.extract_keywords("   ", corpus="quran")
        assert result == []

    def test_whitespace_with_tabs_returns_empty(self, enhancer):
        """Test tabs and spaces return empty list."""
        result = enhancer.extract_keywords("\t\n  ", corpus="bible")
        assert result == []


class TestDeduplication:
    """Test keyword deduplication with Turkish character normalization."""

    @patch.object(QueryEnhancer, "_call_llm_json")
    def test_keyword_deduplication(self, mock_llm, enhancer):
        """Test that duplicate keywords are removed."""
        mock_llm.return_value = {
            "original_language": "tr",
            "translated_query": "sabır",
            "expanded_terms": ["sabır", "sabır", "direnç"],  # Duplicate "sabır"
            "final_search_query": "sabır direnç",
        }
        result = enhancer.extract_keywords("sabır", corpus="quran")
        # Count occurrences of "sabır"
        sabir_count = sum(1 for kw in result if kw.text == "sabır")
        assert sabir_count == 1  # Should appear only once

    @patch.object(QueryEnhancer, "_call_llm_json")
    def test_turkish_char_normalization_dedup(self, mock_llm, enhancer):
        """Test Turkish character normalization in deduplication."""
        mock_llm.return_value = {
            "original_language": "tr",
            "translated_query": "test",
            "expanded_terms": ["şehir", "sehir"],  # ş and s should be treated as same
            "final_search_query": "şehir sehir",
        }
        result = enhancer.extract_keywords("test", corpus="quran")
        # Should deduplicate ş and s
        assert len(result) <= 2  # At most 2 unique (after dedup)


class TestLanguageAssignment:
    """Test language assignment based on corpus."""

    def test_quran_corpus_turkish_language(self, enhancer):
        """Test corpus='quran' assigns language='tr'."""
        result = enhancer.extract_keywords("sabır ve namaz", corpus="quran")
        assert all(kw.language == "tr" for kw in result)

    def test_bible_corpus_english_language(self, enhancer):
        """Test corpus='bible' assigns language='en'."""
        result = enhancer.extract_keywords("patience and prayer", corpus="bible")
        assert all(kw.language == "en" for kw in result)


class TestSelectionLimit:
    """Test selection limit (first 7 selected, rest unselected)."""

    @patch.object(QueryEnhancer, "_call_llm_json")
    def test_max_selection_limit(self, mock_llm, enhancer):
        """Test first 7 keywords selected=True, rest selected=False."""
        mock_llm.return_value = {
            "original_language": "tr",
            "translated_query": "test",
            "expanded_terms": [f"term{i}" for i in range(10)],  # 10 terms
            "final_search_query": " ".join([f"term{i}" for i in range(10)]),
        }
        result = enhancer.extract_keywords("test", corpus="quran")

        selected_count = sum(1 for kw in result if kw.selected)
        unselected_count = sum(1 for kw in result if not kw.selected)

        # First 7 should be selected
        assert selected_count >= 7
        # Rest should be unselected
        if len(result) > 7:
            assert unselected_count > 0


class TestBlacklistFilter:
    """Test Quran blacklist filtering of English terms."""

    @patch.object(QueryEnhancer, "_call_llm_json")
    def test_quran_blacklist_filters_english(self, mock_llm, enhancer):
        """Test that English terms are filtered for Quran corpus."""
        mock_llm.return_value = {
            "original_language": "tr",
            "translated_query": "test",
            "expanded_terms": [
                "god",
                "lord",
                "sabır",
                "namaz",
            ],  # god, lord are blacklisted
            "final_search_query": "god lord sabır namaz",
        }
        result = enhancer.extract_keywords("test", corpus="quran")

        # Blacklisted terms should be removed
        assert not any(kw.text.lower() == "god" for kw in result)
        assert not any(kw.text.lower() == "lord" for kw in result)
        # Turkish terms should remain
        assert any(kw.text == "sabır" for kw in result)

    @patch.object(QueryEnhancer, "_call_llm_json")
    def test_bible_corpus_no_blacklist(self, mock_llm, enhancer):
        """Test that Bible corpus does NOT apply blacklist."""
        mock_llm.return_value = {
            "original_language": "en",
            "translated_query": "test",
            "expanded_terms": ["god", "lord", "love"],
            "final_search_query": "god lord love",
        }
        result = enhancer.extract_keywords("test", corpus="bible")

        # Bible mode should NOT filter "god" and "lord"
        assert any(kw.text.lower() == "god" for kw in result)
        assert any(kw.text.lower() == "lord" for kw in result)


class TestLLMFailureFallback:
    """Test fallback behavior when LLM fails."""

    @patch.object(QueryEnhancer, "_call_llm_json")
    def test_llm_failure_fallback(self, mock_llm, enhancer):
        """Test fallback to simple word split when LLM fails."""
        mock_llm.return_value = {}  # Empty response simulates LLM failure

        result = enhancer.extract_keywords("sabır namaz", corpus="quran")

        # Should fall back to word splitting
        assert len(result) > 0
        assert all(kw.source == "fallback" for kw in result)

    @patch.object(QueryEnhancer, "_call_llm_json")
    def test_llm_exception_fallback(self, mock_llm, enhancer):
        """Test fallback when LLM raises exception."""
        mock_llm.side_effect = Exception("API Error")

        result = enhancer.extract_keywords("sabır namaz", corpus="quran")

        # Should fall back to word splitting
        assert len(result) > 0
        assert all(kw.source == "fallback" for kw in result)


class TestPydanticModels:
    """Test Pydantic model validation."""

    def test_keyword_suggestion_model(self):
        """Test KeywordSuggestion Pydantic model validates correctly."""
        kw = KeywordSuggestion(
            text="sabır", language="tr", confidence=0.95, selected=True, source="llm"
        )
        assert kw.text == "sabır"
        assert kw.language == "tr"
        assert kw.confidence == 0.95
        assert kw.selected is True
        assert kw.source == "llm"

    def test_keyword_suggestion_defaults(self):
        """Test KeywordSuggestion default values."""
        kw = KeywordSuggestion(text="test")
        assert kw.language == "tr"
        assert kw.confidence == 1.0
        assert kw.selected is True
        assert kw.source == "llm"

    def test_keyword_suggestion_confidence_validation(self):
        """Test KeywordSuggestion confidence bounds validation."""
        # Valid: 0.0 to 1.0
        kw = KeywordSuggestion(text="test", confidence=0.5)
        assert kw.confidence == 0.5

        # Invalid: > 1.0 should raise
        with pytest.raises(ValueError):
            KeywordSuggestion(text="test", confidence=1.5)

    def test_enhance_response_model(self):
        """Test EnhanceResponse Pydantic model validates correctly."""
        keywords = [
            KeywordSuggestion(text="sabır", language="tr"),
            KeywordSuggestion(text="namaz", language="tr"),
        ]
        response = EnhanceResponse(
            original_query="sabır ve namaz", keywords=keywords, corpus="quran"
        )
        assert response.original_query == "sabır ve namaz"
        assert len(response.keywords) == 2
        assert response.corpus == "quran"

    def test_enhance_response_defaults(self):
        """Test EnhanceResponse default values."""
        response = EnhanceResponse(original_query="test")
        assert response.original_query == "test"
        assert response.keywords == []
        assert response.corpus == "bible"


class TestIntegration:
    """Integration tests combining multiple features."""

    def test_rule_based_with_dedup_and_selection(self, enhancer):
        """Test rule-based extraction with deduplication and selection limit."""
        # Create a query that will produce many keywords
        result = enhancer.extract_keywords("sabır ve namaz ve oruç ve zekât ve hac", corpus="quran")

        # Should have multiple keywords
        assert len(result) >= 5
        # All should be rule-based
        assert all(kw.source == "rule_based" for kw in result)
        # First 7 should be selected
        selected = [kw for kw in result if kw.selected]
        assert len(selected) >= 5

    @patch.object(QueryEnhancer, "_call_llm_json")
    def test_llm_with_blacklist_and_selection(self, mock_llm, enhancer):
        """Test LLM extraction with blacklist and selection limit."""
        mock_llm.return_value = {
            "original_language": "tr",
            "translated_query": "test",
            "expanded_terms": [
                "god",
                "lord",
                "sabır",
                "namaz",
                "oruç",
                "zekât",
                "hac",
                "dua",
                "tövbe",
            ],
            "final_search_query": "god lord sabır namaz oruç zekât hac dua tövbe",
        }
        result = enhancer.extract_keywords("test", corpus="quran")

        # Blacklisted terms should be removed
        assert not any(kw.text.lower() in ["god", "lord"] for kw in result)
        # Turkish terms should remain
        assert any(kw.text == "sabır" for kw in result)
        # Selection limit should apply
        selected = [kw for kw in result if kw.selected]
        assert len(selected) <= 7
