"""Greek text normalization utilities for morphological search.

Provides consistent normalization for both ETL indexing and query-time
processing. Handles accent removal, transliteration, and script detection
for Bible keyword search (New Testament Greek).
"""

import re
import unicodedata
from typing import Optional


def remove_greek_accents(text: str) -> str:
    """Strip Greek accents and diacritical marks.

    Removes combining diacritical marks (category 'Mn' - Mark, Nonspacing)
    while preserving base Greek letters. Handles both polytonic (ancient)
    and monotonic (modern) Greek.

    Unicode ranges affected:
    - U+0300-U+036F: Combining Diacritical Marks
    - U+1AB0-U+1AFF: Combining Diacritical Marks Extended
    - U+1DC0-U+1DFF: Combining Diacritical Marks Supplement

    Args:
        text: Greek text with accents and diacritics

    Returns:
        Text with accents removed

    Example:
        >>> remove_greek_accents("λόγος")
        'λογος'
        >>> remove_greek_accents("ἀγάπη")
        'αγαπη'
    """
    # First normalize to NFD (decomposed form) to separate base letters from accents
    nfd_text = unicodedata.normalize("NFD", text)
    # Strip combining characters (category Mn = Mark, nonspacing)
    result = "".join(c for c in nfd_text if unicodedata.category(c) != "Mn")
    return result


def normalize_greek(text: str) -> str:
    """Full normalization pipeline for Greek text.

    Steps:
      1. Remove accents and diacritical marks
      2. Apply NFC Unicode normalization
      3. Strip any remaining combining characters

    Handles both polytonic (ancient) and monotonic (modern) Greek.

    Args:
        text: Greek text to normalize

    Returns:
        Normalized Greek text

    Example:
        >>> normalize_greek("λόγος")
        'λογος'
        >>> normalize_greek("ΘΕΟΣ")
        'ΘΕΟΣ'
    """
    result = remove_greek_accents(text)
    result = unicodedata.normalize("NFC", result)
    # Strip any remaining combining characters
    result = "".join(c for c in result if unicodedata.category(c) != "Mn")
    return result


def transliterate_greek(text: str) -> str:
    """Convert Greek text to ALA-LC standard romanization.

    Uses standard scholarly transliteration mapping for Greek consonants
    and vowels. Handles both regular and final forms of letters.

    Mapping (ALA-LC standard):
    - α→a, β→b, γ→g, δ→d, ε→e, ζ→z, η→ē, θ→th, ι→i, κ→k
    - λ→l, μ→m, ν→n, ξ→x, ο→o, π→p, ρ→r, σ/ς→s, τ→t, υ→y
    - φ→ph, χ→ch, ψ→ps, ω→ō

    Final sigma (ς) is treated the same as regular sigma (σ).

    Args:
        text: Greek text to transliterate

    Returns:
        Transliterated Latin text

    Example:
        >>> transliterate_greek("λογος")
        'logos'
        >>> transliterate_greek("θεος")
        'theos'
    """
    # First remove accents
    text = remove_greek_accents(text)

    # ALA-LC standard Greek transliteration mapping
    mapping = {
        # Lowercase vowels
        "α": "a",
        "ε": "e",
        "η": "ē",
        "ι": "i",
        "ο": "o",
        "υ": "y",
        "ω": "ō",
        # Lowercase consonants
        "β": "b",
        "γ": "g",
        "δ": "d",
        "ζ": "z",
        "θ": "th",
        "κ": "k",
        "λ": "l",
        "μ": "m",
        "ν": "n",
        "ξ": "x",
        "π": "p",
        "ρ": "r",
        "σ": "s",  # Regular sigma
        "ς": "s",  # Final sigma
        "τ": "t",
        "φ": "ph",
        "χ": "ch",
        "ψ": "ps",
        # Uppercase vowels
        "Α": "A",
        "Ε": "E",
        "Η": "Ē",
        "Ι": "I",
        "Ο": "O",
        "Υ": "Y",
        "Ω": "Ō",
        # Uppercase consonants
        "Β": "B",
        "Γ": "G",
        "Δ": "D",
        "Ζ": "Z",
        "Θ": "Th",
        "Κ": "K",
        "Λ": "L",
        "Μ": "M",
        "Ν": "N",
        "Ξ": "X",
        "Π": "P",
        "Ρ": "R",
        "Σ": "S",
        "Τ": "T",
        "Φ": "Ph",
        "Χ": "Ch",
        "Ψ": "Ps",
    }

    result = ""
    i = 0
    while i < len(text):
        # Check for two-character combinations first (θ→th, φ→ph, χ→ch, ψ→ps, etc.)
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
        >>> detect_script("λόγος")
        'greek'
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
        # Greek: U+0370-U+03FF (Greek and Coptic) or U+1F00-U+1FFF (Greek Extended)
        if (0x0370 <= code <= 0x03FF) or (0x1F00 <= code <= 0x1FFF):
            return "greek"

    return "latin"


def reverse_transliterate_greek(text: str) -> str:
    """Convert Latin transliteration back to Greek.

    Handles common scholarly transliterations (reverse of ALA-LC standard).
    Multi-character sequences are processed first (th→θ, ph→φ, ch→χ, ps→ψ),
    then single characters. Final sigma (ς) is used at word boundaries.

    Mapping (reverse of ALA-LC):
    - th→θ, ph→φ, ch→χ, ps→ψ
    - a→α, b→β, g→γ, d→δ, e→ε, z→ζ, i→ι, k→κ
    - l→λ, m→μ, n→ν, x→ξ, o→ο, p→π, r→ρ, s→σ/ς, t→τ, y→υ
    - ē→η, ō→ω (macron vowels)

    Args:
        text: Latin transliteration to convert

    Returns:
        Greek text (lowercase, no accents, with proper final sigma)

    Example:
        >>> reverse_transliterate_greek("logos")
        'λογος'
        >>> reverse_transliterate_greek("theos")
        'θεος'
        >>> reverse_transliterate_greek("agape")
        'αγαπε'
    """
    # Work with lowercase for consistent mapping
    text = text.lower()

    # Multi-character sequences first (order matters: longer sequences first)
    multi_char_mapping = {
        "th": "θ",
        "ph": "φ",
        "ch": "χ",
        "ps": "ψ",
    }

    # Single character mapping (reverse of transliterate_greek)
    # Note: 's' is handled specially for final sigma
    single_char_mapping = {
        # Vowels
        "a": "α",
        "e": "ε",
        "ē": "η",  # eta with macron
        "i": "ι",
        "o": "ο",
        "y": "υ",
        "ō": "ω",  # omega with macron
        "u": "υ",  # alternative for upsilon
        # Consonants
        "b": "β",
        "g": "γ",
        "d": "δ",
        "z": "ζ",
        "k": "κ",
        "l": "λ",
        "m": "μ",
        "n": "ν",
        "x": "ξ",
        "p": "π",
        "r": "ρ",
        "t": "τ",
        # Alternative mappings
        "c": "κ",  # 'c' often used for kappa
        "h": "η",  # standalone 'h' could be eta (context-dependent)
    }

    result = ""
    i = 0
    while i < len(text):
        # Check for two-character sequences first
        if i + 1 < len(text):
            two_char = text[i : i + 2]
            if two_char in multi_char_mapping:
                result += multi_char_mapping[two_char]
                i += 2
                continue

        # Single character mapping
        char = text[i]
        if char == "s":
            # Use final sigma (ς) at word end, regular sigma (σ) otherwise
            # Word end = last char OR next char is not a letter
            is_word_end = (i == len(text) - 1) or not text[i + 1].isalpha()
            result += "ς" if is_word_end else "σ"
        elif char in single_char_mapping:
            result += single_char_mapping[char]
        else:
            # Keep non-mapped characters as-is (spaces, punctuation, etc.)
            result += char
        i += 1

    return result


# ============================================================================
# INLINE VERIFICATION TESTS
# ============================================================================

if __name__ == "__main__":
    from rich.console import Console
    from rich.table import Table

    console = Console()

    # Test data
    tests = [
        {
            "name": "remove_greek_accents",
            "cases": [
                ("λόγος", "λογος"),
                ("ἀγάπη", "αγαπη"),
                ("ΘΕΟΣ", "ΘΕΟΣ"),
            ],
        },
        {
            "name": "normalize_greek",
            "cases": [
                ("λόγος", "λογος"),
                ("ἀγάπη", "αγαπη"),
            ],
        },
        {
            "name": "transliterate_greek",
            "cases": [
                ("λογος", "logos"),
                ("θεος", "theos"),
                ("αγαπη", "agapē"),
            ],
        },
        {
            "name": "detect_script",
            "cases": [
                ("λόγος", "greek"),
                ("בראשית", "hebrew"),
                ("الله", "arabic"),
                ("hello", "latin"),
            ],
        },
        {
            "name": "reverse_transliterate_greek",
            "cases": [
                ("logos", "λογος"),
                ("theos", "θεος"),
                ("agape", "αγαπε"),
                ("christos", "χριστος"),
                ("pistis", "πιστις"),
                ("pneuma", "πνευμα"),
            ],
        },
    ]

    # Run tests
    all_passed = True
    results = []

    for test_group in tests:
        func_name = test_group["name"]
        func = globals()[func_name]
        passed = 0
        failed = 0

        for input_val, expected in test_group["cases"]:
            try:
                result = func(input_val)
                if result == expected:
                    passed += 1
                else:
                    failed += 1
                    all_passed = False
                    console.print(
                        f"[red]✗ {func_name}({input_val!r})[/red]"
                        f"\n  Expected: {expected!r}\n  Got: {result!r}"
                    )
            except Exception as e:
                failed += 1
                all_passed = False
                console.print(
                    f"[red]✗ {func_name}({input_val!r}) raised {type(e).__name__}: {e}[/red]"
                )

        results.append((func_name, passed, failed))

    # Print summary table
    console.print("\n")
    table = Table(title="Greek Normalizer Test Results")
    table.add_column("Function", style="cyan")
    table.add_column("Passed", style="green")
    table.add_column("Failed", style="red")
    table.add_column("Status", style="bold")

    for func_name, passed, failed in results:
        status = "[green]✓ PASS[/green]" if failed == 0 else "[red]✗ FAIL[/red]"
        table.add_row(func_name, str(passed), str(failed), status)

    console.print(table)

    # Print overall result
    total_passed = sum(p for _, p, _ in results)
    total_failed = sum(f for _, _, f in results)
    console.print(
        f"\n[bold]TOTAL: {total_passed}/{total_passed + total_failed} tests pass[/bold]"
    )

    if all_passed:
        console.print("[green]✓ ALL TESTS PASSED[/green]")
        exit(0)
    else:
        console.print("[red]✗ SOME TESTS FAILED[/red]")
        exit(1)
