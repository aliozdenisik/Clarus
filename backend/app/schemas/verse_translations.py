"""Pydantic schemas for verse translations API requests and responses."""

from pydantic import BaseModel, Field


class TranslationItem(BaseModel):
    """Single translation of a Quran verse.

    Contains the translator identifier, display name, and the actual translation text.
    """

    translator: str = Field(..., description="Translator identifier (e.g., 'diyanet', 'yazir')")
    translator_display: str = Field(
        ..., description="Human-readable translator name (e.g., 'Diyanet İşleri', 'Elmalılı Yazır')"
    )
    text: str = Field(..., description="Translation text")


class VerseTranslationsResponse(BaseModel):
    """Response containing all 8 Turkish translations for a single Quran verse.

    Example:
    {
        "success": true,
        "surah_id": 2,
        "verse_id": 255,
        "surah_name": "Bakara",
        "arabic_text": "اللَّهُ لَا إِلَٰهَ إِلَّا هُوَ...",
        "translations": [
            {
                "translator": "diyanet",
                "translator_display": "Diyanet İşleri",
                "text": "Allah, kendisinden başka ilah olmayan..."
            },
            ...
        ]
    }
    """

    success: bool = Field(default=True, description="Always true for successful responses")
    surah_id: int = Field(..., ge=1, le=114, description="Surah number (1-114)")
    verse_id: int = Field(..., ge=1, description="Verse number within the surah")
    surah_name: str = Field(..., description="Turkish surah name")
    arabic_text: str = Field(..., description="Original Arabic text (Uthmani script)")
    translations: list[TranslationItem] = Field(..., description="List of all available translations (up to 8)")
