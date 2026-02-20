"""Pydantic schemas documenting SSE event types for streaming endpoints.

These models are NOT used at runtime for serialization (SSE events are
manually JSON-encoded via ``json.dumps``). They exist solely to provide
accurate OpenAPI documentation so that generated TypeScript types are
fully typed instead of ``unknown``.
"""

from typing import Literal

from pydantic import BaseModel, Field


class SSECompleteEvent(BaseModel):
    """Signals end of the SSE stream (emitted by /stream/compare and error paths of /stream/search)."""

    type: Literal["complete"] = "complete"


class SSEErrorEvent(BaseModel):
    """Error event — the stream should be considered terminated after this."""

    error: str = Field(..., description="Human-readable error description")


class SearchStatusEvent(BaseModel):
    """Pipeline status update during search processing."""

    status: Literal["searching", "found", "generating", "translating"] = Field(
        ..., description="Current pipeline stage"
    )
    message: str | None = Field(
        default=None,
        description="Human-readable status message (absent when status='found')",
    )
    count: int | None = Field(
        default=None,
        description="Number of search results found (only present when status='found')",
    )


class SearchTokenEvent(BaseModel):
    """Single answer token streamed word-by-word from the AI answer generation."""

    type: Literal["token"] = "token"
    content: str = Field(..., description="A single word/token of the generated answer, with trailing space")


class SearchCitationsEvent(BaseModel):
    """Citation list sent once after all answer tokens have been streamed."""

    citations: list[str] = Field(..., description="Array of citation reference strings")


class SearchVerseDetailsEvent(BaseModel):
    """Verse metadata map sent before the final complete event."""

    verse_details: dict = Field(
        ...,
        description="Map of verse reference string to verse metadata object (schema varies by source collection)",
    )


class SearchResultItem(BaseModel):
    """A single search result item included in the complete event payload."""

    source: str = Field(
        ...,
        description="Source collection identifier (e.g., 'quran', 'bible_ot', 'bible_nt', 'bible_apocrypha')",
    )
    reference: str = Field(..., description="Verse reference string (e.g., 'Al-Fatiha:1' or 'Genesis 1:1')")
    text: str = Field(..., description="Verse text content")
    score: float = Field(..., description="Relevance score from the vector search")


class SearchCompleteResult(BaseModel):
    """Aggregated result payload included in the search stream's final complete event."""

    results: list[SearchResultItem] = Field(..., description="All retrieved search result items")
    answer: str = Field(..., description="Complete AI-generated answer text (after optional translation)")
    citations: list[str] = Field(..., description="Array of citation reference strings")


class SearchCompleteEvent(BaseModel):
    """Final event for /api/stream/search — signals stream completion with full result data."""

    type: Literal["complete"] = "complete"
    result: SearchCompleteResult | None = Field(
        default=None,
        description="Aggregated result; absent in error cases where a preceding error event was sent",
    )


class CompareProgressEvent(BaseModel):
    """Real-time progress update from the multi-agent comparative analysis pipeline."""

    type: Literal["progress"] = "progress"
    step: str = Field(
        ...,
        description=(
            "Machine-readable step identifier emitted by the pipeline "
            "(e.g., 'pipeline_started', 'building_verse_details', 'translating_response')"
        ),
    )
    message: str = Field(..., description="Human-readable progress message")


class CompareVerseDetailsEvent(BaseModel):
    """Verse metadata map emitted before paragraph streaming begins."""

    verse_details: dict = Field(
        ...,
        description="Map of verse reference string to verse metadata object (schema varies by source collection)",
    )


class CompareParagraphData(BaseModel):
    """Content payload for a single comparative analysis paragraph."""

    title: str = Field(..., description="Section title (e.g., 'Introduction', 'Quran Perspective')")
    content: str = Field(..., description="Full markdown text content of the paragraph")


class CompareParagraphEvent(BaseModel):
    """A single structured paragraph streamed from the multi-agent comparative essay."""

    type: Literal["paragraph"] = "paragraph"
    data: CompareParagraphData = Field(..., description="Paragraph title and markdown content")


class CompareStatsData(BaseModel):
    """Statistical summary collected at the end of the compare pipeline."""

    confidence: float = Field(..., ge=0.0, le=1.0, description="Overall confidence score (0.0–1.0)")
    confidence_breakdown: dict | None = Field(
        default=None,
        description="Per-agent confidence breakdown dict (present when available)",
    )
    latency_ms: int = Field(..., description="Total pipeline latency in milliseconds")
    total_verses: int = Field(..., description="Total number of verses retrieved across all collections")
    total_citations: int = Field(..., description="Total number of citations in the generated essay")


class CompareStatsEvent(BaseModel):
    """Statistics event sent after all paragraphs have been streamed."""

    type: Literal["stats"] = "stats"
    data: CompareStatsData = Field(..., description="Pipeline statistics and performance metrics")
