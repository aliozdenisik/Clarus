"""
Unit tests for etymology API endpoints (Issue #60).

Tests cover:
- GET /api/etymology/{root} - Root etymology lookup
- GET /api/quran/verses/{surah_id}/{ayah_number}/words - Verse word tokenization
- Response structure and field validation
- Error handling (404 for unknown roots, invalid verse references)

Uses httpx.AsyncClient with ASGITransport for proper async event loop handling
with SQLAlchemy async database operations (avoids TestClient event loop conflicts).
"""

# pyright: reportMissingImports=false

import sys

import pytest
from httpx import ASGITransport, AsyncClient

# Add backend to path for imports
sys.path.insert(0, "/home/freyja/qdrant/backend")

from app.db import engine
from app.main import app


class TestEtymologyEndpoint:
    """Test GET /api/etymology/{root} endpoint."""

    @pytest.fixture(autouse=True)
    async def setup_client(self):
        self.client = AsyncClient(transport=ASGITransport(app=app), base_url="http://test")
        yield
        await self.client.aclose()
        await engine.dispose()

    async def test_etymology_valid_arabic_root(self):
        """GET /api/etymology/كتب should return 200 with root field."""
        response = await self.client.get("/api/etymology/كتب")
        assert response.status_code == 200

        data = response.json()
        assert "root" in data
        assert data["root"] == "كتب"

    async def test_etymology_valid_buckwalter_root(self):
        """GET /api/etymology/ktb should return 200 with root field."""
        response = await self.client.get("/api/etymology/ktb")
        assert response.status_code == 200

        data = response.json()
        assert "root_buckwalter" in data
        assert data["root_buckwalter"] == "ktb"

    async def test_etymology_unknown_root_404(self):
        """GET /api/etymology/ZZZZZ should return 404."""
        response = await self.client.get("/api/etymology/ZZZZZ")
        assert response.status_code == 404

    async def test_etymology_response_has_required_fields(self):
        """Response should have root, root_buckwalter, source, confidence fields."""
        response = await self.client.get("/api/etymology/كتب")
        assert response.status_code == 200

        data = response.json()
        required_fields = ["root", "root_buckwalter", "source", "confidence"]
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"

    async def test_etymology_morphological_forms_is_list(self):
        """morphological_forms field should be a list."""
        response = await self.client.get("/api/etymology/كتب")
        assert response.status_code == 200

        data = response.json()
        assert "morphological_forms" in data
        assert isinstance(data["morphological_forms"], list)

    async def test_etymology_quran_frequency_positive(self):
        """quran_frequency should be positive for known root."""
        response = await self.client.get("/api/etymology/كتب")
        assert response.status_code == 200

        data = response.json()
        assert "quran_frequency" in data
        assert isinstance(data["quran_frequency"], int)
        assert data["quran_frequency"] > 0

    async def test_etymology_definition_en_is_string(self):
        """definition_en should be a string."""
        response = await self.client.get("/api/etymology/كتب")
        assert response.status_code == 200

        data = response.json()
        assert "definition_en" in data
        if data["definition_en"] is not None:
            assert isinstance(data["definition_en"], str)
            assert len(data["definition_en"]) > 0

    async def test_etymology_definition_tr_is_string(self):
        """definition_tr should be a string."""
        response = await self.client.get("/api/etymology/كتب")
        assert response.status_code == 200

        data = response.json()
        assert "definition_tr" in data
        if data["definition_tr"] is not None:
            assert isinstance(data["definition_tr"], str)
            assert len(data["definition_tr"]) > 0

    async def test_etymology_confidence_valid_enum(self):
        """confidence field should be one of: high, medium, low."""
        response = await self.client.get("/api/etymology/كتب")
        assert response.status_code == 200

        data = response.json()
        assert "confidence" in data
        assert data["confidence"] in ["high", "medium", "low"]

    async def test_etymology_source_valid_enum(self):
        """source field should be one of: lane, corpus_only."""
        response = await self.client.get("/api/etymology/كتب")
        assert response.status_code == 200

        data = response.json()
        assert "source" in data
        assert data["source"] in ["lane", "corpus_only"]


class TestVerseWordsEndpoint:
    """Test GET /api/quran/verses/{surah_id}/{ayah_number}/words endpoint."""

    @pytest.fixture(autouse=True)
    async def setup_client(self):
        self.client = AsyncClient(transport=ASGITransport(app=app), base_url="http://test")
        yield
        await self.client.aclose()
        await engine.dispose()

    async def test_verse_words_valid_verse(self):
        """GET /api/quran/verses/1/1/words should return 200 with words array."""
        response = await self.client.get("/api/quran/verses/1/1/words")
        assert response.status_code == 200

        data = response.json()
        assert "words" in data
        assert isinstance(data["words"], list)
        assert len(data["words"]) > 0

    async def test_verse_words_invalid_surah_404(self):
        """GET /api/quran/verses/999/1/words should return 422."""
        response = await self.client.get("/api/quran/verses/999/1/words")
        assert response.status_code == 422

        data = response.json()
        assert "detail" in data
        assert isinstance(data["detail"], list)

    async def test_verse_words_invalid_ayah_404(self):
        """GET /api/quran/verses/1/999/words should return 404 (ayah out of bounds)."""
        response = await self.client.get("/api/quran/verses/1/999/words")
        assert response.status_code == 404

        data = response.json()
        assert "detail" in data
        detail = data["detail"]
        assert detail["success"] is False
        assert detail["error"] == "AYAH_OUT_OF_BOUNDS"

    async def test_verse_words_has_etymology_flag(self):
        """At least one word should have has_etymology=true for Al-Fatihah 1:1."""
        response = await self.client.get("/api/quran/verses/1/1/words")
        assert response.status_code == 200

        data = response.json()
        words = data["words"]
        assert any(word.get("has_etymology") is True for word in words)

    async def test_verse_words_response_structure(self):
        """Response should have surah_id, ayah_number, words, word_count fields."""
        response = await self.client.get("/api/quran/verses/1/1/words")
        assert response.status_code == 200

        data = response.json()
        required_fields = ["surah_id", "ayah_number", "words", "word_count"]
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"

    async def test_verse_words_word_structure(self):
        """Each word should have position, token, root fields."""
        response = await self.client.get("/api/quran/verses/1/1/words")
        assert response.status_code == 200

        data = response.json()
        words = data["words"]
        assert len(words) > 0

        first_word = words[0]
        required_word_fields = ["position", "token", "has_etymology"]
        for field in required_word_fields:
            assert field in first_word, f"Missing required word field: {field}"

    async def test_verse_words_positions_sequential(self):
        """Word positions should be sequential starting from 1."""
        response = await self.client.get("/api/quran/verses/1/1/words")
        assert response.status_code == 200

        data = response.json()
        words = data["words"]
        positions = [word["position"] for word in words]
        assert positions == list(range(1, len(words) + 1))

    async def test_verse_words_count_matches_array_length(self):
        """word_count field should match length of words array."""
        response = await self.client.get("/api/quran/verses/1/1/words")
        assert response.status_code == 200

        data = response.json()
        assert data["word_count"] == len(data["words"])


class TestEtymologyIntegration:
    """Integration tests for etymology API endpoints."""

    @pytest.fixture(autouse=True)
    async def setup_client(self):
        self.client = AsyncClient(transport=ASGITransport(app=app), base_url="http://test")
        yield
        await self.client.aclose()
        await engine.dispose()

    async def test_verse_words_to_etymology_flow(self):
        """Should be able to fetch verse words and then etymology for a word."""
        # Step 1: Get verse words
        verse_response = await self.client.get("/api/quran/verses/1/1/words")
        assert verse_response.status_code == 200

        verse_data = verse_response.json()
        words = verse_data["words"]

        # Step 2: Find a word with etymology
        word_with_etymology = next((w for w in words if w.get("has_etymology")), None)
        assert word_with_etymology is not None, "No word with etymology found"

        root = word_with_etymology.get("root")
        assert root is not None, "Word with etymology has no root"

        # Step 3: Fetch etymology
        etymology_response = await self.client.get(f"/api/etymology/{root}")
        assert etymology_response.status_code == 200

        etymology_data = etymology_response.json()
        assert etymology_data["root"] == root


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
