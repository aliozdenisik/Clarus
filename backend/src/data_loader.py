"""
Quran JSON Data Loader

Loads Quran data from risan/quran-json repository and prepares chunks for indexing.
"""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import requests
from tqdm import tqdm


@dataclass
class QuranChunk:
    """Represents a single searchable chunk (verse)"""

    id: str  # Format: surah_id:verse_id
    surah_id: int
    surah_name: str
    surah_name_arabic: str
    surah_transliteration: str
    surah_type: str  # meccan or medinan
    verse_id: int
    arabic_text: str
    translation: str  # Turkish meal
    translation_normalized: str = ""  # ASCII normalized for search
    translation_lemma: str = ""  # Lemmatized for morphological search

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "surah_id": self.surah_id,
            "surah_name": self.surah_name,
            "surah_name_arabic": self.surah_name_arabic,
            "surah_transliteration": self.surah_transliteration,
            "surah_type": self.surah_type,
            "verse_id": self.verse_id,
            "arabic_text": self.arabic_text,
            "translation": self.translation,
            "translation_normalized": self.translation_normalized,
            "translation_lemma": self.translation_lemma,
        }


class QuranDataLoader:
    """Loads and processes Quran data for hybrid search indexing"""

    CDN_URL = "https://cdn.jsdelivr.net/npm/quran-json@3.1.2/dist/quran_tr.json"

    def __init__(self, data_dir: Path | None = None):
        self.data_dir = data_dir or Path("data")
        self.data_dir.mkdir(exist_ok=True)
        self.cache_path = self.data_dir / "quran_tr.json"
        self._data: list[dict] | None = None

    def download_data(self, force: bool = False) -> Path:
        """Download Quran Turkish translation from CDN"""
        if self.cache_path.exists() and not force:
            print(f"Using cached data: {self.cache_path}")
            return self.cache_path

        print(f"Downloading Quran data from {self.CDN_URL}...")
        response = requests.get(self.CDN_URL, timeout=30)
        response.raise_for_status()

        with open(self.cache_path, "w", encoding="utf-8") as f:
            json.dump(response.json(), f, ensure_ascii=False, indent=2)

        print(f"Downloaded and cached to: {self.cache_path}")
        return self.cache_path

    def load_data(self) -> list[dict]:
        """Load Quran data from cache or download"""
        if self._data is not None:
            return self._data

        if not self.cache_path.exists():
            self.download_data()

        with open(self.cache_path, encoding="utf-8") as f:
            loaded = json.load(f)
            self._data = loaded if isinstance(loaded, list) else []

        assert self._data is not None
        return self._data

    def create_chunks(self, show_progress: bool = True, with_preprocessing: bool = True) -> list[QuranChunk]:
        """
        Create verse-based chunks for indexing.
        Each verse becomes a separate searchable chunk.

        Args:
            show_progress: Show tqdm progress bar
            with_preprocessing: If True, compute normalized and lemmatized fields
        """
        data = self.load_data()
        chunks: list[QuranChunk] = []

        # Lazy import preprocessing modules
        normalize_fn = None
        lemmatize_fn = None

        if with_preprocessing:
            try:
                from src.turkish_utils import normalize_turkish

                normalize_fn = normalize_turkish
                print("Turkish normalization enabled")
            except ImportError:
                print("Warning: turkish_utils not available")

            try:
                from src.lemmatizer import lemmatize_text

                lemmatize_fn = lemmatize_text
                print("Lemmatization enabled (Zeyrek)")
            except ImportError:
                print("Warning: lemmatizer not available")

        iterator = tqdm(data, desc="Creating chunks") if show_progress else data

        for surah in iterator:
            surah_id = surah["id"]
            surah_name = surah["translation"]  # Turkish name
            surah_name_arabic = surah["name"]
            surah_transliteration = surah["transliteration"]
            surah_type = surah["type"]

            for verse in surah["verses"]:
                translation = verse["translation"]

                # Compute normalized version
                translation_normalized = ""
                if normalize_fn:
                    translation_normalized = normalize_fn(translation.lower())

                # Compute lemmatized version
                translation_lemma = ""
                if lemmatize_fn:
                    translation_lemma = lemmatize_fn(translation)

                chunk = QuranChunk(
                    id=f"{surah_id}:{verse['id']}",
                    surah_id=surah_id,
                    surah_name=surah_name,
                    surah_name_arabic=surah_name_arabic,
                    surah_transliteration=surah_transliteration,
                    surah_type=surah_type,
                    verse_id=verse["id"],
                    arabic_text=verse["text"],
                    translation=translation,
                    translation_normalized=translation_normalized,
                    translation_lemma=translation_lemma,
                )
                chunks.append(chunk)

        return chunks

    def get_stats(self) -> dict[str, int]:
        """Get statistics about the loaded data"""
        data = self.load_data()
        total_verses = sum(surah["total_verses"] for surah in data)
        meccan = sum(1 for s in data if s["type"] == "meccan")
        medinan = sum(1 for s in data if s["type"] == "medinan")

        return {
            "total_surahs": len(data),
            "total_verses": total_verses,
            "meccan_surahs": meccan,
            "medinan_surahs": medinan,
        }


if __name__ == "__main__":
    # Test the loader
    loader = QuranDataLoader()
    loader.download_data()

    stats = loader.get_stats()
    print("\nQuran Stats:")
    for key, value in stats.items():
        print(f"  {key}: {value}")

    chunks = loader.create_chunks()
    print(f"\nCreated {len(chunks)} chunks")

    # Show sample
    sample = chunks[0]
    print("\nSample chunk:")
    print(f"  ID: {sample.id}")
    print(f"  Surah: {sample.surah_name} ({sample.surah_transliteration})")
    print(f"  Translation: {sample.translation[:80]}...")
