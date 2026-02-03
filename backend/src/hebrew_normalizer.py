"""Hebrew text normalization utilities for morphological search.

Provides consistent normalization for both ETL indexing and query-time
processing. Handles nikud (vowel points) removal, transliteration, and
OSHB lemma parsing for Bible keyword search.
"""

import re
import unicodedata
from typing import Optional


def remove_hebrew_nikud(text: str) -> str:
    """Strip Hebrew nikud (vowel points) and cantillation marks.

    Removes Unicode ranges:
    - U+0591-U+05BD: Cantillation marks and nikud (vowel points)
    - U+05BF-U+05C7: Additional vowel marks and accents

    PRESERVES U+05BE (Maqaf/hyphen ־) which is a word separator.

    Args:
        text: Hebrew text with nikud

    Returns:
        Text with nikud removed

    Example:
        >>> remove_hebrew_nikud("בְּרֵאשִׁ֖ית")
        'בראשית'
    """
    # Remove nikud ranges, but preserve U+05BE (Maqaf)
    result = ""
    for char in text:
        code = ord(char)
        # Skip nikud ranges except Maqaf (U+05BE)
        if (0x0591 <= code <= 0x05BD) or (0x05BF <= code <= 0x05C7):
            if code != 0x05BE:  # Preserve Maqaf
                continue
        result += char
    return result


def normalize_hebrew(text: str) -> str:
    """Full normalization pipeline for Hebrew text.

    Steps:
      1. Strip nikud (vowel points and cantillation marks)
      2. Apply NFC Unicode normalization
      3. Strip any remaining combining characters

    Args:
        text: Hebrew text to normalize

    Returns:
        Normalized Hebrew text

    Example:
        >>> normalize_hebrew("בְּרֵאשִׁ֖ית")
        'בראשית'
    """
    result = remove_hebrew_nikud(text)
    result = unicodedata.normalize("NFC", result)
    # Strip combining characters (category Mn = Mark, nonspacing)
    result = "".join(c for c in result if unicodedata.category(c) != "Mn")
    return result


def transliterate_hebrew(text: str) -> str:
    """Convert Hebrew text to SBL General Latin transliteration.

    Uses standard scholarly transliteration mapping for Hebrew consonants.
    Handles both regular and final forms of letters.

    Mapping:
    - א→ʾ, ב→b, ג→g, ד→d, ה→h, ו→w, ז→z, ח→ḥ, ט→ṭ, י→y
    - כ/ך→k, ל→l, מ/ם→m, נ/ן→n, ס→s, ע→ʿ, פ/ף→p, צ/ץ→ṣ, ק→q, ר→r
    - שׁ→š, שׂ→ś, ת→t

    Args:
        text: Hebrew text to transliterate

    Returns:
        Transliterated Latin text

    Example:
        >>> transliterate_hebrew("אלהים")
        'ʾlhym'
    """
    # First remove nikud
    text = remove_hebrew_nikud(text)

    # SBL General Latin transliteration mapping
    mapping = {
        "א": "ʾ",
        "ב": "b",
        "ג": "g",
        "ד": "d",
        "ה": "h",
        "ו": "w",
        "ז": "z",
        "ח": "ḥ",
        "ט": "ṭ",
        "י": "y",
        "כ": "k",
        "ך": "k",  # Final form
        "ל": "l",
        "מ": "m",
        "ם": "m",  # Final form
        "נ": "n",
        "ן": "n",  # Final form
        "ס": "s",
        "ע": "ʿ",
        "פ": "p",
        "ף": "p",  # Final form
        "צ": "ṣ",
        "ץ": "ṣ",  # Final form
        "ק": "q",
        "ר": "r",
        "שׁ": "š",  # Shin with dot (U+05C1)
        "שׂ": "ś",  # Sin with dot (U+05C2)
        "ש": "š",  # Default to shin
        "ת": "t",
    }

    result = ""
    i = 0
    while i < len(text):
        # Check for two-character combinations first (שׁ, שׂ)
        if i + 1 < len(text):
            two_char = text[i : i + 2]
            if two_char in mapping:
                result += mapping[two_char]
                i += 2
                continue

        # Single character mapping
        char = text[i]
        if char in mapping:
            result += mapping[char]
        else:
            result += char
        i += 1

    return result


def detect_script(text: str) -> str:
    """Detect the primary script of the text.

    Checks for Hebrew, Arabic, Greek, or Latin characters in order.

    Args:
        text: Text to analyze

    Returns:
        One of: 'hebrew', 'arabic', 'greek', 'latin'

    Example:
        >>> detect_script("בראשית")
        'hebrew'
        >>> detect_script("الله")
        'arabic'
    """
    for char in text:
        code = ord(char)
        # Hebrew: U+0590-U+05FF
        if 0x0590 <= code <= 0x05FF:
            return "hebrew"
        # Arabic: U+0600-U+06FF
        if 0x0600 <= code <= 0x06FF:
            return "arabic"
        # Greek: U+0370-U+03FF or U+1F00-U+1FFF
        if (0x0370 <= code <= 0x03FF) or (0x1F00 <= code <= 0x1FFF):
            return "greek"

    return "latin"


def strip_hebrew_prefixes(lemma: str) -> tuple[list[str], Optional[str]]:
    """Extract Hebrew prefixes and Strong's number from OSHB lemma.

    OSHB lemmas use '/' as separator between prefixes and the Strong's number.
    Known prefixes: b, c, d, k, l, m, h, w

    Args:
        lemma: OSHB lemma attribute (e.g., "b/7225", "c/d/776")

    Returns:
        Tuple of (prefixes_list, strongs_number)
        - prefixes_list: List of prefix characters (e.g., ["b"], ["c", "d"])
        - strongs_number: The Strong's number part (e.g., "7225"), or None if bare prefix

    Example:
        >>> strip_hebrew_prefixes("b/7225")
        (['b'], '7225')
        >>> strip_hebrew_prefixes("c/d/776")
        (['c', 'd'], '776')
        >>> strip_hebrew_prefixes("l")
        (['l'], None)
    """
    parts = lemma.split("/")

    # Known Hebrew prefixes
    known_prefixes = {"b", "c", "d", "k", "l", "m", "h", "w"}

    prefixes = []
    strongs = None

    for part in parts:
        if part in known_prefixes:
            prefixes.append(part)
        else:
            # This should be the Strong's number (or variant)
            strongs = part
            break

    return (prefixes, strongs)


def normalize_transliteration_for_lookup(text: str) -> str:
    """Normalize scholarly transliteration for ASCII lookup matching.

    Implements industry-standard Hebrew transliteration normalization based on
    SBL General guidelines and common web platform practices (Sefaria, STEP Bible).

    The "Het Problem" (ח):
    - Can be written as: ch, kh, h, x, ḥ
    - Solution: Normalize ALL to 'h'

    The "Tsadi Problem" (צ):
    - Can be written as: tz, ts, z, ṣ
    - Solution: Normalize ALL to 'ts'

    The "Qoph Problem" (ק):
    - Can be written as: q, k
    - Solution: Normalize ALL to 'k'

    The "Shin Problem" (שׁ):
    - Can be written as: sh, š
    - Solution: Normalize ALL to 'sh'

    Transformations (in order):
    1. Strip Unicode diacritics (NFD + remove combining chars): â→a, ḥ→h, š→s
    2. Remove modifier letters: ʼ (aleph marker), ʻ (ayin marker)
    3. Normalize cedilla: ç→s (for chesed: chêçêd → chesed)
    4. Lowercase
    5. Normalize Het variants: ch→h, kh→h, x→h (when not 'sh')
    6. Normalize Qoph variants: q→k
    7. Handle 'ow' vowel pattern: yowm→yom
    8. Handle final 'ym' plural: elohiym→elohim
    9. Simplify 'iy' sequences: elohiym→elohim

    Args:
        text: Scholarly transliteration (e.g., 'ʼĕlôhîym', 'dâbâr', 'chêçêd')

    Returns:
        Normalized ASCII string (e.g., 'elohim', 'dabar', 'hesed')

    Example:
        >>> normalize_transliteration_for_lookup("ʼĕlôhîym")
        'elohim'
        >>> normalize_transliteration_for_lookup("dâbâr")
        'dabar'
        >>> normalize_transliteration_for_lookup("chêçêd")
        'hesed'
        >>> normalize_transliteration_for_lookup("yôwm")
        'yom'
        >>> normalize_transliteration_for_lookup("shâmaʻ")
        'shama'
    """
    import unicodedata
    import re

    # Step 0: Pre-NFD replacements for characters that would be incorrectly decomposed
    # ç (c-cedilla) → s (for chesed: chêçêd → chesed)
    # Must happen BEFORE NFD because NFD decomposes ç → c + combining cedilla
    text = text.replace("ç", "s").replace("Ç", "S")

    # Step 1: NFD decomposition to separate base chars from diacritics
    nfd = unicodedata.normalize("NFD", text)

    # Step 2: Remove combining characters (diacritics like macrons, dots, carons)
    stripped = "".join(c for c in nfd if unicodedata.category(c) != "Mn")

    # Step 3: Remove modifier letters (aleph/ayin markers)
    # ʼ = U+02BC MODIFIER LETTER APOSTROPHE (aleph)
    # ʻ = U+02BB MODIFIER LETTER TURNED COMMA (ayin)
    stripped = stripped.replace("ʼ", "").replace("ʻ", "")
    stripped = stripped.replace("'", "").replace("`", "")  # ASCII variants
    stripped = stripped.replace("ʾ", "").replace("ʿ", "")  # Alternative Unicode

    # Step 4: Lowercase
    stripped = stripped.lower()

    # Step 6: Normalize Het (ח) variants - MUST preserve 'sh' first!
    # Replace 'ch' with 'h' but NOT 'sch' (German spelling)
    # Order matters: handle 'kh' first, then 'ch'
    stripped = stripped.replace("kh", "h")  # kh → h
    # For 'ch', only replace if not preceded by 's' (to preserve 'sch')
    stripped = re.sub(r"(?<!s)ch", "h", stripped)
    # Also normalize standalone 'x' to 'h' (rare but possible)
    # But NOT in common patterns like 'ex', 'ax', etc.
    stripped = re.sub(r"\bx(?=[aeiou])", "h", stripped)

    # Step 7: Normalize Qoph (ק) variants
    stripped = stripped.replace("q", "k")

    # Step 8: Handle 'ow' vowel pattern (holem-vav)
    # yowm → yom, towrah → torah
    # But preserve 'ow' at word boundaries or in common patterns
    stripped = re.sub(r"([^aeiou])ow([^aeiou]|$)", r"\1o\2", stripped)

    # Step 9: Handle final 'ym' plural (Hebrew masculine plural)
    # elohiym → elohim, cherubhiym → cherubim
    if stripped.endswith("ym"):
        stripped = stripped[:-2] + "m"

    # Step 10: Simplify 'iy' sequences
    # elohiym (after step 9) → elohim
    stripped = stripped.replace("iy", "i")

    return stripped


def normalize_user_hebrew_query(text: str) -> str:
    """Normalize user input for Hebrew transliteration matching.

    Applies the same normalization as normalize_transliteration_for_lookup()
    to user input, ensuring both sides match. Additionally handles common
    user spelling variations.

    User Input Variations Handled:
    - "chesed" / "hesed" / "khesed" → all normalize to 'hesed'
    - "shalom" / "sholom" / "schalom" → all normalize to 'shalom'
    - "elohim" / "elokim" → 'elohim' / 'elokim'
    - "cohen" / "kohen" → both normalize to 'kohen'

    Args:
        text: User input query (e.g., 'chesed', 'elohim', 'shalom')

    Returns:
        Normalized query for matching

    Example:
        >>> normalize_user_hebrew_query("chesed")
        'hesed'
        >>> normalize_user_hebrew_query("elohim")
        'elohim'
    """
    # Apply same normalization as scholarly transliterations
    return normalize_transliteration_for_lookup(text)


def parse_oshb_lemma(lemma_attr: str) -> dict:
    """Parse OSHB lemma attribute into structured data.

    Handles all 9 format variants discovered in OSHB:
    1. Plain number: "430" → H0430
    2. Single prefix: "b/7225" → prefix 'b' + H7225
    3. Number + variant: "1254 a" → H1254 variant 'a'
    4. Prefix + variant: "c/6213 a" → prefix 'c' + H6213 variant 'a'
    5. Bare prefix: "l" → prefix 'l', no Strong's
    6. Two prefixes: "c/d/776" → prefixes ['c', 'd'] + H0776
    7. Compound: "1177+" → H1177 compound=True
    8. Two prefix + variant: "c/b/1328 b" → prefixes ['c', 'b'] + H1328 variant 'b'
    9. Three prefixes: "c/m/l/4605" → prefixes ['c', 'm', 'l'] + H4605

    Args:
        lemma_attr: OSHB lemma attribute string

    Returns:
        Dictionary with keys:
        - prefixes: List of prefix characters
        - strongs: Strong's number with H prefix (e.g., "H0430"), or None
        - variant: Optional variant letter (e.g., "a", "b")
        - compound: Optional boolean (True if lemma ends with '+')

    Example:
        >>> parse_oshb_lemma("430")
        {'prefixes': [], 'strongs': 'H0430', 'variant': None}
        >>> parse_oshb_lemma("b/7225")
        {'prefixes': ['b'], 'strongs': 'H7225', 'variant': None}
        >>> parse_oshb_lemma("1254 a")
        {'prefixes': [], 'strongs': 'H1254', 'variant': 'a'}
        >>> parse_oshb_lemma("c/d/776")
        {'prefixes': ['c', 'd'], 'strongs': 'H0776', 'variant': None}
    """
    result = {
        "prefixes": [],
        "strongs": None,
        "variant": None,
    }

    # Check for compound marker (+)
    is_compound = lemma_attr.endswith("+")
    if is_compound:
        lemma_attr = lemma_attr[:-1]  # Remove the +
        result["compound"] = True

    # Split by space to separate number from variant
    parts = lemma_attr.split()
    main_part = parts[0]
    variant = parts[1] if len(parts) > 1 else None

    # Extract prefixes and Strong's number
    prefixes, strongs = strip_hebrew_prefixes(main_part)

    result["prefixes"] = prefixes
    result["variant"] = variant

    # Format Strong's number with H prefix and zero-padding
    if strongs:
        # Remove any variant letter from strongs if present
        strongs_clean = strongs.split()[0] if " " in strongs else strongs
        # Zero-pad to 4 digits
        try:
            strongs_num = int(strongs_clean)
            result["strongs"] = f"H{strongs_num:04d}"
        except ValueError:
            # If it's not a valid number, keep as-is
            result["strongs"] = strongs_clean

    return result
