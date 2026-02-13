"""
Locale detection for i18n support.

Provides FastAPI dependency for detecting user locale with priority:
1. Query parameter (?lang=en)
2. Cookie (preferred_locale)
3. Accept-Language header (RFC 7231 with quality values)
4. Default locale (tr)
"""

from fastapi import Query, Request

SUPPORTED_LOCALES = ["tr", "en"]
DEFAULT_LOCALE = "tr"


def parse_accept_language(accept_language: str) -> str | None:
    """
    Parse Accept-Language header according to RFC 7231.

    Examples:
        "en-US,en;q=0.9,tr;q=0.8" -> "en"
        "tr-TR,tr;q=0.9" -> "tr"
        "fr-FR,fr;q=0.9,en;q=0.8" -> "en" (fallback to first supported)

    Args:
        accept_language: Accept-Language header value

    Returns:
        Best matching supported locale or None if no match
    """
    if not accept_language:
        return None

    # Parse language tags with quality values
    languages: list[tuple[str, float]] = []

    for lang_range in accept_language.split(","):
        parts = lang_range.strip().split(";")
        lang = parts[0].strip().lower()

        # Extract quality value (default 1.0 if not specified)
        quality = 1.0
        if len(parts) > 1:
            for part in parts[1:]:
                if part.strip().startswith("q="):
                    try:
                        quality = float(part.strip()[2:])
                    except ValueError:
                        quality = 0.0
                    break

        languages.append((lang, quality))

    # Sort by quality value (descending)
    languages.sort(key=lambda x: x[1], reverse=True)

    # Find first supported locale
    for lang, _ in languages:
        # Extract primary language tag (e.g., "en" from "en-US")
        primary_lang = lang.split("-")[0]

        if primary_lang in SUPPORTED_LOCALES:
            return primary_lang

    return None


async def get_locale(
    request: Request,
    lang: str | None = Query(None, description="Override locale (tr, en)"),
) -> str:
    """
    Detect user locale with priority order.

    Priority:
        1. Query parameter (?lang=en) - highest priority
        2. Cookie (preferred_locale)
        3. Accept-Language header (RFC 7231)
        4. Default locale (tr)

    Args:
        request: FastAPI request object
        lang: Optional query parameter for locale override

    Returns:
        Detected locale code (tr or en)

    Examples:
        GET /api/search?lang=en -> "en"
        GET /api/search (Cookie: preferred_locale=en) -> "en"
        GET /api/search (Accept-Language: en-US,en;q=0.9) -> "en"
        GET /api/search -> "tr" (default)
    """
    # 1. Query parameter (explicit override)
    if lang and lang in SUPPORTED_LOCALES:
        return lang

    # 2. Cookie (user preference persisted)
    cookie_locale = request.cookies.get("preferred_locale")
    if cookie_locale and cookie_locale in SUPPORTED_LOCALES:
        return cookie_locale

    # 3. Accept-Language header (browser preference)
    accept_lang = request.headers.get("accept-language", "")
    if accept_lang:
        detected = parse_accept_language(accept_lang)
        if detected:
            return detected

    # 4. Default fallback
    return DEFAULT_LOCALE
