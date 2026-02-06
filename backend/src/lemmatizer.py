"""
Turkish Lemmatization Module

Zeyrek kütüphanesi ile Türkçe kelimeleri kök formuna indirir.
İndeksleme ve arama sırasında kullanılır.

Örnek:
    sabrı → sabır
    namazla → namaz
    Allaha → Allah
"""

import re
import logging
import warnings
import os

# Suppress ALL Zeyrek verbose output
logging.basicConfig(level=logging.ERROR)
logging.getLogger().setLevel(logging.ERROR)
logging.getLogger("zeyrek").setLevel(logging.CRITICAL)
logging.getLogger("zeyrek.morphology").setLevel(logging.CRITICAL)
warnings.filterwarnings("ignore")

# Disable print statements from Zeyrek by setting environment variable
os.environ["ZEYREK_DEBUG"] = "0"

# Lazy load Zeyrek (yavaş başlatma)
_analyzer = None


def get_analyzer():
    """Zeyrek analyzer'ı lazy load et"""
    global _analyzer
    if _analyzer is None:
        try:
            # Suppress all output during import
            import sys
            import io

            old_stdout = sys.stdout
            old_stderr = sys.stderr
            sys.stdout = io.StringIO()
            sys.stderr = io.StringIO()

            from zeyrek import MorphAnalyzer

            _analyzer = MorphAnalyzer()

            # Disable debug mode if available
            if hasattr(_analyzer, "debug"):
                _analyzer.debug = False

            sys.stdout = old_stdout
            sys.stderr = old_stderr

        except ImportError:
            sys.stdout = old_stdout
            sys.stderr = old_stderr
            return None
        except Exception:
            sys.stdout = old_stdout
            sys.stderr = old_stderr
            return None
    return _analyzer


# Known corrections for Zeyrek errors
KNOWN_LEMMA_CORRECTIONS = {
    # word: correct_lemma
    "yardım": "yardım",  # Zeyrek incorrectly returns "yarmak"
    "yardımı": "yardım",
    "yardıma": "yardım",
    "yardımla": "yardım",
    "kavuşacaklarını": "kavuşmak",
    "döneceklerini": "dönmek",
    "umanlar": "ummak",
    "huşu": "huşu",
}


def get_lemma(word: str) -> str:
    """
    Kelimeyi kök formuna (lemma) çevir.

    Args:
        word: Türkçe kelime

    Returns:
        Kök form (lemma) veya orijinal kelime

    Example:
        >>> get_lemma("sabrı")
        "sabır"
        >>> get_lemma("namazla")
        "namaz"
    """
    import sys
    import io

    # Küçük harfe çevir ve temizle
    word_lower = word.lower().strip()
    word_clean = re.sub(r"[^\w\s]", "", word_lower)

    if not word_clean:
        return word

    # Check known corrections first
    if word_clean in KNOWN_LEMMA_CORRECTIONS:
        return KNOWN_LEMMA_CORRECTIONS[word_clean]

    analyzer = get_analyzer()
    if analyzer is None:
        return word_clean

    try:
        # Suppress Zeyrek debug output during lemmatize
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        sys.stdout = io.StringIO()
        sys.stderr = io.StringIO()

        try:
            results = analyzer.lemmatize(word_clean)
        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr

        if results and results[0][1]:
            # Get all lemmas and pick the best one
            lemmas = results[0][1]

            # Prefer nouns over verbs for common words
            for lemma in lemmas:
                # If lemma looks like the original word (similar), prefer it
                if lemma in word_clean or word_clean.startswith(lemma[:3]):
                    return lemma

            # Otherwise return first lemma
            return lemmas[0]

        return word_clean

    except Exception:
        return word_clean


def lemmatize_text(text: str) -> str:
    """
    Tüm metni lemmatize et.

    Args:
        text: Türkçe metin

    Returns:
        Lemmatize edilmiş metin

    Example:
        >>> lemmatize_text("Sabır ve namazla Allah'a sığınıp yardım isteyin")
        "sabır ve namaz allah sığın yardım iste"
    """
    if not text:
        return ""

    words = text.split()
    lemmas = [get_lemma(word) for word in words]
    return " ".join(lemmas)


if __name__ == "__main__":
    # Test
    print("Zeyrek Lemmatization Test")
    print("=" * 40)

    test_words = [
        "sabrı",
        "sabra",
        "sabırla",
        "namazla",
        "namazını",
        "Allaha",
        "Allah'ın",
        "yardım",
    ]

    print("\nKelime Testleri:")
    for word in test_words:
        lemma = get_lemma(word)
        print(f"  {word} → {lemma}")

    print("\nMetin Testi:")
    text = "Sabır ve namazla Allah'a sığınıp yardım isteyin"
    print(f"  Orijinal: {text}")
    print(f"  Lemmatized: {lemmatize_text(text)}")
