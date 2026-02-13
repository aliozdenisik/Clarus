"""
Tests for error message i18n support.

Verifies that error messages are localized correctly.
"""

from app.i18n.messages import get_error_message
from app.middleware.error_handler import (
    AuthenticationError,
    NotFoundError,
    RateLimitError,
    ValidationError,
)


class TestErrorMessageCatalog:
    """Test error message catalog returns correct localized messages."""

    def test_auth_failed_english(self):
        message = get_error_message("auth_failed", "en")
        assert message == "Authentication failed"

    def test_auth_failed_turkish(self):
        message = get_error_message("auth_failed", "tr")
        assert message == "Kimlik dogrulama basarisiz"

    def test_rate_limit_english(self):
        message = get_error_message("rate_limit", "en")
        assert message == "Daily query limit reached"

    def test_rate_limit_turkish(self):
        message = get_error_message("rate_limit", "tr")
        assert message == "Gunluk sorgu limitine ulastiniz"

    def test_not_found_english(self):
        message = get_error_message("not_found", "en")
        assert message == "Resource not found"

    def test_not_found_turkish(self):
        message = get_error_message("not_found", "tr")
        assert message == "Kaynak bulunamadi"

    def test_internal_error_english(self):
        message = get_error_message("internal_error", "en")
        assert message == "An unexpected error occurred"

    def test_internal_error_turkish(self):
        message = get_error_message("internal_error", "tr")
        assert message == "Beklenmeyen bir hata olustu"

    def test_query_too_short_interpolation_english(self):
        message = get_error_message("query_too_short", "en", min_length=5)
        assert message == "Query must be at least 5 characters"

    def test_query_too_short_interpolation_turkish(self):
        message = get_error_message("query_too_short", "tr", min_length=5)
        assert message == "Sorgu en az 5 karakter olmali"

    def test_query_too_long_interpolation_english(self):
        message = get_error_message("query_too_long", "en", max_length=500)
        assert message == "Query must be at most 500 characters"

    def test_query_too_long_interpolation_turkish(self):
        message = get_error_message("query_too_long", "tr", max_length=500)
        assert message == "Sorgu en fazla 500 karakter olmali"

    def test_unknown_key_returns_key(self):
        message = get_error_message("unknown_error_key", "en")
        assert message == "unknown_error_key"

    def test_unsupported_locale_falls_back_to_turkish(self):
        message = get_error_message("not_found", "fr")
        assert message == "Kaynak bulunamadi"


class TestErrorExceptions:
    """Test error exception classes use localized messages."""

    def test_authentication_error_english(self):
        error = AuthenticationError(locale="en")
        assert error.message == "Authentication failed"
        assert error.status_code == 401

    def test_authentication_error_turkish(self):
        error = AuthenticationError(locale="tr")
        assert error.message == "Kimlik dogrulama basarisiz"
        assert error.status_code == 401

    def test_rate_limit_error_english(self):
        error = RateLimitError(locale="en")
        assert error.message == "Daily query limit reached"
        assert error.status_code == 429

    def test_rate_limit_error_turkish(self):
        error = RateLimitError(locale="tr")
        assert error.message == "Gunluk sorgu limitine ulastiniz"
        assert error.status_code == 429

    def test_not_found_error_english(self):
        error = NotFoundError(locale="en")
        assert error.message == "Resource not found"
        assert error.status_code == 404

    def test_not_found_error_turkish(self):
        error = NotFoundError(locale="tr")
        assert error.message == "Kaynak bulunamadi"
        assert error.status_code == 404

    def test_validation_error_with_custom_message(self):
        error = ValidationError(message="Custom validation error")
        assert error.message == "Custom validation error"
        assert error.status_code == 422
