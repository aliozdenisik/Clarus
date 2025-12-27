"""
Quran Verse Preprocessing Script

Tüm ayetleri normalize ve lemmatize eder, sonuçları JSON'a kayder.
Bir kez çalıştırılır, sonra ön-işlenmiş veri hızlıca yüklenir.

Kullanım:
    python preprocess_verses.py

Çıktı:
    data/quran_preprocessed.json
"""
import json
import time
import sys
import io
from pathlib import Path
from tqdm import tqdm


def preprocess_all_verses():
    """Tüm ayetleri ön-işle ve JSON'a kaydet"""
    
    print("="*60)
    print("QURAN VERSE PREPROCESSING")
    print("="*60)
    
    # Load raw data
    data_dir = Path("data")
    raw_path = data_dir / "quran_tr.json"
    output_path = data_dir / "quran_preprocessed.json"
    
    if not raw_path.exists():
        print("Downloading Quran data...")
        from src.data_loader import QuranDataLoader
        loader = QuranDataLoader()
        loader.download_data()
    
    print(f"Loading raw data...")
    with open(raw_path, "r", encoding="utf-8") as f:
        raw_data = json.load(f)
    
    # Import preprocessing functions (suppress output)
    print("Initializing...")
    
    # Suppress Zeyrek verbose output
    old_stdout = sys.stdout
    sys.stdout = io.StringIO()
    
    from src.turkish_utils import normalize_turkish
    from src.lemmatizer import get_lemma
    
    # Force Zeyrek initialization (quiet)
    _ = get_lemma("test")
    
    sys.stdout = old_stdout
    print("Ready!")
    
    # Count total verses
    total_verses = sum(surah["total_verses"] for surah in raw_data)
    print(f"Processing {total_verses} verses...")
    
    start_time = time.time()
    
    # Process all verses with single progress bar
    preprocessed_verses = []
    
    # Flatten all verses for single progress bar
    all_verses = []
    for surah in raw_data:
        for verse in surah["verses"]:
            all_verses.append((surah, verse))
    
    for surah, verse in tqdm(all_verses, desc="Progress", unit="verse", 
                              bar_format='{desc}: {percentage:3.0f}%|{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]'):
        surah_id = surah["id"]
        verse_id = verse["id"]
        translation = verse["translation"]
        
        # Normalize (quiet) - remove punctuation for cleaner matching
        translation_normalized = normalize_turkish(translation.lower(), remove_punctuation=True)
        
        # Lemmatize (quiet - suppress Zeyrek output)
        old_stdout = sys.stdout
        sys.stdout = io.StringIO()
        
        words = translation.split()
        lemmas = [get_lemma(word) for word in words]
        translation_lemma = " ".join(lemmas)
        
        sys.stdout = old_stdout
        
        # Create record
        record = {
            "id": f"{surah_id}:{verse_id}",
            "surah_id": surah_id,
            "surah_name": surah["translation"],
            "surah_name_arabic": surah["name"],
            "surah_transliteration": surah["transliteration"],
            "surah_type": surah["type"],
            "verse_id": verse_id,
            "arabic_text": verse["text"],
            "translation": translation,
            "translation_normalized": translation_normalized,
            "translation_lemma": translation_lemma,
        }
        preprocessed_verses.append(record)
    
    elapsed = time.time() - start_time
    
    # Save
    print(f"\nSaving to {output_path}...")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(preprocessed_verses, f, ensure_ascii=False, indent=2)
    
    # Summary
    print("\n" + "="*60)
    print("COMPLETE!")
    print("="*60)
    print(f"Verses: {len(preprocessed_verses)}")
    print(f"Time: {elapsed/60:.1f} minutes")
    print(f"Output: {output_path}")
    
    return output_path


if __name__ == "__main__":
    preprocess_all_verses()
