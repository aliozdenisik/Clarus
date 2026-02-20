"""Pydantic schemas for verse lookup API requests and responses."""

from typing import Literal

from pydantic import BaseModel, Field


class VerseLookupRequest(BaseModel):
    """Request to lookup verses by reference.

    Supports multiple reference formats:
    - Quran: "2:183", "Bakara 183", "Bakara:183"
    - Bible: "Genesis 1:1", "Gen 1:1", "1:1" (with book context)
    """

    reference: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Verse reference: '2:183', 'Bakara 183', 'Genesis 1:1', etc.",
    )


class LookupVerseResult(BaseModel):
    """Single verse result with full metadata.

    Contains both Quran and Bible-specific fields. Fields are null
    when not applicable to the source (e.g., surah_id is null for Bible verses).
    """

    reference: str = Field(..., description="Canonical reference: '2:183' or 'Genesis 1:1'")
    text: str = Field(..., description="Verse text in original language or translation")
    source: Literal["quran", "bible_ot", "bible_nt", "bible_apocrypha"] = Field(
        ..., description="Source collection identifier"
    )

    # Quran-specific fields (null for Bible)
    surah_id: int | None = Field(None, ge=1, le=114, description="Surah number 1-114")
    surah_name: str | None = Field(None, description="Turkish surah name")
    verse_id: int | None = Field(None, ge=1, description="Verse number within surah")
    arabic_text: str | None = Field(None, description="Original Arabic text")

    # Bible-specific fields (null for Quran)
    book_id: int | None = Field(None, ge=1, le=81, description="Book number 1-81")
    book_name: str | None = Field(None, description="English book name")
    chapter: int | None = Field(None, ge=1, description="Chapter number")
    verse: int | None = Field(None, ge=1, description="Verse number within chapter")


class VerseLookupResponse(BaseModel):
    """Successful verse lookup response.

    Example:
    {
        "success": true,
        "verses": [
            {
                "reference": "2:183",
                "text": "Ey iman edenler, sizden önce gelenler üzerine farz kılındığı gibi...",
                "source": "quran",
                "surah_id": 2,
                "surah_name": "Bakara",
                "verse_id": 183,
                "arabic_text": "يا أيها الذين آمنوا كتب عليكم الصيام..."
            }
        ],
        "query": "2:183",
        "count": 1
    }
    """

    success: bool = Field(default=True, description="Always true for successful responses")
    verses: list[LookupVerseResult] = Field(..., description="List of matching verses (empty if none found)")
    query: str = Field(..., description="Original input query")
    count: int = Field(..., ge=0, description="Number of verses returned")
