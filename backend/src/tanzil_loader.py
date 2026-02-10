"""
Tanzil XML Quran Loader

Loads Turkish Quran translations from Tanzil XML format.
Supports 8 translators: diyanet, yazir, ates, bulac, ozturk, vakfi, yildirim, yuksel.

Note: Tanzil XML files contain malformed comments (with -- sequences inside comments)
which violates XML 1.0 spec. This loader strips comments before parsing.
"""

import xml.etree.ElementTree as ET
from pathlib import Path
from typing import List, Dict, Optional, Any
import logging
import re

logger = logging.getLogger(__name__)

# Valid translator keys mapping to XML files
VALID_TRANSLATORS = {
    "diyanet",
    "yazir",
    "ates",
    "bulac",
    "ozturk",
    "vakfi",
    "yildirim",
    "yuksel",
}

# Expected verse count per translation
EXPECTED_VERSE_COUNT = 6236
EXPECTED_SURAH_COUNT = 114


class TanzilLoader:
    """
    Loads Turkish Quran translations from Tanzil XML files.

    Each translation is stored in backend/data/turkish_quran/tr.{translator}.xml
    Surah metadata is loaded from backend/data/tanzil/quran-data.xml
    """

    def __init__(self, data_dir: Optional[Path] = None):
        """
        Initialize the Tanzil loader.

        Args:
            data_dir: Base data directory (defaults to backend/data)
        """
        if data_dir is None:
            # Assume we're in backend/ directory or backend/src/
            current = Path(__file__).parent
            if current.name == "src":
                data_dir = current.parent / "data"
            else:
                data_dir = current / "data"

        self.data_dir = Path(data_dir)
        self.turkish_quran_dir = self.data_dir / "turkish_quran"
        self.metadata_path = self.data_dir / "tanzil" / "quran-data.xml"

        # Cache for surah metadata
        self._surah_metadata: Optional[Dict[int, Dict[str, str]]] = None

    def _load_surah_metadata(self) -> Dict[int, Dict[str, str]]:
        """
        Load surah metadata from quran-data.xml.

        Returns:
            Dictionary mapping surah_number to metadata (name, tname, ename, type)

        Raises:
            FileNotFoundError: If quran-data.xml is not found
            ET.ParseError: If XML is malformed
        """
        if self._surah_metadata is not None:
            return self._surah_metadata

        if not self.metadata_path.exists():
            raise FileNotFoundError(
                f"Surah metadata not found: {self.metadata_path}\n"
                f"Expected at: {self.metadata_path.absolute()}"
            )

        try:
            with open(self.metadata_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Remove XML comments (Tanzil files have -- inside comments)
            content_no_comments = re.sub(r"<!--.*?-->", "", content, flags=re.DOTALL)

            root = ET.fromstring(content_no_comments)
        except ET.ParseError as e:
            raise ET.ParseError(f"Failed to parse {self.metadata_path}: {e}")
        except FileNotFoundError:
            raise
        except Exception as e:
            raise RuntimeError(f"Unexpected error parsing {self.metadata_path}: {e}")

        metadata = {}
        suras_element = root.find("suras")
        if suras_element is None:
            raise ValueError("quran-data.xml missing <suras> element")

        for sura in suras_element.findall("sura"):
            index = int(sura.get("index", 0))
            metadata[index] = {
                "name": sura.get("name", ""),  # Arabic name
                "tname": sura.get("tname", ""),  # Transliteration
                "ename": sura.get("ename", ""),  # English name
                "type": sura.get("type", ""),  # Meccan/Medinan
                "ayas": int(sura.get("ayas", 0)),  # Verse count
            }

        logger.info(f"Loaded metadata for {len(metadata)} surahs")
        self._surah_metadata = metadata
        return metadata

    def load_translation(self, translator: str) -> List[Dict[str, Any]]:
        """
        Load a single Turkish Quran translation.

        Args:
            translator: Translator key (e.g., "diyanet", "yazir")

        Returns:
            List of verse dictionaries with keys:
                - surah_number (int): Surah number (1-114)
                - verse_number (int): Verse number within surah
                - text (str): Translated verse text
                - surah_name (str): Surah transliteration name
                - translator (str): Translator key

        Raises:
            ValueError: If translator is invalid
            FileNotFoundError: If XML file is not found
            ET.ParseError: If XML is malformed
        """
        if translator not in VALID_TRANSLATORS:
            raise ValueError(
                f"Invalid translator: {translator}\n"
                f"Valid translators: {', '.join(sorted(VALID_TRANSLATORS))}"
            )

        xml_path = self.turkish_quran_dir / f"tr.{translator}.xml"
        if not xml_path.exists():
            raise FileNotFoundError(
                f"Translation XML not found: {xml_path}\n"
                f"Expected at: {xml_path.absolute()}"
            )

        # Load surah metadata
        surah_metadata = self._load_surah_metadata()

        # Parse translation XML
        # Note: Tanzil XML files have malformed comments (containing -- sequences)
        # We need to strip comments before parsing
        try:
            with open(xml_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Remove XML comments (<!-- ... -->)
            # This is necessary because Tanzil XMLs have -- inside comments which violates XML spec
            content_no_comments = re.sub(r"<!--.*?-->", "", content, flags=re.DOTALL)

            root = ET.fromstring(content_no_comments)
        except ET.ParseError as e:
            raise ET.ParseError(f"Failed to parse {xml_path}: {e}")
        except FileNotFoundError:
            raise
        except Exception as e:
            raise RuntimeError(f"Unexpected error parsing {xml_path}: {e}")

        verses = []

        for sura in root.findall("sura"):
            surah_number = int(sura.get("index", 0))

            # Get surah name from metadata
            metadata = surah_metadata.get(surah_number, {})
            surah_name = metadata.get("tname", f"Surah-{surah_number}")

            for aya in sura.findall("aya"):
                verse_number = int(aya.get("index", 0))
                text = aya.get("text", "")

                if not text.strip():
                    logger.warning(
                        f"Empty verse text: {translator} {surah_number}:{verse_number}"
                    )
                    continue

                verses.append(
                    {
                        "surah_number": surah_number,
                        "verse_number": verse_number,
                        "text": text,
                        "surah_name": surah_name,
                        "translator": translator,
                    }
                )

        # Validate verse count
        if len(verses) != EXPECTED_VERSE_COUNT:
            logger.warning(
                f"Translation {translator} has {len(verses)} verses, "
                f"expected {EXPECTED_VERSE_COUNT}"
            )

        # Validate surah count
        unique_surahs = len(set(v["surah_number"] for v in verses))
        if unique_surahs != EXPECTED_SURAH_COUNT:
            logger.warning(
                f"Translation {translator} has {unique_surahs} surahs, "
                f"expected {EXPECTED_SURAH_COUNT}"
            )

        # Validate Surah 9 (At-Tawba) has 129 verses
        surah_9_verses = [v for v in verses if v["surah_number"] == 9]
        if len(surah_9_verses) != 129:
            logger.warning(
                f"Translation {translator} Surah 9 has {len(surah_9_verses)} verses, "
                f"expected 129"
            )

        logger.info(
            f"Loaded {translator}: {len(verses)} verses across {unique_surahs} surahs"
        )

        return verses

    def load_all_translations(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Load all available Turkish Quran translations.

        Returns:
            Dictionary mapping translator key to list of verses

        Raises:
            FileNotFoundError: If any translation XML is not found
            ET.ParseError: If any XML is malformed
        """
        translations = {}

        for translator in sorted(VALID_TRANSLATORS):
            try:
                translations[translator] = self.load_translation(translator)
            except FileNotFoundError as e:
                logger.error(f"Failed to load {translator}: {e}")
                raise
            except ET.ParseError as e:
                logger.error(f"Failed to parse {translator}: {e}")
                raise

        logger.info(f"Loaded {len(translations)} translations")
        return translations


if __name__ == "__main__":
    # Test the loader
    import sys

    # Configure logging
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    print("Testing TanzilLoader...")
    print("=" * 60)

    loader = TanzilLoader()

    # Test single translation
    print("\nTesting single translation (diyanet)...")
    try:
        verses = loader.load_translation("diyanet")
        print(f"✓ Loaded {len(verses)} verses")

        # Show sample verse
        if verses:
            sample = verses[0]
            print("\nSample verse:")
            print(f"  Surah: {sample['surah_name']} ({sample['surah_number']})")
            print(f"  Verse: {sample['verse_number']}")
            print(f"  Text: {sample['text'][:80]}...")
            print(f"  Translator: {sample['translator']}")

        # Verify Surah 9
        surah_9 = [v for v in verses if v["surah_number"] == 9]
        print(f"\n✓ Surah 9 (At-Tawba): {len(surah_9)} verses")
    except Exception as e:
        print(f"✗ Failed: {e}")
        sys.exit(1)

    # Test all translations
    print("\n" + "=" * 60)
    print("Testing all translations...")
    try:
        all_translations = loader.load_all_translations()
        print(f"✓ Loaded {len(all_translations)} translations")

        for translator, verses in sorted(all_translations.items()):
            print(f"  {translator:12s}: {len(verses):,} verses")
    except Exception as e:
        print(f"✗ Failed: {e}")
        sys.exit(1)

    print("\n" + "=" * 60)
    print("✓ All tests passed!")
    print(f"✓ VALID_TRANSLATORS exported: {sorted(VALID_TRANSLATORS)}")
