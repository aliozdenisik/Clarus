"""Verse parser module for Quran surah name mapping and lookup utilities.

This module provides a comprehensive mapping of Turkish surah names to their IDs
and verse counts, along with helper functions for case-insensitive lookups.

Also includes a pure function verse reference parser that supports:
- Quran numeric: 2:183, 2:183-185, 2:183,185
- Quran Turkish: Bakara 183, Bakara 183-185
- Bible: Genesis 1:1, Genesis 1:1-3, John 3:16
"""

import re
from dataclasses import dataclass, field
from typing import Literal


def normalize_turkish(text: str) -> str:
    """Normalize Turkish characters for case-insensitive lookup.

    Converts Turkish special characters to their ASCII equivalents:
    - İ → I, ı → i (dotted/dotless i)
    - ğ → g, ü → u, ş → s, ö → o, ç → c
    - â → a (circumflex a)

    Args:
        text: Input string with potential Turkish characters

    Returns:
        Normalized string in lowercase ASCII
    """
    # Turkish character normalization mapping
    turkish_map = {
        "İ": "I",
        "ı": "i",  # Dotted/dotless i
        "ğ": "g",
        "Ğ": "G",  # g with breve
        "ü": "u",
        "Ü": "U",  # u with umlaut
        "ş": "s",
        "Ş": "S",  # s with cedilla
        "ö": "o",
        "Ö": "O",  # o with umlaut
        "ç": "c",
        "Ç": "C",  # c with cedilla
        "â": "a",
        "Â": "A",  # a with circumflex
    }

    # Apply character mapping
    normalized = text
    for turkish_char, ascii_char in turkish_map.items():
        normalized = normalized.replace(turkish_char, ascii_char)

    # Convert to lowercase for case-insensitive comparison
    return normalized.lower()


# Surah name mapping: Turkish name → {id, verses}
# Extracted from backend/data/quran_tr.json (114 surahs total)
SURAH_NAME_MAP: dict[str, dict[str, int]] = {
    "Fâtiha": {"id": 1, "verses": 7},
    "Bakara": {"id": 2, "verses": 286},
    "Âl-i İmrân": {"id": 3, "verses": 200},
    "Nisâ": {"id": 4, "verses": 176},
    "Mâide": {"id": 5, "verses": 120},
    "En'âm": {"id": 6, "verses": 165},
    "A'râf": {"id": 7, "verses": 206},
    "Enfâl": {"id": 8, "verses": 75},
    "Tevbe": {"id": 9, "verses": 129},
    "Yûnus": {"id": 10, "verses": 109},
    "Hûd": {"id": 11, "verses": 123},
    "Yûsuf": {"id": 12, "verses": 111},
    "Ra'd": {"id": 13, "verses": 43},
    "İbrâhîm": {"id": 14, "verses": 52},
    "Hicr": {"id": 15, "verses": 99},
    "Nahl": {"id": 16, "verses": 128},
    "İsrâ": {"id": 17, "verses": 111},
    "Kehf": {"id": 18, "verses": 110},
    "Meryem": {"id": 19, "verses": 98},
    "Tâhâ": {"id": 20, "verses": 135},
    "Enbiyâ": {"id": 21, "verses": 112},
    "Hac": {"id": 22, "verses": 78},
    "Mü'minûn": {"id": 23, "verses": 118},
    "Nûr": {"id": 24, "verses": 64},
    "Furkân": {"id": 25, "verses": 77},
    "Şuarâ": {"id": 26, "verses": 227},
    "Neml": {"id": 27, "verses": 93},
    "Kasas": {"id": 28, "verses": 88},
    "Ankebût": {"id": 29, "verses": 69},
    "Rûm": {"id": 30, "verses": 60},
    "Lokmân": {"id": 31, "verses": 34},
    "Secde": {"id": 32, "verses": 30},
    "Ahzâb": {"id": 33, "verses": 73},
    "Sebe'": {"id": 34, "verses": 54},
    "Fâtır": {"id": 35, "verses": 45},
    "Yâsîn": {"id": 36, "verses": 83},
    "Sâffât": {"id": 37, "verses": 182},
    "Sâd": {"id": 38, "verses": 88},
    "Zümer": {"id": 39, "verses": 75},
    "Mü'min": {"id": 40, "verses": 85},
    "Fussilet": {"id": 41, "verses": 54},
    "Şûrâ": {"id": 42, "verses": 53},
    "Zuhruf": {"id": 43, "verses": 89},
    "Duhân": {"id": 44, "verses": 59},
    "Câsiye": {"id": 45, "verses": 37},
    "Ahkâf": {"id": 46, "verses": 35},
    "Muhammed": {"id": 47, "verses": 38},
    "Fetih": {"id": 48, "verses": 29},
    "Hucurât": {"id": 49, "verses": 18},
    "Kâf": {"id": 50, "verses": 45},
    "Zâriyât": {"id": 51, "verses": 60},
    "Tûr": {"id": 52, "verses": 49},
    "Necm": {"id": 53, "verses": 62},
    "Kamer": {"id": 54, "verses": 55},
    "Rahmân": {"id": 55, "verses": 78},
    "Vâkıa": {"id": 56, "verses": 96},
    "Hadîd": {"id": 57, "verses": 29},
    "Mücâdele": {"id": 58, "verses": 22},
    "Haşr": {"id": 59, "verses": 24},
    "Mümtehine": {"id": 60, "verses": 13},
    "Saf": {"id": 61, "verses": 14},
    "Cuma": {"id": 62, "verses": 11},
    "Münâfikûn": {"id": 63, "verses": 11},
    "Tegâbün": {"id": 64, "verses": 18},
    "Talâk": {"id": 65, "verses": 12},
    "Tahrîm": {"id": 66, "verses": 12},
    "Mülk": {"id": 67, "verses": 30},
    "Kalem": {"id": 68, "verses": 52},
    "Hâkka": {"id": 69, "verses": 52},
    "Meâric": {"id": 70, "verses": 44},
    "Nûh": {"id": 71, "verses": 28},
    "Cin": {"id": 72, "verses": 28},
    "Müzzemmil": {"id": 73, "verses": 20},
    "Müddessir": {"id": 74, "verses": 56},
    "Kıyâmet": {"id": 75, "verses": 40},
    "İnsân": {"id": 76, "verses": 31},
    "Mürselât": {"id": 77, "verses": 50},
    "Nebe": {"id": 78, "verses": 40},
    "Naziât": {"id": 79, "verses": 46},
    "Abese": {"id": 80, "verses": 42},
    "Tekvîr": {"id": 81, "verses": 29},
    "İnfitâh": {"id": 82, "verses": 19},
    "Mutaffifîn": {"id": 83, "verses": 36},
    "İnşikâk": {"id": 84, "verses": 25},
    "Burûc": {"id": 85, "verses": 22},
    "Târık": {"id": 86, "verses": 17},
    "A'lâ": {"id": 87, "verses": 19},
    "Gâşiye": {"id": 88, "verses": 26},
    "Fecr": {"id": 89, "verses": 30},
    "Beled": {"id": 90, "verses": 20},
    "Şems": {"id": 91, "verses": 15},
    "Leyl": {"id": 92, "verses": 21},
    "Duhâ": {"id": 93, "verses": 11},
    "İnşirâh": {"id": 94, "verses": 8},
    "Tîn": {"id": 95, "verses": 8},
    "Alak": {"id": 96, "verses": 19},
    "Kadir": {"id": 97, "verses": 5},
    "Beyyine": {"id": 98, "verses": 8},
    "Zilzâl": {"id": 99, "verses": 8},
    "Âdiyât": {"id": 100, "verses": 11},
    "Kâria": {"id": 101, "verses": 11},
    "Tekâsür": {"id": 102, "verses": 8},
    "Asr": {"id": 103, "verses": 3},
    "Hümeze": {"id": 104, "verses": 9},
    "Fîl": {"id": 105, "verses": 5},
    "Kureyş": {"id": 106, "verses": 4},
    "Maûn": {"id": 107, "verses": 7},
    "Kevser": {"id": 108, "verses": 3},
    "Kâfirûn": {"id": 109, "verses": 6},
    "Nasr": {"id": 110, "verses": 3},
    "Tebbet": {"id": 111, "verses": 5},
    "İhlâs": {"id": 112, "verses": 4},
    "Felak": {"id": 113, "verses": 5},
    "Nâs": {"id": 114, "verses": 6},
}


def get_surah_by_name(name: str) -> dict[str, int] | None:
    """Lookup surah by Turkish name (case-insensitive).

    Supports both exact matches and normalized Turkish character matching.
    For example, both "Fatiha" and "Fâtiha" will return surah 1.

    Args:
        name: Turkish surah name (case-insensitive)

    Returns:
        Dictionary with 'id' and 'verses' keys, or None if not found

    Examples:
        >>> get_surah_by_name("Bakara")
        {'id': 2, 'verses': 286}
        >>> get_surah_by_name("bakara")  # case-insensitive
        {'id': 2, 'verses': 286}
        >>> get_surah_by_name("Fatiha")  # normalized Turkish chars
        {'id': 1, 'verses': 7}
    """
    # Try exact match first (with original Turkish characters)
    if name in SURAH_NAME_MAP:
        return SURAH_NAME_MAP[name]

    # Try normalized match (handles Turkish character variations)
    normalized_input = normalize_turkish(name)
    for original_name, surah_data in SURAH_NAME_MAP.items():
        if normalize_turkish(original_name) == normalized_input:
            return surah_data

    # Not found
    return None


def get_surah_id_by_name(name: str) -> int | None:
    """Lookup surah ID by Turkish name.

    Convenience function that returns just the surah ID.

    Args:
        name: Turkish surah name (case-insensitive)

    Returns:
        Surah ID (1-114), or None if not found
    """
    surah = get_surah_by_name(name)
    return surah["id"] if surah else None


def get_surah_verses_by_name(name: str) -> int | None:
    """Lookup verse count by Turkish surah name.

    Convenience function that returns just the verse count.

    Args:
        name: Turkish surah name (case-insensitive)

    Returns:
        Total verse count, or None if not found
    """
    surah = get_surah_by_name(name)
    return surah["verses"] if surah else None


# Bible book name mapping (80 books: 39 OT + 27 NT + 14 Apocrypha)
# Maps English book name → {id, testament, chapters}
# Extracted from backend/data/bible_kjva.json
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
    """Lookup Bible book by name (case-insensitive).

    Args:
        name: Book name (e.g., "Genesis", "matthew", "1 CORINTHIANS")

    Returns:
        Dictionary with keys: id (int), testament (str), chapters (int)
        Returns None if book not found.

    Examples:
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


# ============================================================================
# VERSE REFERENCE PARSER
# ============================================================================


@dataclass
class ParsedReference:
    """Parsed verse reference result.

    Attributes:
        source: "quran" or "bible"
        surah_id: Quran surah ID (1-114), None for Bible
        surah_name: Original Turkish surah name, None for Bible
        book_id: Bible book ID (1-81), None for Quran
        book_name: Bible book name, None for Quran
        testament: "OT", "NT", or "Apocrypha", None for Quran
        chapter: Bible chapter number, None for Quran
        verses: List of verse numbers
    """

    source: Literal["quran", "bible"]
    surah_id: int | None = None
    surah_name: str | None = None
    book_id: int | None = None
    book_name: str | None = None
    testament: str | None = None
    chapter: int | None = None
    verses: list[int] = field(default_factory=list)


@dataclass
class ParseError:
    """Parse error result.

    Attributes:
        code: Error code (INVALID_FORMAT, SURAH_NOT_FOUND, etc.)
        message: Human-readable error message
        input: Original input string
    """

    code: str
    message: str
    input: str


# Regex patterns for verse reference parsing
QURAN_NUMERIC_PATTERN = re.compile(r"^(\d{1,3}):(\d{1,3})(?:-(\d{1,3}))?$")
QURAN_NUMERIC_MULTI_PATTERN = re.compile(r"^(\d{1,3}):([\d,]+)$")
QURAN_TURKISH_PATTERN = re.compile(r"^([A-Za-zÀ-ÿ\'\-\s]+)\s+([\d,\-]+)$")
BIBLE_PATTERN = re.compile(r"^([\w\s]+?)\s+(\d{1,3}):(\d{1,3})(?:-(\d{1,3}))?$")


def parse_verse_reference(input_str: str) -> ParsedReference | ParseError:
    """Parse verse reference from user input.

    Supports:
    - Quran numeric: 2:183, 2:183-185, 2:183,185,190
    - Quran Turkish: Bakara 183, Bakara 183-185
    - Bible: Genesis 1:1, Genesis 1:1-3, John 3:16

    Args:
        input_str: User input string

    Returns:
        ParsedReference on success, ParseError on failure

    Examples:
        >>> parse_verse_reference("2:183")
        ParsedReference(source='quran', surah_id=2, verses=[183])

        >>> parse_verse_reference("Bakara 183")
        ParsedReference(source='quran', surah_id=2, surah_name='Bakara', verses=[183])

        >>> parse_verse_reference("Genesis 1:1")
        ParsedReference(source='bible', book_id=1, book_name='Genesis', chapter=1, verses=[1])

        >>> parse_verse_reference("invalid")
        ParseError(code='INVALID_FORMAT', message='...', input='invalid')
    """
    # Normalize input: trim whitespace
    normalized = input_str.strip()

    # Try Quran numeric format first (2:183 or 2:183-185)
    match = QURAN_NUMERIC_PATTERN.match(normalized)
    if match:
        return _parse_quran_numeric(normalized, match)

    # Try Quran numeric multiple format (2:183,185,190)
    match = QURAN_NUMERIC_MULTI_PATTERN.match(normalized)
    if match:
        return _parse_quran_numeric_multi(normalized, match)

    # Try Quran Turkish format (Bakara 183 or Bakara 183-185)
    match = QURAN_TURKISH_PATTERN.match(normalized)
    if match:
        return _parse_quran_turkish(normalized, match)

    # Try Bible format (Genesis 1:1 or Genesis 1:1-3)
    match = BIBLE_PATTERN.match(normalized)
    if match:
        return _parse_bible(normalized, match)

    # No pattern matched
    return ParseError(
        code="INVALID_FORMAT",
        message=f"Cannot parse input: '{input_str}'. Expected formats: '2:183', 'Bakara 183', or 'Genesis 1:1'",
        input=input_str,
    )


def _parse_quran_numeric(
    input_str: str, match: re.Match
) -> ParsedReference | ParseError:
    """Parse Quran numeric format: 2:183 or 2:183-185."""
    surah_num = int(match.group(1))
    verse_start = int(match.group(2))
    verse_end = match.group(3)

    # Validate surah number
    if surah_num < 1 or surah_num > 114:
        return ParseError(
            code="SURAH_NOT_FOUND",
            message=f"Surah number {surah_num} is out of range (1-114)",
            input=input_str,
        )

    # Get surah info by ID
    surah_info = None
    for name, info in SURAH_NAME_MAP.items():
        if info["id"] == surah_num:
            surah_info = info
            break

    if not surah_info:
        return ParseError(
            code="SURAH_NOT_FOUND",
            message=f"Surah {surah_num} not found",
            input=input_str,
        )

    max_verse = surah_info["verses"]

    # Parse verses
    if verse_end:
        # Range format
        verse_end_num = int(verse_end)
        verses = list(range(verse_start, verse_end_num + 1))

        # Validate range size
        if len(verses) > 10:
            return ParseError(
                code="RANGE_TOO_LARGE",
                message=f"Range {verse_start}-{verse_end_num} exceeds maximum of 10 verses",
                input=input_str,
            )

        # Validate verse bounds
        if verse_end_num > max_verse:
            return ParseError(
                code="VERSE_OUT_OF_BOUNDS",
                message=f"Verse {verse_end_num} exceeds maximum {max_verse} for surah {surah_num}",
                input=input_str,
            )
    else:
        # Single verse
        verses = [verse_start]

    # Validate verse bounds
    if verse_start > max_verse:
        return ParseError(
            code="VERSE_OUT_OF_BOUNDS",
            message=f"Verse {verse_start} exceeds maximum {max_verse} for surah {surah_num}",
            input=input_str,
        )

    return ParsedReference(
        source="quran",
        surah_id=surah_num,
        verses=verses,
    )


def _parse_quran_numeric_multi(
    input_str: str, match: re.Match
) -> ParsedReference | ParseError:
    """Parse Quran numeric multiple format: 2:183,185,190."""
    surah_num = int(match.group(1))
    verse_list_str = match.group(2)

    # Validate surah number
    if surah_num < 1 or surah_num > 114:
        return ParseError(
            code="SURAH_NOT_FOUND",
            message=f"Surah number {surah_num} is out of range (1-114)",
            input=input_str,
        )

    # Get surah info by ID
    surah_info = None
    for name, info in SURAH_NAME_MAP.items():
        if info["id"] == surah_num:
            surah_info = info
            break

    if not surah_info:
        return ParseError(
            code="SURAH_NOT_FOUND",
            message=f"Surah {surah_num} not found",
            input=input_str,
        )

    max_verse = surah_info["verses"]

    # Parse verse list
    verse_parts = verse_list_str.split(",")
    verses = []
    for part in verse_parts:
        try:
            verse_num = int(part.strip())
            verses.append(verse_num)
        except ValueError:
            return ParseError(
                code="INVALID_FORMAT",
                message=f"Invalid verse number: '{part}'",
                input=input_str,
            )

    # Validate count
    if len(verses) > 5:
        return ParseError(
            code="TOO_MANY_REFS",
            message=f"Too many verse references ({len(verses)}). Maximum is 5.",
            input=input_str,
        )

    # Validate verse bounds
    for verse_num in verses:
        if verse_num > max_verse:
            return ParseError(
                code="VERSE_OUT_OF_BOUNDS",
                message=f"Verse {verse_num} exceeds maximum {max_verse} for surah {surah_num}",
                input=input_str,
            )

    return ParsedReference(
        source="quran",
        surah_id=surah_num,
        verses=verses,
    )


def _parse_quran_turkish(
    input_str: str, match: re.Match
) -> ParsedReference | ParseError:
    """Parse Quran Turkish format: Bakara 183, Bakara 183-185, or Bakara 1,3,5."""
    surah_name = match.group(1).strip()
    verse_spec = match.group(2).strip()

    # Lookup surah by name (case-insensitive, Turkish-normalized)
    surah_info = get_surah_by_name(surah_name)
    if not surah_info:
        # Try partial matching for common abbreviations
        surah_info = _find_surah_by_partial_name(surah_name)
        if not surah_info:
            return ParseError(
                code="SURAH_NOT_FOUND",
                message=f"Surah '{surah_name}' not found",
                input=input_str,
            )

    surah_id = surah_info["id"]
    max_verse = surah_info["verses"]

    # Parse verse specification (single, range, or multiple)
    if "," in verse_spec:
        # Multiple verses: "1,3,5"
        verse_parts = verse_spec.split(",")
        verses = []
        for part in verse_parts:
            try:
                verse_num = int(part.strip())
                verses.append(verse_num)
            except ValueError:
                return ParseError(
                    code="INVALID_FORMAT",
                    message=f"Invalid verse number: '{part}'",
                    input=input_str,
                )

        # Validate count
        if len(verses) > 5:
            return ParseError(
                code="TOO_MANY_REFS",
                message=f"Too many verse references ({len(verses)}). Maximum is 5.",
                input=input_str,
            )

        # Validate verse bounds
        for verse_num in verses:
            if verse_num > max_verse:
                return ParseError(
                    code="VERSE_OUT_OF_BOUNDS",
                    message=f"Verse {verse_num} exceeds maximum {max_verse} for surah '{surah_name}'",
                    input=input_str,
                )
    elif "-" in verse_spec:
        # Range format: "183-185"
        parts = verse_spec.split("-")
        verse_start = int(parts[0])
        verse_end = int(parts[1])
        verses = list(range(verse_start, verse_end + 1))

        # Validate range size
        if len(verses) > 10:
            return ParseError(
                code="RANGE_TOO_LARGE",
                message=f"Range {verse_start}-{verse_end} exceeds maximum of 10 verses",
                input=input_str,
            )

        # Validate verse bounds
        if verse_end > max_verse:
            return ParseError(
                code="VERSE_OUT_OF_BOUNDS",
                message=f"Verse {verse_end} exceeds maximum {max_verse} for surah '{surah_name}'",
                input=input_str,
            )
        if verse_start > max_verse:
            return ParseError(
                code="VERSE_OUT_OF_BOUNDS",
                message=f"Verse {verse_start} exceeds maximum {max_verse} for surah '{surah_name}'",
                input=input_str,
            )
    else:
        # Single verse: "183"
        verse_start = int(verse_spec)
        verses = [verse_start]

        # Validate verse bounds
        if verse_start > max_verse:
            return ParseError(
                code="VERSE_OUT_OF_BOUNDS",
                message=f"Verse {verse_start} exceeds maximum {max_verse} for surah '{surah_name}'",
                input=input_str,
            )

    return ParsedReference(
        source="quran",
        surah_id=surah_id,
        surah_name=surah_name,
        verses=verses,
    )


def _find_surah_by_partial_name(partial_name: str) -> dict[str, int] | None:
    """Find surah by partial name match (for common abbreviations).

    Examples:
        "Imran" -> matches "Âl-i İmrân"
        "Fatiha" -> matches "Fâtiha"
    """
    normalized_partial = normalize_turkish(partial_name)

    for original_name, surah_data in SURAH_NAME_MAP.items():
        normalized_full = normalize_turkish(original_name)
        # Check if partial name is contained in full name
        if normalized_partial in normalized_full:
            return surah_data

    return None


def _parse_bible(input_str: str, match: re.Match) -> ParsedReference | ParseError:
    """Parse Bible format: Genesis 1:1 or Genesis 1:1-3."""
    book_name = match.group(1).strip()
    chapter = int(match.group(2))
    verse_start = int(match.group(3))
    verse_end = match.group(4)

    # Lookup book by name (case-insensitive)
    book_info = get_book_by_name(book_name)
    if not book_info:
        # Try partial matching for common abbreviations
        book_info = _find_book_by_partial_name(book_name)
        if not book_info:
            return ParseError(
                code="BOOK_NOT_FOUND",
                message=f"Bible book '{book_name}' not found",
                input=input_str,
            )

    book_id = int(book_info["id"])
    testament = str(book_info["testament"])
    max_chapter = int(book_info["chapters"])
    # Get the actual book name from the map (for "Revelation" -> "Revelation of John")
    actual_book_name = _get_book_name_by_id(book_id)

    # Validate chapter
    if chapter > max_chapter:
        return ParseError(
            code="CHAPTER_OUT_OF_BOUNDS",
            message=f"Chapter {chapter} exceeds maximum {max_chapter} for book '{book_name}'",
            input=input_str,
        )

    # Parse verses
    if verse_end:
        # Range format
        verse_end_num = int(verse_end)
        verses = list(range(verse_start, verse_end_num + 1))

        # Validate range size
        if len(verses) > 10:
            return ParseError(
                code="RANGE_TOO_LARGE",
                message=f"Range {verse_start}-{verse_end_num} exceeds maximum of 10 verses",
                input=input_str,
            )
    else:
        # Single verse
        verses = [verse_start]

    # Note: We don't validate verse bounds for Bible because we don't have
    # verse count per chapter in BIBLE_BOOK_MAP. This is acceptable for now.

    return ParsedReference(
        source="bible",
        book_id=book_id,
        book_name=actual_book_name,
        testament=testament,
        chapter=chapter,
        verses=verses,
    )


def _find_book_by_partial_name(partial_name: str) -> dict[str, int | str] | None:
    """Find Bible book by partial name match (for common abbreviations).

    Examples:
        "Revelation" -> matches "Revelation of John"
        "Song" -> matches "Song of Solomon"
    """
    partial_lower = partial_name.lower()

    for book_name, book_data in BIBLE_BOOK_MAP.items():
        book_lower = book_name.lower()
        # Check if partial name is at the start of the full name
        if book_lower.startswith(partial_lower):
            return book_data

    return None


def _get_book_name_by_id(book_id: int) -> str:
    """Get Bible book name by ID."""
    for book_name, book_data in BIBLE_BOOK_MAP.items():
        if book_data["id"] == book_id:
            return book_name
    return ""
