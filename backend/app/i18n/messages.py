"""
Error message catalog for i18n support.

Provides localized error messages for TR (Turkish) and EN (English).
"""

ERROR_MESSAGES: dict[str, dict[str, str]] = {
    "tr": {
        "auth_failed": "Kimlik dogrulama basarisiz",
        "rate_limit": "Gunluk sorgu limitine ulastiniz",
        "rate_limit_with_count": "Gunluk sorgu limitine ulastiniz ({limit}/gun)",
        "not_found": "Kaynak bulunamadi",
        "user_not_found": "Kullanici bulunamadi",
        "history_not_found": "Gecmis ogesi bulunamadi",
        "history_deleted": "Gecmis ogesi silindi",
        "all_history_cleared": "Tum gecmis temizlendi",
        "user_deleted": "Kullanici silindi",
        "internal_error": "Beklenmeyen bir hata olustu",
        "query_too_short": "Sorgu en az {min_length} karakter olmali",
        "query_too_long": "Sorgu en fazla {max_length} karakter olmali",
        "invalid_source": "Gecersiz kaynak",
        "search_failed": "Arama basarisiz oldu",
        "cannot_delete_own_account": "Kendi hesabinizi silemezsiniz",
        "validation_error": "Dogrulama hatasi",
        "min_collections_required": "Karsilastirma icin en az {min_count} koleksiyon gereklidir",
    },
    "en": {
        "auth_failed": "Authentication failed",
        "rate_limit": "Daily query limit reached",
        "rate_limit_with_count": "Daily query limit reached ({limit}/day)",
        "not_found": "Resource not found",
        "user_not_found": "User not found",
        "history_not_found": "Search history not found",
        "history_deleted": "Search history deleted",
        "all_history_cleared": "All search history cleared",
        "user_deleted": "User deleted",
        "internal_error": "An unexpected error occurred",
        "query_too_short": "Query must be at least {min_length} characters",
        "query_too_long": "Query must be at most {max_length} characters",
        "invalid_source": "Invalid source",
        "search_failed": "Search failed",
        "cannot_delete_own_account": "Cannot delete your own account",
        "validation_error": "Validation error",
        "min_collections_required": "At least {min_count} collections required for comparison",
    },
}


def get_error_message(key: str, locale: str = "tr", **kwargs) -> str:
    """
    Get localized error message by key.

    Args:
        key: Message key (e.g., "auth_failed", "not_found")
        locale: Locale code (tr or en), defaults to tr
        **kwargs: Format variables for message interpolation

    Returns:
        Localized error message with variables interpolated

    Examples:
        >>> get_error_message("auth_failed", "en")
        'Authentication failed'

        >>> get_error_message("query_too_short", "tr", min_length=3)
        'Sorgu en az 3 karakter olmali'

        >>> get_error_message("rate_limit_with_count", "en", limit=50)
        'Daily query limit reached (50/day)'

        >>> get_error_message("unknown_key", "en")
        'unknown_key'
    """
    locale_messages = ERROR_MESSAGES.get(locale, ERROR_MESSAGES["tr"])

    message = locale_messages.get(key)

    if message is None:
        message = ERROR_MESSAGES["tr"].get(key, key)

    if kwargs:
        try:
            message = message.format(**kwargs)
        except (KeyError, ValueError):
            pass

    return message
