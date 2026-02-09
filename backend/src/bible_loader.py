"""
Bible JSON Data Loader

Loads Bible data from getBible API and prepares chunks for indexing.
Supports English translations: KJV and KJVA (King James Version with Apocrypha).
"""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests
from tqdm import tqdm


@dataclass
class BibleChunk:
    """Represents a single searchable chunk (verse)"""

    id: str  # Format: translation:book_id:chapter:verse
    translation: str  # e.g., "kjva", "kjv"
    book_id: int
    book_name: str
    chapter: int
    verse: int
    text: str
    testament: str  # "OT" (Old Testament) or "NT" (New Testament)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "translation": self.translation,
            "book_id": self.book_id,
            "book_name": self.book_name,
            "chapter": self.chapter,
            "verse": self.verse,
            "text": self.text,
            "testament": self.testament,
        }


# Old Testament book IDs (1-39 Protestant canon)
OLD_TESTAMENT_BOOKS = set(range(1, 40))

# New Testament book IDs (40-66)
NEW_TESTAMENT_BOOKS = set(range(40, 67))

# Apocrypha/Deuterocanonical book IDs (67-81+)
# Includes: 1 Esdras, 2 Esdras, Tobit, Judith, Additions to Esther, Wisdom,
# Sirach, Baruch, Prayer of Azariah, Susanna, Bel and the Dragon,
# Prayer of Manasses, 1 Maccabees, 2 Maccabees
APOCRYPHA_BOOKS = {67, 68, 69, 70, 71, 73, 74, 75, 76, 77, 78, 79, 80, 81}


def get_testament(book_id: int) -> str:
    """
    Determine testament category for a book ID.

    Args:
        book_id: The numerical ID of the book

    Returns:
        "OT" for Old Testament, "NT" for New Testament, "Apocrypha" for Apocryphal books
    """
    if book_id in OLD_TESTAMENT_BOOKS:
        return "OT"
    elif book_id in NEW_TESTAMENT_BOOKS:
        return "NT"
    elif book_id in APOCRYPHA_BOOKS:
        return "Apocrypha"
    else:
        # Fallback for unknown IDs based on ID ranges
        if book_id < 40:
            return "OT"
        elif book_id < 67:
            return "NT"
        else:
            return "Apocrypha"


class BibleDataLoader:
    """Loads and processes Bible data for hybrid search indexing"""

    API_URL = "https://api.getbible.net/v2"

    # Available translations
    TRANSLATIONS = {
        "kjva": {
            "name": "King James Version with Apocrypha",
            "language": "English",
            "has_apocrypha": True,
        },
        "kjv": {
            "name": "King James Version",
            "language": "English",
            "has_apocrypha": False,
        },
    }

    def __init__(self, translation: str = "kjva", data_dir: Optional[Path] = None):
        if translation not in self.TRANSLATIONS:
            available = ", ".join(self.TRANSLATIONS.keys())
            raise ValueError(f"Unknown translation: {translation}. Available: {available}")

        self.translation = translation
        self.data_dir = data_dir or Path("data")
        self.data_dir.mkdir(exist_ok=True)
        self.cache_path = self.data_dir / f"bible_{translation}.json"
        self._data: Optional[Dict] = None

    def download_data(self, force: bool = False) -> Path:
        """Download Bible translation from getBible API"""
        if self.cache_path.exists() and not force:
            print(f"Using cached data: {self.cache_path}")
            return self.cache_path

        url = f"{self.API_URL}/{self.translation}.json"
        print(f"Downloading Bible data from {url}...")

        response = requests.get(url, timeout=120)
        response.raise_for_status()

        with open(self.cache_path, "w", encoding="utf-8") as f:
            json.dump(response.json(), f, ensure_ascii=False, indent=2)

        print(f"Downloaded and cached to: {self.cache_path}")
        return self.cache_path

    def load_data(self) -> Dict:
        """Load Bible data from cache or download"""
        if self._data is not None:
            return self._data

        if not self.cache_path.exists():
            self.download_data()

        with open(self.cache_path, "r", encoding="utf-8") as f:
            self._data = json.load(f)

        return self._data if self._data is not None else {}

    def create_chunks(self, show_progress: bool = True) -> List[BibleChunk]:
        """
        Create verse-based chunks for indexing.
        Each verse becomes a separate searchable chunk.
        """
        data = self.load_data()
        chunks: List[BibleChunk] = []

        # getBible API structure: data contains books, each book contains chapters
        books = data.get("books", data)  # Handle both formats

        if isinstance(books, dict):
            book_list = list(books.values())
        else:
            book_list = books

        iterator = tqdm(book_list, desc="Creating chunks") if show_progress else book_list

        for book in iterator:
            book_id = book.get("nr", book.get("book_nr", 0))
            book_name = book.get("name", book.get("book_name", "Unknown"))

            # Determine testament based on book ID using proper categorization
            testament = get_testament(book_id)

            chapters = book.get("chapters", {})
            if isinstance(chapters, dict):
                chapter_list = list(chapters.values())
            else:
                chapter_list = chapters

            for chapter_data in chapter_list:
                chapter_num = chapter_data.get("chapter", 0)

                verses = chapter_data.get("verses", {})
                if isinstance(verses, dict):
                    verse_list = list(verses.values())
                else:
                    verse_list = verses

                for verse_data in verse_list:
                    verse_num = verse_data.get("verse", 0)
                    text = verse_data.get("text", "")

                    if not text.strip():
                        continue

                    chunk = BibleChunk(
                        id=f"{self.translation}:{book_id}:{chapter_num}:{verse_num}",
                        translation=self.translation,
                        book_id=book_id,
                        book_name=book_name,
                        chapter=chapter_num,
                        verse=verse_num,
                        text=text,
                        testament=testament,
                    )
                    chunks.append(chunk)

        return chunks

    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the loaded data"""
        data = self.load_data()

        books = data.get("books", data)
        if isinstance(books, dict):
            book_list = list(books.values())
        else:
            book_list = books

        total_chapters = 0
        total_verses = 0
        ot_books = 0
        nt_books = 0
        apocrypha_books = 0

        for book in book_list:
            book_id = book.get("nr", book.get("book_nr", 0))
            testament = get_testament(book_id)
            if testament == "OT":
                ot_books += 1
            elif testament == "NT":
                nt_books += 1
            elif testament == "Apocrypha":
                apocrypha_books += 1

            chapters = book.get("chapters", {})
            if isinstance(chapters, dict):
                chapter_list = list(chapters.values())
            else:
                chapter_list = chapters

            total_chapters += len(chapter_list)

            for chapter_data in chapter_list:
                verses = chapter_data.get("verses", {})
                if isinstance(verses, dict):
                    total_verses += len(verses)
                else:
                    total_verses += len(verses)

        translation_info = self.TRANSLATIONS.get(self.translation, {})

        return {
            "translation": self.translation,
            "translation_name": translation_info.get("name", "Unknown"),
            "language": translation_info.get("language", "Unknown"),
            "total_books": len(book_list),
            "old_testament_books": ot_books,
            "new_testament_books": nt_books,
            "apocrypha_books": apocrypha_books,
            "total_chapters": total_chapters,
            "total_verses": total_verses,
            "has_apocrypha": translation_info.get("has_apocrypha", False) or apocrypha_books > 0,
        }


if __name__ == "__main__":
    # Test the loader
    print("Testing BibleDataLoader...")

    loader = BibleDataLoader("kjva")
    loader.download_data()

    stats = loader.get_stats()
    print(f"\nBible Stats ({loader.translation}):")
    for key, value in stats.items():
        print(f"  {key}: {value}")

    chunks = loader.create_chunks()
    print(f"\nCreated {len(chunks)} chunks")

    # Show sample
    if chunks:
        sample = chunks[0]
        print("\nSample chunk:")
        print(f"  ID: {sample.id}")
        print(f"  Book: {sample.book_name}")
        print(f"  Chapter: {sample.chapter}")
        print(f"  Verse: {sample.verse}")
        print(f"  Testament: {sample.testament}")
        print(f"  Text: {sample.text[:100]}...")
