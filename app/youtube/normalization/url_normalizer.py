"""YouTube URL normalizer.

Handles URL recognition, video ID extraction, and canonicalization.
"""

import re
from urllib.parse import parse_qs, urlparse

from app.youtube.domain.value_objects import YoutubeUrlInfo, YoutubeUrlType

# Supported YouTube hosts
YOUTUBE_HOSTS = {
    "youtube.com",
    "www.youtube.com",
    "m.youtube.com",
    "youtu.be",
    "www.youtu.be",
}


class YoutubeUrlNormalizer:
    """YouTube URL normalization service.

    Responsible for:
    - Recognizing YouTube URLs
    - Extracting video IDs
    - Generating canonical URLs
    """

    @staticmethod
    def is_youtube_url(url: str) -> bool:
        """Check if a URL is a YouTube URL.

        Args:
            url: URL to check

        Returns:
            True if the URL is a YouTube URL
        """
        try:
            parsed = urlparse(url)
            return parsed.hostname and parsed.hostname.lower() in YOUTUBE_HOSTS
        except Exception:
            return False

    @staticmethod
    def extract_video_id(url: str) -> str | None:
        """Extract video ID from a YouTube URL.

        Supports:
        - watch?v=VIDEO_ID
        - shorts/VIDEO_ID
        - live/VIDEO_ID
        - embed/VIDEO_ID
        - youtu.be/VIDEO_ID

        Args:
            url: YouTube URL

        Returns:
            Video ID if found, None otherwise
        """
        try:
            parsed = urlparse(url)
            hostname = (parsed.hostname or "").lower()
            path = parsed.path.rstrip("/")

            # Handle youtu.be short links
            if hostname == "youtu.be" or hostname == "www.youtu.be":
                # Extract from path: youtu.be/VIDEO_ID
                parts = path.split("/")
                if len(parts) >= 2 and parts[1]:
                    return parts[1]
                return None

            # Handle youtube.com URLs
            if hostname in {"youtube.com", "www.youtube.com", "m.youtube.com"}:
                # watch page: ?v=VIDEO_ID
                if "/watch" in path:
                    query_params = parse_qs(parsed.query)
                    video_ids = query_params.get("v", [])
                    if video_ids:
                        return video_ids[0]
                    return None

                # shorts, live, embed: /shorts/VIDEO_ID, /live/VIDEO_ID, /embed/VIDEO_ID
                for prefix in ["/shorts/", "/live/", "/embed/"]:
                    if path.startswith(prefix):
                        video_id = path[len(prefix) :]
                        if video_id:
                            return video_id
                        return None

            return None
        except Exception:
            return None

    @staticmethod
    def determine_url_type(url: str) -> YoutubeUrlType:
        """Determine the type of YouTube URL.

        Args:
            url: YouTube URL

        Returns:
            YoutubeUrlType enum value
        """
        try:
            parsed = urlparse(url)
            hostname = (parsed.hostname or "").lower()
            path = parsed.path.lower()

            if hostname in {"youtu.be", "www.youtu.be"}:
                return YoutubeUrlType.SHORT_LINK

            if "/watch" in path:
                return YoutubeUrlType.WATCH

            if path.startswith("/shorts/"):
                return YoutubeUrlType.SHORTS

            if path.startswith("/live/"):
                return YoutubeUrlType.LIVE

            if path.startswith("/embed/"):
                return YoutubeUrlType.EMBED

            return YoutubeUrlType.UNKNOWN
        except Exception:
            return YoutubeUrlType.UNKNOWN

    @staticmethod
    def canonicalize_url(video_id: str) -> str:
        """Generate canonical URL from video ID.

        All YouTube URLs are canonicalized to the watch format:
        https://www.youtube.com/watch?v=VIDEO_ID

        Args:
            video_id: YouTube video ID

        Returns:
            Canonical URL
        """
        return f"https://www.youtube.com/watch?v={video_id}"

    @classmethod
    def normalize(cls, url: str) -> YoutubeUrlInfo | None:
        """Normalize a YouTube URL.

        This is the main entry point for URL normalization.
        It extracts all relevant information from a YouTube URL.

        Args:
            url: YouTube URL to normalize

        Returns:
            YoutubeUrlInfo if valid, None if not a valid YouTube URL
        """
        if not cls.is_youtube_url(url):
            return None

        video_id = cls.extract_video_id(url)
        if not video_id:
            return None

        url_type = cls.determine_url_type(url)
        canonical_url = cls.canonicalize_url(video_id)

        return YoutubeUrlInfo(
            video_id=video_id,
            url_type=url_type,
            original_url=url,
            canonical_url=canonical_url,
            is_valid=True,
        )

    @staticmethod
    def extract_url_from_text(text: str) -> str | None:
        """Extract YouTube URL from text.

        Looks for YouTube URLs in text content like share messages.

        Args:
            text: Text that may contain a YouTube URL

        Returns:
            First YouTube URL found, or None
        """
        # Pattern to match YouTube URLs
        patterns = [
            # youtu.be short links
            r"https?://(?:www\.)?youtu\.be/[^\s]+",
            # youtube.com watch/shorts/live/embed
            r"https?://(?:www\.|m\.)?youtube\.com/(?:watch\?v=|shorts/|live/|embed/)[^\s]+",
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                # Clean up the URL (remove trailing punctuation)
                url = match.group(0)
                url = url.rstrip(".,;!?)\"'>]}")
                return url

        return None