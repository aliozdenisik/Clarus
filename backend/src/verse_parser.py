"""Verse parser module for Quran surah name mapping and lookup utilities.

This module provides a comprehensive mapping of Turkish surah names to their IDs
and verse counts, along with helper functions for case-insensitive lookups.
"""


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
        'İ': 'I', 'ı': 'i',  # Dotted/dotless i
        'ğ': 'g', 'Ğ': 'G',  # g with breve
        'ü': 'u', 'Ü': 'U',  # u with umlaut
        'ş': 's', 'Ş': 'S',  # s with cedilla
        'ö': 'o', 'Ö': 'O',  # o with umlaut
        'ç': 'c', 'Ç': 'C',  # c with cedilla
        'â': 'a', 'Â': 'A',  # a with circumflex
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
    return surah['id'] if surah else None


def get_surah_verses_by_name(name: str) -> int | None:
    """Lookup verse count by Turkish surah name.
    
    Convenience function that returns just the verse count.
    
    Args:
        name: Turkish surah name (case-insensitive)
        
    Returns:
        Total verse count, or None if not found
    """
    surah = get_surah_by_name(name)
    return surah['verses'] if surah else None
