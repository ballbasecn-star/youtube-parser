"""Request and response schemas for parser contract.

This module defines all Pydantic models for the parser API,
including request bodies and response payloads.
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


# =============================================================================
# Request Schemas
# =============================================================================


class ParserInput(BaseModel):
    """Input source for parsing.

    At least one of source_text or source_url must be provided.
    """

    source_text: str | None = Field(
        default=None,
        alias="sourceText",
        description="Text containing a URL to extract",
        examples=["看看这个视频 https://youtu.be/abc123"],
    )
    source_url: str | None = Field(
        default=None,
        alias="sourceUrl",
        description="Direct URL to parse",
        examples=["https://www.youtube.com/watch?v=abc123"],
    )
    platform_hint: str | None = Field(
        default=None,
        alias="platformHint",
        description="Hint about the platform (only used as suggestion)",
        examples=["youtube"],
    )

    model_config = {"populate_by_name": True}


class Options(BaseModel):
    """Parse options controlling what data to fetch."""

    fetch_transcript: bool = Field(
        default=True,
        alias="fetchTranscript",
        description="Whether to fetch transcript/subtitles",
    )
    fetch_media: bool = Field(
        default=True,
        alias="fetchMedia",
        description="Whether to fetch media information",
    )
    fetch_metrics: bool = Field(
        default=True,
        alias="fetchMetrics",
        description="Whether to fetch metrics (views, likes, etc.)",
    )
    deep_analysis: bool = Field(
        default=False,
        alias="deepAnalysis",
        description="Whether to perform deep analysis",
    )
    language_hint: str | None = Field(
        default=None,
        alias="languageHint",
        description="Preferred language for transcript",
        examples=["zh-CN", "en-US"],
    )

    model_config = {"populate_by_name": True}


class ParserParseRequest(BaseModel):
    """Request body for the parse endpoint."""

    request_id: str | None = Field(
        default=None,
        alias="requestId",
        description="Optional request ID for tracing",
    )
    input: ParserInput = Field(..., description="Input source to parse")
    options: Options = Field(default_factory=Options, description="Parse options")

    model_config = {"populate_by_name": True}


# =============================================================================
# Response Schemas
# =============================================================================


class AuthorInfo(BaseModel):
    """Author/channel information."""

    external_author_id: str | None = Field(
        default=None,
        alias="externalAuthorId",
        description="External author ID (channel ID)",
    )
    name: str | None = Field(default=None, description="Author/channel name")
    handle: str | None = Field(default=None, description="Author handle (@handle)")
    profile_url: str | None = Field(
        default=None,
        alias="profileUrl",
        description="Author profile URL",
    )
    avatar_url: str | None = Field(
        default=None,
        alias="avatarUrl",
        description="Author avatar URL",
    )

    model_config = {"populate_by_name": True}


class TranscriptSegment(BaseModel):
    """A single transcript segment with timing."""

    text: str = Field(..., description="Segment text")
    start_ms: int = Field(..., alias="startMs", description="Start time in milliseconds")
    end_ms: int = Field(..., alias="endMs", description="End time in milliseconds")
    speaker: str | None = Field(default=None, description="Speaker identifier if available")

    model_config = {"populate_by_name": True}


class ContentInfo(BaseModel):
    """Content including raw text, transcript, and segments."""

    raw_text: str | None = Field(
        default=None,
        alias="rawText",
        description="Raw text content (description, etc.)",
    )
    transcript: str | None = Field(
        default=None,
        description="Full transcript text",
    )
    segments: list[TranscriptSegment] = Field(
        default_factory=list,
        description="Transcript segments with timing",
    )

    model_config = {"populate_by_name": True}


class MetricsInfo(BaseModel):
    """Content metrics."""

    views: int | None = Field(default=None, description="View count")
    likes: int | None = Field(default=None, description="Like count")
    comments: int | None = Field(default=None, description="Comment count")
    shares: int | None = Field(default=None, description="Share count")
    favorites: int | None = Field(default=None, description="Favorite count")

    model_config = {"populate_by_name": True}


class CoverImage(BaseModel):
    """Cover image information."""

    url: str = Field(..., description="Image URL")
    width: int | None = Field(default=None, description="Image width")
    height: int | None = Field(default=None, description="Image height")


class MediaInfo(BaseModel):
    """Media information (covers, images, videos, audios)."""

    covers: list[CoverImage] = Field(
        default_factory=list,
        description="Cover/thumbnail images",
    )
    images: list[CoverImage] = Field(
        default_factory=list,
        description="Additional images",
    )
    videos: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Video files (not implemented)",
    )
    audios: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Audio files (not implemented)",
    )

    model_config = {"populate_by_name": True}


class Warning(BaseModel):
    """Warning information for partial success."""

    code: str = Field(..., description="Warning code")
    message: str = Field(..., description="Human-readable warning message")


class ParsedContentPayload(BaseModel):
    """The main response payload for successful parse operations.

    This structure must conform to the unified parser contract
    defined in the linker-platform architecture.
    """

    platform: str = Field(..., description="Platform identifier (e.g., 'youtube')")
    source_type: str = Field(
        ...,
        alias="sourceType",
        description="Source type (e.g., 'video')",
    )
    external_id: str = Field(
        ...,
        alias="externalId",
        description="External ID (e.g., YouTube videoId)",
    )
    canonical_url: str = Field(
        ...,
        alias="canonicalUrl",
        description="Canonical URL for the content",
    )
    title: str | None = Field(default=None, description="Content title")
    summary: str | None = Field(default=None, description="Content summary/description")
    author: AuthorInfo | None = Field(default=None, description="Author information")
    published_at: datetime | None = Field(
        default=None,
        alias="publishedAt",
        description="Publication timestamp",
    )
    language: str | None = Field(default=None, description="Content language")
    content: ContentInfo = Field(default_factory=ContentInfo, description="Content text")
    metrics: MetricsInfo = Field(default_factory=MetricsInfo, description="Content metrics")
    tags: list[str] = Field(default_factory=list, description="Tags/keywords")
    media: MediaInfo = Field(default_factory=MediaInfo, description="Media information")
    raw_payload: dict[str, Any] = Field(
        default_factory=dict,
        alias="rawPayload",
        description="Raw platform data for debugging",
    )
    warnings: list[Warning] = Field(
        default_factory=list,
        description="Warnings for partial success",
    )

    model_config = {"populate_by_name": True}


# =============================================================================
# Capabilities Response
# =============================================================================


class CapabilitiesResponse(BaseModel):
    """Response for the capabilities endpoint."""

    platform: str = Field(default="youtube", description="Platform identifier")
    supported_source_types: list[str] = Field(
        default=["video", "share_text"],
        alias="supportedSourceTypes",
        description="Supported source types",
    )
    features: dict[str, bool] = Field(
        default_factory=lambda: {
            "transcript": False,
            "images": False,
            "metrics": False,
            "authorProfile": False,
            "deepAnalysis": False,
            "batchParse": False,
            "asyncParse": False,
        },
        description="Available features",
    )

    model_config = {"populate_by_name": True}


# =============================================================================
# Health Response
# =============================================================================


class HealthResponse(BaseModel):
    """Response for the health endpoint."""

    status: str = Field(default="UP", description="Service status")