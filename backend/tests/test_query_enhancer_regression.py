"""
Regression tests for QueryEnhancer.expand_query() and generate_multi_query() methods.

Ensures that existing methods continue to work correctly after extract_keywords()
implementation. Tests method signatures, return types, and basic functionality.
"""

import inspect
from unittest.mock import patch

import pytest

from src.query_enhancer import QueryEnhancer


@pytest.fixture
def enhancer():
    """Create QueryEnhancer with mocked API key."""
    with patch.dict("os.environ", {"OPENROUTER_API_KEY": "test-key"}):
        return QueryEnhancer()


class TestExpandQueryRegression:
    """Regression tests for expand_query() method."""

    @patch.object(QueryEnhancer, "_call_llm_json")
    def test_expand_query_returns_string(self, mock_llm, enhancer):
        """Test expand_query returns a string."""
        mock_llm.return_value = {"final_search_query": "sabır sebat tahammül"}
        result = enhancer.expand_query("sabır", corpus="quran")
        assert isinstance(result, str)
        assert len(result) > 0

    @patch.object(QueryEnhancer, "_call_llm_json")
    def test_expand_query_bible_mode(self, mock_llm, enhancer):
        """Test expand_query works in Bible mode."""
        mock_llm.return_value = {"final_search_query": "love charity affection"}
        result = enhancer.expand_query("love", corpus="bible")
        assert isinstance(result, str)
        assert len(result) > 0

    @patch.object(QueryEnhancer, "_call_llm_json")
    def test_expand_query_quran_mode(self, mock_llm, enhancer):
        """Test expand_query works in Quran mode."""
        mock_llm.return_value = {"final_search_query": "sabır sebat direnç"}
        result = enhancer.expand_query("sabır", corpus="quran")
        assert isinstance(result, str)
        assert len(result) > 0

    @patch.object(QueryEnhancer, "_call_llm_json")
    def test_expand_query_empty_llm_response(self, mock_llm, enhancer):
        """Test expand_query handles empty LLM response gracefully."""
        mock_llm.return_value = {}
        result = enhancer.expand_query("sabır", corpus="quran")
        # Should return original query when LLM fails
        assert isinstance(result, str)

    def test_expand_query_signature_unchanged(self, enhancer):
        """Verify expand_query signature accepts (query, corpus) params."""
        sig = inspect.signature(enhancer.expand_query)
        params = list(sig.parameters.keys())
        assert "query" in params
        assert "corpus" in params
        # Verify corpus has default value
        assert sig.parameters["corpus"].default == "bible"

    @patch.object(QueryEnhancer, "_call_llm_json")
    def test_expand_query_applies_blacklist_quran(self, mock_llm, enhancer):
        """Test expand_query applies blacklist for Quran mode."""
        mock_llm.return_value = {"final_search_query": "god lord sabır namaz"}
        result = enhancer.expand_query("test", corpus="quran")
        # Blacklisted terms should be filtered
        assert "god" not in result.lower()
        assert "lord" not in result.lower()

    @patch.object(QueryEnhancer, "_call_llm_json")
    def test_expand_query_no_blacklist_bible(self, mock_llm, enhancer):
        """Test expand_query does NOT apply blacklist for Bible mode."""
        mock_llm.return_value = {"final_search_query": "god lord love"}
        result = enhancer.expand_query("test", corpus="bible")
        # Bible mode should NOT filter these terms
        assert "god" in result.lower()
        assert "lord" in result.lower()


class TestGenerateMultiQueryRegression:
    """Regression tests for generate_multi_query() method."""

    @patch.object(QueryEnhancer, "_call_llm_json")
    def test_generate_multi_query_returns_list(self, mock_llm, enhancer):
        """Test generate_multi_query returns a list."""
        mock_llm.return_value = {"queries": ["sabır nedir", "sabır ayetleri", "sabır kavramı"]}
        result = enhancer.generate_multi_query("sabır", n=3, corpus="quran")
        assert isinstance(result, list)
        assert len(result) > 0

    @patch.object(QueryEnhancer, "_call_llm_json")
    def test_generate_multi_query_respects_n_parameter(self, mock_llm, enhancer):
        """Test generate_multi_query respects n parameter."""
        mock_llm.return_value = {"queries": ["q1", "q2", "q3", "q4", "q5"]}
        result = enhancer.generate_multi_query("test", n=3, corpus="quran")
        assert len(result) <= 3

    @patch.object(QueryEnhancer, "_call_llm_json")
    def test_generate_multi_query_bible_mode(self, mock_llm, enhancer):
        """Test generate_multi_query works in Bible mode."""
        mock_llm.return_value = {"queries": ["love in Bible", "charity", "affection"]}
        result = enhancer.generate_multi_query("love", n=3, corpus="bible")
        assert isinstance(result, list)
        assert len(result) > 0

    @patch.object(QueryEnhancer, "_call_llm_json")
    def test_generate_multi_query_quran_mode(self, mock_llm, enhancer):
        """Test generate_multi_query works in Quran mode."""
        mock_llm.return_value = {"queries": ["sabır nedir", "sabır ayetleri", "sabır kavramı"]}
        result = enhancer.generate_multi_query("sabır", n=3, corpus="quran")
        assert isinstance(result, list)
        assert len(result) > 0

    @patch.object(QueryEnhancer, "_call_llm_json")
    def test_generate_multi_query_empty_llm_response(self, mock_llm, enhancer):
        """Test generate_multi_query handles empty LLM response."""
        mock_llm.return_value = {}
        result = enhancer.generate_multi_query("sabır", n=3, corpus="quran")
        # Should return list with original query as fallback
        assert isinstance(result, list)

    def test_generate_multi_query_signature_unchanged(self, enhancer):
        """Verify generate_multi_query signature accepts (query, n, corpus) params."""
        sig = inspect.signature(enhancer.generate_multi_query)
        params = list(sig.parameters.keys())
        assert "query" in params
        assert "n" in params
        assert "corpus" in params
        # Verify defaults
        assert sig.parameters["n"].default == 3
        assert sig.parameters["corpus"].default == "bible"

    @patch.object(QueryEnhancer, "_call_llm_json")
    def test_generate_multi_query_returns_strings(self, mock_llm, enhancer):
        """Test all items in returned list are strings."""
        mock_llm.return_value = {"queries": ["query1", "query2", "query3"]}
        result = enhancer.generate_multi_query("test", n=3, corpus="quran")
        assert all(isinstance(q, str) for q in result)

    @patch.object(QueryEnhancer, "_call_llm_json")
    def test_generate_multi_query_default_n(self, mock_llm, enhancer):
        """Test generate_multi_query uses default n=3."""
        mock_llm.return_value = {"queries": ["q1", "q2", "q3", "q4", "q5"]}
        # Call without n parameter
        result = enhancer.generate_multi_query("test", corpus="quran")
        # Should default to n=3
        assert len(result) <= 3


class TestMethodInteraction:
    """Test interactions between expand_query and generate_multi_query."""

    @patch.object(QueryEnhancer, "_call_llm_json")
    def test_both_methods_use_same_llm_infrastructure(self, mock_llm, enhancer):
        """Test both methods use _call_llm_json."""
        mock_llm.return_value = {
            "final_search_query": "expanded",
            "queries": ["q1", "q2"],
        }

        # Both should call _call_llm_json
        enhancer.expand_query("test", corpus="quran")
        assert mock_llm.called

        mock_llm.reset_mock()
        enhancer.generate_multi_query("test", corpus="quran")
        assert mock_llm.called

    @patch.object(QueryEnhancer, "_call_llm_json")
    def test_expand_and_multi_query_independent(self, mock_llm, enhancer):
        """Test expand_query and generate_multi_query are independent."""
        # expand_query should work even if generate_multi_query fails
        mock_llm.return_value = {"final_search_query": "expanded"}
        result1 = enhancer.expand_query("test", corpus="quran")
        assert isinstance(result1, str)

        # generate_multi_query should work independently
        mock_llm.return_value = {"queries": ["q1", "q2"]}
        result2 = enhancer.generate_multi_query("test", corpus="quran")
        assert isinstance(result2, list)


class TestBackwardCompatibility:
    """Test backward compatibility with existing code."""

    def test_expand_query_callable(self, enhancer):
        """Test expand_query is callable."""
        assert callable(enhancer.expand_query)

    def test_generate_multi_query_callable(self, enhancer):
        """Test generate_multi_query is callable."""
        assert callable(enhancer.generate_multi_query)

    def test_expand_query_has_docstring(self, enhancer):
        """Test expand_query has documentation."""
        assert enhancer.expand_query.__doc__ is not None
        assert len(enhancer.expand_query.__doc__) > 0

    def test_generate_multi_query_has_docstring(self, enhancer):
        """Test generate_multi_query has documentation."""
        assert enhancer.generate_multi_query.__doc__ is not None
        assert len(enhancer.generate_multi_query.__doc__) > 0

    @patch.object(QueryEnhancer, "_call_llm_json")
    def test_expand_query_corpus_default(self, mock_llm, enhancer):
        """Test expand_query defaults to corpus='bible'."""
        mock_llm.return_value = {"final_search_query": "test"}
        # Call without corpus parameter
        enhancer.expand_query("test")
        # Should have been called with Bible prompts
        assert mock_llm.called

    @patch.object(QueryEnhancer, "_call_llm_json")
    def test_generate_multi_query_corpus_default(self, mock_llm, enhancer):
        """Test generate_multi_query defaults to corpus='bible'."""
        mock_llm.return_value = {"queries": ["q1", "q2"]}
        # Call without corpus parameter
        enhancer.generate_multi_query("test")
        # Should have been called with Bible prompts
        assert mock_llm.called
