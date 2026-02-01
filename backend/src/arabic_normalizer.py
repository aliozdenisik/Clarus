"""Arabic text normalization utilities for morphological search.

Provides consistent normalization for both ETL indexing and query-time
processing. The normalize_arabic() function MUST match the logic used
in backend/scripts/setup_quran_morphology.py to ensure index-query
consistency.
"""

import unicodedata

from pyarabic import araby
from pyarabic.trans import utf82latin as _arabic_to_buckwalter


def normalize_arabic(text: str) -> str:
    """Full normalization pipeline matching ETL indexing logic.

    Steps:
      1. Strip tashkeel (diacritics/harakat)
      2. Normalize hamza variants -> bare alef/waw/ya
      3. Ta-marbuta -> ha
      4. Alef-maksura -> ya
      5. Strip tatweel
      6. NFC normalization
    """
    result = araby.strip_tashkeel(text)
    # Hamza normalization
    result = result.replace("\u0623", "\u0627")  # أ → ا
    result = result.replace("\u0625", "\u0627")  # إ → ا
    result = result.replace("\u0622", "\u0627")  # آ → ا
    result = result.replace("\u0624", "\u0648")  # ؤ → و
    result = result.replace("\u0626", "\u064a")  # ئ → ي
    # Ta-marbuta → ha
    result = result.replace("\u0629", "\u0647")  # ة → ه
    # Alef-maksura → ya
    result = result.replace("\u0649", "\u064a")  # ى → ي
    # Strip tatweel
    result = result.replace("\u0640", "")
    # NFC normalization
    result = unicodedata.normalize("NFC", result)
    return result


def is_arabic(text: str) -> bool:
    """Check if text contains Arabic characters.

    Covers the main Arabic Unicode ranges:
    - U+0621-U+064A (Arabic block)
    - U+0671-U+06D3 (Extended Arabic)
    """
    return any("\u0621" <= c <= "\u064a" or "\u0671" <= c <= "\u06d3" for c in text)


def arabic_to_buckwalter(text: str) -> str:
    """Convert Arabic text to Buckwalter Latin transliteration."""
    return _arabic_to_buckwalter(text)


def normalize_latin_query(text: str) -> str:
    """Normalize Latin input: lowercase + strip Turkish characters.

    Maps: ş→s, ç→c, ğ→g, ı→i, ö→o, ü→u
    """
    text = text.lower()
    tr_map = str.maketrans("şçğıöü", "scgiou")
    return text.translate(tr_map)
