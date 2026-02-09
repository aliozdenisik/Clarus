"""
OSIS XML Bible Loader

Loads Turkish Bible from OSIS XML format and prepares data for indexing.
Supports separation into Old Testament (OT) and New Testament (NT) collections.
"""

import logging
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)


# OSIS book ID to Bible book mapping
# Based on Protestant canon: OT (1-39), NT (40-66)
OSIS_BOOK_MAP = {
    # Old Testament (1-39)
    "Gen": (1, "Genesis", "OT"),
    "Exod": (2, "Exodus", "OT"),
    "Lev": (3, "Leviticus", "OT"),
    "Num": (4, "Numbers", "OT"),
    "Deut": (5, "Deuteronomy", "OT"),
    "Josh": (6, "Joshua", "OT"),
    "Judg": (7, "Judges", "OT"),
    "Ruth": (8, "Ruth", "OT"),
    "1Sam": (9, "1 Samuel", "OT"),
    "2Sam": (10, "2 Samuel", "OT"),
    "1Kgs": (11, "1 Kings", "OT"),
    "2Kgs": (12, "2 Kings", "OT"),
    "1Chr": (13, "1 Chronicles", "OT"),
    "2Chr": (14, "2 Chronicles", "OT"),
    "Ezra": (15, "Ezra", "OT"),
    "Neh": (16, "Nehemiah", "OT"),
    "Esth": (17, "Esther", "OT"),
    "Job": (18, "Job", "OT"),
    "Ps": (19, "Psalms", "OT"),
    "Prov": (20, "Proverbs", "OT"),
    "Eccl": (21, "Ecclesiastes", "OT"),
    "Song": (22, "Song of Solomon", "OT"),
    "Isa": (23, "Isaiah", "OT"),
    "Jer": (24, "Jeremiah", "OT"),
    "Lam": (25, "Lamentations", "OT"),
    "Ezek": (26, "Ezekiel", "OT"),
    "Dan": (27, "Daniel", "OT"),
    "Hos": (28, "Hosea", "OT"),
    "Joel": (29, "Joel", "OT"),
    "Amos": (30, "Amos", "OT"),
    "Obad": (31, "Obadiah", "OT"),
    "Jonah": (32, "Jonah", "OT"),
    "Mic": (33, "Micah", "OT"),
    "Nah": (34, "Nahum", "OT"),
    "Hab": (35, "Habakkuk", "OT"),
    "Zeph": (36, "Zephaniah", "OT"),
    "Hag": (37, "Haggai", "OT"),
    "Zech": (38, "Zechariah", "OT"),
    "Mal": (39, "Malachi", "OT"),
    # New Testament (40-66)
    "Matt": (40, "Matthew", "NT"),
    "Mark": (41, "Mark", "NT"),
    "Luke": (42, "Luke", "NT"),
    "John": (43, "John", "NT"),
    "Acts": (44, "Acts", "NT"),
    "Rom": (45, "Romans", "NT"),
    "1Cor": (46, "1 Corinthians", "NT"),
    "2Cor": (47, "2 Corinthians", "NT"),
    "Gal": (48, "Galatians", "NT"),
    "Eph": (49, "Ephesians", "NT"),
    "Phil": (50, "Philippians", "NT"),
    "Col": (51, "Colossians", "NT"),
    "1Thess": (52, "1 Thessalonians", "NT"),
    "2Thess": (53, "2 Thessalonians", "NT"),
    "1Tim": (54, "1 Timothy", "NT"),
    "2Tim": (55, "2 Timothy", "NT"),
    "Titus": (56, "Titus", "NT"),
    "Phlm": (57, "Philemon", "NT"),
    "Heb": (58, "Hebrews", "NT"),
    "Jas": (59, "James", "NT"),
    "1Pet": (60, "1 Peter", "NT"),
    "2Pet": (61, "2 Peter", "NT"),
    "1John": (62, "1 John", "NT"),
    "2John": (63, "2 John", "NT"),
    "3John": (64, "3 John", "NT"),
    "Jude": (65, "Jude", "NT"),
    "Rev": (66, "Revelation", "NT"),
}


def get_testament(book_id: str) -> str:
    """
    Determine testament for a book ID.

    Args:
        book_id: OSIS book ID (e.g., "Gen", "Matt")

    Returns:
        "OT" for Old Testament, "NT" for New Testament

    Raises:
        ValueError: If book_id is not recognized
    """
    if book_id not in OSIS_BOOK_MAP:
        raise ValueError(f"Unknown OSIS book ID: {book_id}")

    return OSIS_BOOK_MAP[book_id][2]


def strip_xml_tags(text: str) -> str:
    """
    Strip all XML tags from text while preserving content.

    Args:
        text: Text with potential XML tags

    Returns:
        Clean text without XML tags
    """
    # Remove all XML tags but keep the text content
    cleaned = re.sub(r"<[^>]+>", "", text)
    # Normalize whitespace
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned.strip()


class OsisLoader:
    """Loads Turkish Bible from OSIS XML format"""

    def __init__(self, file_path: str):
        """
        Initialize OSIS loader.

        Args:
            file_path: Path to OSIS XML file

        Raises:
            FileNotFoundError: If OSIS file does not exist
        """
        self.file_path = Path(file_path)
        if not self.file_path.exists():
            raise FileNotFoundError(f"OSIS file not found: {file_path}")

    def load(self) -> Tuple[List[Dict], List[Dict]]:
        """
        Load and parse OSIS XML file.

        Returns:
            Tuple of (ot_verses, nt_verses) where each is a list of verse dicts with keys:
            - book: Book name (str)
            - chapter: Chapter number (int)
            - verse: Verse number (int)
            - text: Verse text (str)
            - testament: "OT" or "NT" (str)

        Raises:
            ValueError: If XML parsing fails
        """
        try:
            tree = ET.parse(self.file_path)
            root = tree.getroot()
        except ET.ParseError as e:
            raise ValueError(f"Failed to parse OSIS XML: {e}")

        # Handle XML namespace
        namespace = {"osis": "http://www.bibletechnologies.net/2003/OSIS/namespace"}

        ot_verses = []
        nt_verses = []

        # Find all book divs
        books = root.findall('.//osis:div[@type="book"]', namespace)

        logger.info(f"Found {len(books)} books in OSIS file")

        for book_elem in books:
            book_id = book_elem.get("osisID")

            # Skip unknown books (e.g., Apocrypha if present in OSIS)
            if book_id not in OSIS_BOOK_MAP:
                logger.warning(f"Skipping unknown book: {book_id}")
                continue

            book_num, book_name, testament = OSIS_BOOK_MAP[book_id]

            # Find all verses in this book
            verses = book_elem.findall(".//osis:verse", namespace)

            for verse_elem in verses:
                osis_id = verse_elem.get("osisID")

                if not osis_id:
                    logger.warning(f"Verse element missing osisID in {book_name}")
                    continue

                # Parse osisID format: "Gen.1.1" -> book=Gen, chapter=1, verse=1
                match = re.match(r"([^.]+)\.(\d+)\.(\d+)", osis_id)
                if not match:
                    logger.warning(f"Invalid osisID format: {osis_id}")
                    continue

                _, chapter_str, verse_str = match.groups()
                chapter = int(chapter_str)
                verse = int(verse_str)

                # Get text content - itertext() gets all text including from nested elements
                text = "".join(verse_elem.itertext()).strip()
                # Strip any remaining XML tags as safety measure
                text = strip_xml_tags(text)

                if not text:
                    logger.warning(f"Empty verse text: {osis_id}")
                    continue

                verse_dict = {
                    "book": book_name,
                    "chapter": chapter,
                    "verse": verse,
                    "text": text,
                    "testament": testament,
                }

                # Add to appropriate list
                if testament == "OT":
                    ot_verses.append(verse_dict)
                else:
                    nt_verses.append(verse_dict)

        logger.info(f"Loaded {len(ot_verses)} OT verses and {len(nt_verses)} NT verses")

        return ot_verses, nt_verses


if __name__ == "__main__":
    # Test the loader
    import sys

    # Configure logging for testing
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        file_path = "data/turkish_bible/tur-turkish.osis.xml"

    print(f"Loading OSIS Bible from: {file_path}")

    try:
        loader = OsisLoader(file_path)
        ot_verses, nt_verses = loader.load()

        print(f"\n{'=' * 60}")
        print("OSIS LOADER TEST RESULTS")
        print(f"{'=' * 60}")
        print(f"OT Verses: {len(ot_verses):,}")
        print(f"NT Verses: {len(nt_verses):,}")
        print(f"Total:     {len(ot_verses) + len(nt_verses):,}")
        print(f"{'=' * 60}")

        # Show samples
        if ot_verses:
            print("\nFirst OT verse:")
            v = ot_verses[0]
            print(f"  {v['book']} {v['chapter']}:{v['verse']}")
            print(f"  Testament: {v['testament']}")
            print(f"  Text: {v['text'][:100]}...")

        if nt_verses:
            print("\nFirst NT verse:")
            v = nt_verses[0]
            print(f"  {v['book']} {v['chapter']}:{v['verse']}")
            print(f"  Testament: {v['testament']}")
            print(f"  Text: {v['text'][:100]}...")

        # Show last verses
        if ot_verses:
            print("\nLast OT verse:")
            v = ot_verses[-1]
            print(f"  {v['book']} {v['chapter']}:{v['verse']}")
            print(f"  Text: {v['text'][:100]}...")

        if nt_verses:
            print("\nLast NT verse:")
            v = nt_verses[-1]
            print(f"  {v['book']} {v['chapter']}:{v['verse']}")
            print(f"  Text: {v['text'][:100]}...")

        # Verify OT/NT separation
        print(f"\n{'=' * 60}")
        print("VERIFICATION")
        print(f"{'=' * 60}")

        # Check for OT/NT overlap
        ot_books = set(v["book"] for v in ot_verses)
        nt_books = set(v["book"] for v in nt_verses)

        print(f"OT Books ({len(ot_books)}): {', '.join(sorted(ot_books))}")
        print(f"NT Books ({len(nt_books)}): {', '.join(sorted(nt_books))}")

        overlap = ot_books & nt_books
        if overlap:
            print(f"\n⚠️  WARNING: Books in both OT and NT: {overlap}")
        else:
            print("\n✅ No book overlap between OT and NT")

        # Check all verses have correct testament
        ot_wrong = [v for v in ot_verses if v["testament"] != "OT"]
        nt_wrong = [v for v in nt_verses if v["testament"] != "NT"]

        if ot_wrong or nt_wrong:
            print("⚠️  WARNING: Testament mismatch found!")
            if ot_wrong:
                print(f"  {len(ot_wrong)} verses in OT list with wrong testament")
            if nt_wrong:
                print(f"  {len(nt_wrong)} verses in NT list with wrong testament")
        else:
            print("✅ All verses have correct testament")

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
