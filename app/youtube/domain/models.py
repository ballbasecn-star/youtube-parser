"""YouTube domain models.

Internal domain models representing YouTube entities.
These are separate from the contract schemas to allow
independent evolution of the internal model.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class YoutubeChannel:
    """YouTube channel information."""

    channel_id: str | None = None
    name: str | None = None
    handle: str | None = None
    profile_url: str | None = None
    avatar_url: str | None = None


@dataclass
class YoutubeThumbnail:
    """YouTube video thumbnail."""

    url: str
    width: int | None = None
    height: int | None = None


@dataclass
class YoutubeTranscriptSegment:
    """A single transcript segment."""

    text: str
    start_ms: int
    end_ms: int
    speaker: str | None = None


@dataclass
class YoutubeTranscript:
    """YouTube video transcript."""

    text: str
    segments: list[YoutubeTranscriptSegment] = field(default_factory=list)
    language: str | None = None
    is_auto_generated: bool = False


@dataclass
class YoutubeMetrics:
    """YouTube video metrics."""

    views: int | None = None
    likes: int | None = None
    comments: int | None = None


@dataclass
class YoutubeVideo:
    """YouTube video domain model.

    This represents the internal model of a YouTube video,
    before mapping to the contract schema.
    """

    video_id: str
    canonical_url: str

    # Basic metadata
    title: str | None = None
    description: str | None = None
    published_at: datetime | None = None
    duration_seconds: int | None = None
    language: str | None = None
    tags: list[str] = field(default_factory=list)

    # Channel info
    channel: YoutubeChannel | None = None

    # Media
    thumbnails: list[YoutubeThumbnail] = field(default_factory=list)

    # Transcript
    transcript: YoutubeTranscript | None = None

    # Metrics
    metrics: YoutubeMetrics | None = None

    # Raw data for debugging
    raw_data: dict[str, Any] = field(default_factory=dict)

    # Warnings
    warnings: list[str] = field(default_factory=list)