"""Pydantic schemas for Bible morphological keyword search API."""

from pydantic import BaseModel, Field
from typing import Optional


class BibleKeywordSearchRequest(BaseModel):
    query: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Hebrew/Aramaic word, Strong's number, or Latin transliteration",
    )
    page: int = Field(default=1, ge=1, description="Page number")
    per_page: int = Field(
        default=0,
        ge=0,
        le=10000,
        description="Results per page. 0 = return all verses (no pagination)",
    )
    language_filter: Optional[str] = Field(
        default=None,
        description="Filter by language: 'hebrew', 'aramaic', or None for all",
    )
    word_filter: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Filter verses to only those containing this specific word form",
    )
    testament_filter: Optional[str] = Field(
        default=None,
        description="Filter by testament: 'ot', 'nt', 'apocrypha', or None for all",
    )
    category_filter: Optional[str] = Field(
        default=None,
        description="Filter by category: 'ot', 'nt', 'apocrypha', 'pseudepigrapha', 'gnostic', 'apostolic_fathers', or None for all",
    )


class BookDistItem(BaseModel):
    book_id: int
    book_name: str
    count: int


class BibleVerseMatchItem(BaseModel):
    book_id: int
    book_name: str
    chapter: int
    verse: int
    text_original: Optional[str]
    text_english: Optional[str]
    matched_words: list[str]
    reference: str


class PaginationInfo(BaseModel):
    page: int
    per_page: int
    total_verses: int
    total_pages: int
    has_next: bool
    has_prev: bool


class BibleKeywordSearchResponse(BaseModel):
    success: bool = True
    query: str
    root: Optional[str] = None
    root_source: str
    strong_number: Optional[str] = None
    total_occurrences: int = 0
    unique_words: list[str] = Field(default_factory=list)
    book_distribution: list[BookDistItem] = Field(default_factory=list)
    verses: list[BibleVerseMatchItem] = Field(default_factory=list)
    pagination: PaginationInfo
    transliteration: Optional[str] = None
    word_transliterations: dict[str, str] = Field(default_factory=dict)


class BibleRootListItem(BaseModel):
    strong_number: Optional[str]
    original_word: Optional[str]
    transliteration: Optional[str]
    count: int


class BibleRootListResponse(BaseModel):
    success: bool = True
    roots: list[BibleRootListItem]
    total: int
    page: int
    per_page: int


class BibleStatsResponse(BaseModel):
    success: bool = True
    total_words: int
    unique_roots: int
    total_books: int
    total_verses: int


class CrossReferenceWord(BaseModel):
    word: str
    word_clean: str
    transliteration: str
    language: str  # 'hebrew' | 'greek' | 'aramaic'
    occurrence_count: int


class CrossReferenceResponse(BaseModel):
    success: bool = True
    strongs_number: str
    definition: Optional[str] = None
    original_word: Optional[str] = None
    transliteration: Optional[str] = None
    hebrew_words: list[CrossReferenceWord] = Field(default_factory=list)
    greek_words: list[CrossReferenceWord] = Field(default_factory=list)
    total_occurrences: int = 0
