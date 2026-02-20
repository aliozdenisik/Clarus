from __future__ import annotations

import inspect

import pytest

from app.api.stream import stream_compare
from app.schemas.keyword_search import KeywordSearchRequest


class TestKeywordSearchXSSRejection:
    def test_plain_arabic_query_is_accepted(self) -> None:
        req = KeywordSearchRequest(query="كتب")
        assert req.query == "كتب"

    def test_buckwalter_query_is_accepted(self) -> None:
        req = KeywordSearchRequest(query="ktb")
        assert req.query == "ktb"

    def test_script_tag_payload_is_rejected(self) -> None:
        with pytest.raises(ValueError, match="HTML or script content"):
            KeywordSearchRequest(query="<script>alert(1)</script>")

    def test_img_onerror_payload_is_rejected(self) -> None:
        with pytest.raises(ValueError, match="HTML or script content"):
            KeywordSearchRequest(query='<img src=x onerror="alert(1)">')

    def test_javascript_protocol_payload_is_rejected(self) -> None:
        with pytest.raises(ValueError, match="HTML or script content"):
            KeywordSearchRequest(query="javascript:alert(1)")

    def test_mixed_html_and_text_is_rejected(self) -> None:
        with pytest.raises(ValueError, match="HTML or script content"):
            KeywordSearchRequest(query="<b>bold</b>")

    def test_word_filter_accepts_none(self) -> None:
        req = KeywordSearchRequest(query="صلو", word_filter=None)
        assert req.word_filter is None

    def test_word_filter_accepts_valid_string(self) -> None:
        req = KeywordSearchRequest(query="صلو", word_filter="صَلَّى")
        assert req.word_filter == "صَلَّى"


class TestStreamCompareAuthOrdering:
    def test_auth_check_appears_before_collection_validation_in_source(self) -> None:
        source = inspect.getsource(stream_compare)
        auth_pos = source.index("get_current_user_from_sse")
        collection_validation_pos = source.index("At least 2 valid collections required")
        assert auth_pos < collection_validation_pos, (
            "get_current_user_from_sse must be called before collection validation "
            "to ensure unauthenticated requests always receive 401, not 400"
        )

    def test_rate_limit_appears_before_collection_validation_in_source(self) -> None:
        source = inspect.getsource(stream_compare)
        rate_limit_pos = source.index("check_rate_limit")
        collection_validation_pos = source.index("At least 2 valid collections required")
        assert rate_limit_pos < collection_validation_pos, (
            "check_rate_limit must be called before collection validation"
        )
