"""
Turkish Lemmatization Module

Zeyrek kütüphanesi ile Türkçe kelimeleri kök formuna indirir.
İndeksleme ve arama sırasında kullanılır.

Örnek:
    sabrı → sabır
    namazla → namaz
    Allaha → Allah
"""
from typing import Optional
import re
import logging
import warnings
import os

# Suppress ALL Zeyrek verbose output
logging.basicConfig(level=logging.ERROR)
logging.getLogger().setLevel(logging.ERROR)
logging.getLogger('zeyrek').setLevel(logging.CRITICAL)
logging.getLogger('zeyrek.morphology').setLevel(logging.CRITICAL)
warnings.filterwarnings('ignore')

# Disable print statements from Zeyrek by setting environment variable
os.environ['ZEYREK_DEBUG'] = '0'

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
            if hasattr(_analyzer, 'debug'):
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
    
    analyzer = get_analyzer()
    if analyzer is None:
        return word
    
    try:
        # Küçük harfe çevir
        word_lower = word.lower().strip()
        
        # Noktalama işaretlerini temizle
        word_clean = re.sub(r'[^\w\s]', '', word_lower)
        
        if not word_clean:
            return word
        
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
            # İlk lemma'yı al
            lemma = results[0][1][0]
            return lemma
        
        return word_clean
        
    except Exception:
        return word


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
    return ' '.join(lemmas)


def normalize_and_lemmatize(text: str) -> dict:
    """
    Metni hem normalize hem lemmatize et.
    
    Args:
        text: Orijinal metin
        
    Returns:
        Dict with original, normalized, and lemmatized versions
    """
    from src.turkish_utils import normalize_turkish
    
    return {
        "original": text,
        "normalized": normalize_turkish(text.lower()),
        "lemmatized": lemmatize_text(text),
    }


if __name__ == "__main__":
    # Test
    print("Zeyrek Lemmatization Test")
    print("="*40)
    
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
