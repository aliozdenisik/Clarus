from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from app.i18n import (
    DEFAULT_LOCALE,
    SUPPORTED_LOCALES,
    get_error_message,
    get_locale,
)
from app.i18n.detector import parse_accept_language

app = FastAPI()


@app.get("/test-locale")
async def test_locale_endpoint(locale: str = Depends(get_locale)):
    return {"locale": locale}


client = TestClient(app)


class TestParseAcceptLanguage:
    def test_parse_single_language(self):
        result = parse_accept_language("en")
        assert result == "en"

    def test_parse_language_with_region(self):
        result = parse_accept_language("en-US")
        assert result == "en"

    def test_parse_multiple_languages_with_quality(self):
        result = parse_accept_language("en-US,en;q=0.9,tr;q=0.8")
        assert result == "en"

    def test_parse_turkish_priority(self):
        result = parse_accept_language("tr-TR,tr;q=0.9,en;q=0.8")
        assert result == "tr"

    def test_parse_unsupported_language_fallback(self):
        result = parse_accept_language("fr-FR,fr;q=0.9,en;q=0.8")
        assert result == "en"

    def test_parse_all_unsupported_languages(self):
        result = parse_accept_language("fr-FR,de-DE,es-ES")
        assert result is None

    def test_parse_quality_value_sorting(self):
        result = parse_accept_language("tr;q=0.7,en;q=0.9,fr;q=0.8")
        assert result == "en"

    def test_parse_empty_string(self):
        result = parse_accept_language("")
        assert result is None

    def test_parse_malformed_quality_value(self):
        result = parse_accept_language("en;q=invalid,tr")
        assert result == "tr"

    def test_parse_case_insensitive(self):
        result = parse_accept_language("EN-US,TR;q=0.8")
        assert result == "en"


class TestGetLocale:
    def test_default_locale_no_headers(self):
        response = client.get("/test-locale")
        assert response.status_code == 200
        assert response.json()["locale"] == DEFAULT_LOCALE

    def test_query_param_override(self):
        response = client.get("/test-locale?lang=en")
        assert response.status_code == 200
        assert response.json()["locale"] == "en"

    def test_query_param_turkish(self):
        response = client.get("/test-locale?lang=tr")
        assert response.status_code == 200
        assert response.json()["locale"] == "tr"

    def test_query_param_invalid_fallback(self):
        response = client.get("/test-locale?lang=fr")
        assert response.status_code == 200
        assert response.json()["locale"] == DEFAULT_LOCALE

    def test_accept_language_header(self):
        response = client.get("/test-locale", headers={"Accept-Language": "en-US,en;q=0.9"})
        assert response.status_code == 200
        assert response.json()["locale"] == "en"

    def test_accept_language_turkish(self):
        response = client.get("/test-locale", headers={"Accept-Language": "tr-TR,tr;q=0.9"})
        assert response.status_code == 200
        assert response.json()["locale"] == "tr"

    def test_cookie_locale(self):
        response = client.get("/test-locale", cookies={"preferred_locale": "en"})
        assert response.status_code == 200
        assert response.json()["locale"] == "en"

    def test_query_param_overrides_cookie(self):
        response = client.get(
            "/test-locale?lang=en",
            cookies={"preferred_locale": "tr"},
        )
        assert response.status_code == 200
        assert response.json()["locale"] == "en"

    def test_query_param_overrides_header(self):
        response = client.get(
            "/test-locale?lang=tr",
            headers={"Accept-Language": "en-US"},
        )
        assert response.status_code == 200
        assert response.json()["locale"] == "tr"

    def test_cookie_overrides_header(self):
        response = client.get(
            "/test-locale",
            headers={"Accept-Language": "en-US"},
            cookies={"preferred_locale": "tr"},
        )
        assert response.status_code == 200
        assert response.json()["locale"] == "tr"

    def test_supported_locales_constant(self):
        assert "tr" in SUPPORTED_LOCALES
        assert "en" in SUPPORTED_LOCALES
        assert len(SUPPORTED_LOCALES) == 2

    def test_default_locale_constant(self):
        assert DEFAULT_LOCALE == "tr"


class TestGetErrorMessage:
    def test_auth_failed_turkish(self):
        msg = get_error_message("auth_failed", "tr")
        assert msg == "Kimlik dogrulama basarisiz"

    def test_auth_failed_english(self):
        msg = get_error_message("auth_failed", "en")
        assert msg == "Authentication failed"

    def test_rate_limit_turkish(self):
        msg = get_error_message("rate_limit", "tr")
        assert msg == "Gunluk sorgu limitine ulastiniz"

    def test_rate_limit_english(self):
        msg = get_error_message("rate_limit", "en")
        assert msg == "Daily query limit reached"

    def test_not_found_turkish(self):
        msg = get_error_message("not_found", "tr")
        assert msg == "Kaynak bulunamadi"

    def test_not_found_english(self):
        msg = get_error_message("not_found", "en")
        assert msg == "Resource not found"

    def test_internal_error_turkish(self):
        msg = get_error_message("internal_error", "tr")
        assert msg == "Beklenmeyen bir hata olustu"

    def test_internal_error_english(self):
        msg = get_error_message("internal_error", "en")
        assert msg == "An unexpected error occurred"

    def test_query_too_short_with_kwargs_turkish(self):
        msg = get_error_message("query_too_short", "tr", min_length=3)
        assert msg == "Sorgu en az 3 karakter olmali"

    def test_query_too_short_with_kwargs_english(self):
        msg = get_error_message("query_too_short", "en", min_length=3)
        assert msg == "Query must be at least 3 characters"

    def test_query_too_long_with_kwargs_turkish(self):
        msg = get_error_message("query_too_long", "tr", max_length=500)
        assert msg == "Sorgu en fazla 500 karakter olmali"

    def test_query_too_long_with_kwargs_english(self):
        msg = get_error_message("query_too_long", "en", max_length=500)
        assert msg == "Query must be at most 500 characters"

    def test_rate_limit_with_count_turkish(self):
        msg = get_error_message("rate_limit_with_count", "tr", limit=50)
        assert msg == "Gunluk sorgu limitine ulastiniz (50/gun)"

    def test_rate_limit_with_count_english(self):
        msg = get_error_message("rate_limit_with_count", "en", limit=50)
        assert msg == "Daily query limit reached (50/day)"

    def test_cannot_delete_own_account_turkish(self):
        msg = get_error_message("cannot_delete_own_account", "tr")
        assert msg == "Kendi hesabinizi silemezsiniz"

    def test_cannot_delete_own_account_english(self):
        msg = get_error_message("cannot_delete_own_account", "en")
        assert msg == "Cannot delete your own account"

    def test_user_not_found_turkish(self):
        msg = get_error_message("user_not_found", "tr")
        assert msg == "Kullanici bulunamadi"

    def test_user_not_found_english(self):
        msg = get_error_message("user_not_found", "en")
        assert msg == "User not found"

    def test_history_not_found_turkish(self):
        msg = get_error_message("history_not_found", "tr")
        assert msg == "Gecmis ogesi bulunamadi"

    def test_history_not_found_english(self):
        msg = get_error_message("history_not_found", "en")
        assert msg == "Search history not found"

    def test_validation_error_turkish(self):
        msg = get_error_message("validation_error", "tr")
        assert msg == "Dogrulama hatasi"

    def test_validation_error_english(self):
        msg = get_error_message("validation_error", "en")
        assert msg == "Validation error"

    def test_search_failed_turkish(self):
        msg = get_error_message("search_failed", "tr")
        assert msg == "Arama basarisiz oldu"

    def test_search_failed_english(self):
        msg = get_error_message("search_failed", "en")
        assert msg == "Search failed"

    def test_invalid_source_turkish(self):
        msg = get_error_message("invalid_source", "tr")
        assert msg == "Gecersiz kaynak"

    def test_invalid_source_english(self):
        msg = get_error_message("invalid_source", "en")
        assert msg == "Invalid source"

    def test_unknown_key_fallback_to_turkish(self):
        msg = get_error_message("unknown_key", "en")
        assert msg == "unknown_key"

    def test_unknown_key_returns_key(self):
        msg = get_error_message("nonexistent_error", "tr")
        assert msg == "nonexistent_error"

    def test_unsupported_locale_fallback_to_turkish(self):
        msg = get_error_message("auth_failed", "fr")
        assert msg == "Kimlik dogrulama basarisiz"

    def test_default_locale_when_not_specified(self):
        msg = get_error_message("auth_failed")
        assert msg == "Kimlik dogrulama basarisiz"

    def test_invalid_kwargs_ignored(self):
        msg = get_error_message("auth_failed", "en", invalid_param="test")
        assert msg == "Authentication failed"

    def test_missing_kwargs_preserved(self):
        msg = get_error_message("query_too_short", "en")
        assert "{min_length}" in msg
