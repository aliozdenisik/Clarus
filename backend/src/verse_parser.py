"""
Bible and Quran Verse Parser

Provides book name mappings and verse parsing utilities for Bible (KJVA) and Quran (Turkish).
Supports direct verse reference lookups by book name.
"""

from typing import Optional


# Bible book name mapping (80 books: 39 OT + 27 NT + 14 Apocrypha)
# Maps English book name → {id, testament, chapters}
BIBLE_BOOK_MAP: dict[str, dict[str, int | str]] = {
    # Old Testament (1-39)
    "Genesis": {"id": 1, "testament": "OT", "chapters": 50},
    "Exodus": {"id": 2, "testament": "OT", "chapters": 40},
    "Leviticus": {"id": 3, "testament": "OT", "chapters": 27},
    "Numbers": {"id": 4, "testament": "OT", "chapters": 36},
    "Deuteronomy": {"id": 5, "testament": "OT", "chapters": 34},
    "Joshua": {"id": 6, "testament": "OT", "chapters": 24},
    "Judges": {"id": 7, "testament": "OT", "chapters": 21},
    "Ruth": {"id": 8, "testament": "OT", "chapters": 4},
    "1 Samuel": {"id": 9, "testament": "OT", "chapters": 31},
    "2 Samuel": {"id": 10, "testament": "OT", "chapters": 24},
    "1 Kings": {"id": 11, "testament": "OT", "chapters": 22},
    "2 Kings": {"id": 12, "testament": "OT", "chapters": 25},
    "1 Chronicles": {"id": 13, "testament": "OT", "chapters": 29},
    "2 Chronicles": {"id": 14, "testament": "OT", "chapters": 36},
    "Ezra": {"id": 15, "testament": "OT", "chapters": 10},
    "Nehemiah": {"id": 16, "testament": "OT", "chapters": 13},
    "Esther": {"id": 17, "testament": "OT", "chapters": 10},
    "Job": {"id": 18, "testament": "OT", "chapters": 42},
    "Psalms": {"id": 19, "testament": "OT", "chapters": 150},
    "Proverbs": {"id": 20, "testament": "OT", "chapters": 31},
    "Ecclesiastes": {"id": 21, "testament": "OT", "chapters": 12},
    "Song of Solomon": {"id": 22, "testament": "OT", "chapters": 8},
    "Isaiah": {"id": 23, "testament": "OT", "chapters": 66},
    "Jeremiah": {"id": 24, "testament": "OT", "chapters": 52},
    "Lamentations": {"id": 25, "testament": "OT", "chapters": 5},
    "Ezekiel": {"id": 26, "testament": "OT", "chapters": 48},
    "Daniel": {"id": 27, "testament": "OT", "chapters": 12},
    "Hosea": {"id": 28, "testament": "OT", "chapters": 14},
    "Joel": {"id": 29, "testament": "OT", "chapters": 3},
    "Amos": {"id": 30, "testament": "OT", "chapters": 9},
    "Obadiah": {"id": 31, "testament": "OT", "chapters": 1},
    "Jonah": {"id": 32, "testament": "OT", "chapters": 4},
    "Micah": {"id": 33, "testament": "OT", "chapters": 7},
    "Nahum": {"id": 34, "testament": "OT", "chapters": 3},
    "Habakkuk": {"id": 35, "testament": "OT", "chapters": 3},
    "Zephaniah": {"id": 36, "testament": "OT", "chapters": 3},
    "Haggai": {"id": 37, "testament": "OT", "chapters": 2},
    "Zechariah": {"id": 38, "testament": "OT", "chapters": 14},
    "Malachi": {"id": 39, "testament": "OT", "chapters": 4},
    # New Testament (40-66)
    "Matthew": {"id": 40, "testament": "NT", "chapters": 28},
    "Mark": {"id": 41, "testament": "NT", "chapters": 16},
    "Luke": {"id": 42, "testament": "NT", "chapters": 24},
    "John": {"id": 43, "testament": "NT", "chapters": 21},
    "Acts": {"id": 44, "testament": "NT", "chapters": 28},
    "Romans": {"id": 45, "testament": "NT", "chapters": 16},
    "1 Corinthians": {"id": 46, "testament": "NT", "chapters": 16},
    "2 Corinthians": {"id": 47, "testament": "NT", "chapters": 13},
    "Galatians": {"id": 48, "testament": "NT", "chapters": 6},
    "Ephesians": {"id": 49, "testament": "NT", "chapters": 6},
    "Philippians": {"id": 50, "testament": "NT", "chapters": 4},
    "Colossians": {"id": 51, "testament": "NT", "chapters": 4},
    "1 Thessalonians": {"id": 52, "testament": "NT", "chapters": 5},
    "2 Thessalonians": {"id": 53, "testament": "NT", "chapters": 3},
    "1 Timothy": {"id": 54, "testament": "NT", "chapters": 6},
    "2 Timothy": {"id": 55, "testament": "NT", "chapters": 4},
    "Titus": {"id": 56, "testament": "NT", "chapters": 3},
    "Philemon": {"id": 57, "testament": "NT", "chapters": 1},
    "Hebrews": {"id": 58, "testament": "NT", "chapters": 13},
    "James": {"id": 59, "testament": "NT", "chapters": 5},
    "1 Peter": {"id": 60, "testament": "NT", "chapters": 5},
    "2 Peter": {"id": 61, "testament": "NT", "chapters": 3},
    "1 John": {"id": 62, "testament": "NT", "chapters": 5},
    "2 John": {"id": 63, "testament": "NT", "chapters": 1},
    "3 John": {"id": 64, "testament": "NT", "chapters": 1},
    "Jude": {"id": 65, "testament": "NT", "chapters": 1},
    "Revelation of John": {"id": 66, "testament": "NT", "chapters": 22},
    # Apocrypha/Deuterocanonical (67-81)
    "1 Esdras": {"id": 67, "testament": "Apocrypha", "chapters": 9},
    "2 Esdras": {"id": 68, "testament": "Apocrypha", "chapters": 16},
    "Tobit": {"id": 69, "testament": "Apocrypha", "chapters": 14},
    "Judith": {"id": 70, "testament": "Apocrypha", "chapters": 16},
    "Additions to Esther": {"id": 71, "testament": "Apocrypha", "chapters": 16},
    "Wisdom": {"id": 73, "testament": "Apocrypha", "chapters": 19},
    "Sirach": {"id": 74, "testament": "Apocrypha", "chapters": 51},
    "Baruch": {"id": 75, "testament": "Apocrypha", "chapters": 6},
    "Prayer of Azariah": {"id": 76, "testament": "Apocrypha", "chapters": 1},
    "Susanna": {"id": 77, "testament": "Apocrypha", "chapters": 1},
    "Bel and the Dragon": {"id": 78, "testament": "Apocrypha", "chapters": 1},
    "Prayer of Manasses": {"id": 79, "testament": "Apocrypha", "chapters": 1},
    "1 Maccabees": {"id": 80, "testament": "Apocrypha", "chapters": 16},
    "2 Maccabees": {"id": 81, "testament": "Apocrypha", "chapters": 15},
}


def get_book_by_name(name: str) -> dict[str, int | str] | None:
    """
    Lookup Bible book by name (case-insensitive).

    Args:
        name: Book name (e.g., "Genesis", "matthew", "1 CORINTHIANS")

    Returns:
        Dictionary with keys: id (int), testament (str), chapters (int)
        Returns None if book not found.

    Example:
        >>> get_book_by_name("Genesis")
        {'id': 1, 'testament': 'OT', 'chapters': 50}

        >>> get_book_by_name("matthew")
        {'id': 40, 'testament': 'NT', 'chapters': 28}

        >>> get_book_by_name("unknown")
        None
    """
    # Try exact match first
    if name in BIBLE_BOOK_MAP:
        return BIBLE_BOOK_MAP[name]

    # Try case-insensitive match
    for book_name, book_data in BIBLE_BOOK_MAP.items():
        if book_name.lower() == name.lower():
            return book_data

    return None
