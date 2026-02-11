from datetime import datetime

from pydantic import BaseModel, Field, computed_field


class MorphologicalForm(BaseModel):
    form_pattern: str | None = Field(None, description="Pattern/template (e.g., فَاعِل, مَفْعُول)")
    form_arabic: str | None = Field(None, description="Arabic text of the form")
    form_name: str | None = Field(None, description="Name/category of the form")
    form_category: str | None = Field(None, description="Grammatical category (noun, verb, etc.)")
    example_word: str | None = Field(None, description="Example word using this form")
    occurrences: int | None = Field(None, description="Number of occurrences in Quran")


class RelatedRoot(BaseModel):
    root: str = Field(..., description="Related root in Arabic")
    root_buckwalter: str | None = Field(None, description="Related root in Buckwalter transliteration")
    meaning_hint: str | None = Field(None, description="Brief semantic hint for the relationship")


class RootEtymologyResponse(BaseModel):
    success: bool = True
    id: int = Field(..., description="Etymology database ID")
    root: str = Field(..., description="Arabic root (e.g., كتب)")
    root_buckwalter: str = Field(..., description="Buckwalter Latin transliteration (e.g., ktb)")
    definition_en: str | None = Field(None, description="English definition from Lane's Lexicon")
    definition_tr: str | None = Field(None, description="Turkish translation (LLM-generated)")
    semantic_field: str | None = Field(None, description="Semantic category (e.g., 'writing', 'faith')")
    morphological_forms: list[MorphologicalForm] = Field(
        default_factory=list,
        description="Verb/noun patterns derived from this root (max 15)",
    )
    related_roots: list[RelatedRoot] = Field(
        default_factory=list,
        description="Semantically related Arabic roots (max 20)",
    )
    quran_frequency: int = Field(0, description="Total occurrences in Quran")
    source: str = Field(..., description="Data source (e.g., 'lane', 'corpus_only')")
    lane_match_type: str | None = Field(None, description="Lane's Lexicon match quality (exact/fuzzy/none)")
    lane_volume: int | None = Field(None, description="Lane's Lexicon volume number (1-8)")
    confidence: str = Field(..., description="Overall data confidence (high/medium/low)")
    tr_translation_source: str | None = Field(None, description="Turkish translation source")
    tr_translation_confidence: float | None = Field(
        None,
        ge=0.0,
        le=1.0,
        description="Turkish translation confidence score (0.0-1.0)",
    )
    created_at: datetime = Field(..., description="Record creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    @computed_field  # type: ignore[prop-decorator]
    @property
    def keyword_search_url(self) -> str:
        return f"/keyword-search?q={self.root_buckwalter}"


class WordItem(BaseModel):
    """Individual word item with morphological and etymology metadata."""

    position: int = Field(..., description="Position of word in verse (0-indexed)")
    token: str | None = Field(None, description="Original Arabic token")
    token_clean: str | None = Field(None, description="Cleaned Arabic token (no diacritics)")
    root: str | None = Field(None, description="Arabic root (if available)")
    root_buckwalter: str | None = Field(None, description="Root in Buckwalter transliteration")
    lemma: str | None = Field(None, description="Lemma (base form)")
    pos_tag: str | None = Field(None, description="Part-of-speech tag")
    has_etymology: bool = Field(..., description="Whether etymology data exists for this root")


class VerseWordsResponse(BaseModel):
    """Response containing tokenized words for a specific verse."""

    success: bool = Field(default=True, description="Always true for successful responses")
    surah_id: int = Field(..., description="Surah ID (1-114)")
    ayah_number: int = Field(..., description="Ayah number within the surah")
    words: list[WordItem] = Field(..., description="List of words in the verse")
    word_count: int = Field(..., description="Total number of words")
