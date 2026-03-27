"""YouTube value objects.

Immutable value objects for YouTube-specific concepts.
"""

from dataclasses import dataclass
from enum import Enum


class YoutubeUrlType(str, Enum):
    """Type of YouTube URL."""

    WATCH = "watch"
    SHORTS = "shorts"
    LIVE = "live"
    EMBED = "embed"
    SHORT_LINK = "short_link"  # youtu.be
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class YoutubeUrlInfo:
    """Parsed YouTube URL information.

    This is an immutable value object containing the parsed
    information from a YouTube URL.
    """

    video_id: str
    url_type: YoutubeUrlType
    original_url: str
    canonical_url: str
    is_valid: bool = True