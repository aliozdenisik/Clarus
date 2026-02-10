"""Pydantic schemas for morphological keyword search API."""

from pydantic import BaseModel, Field


class KeywordSearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=100, description="Arabic word or Buckwalter root")
    page: int = Field(default=1, ge=1, description="Page number")
    per_page: int = Field(
        default=0,
        ge=0,
        le=10000,
        description="Results per page. 0 = return all verses (no pagination)",
    )
    word_filter: str | None = Field(
        default=None,
        max_length=100,
        description="Filter verses to only those containing this specific derived word (token_clean form)",
    )


class SurahDistItem(BaseModel):
    surah_id: int
    surah_name: str
    count: int


class VerseMatchItem(BaseModel):
    surah_id: int
    surah_name: str
    ayah_number: int
    text_uthmani: str
    text_clean: str
    matched_words: list[str]


class PaginationInfo(BaseModel):
    page: int
    per_page: int
    total_verses: int
    total_pages: int
    has_next: bool
    has_prev: bool


class KeywordSearchResponse(BaseModel):
    success: bool = True
    query: str
    root: str | None = None
    root_source: str
    total_occurrences: int = 0
    unique_words: list[str] = Field(default_factory=list)
    surah_distribution: list[SurahDistItem] = Field(default_factory=list)
    verses: list[VerseMatchItem] = Field(default_factory=list)
    pagination: PaginationInfo
    root_buckwalter: str | None = None
    word_transliterations: dict[str, str] = Field(default_factory=dict)


class RootListItem(BaseModel):
    root: str
    count: int


class RootListResponse(BaseModel):
    success: bool = True
    roots: list[RootListItem]
    total: int
    page: int
    per_page: int
