"""
i18n (Internationalization) module for backend.

Provides:
- Locale detection via FastAPI dependency
- Localized error message catalog (TR/EN)
"""

from app.i18n.detector import DEFAULT_LOCALE, SUPPORTED_LOCALES, get_locale
from app.i18n.messages import ERROR_MESSAGES, get_error_message

__all__ = [
    "DEFAULT_LOCALE",
    "ERROR_MESSAGES",
    "SUPPORTED_LOCALES",
    "get_error_message",
    "get_locale",
]
