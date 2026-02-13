"""Test Accept-Language header integration in API endpoints."""

import pytest
from fastapi import Request
from fastapi.testclient import TestClient

from app.i18n.detector import get_locale


@pytest.mark.asyncio
async def test_get_locale_from_accept_language_header():
    """Test locale detection from Accept-Language header."""
    # Mock request with Accept-Language header
    request = Request(
        {
            "type": "http",
            "headers": [(b"accept-language", b"en-US,en;q=0.9")],
            "query_string": b"",
        }
    )

    locale = await get_locale(request)
    assert locale == "en"


@pytest.mark.asyncio
async def test_get_locale_from_query_param():
    """Test locale detection from query parameter (highest priority)."""
    request = Request(
        {
            "type": "http",
            "headers": [(b"accept-language", b"tr-TR,tr;q=0.9")],
            "query_string": b"lang=en",
        }
    )

    locale = await get_locale(request, lang="en")
    assert locale == "en"


@pytest.mark.asyncio
async def test_get_locale_from_cookie():
    """Test locale detection from cookie."""
    request = Request(
        {
            "type": "http",
            "headers": [
                (b"accept-language", b"tr-TR,tr;q=0.9"),
                (b"cookie", b"preferred_locale=en"),
            ],
            "query_string": b"",
        }
    )

    locale = await get_locale(request)
    assert locale == "en"


@pytest.mark.asyncio
async def test_get_locale_fallback_to_default():
    """Test locale fallback to default when no locale is detected."""
    request = Request(
        {
            "type": "http",
            "headers": [(b"accept-language", b"fr-FR,fr;q=0.9")],
            "query_string": b"",
        }
    )

    locale = await get_locale(request)
    assert locale == "tr"  # Default locale


@pytest.mark.asyncio
async def test_get_locale_priority_order():
    """Test locale detection priority: query param > cookie > header > default."""
    # Query param wins
    request = Request(
        {
            "type": "http",
            "headers": [
                (b"accept-language", b"tr-TR,tr;q=0.9"),
                (b"cookie", b"preferred_locale=tr"),
            ],
            "query_string": b"lang=en",
        }
    )

    locale = await get_locale(request, lang="en")
    assert locale == "en"

    # Cookie wins over header
    request = Request(
        {
            "type": "http",
            "headers": [
                (b"accept-language", b"tr-TR,tr;q=0.9"),
                (b"cookie", b"preferred_locale=en"),
            ],
            "query_string": b"",
        }
    )

    locale = await get_locale(request)
    assert locale == "en"
