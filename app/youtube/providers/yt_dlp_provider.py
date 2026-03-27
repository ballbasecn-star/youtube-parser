"""yt-dlp provider for YouTube metadata and transcripts.

Uses the yt-dlp library to fetch comprehensive video information
including metadata, metrics, and subtitles.

Pros:
- Complete metadata (title, description, channel info, etc.)
- Transcript/subtitle extraction
- No API key required
- Handles various YouTube URL formats

Cons:
- Slower than oEmbed
- Requires external dependency
- May be affected by YouTube changes
"""

import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Any

import structlog
import yt_dlp

from app.youtube.providers.base import BaseProvider, ProviderResult, TranscriptResult

logger = structlog.get_logger(__name__)

# Thread pool for running yt-dlp (which is blocking)
_executor = ThreadPoolExecutor(max_workers=3)


class YtDlpProvider(BaseProvider):
    """yt-dlp based provider for comprehensive YouTube data.

    This provider uses the yt-dlp library to extract complete video
    information including metadata, metrics, and subtitles.

    It serves as the fallback provider when oEmbed doesn't provide
    enough information, or as the primary provider when subtitles
    are needed.
    """

    name = "yt_dlp"

    # All fields yt-dlp can potentially provide
    SUPPORTED_FIELDS = [
        "title",
        "description",
        "uploader",
        "channel_id",
        "channel_url",
        "view_count",
        "like_count",
        "comment_count",
        "thumbnail",
        "thumbnails",
        "duration",
        "upload_date",
        "tags",
        "subtitles",
        "automatic_captions",
    ]

    # Default language preference for subtitles
    DEFAULT_SUBTITLE_LANGS = ["zh-Hans", "zh-Hant", "en", "zh"]

    @property
    def supported_fields(self) -> list[str]:
        """Return list of fields this provider can retrieve."""
        return self.SUPPORTED_FIELDS

    async def fetch(self, video_id: str) -> ProviderResult:
        """Fetch comprehensive video data using yt-dlp.

        Args:
            video_id: YouTube video ID

        Returns:
            ProviderResult with video data or error
        """
        video_url = f"https://www.youtube.com/watch?v={video_id}"

        logger.debug(
            "ytdlp_fetch_start",
            provider=self.name,
            video_id=video_id,
        )

        # yt-dlp options
        ydl_opts = {
            "quiet": True,
            "no_warnings": True,
            "extract_flat": False,
            "writesubtitles": True,
            "writeautomaticsub": True,
            "subtitleslangs": self.DEFAULT_SUBTITLE_LANGS,
            "skip_download": True,
            "socket_timeout": 30,
            "retries": 2,
        }

        try:
            # Run yt-dlp in thread pool since it's blocking
            loop = asyncio.get_event_loop()
            info = await loop.run_in_executor(
                _executor,
                lambda: self._extract_info(video_url, ydl_opts),
            )

            if info:
                available_fields = self._get_available_fields(info)
                logger.info(
                    "ytdlp_fetch_success",
                    provider=self.name,
                    video_id=video_id,
                    title=info.get("title", "")[:50],
                    fields=available_fields,
                )
                return ProviderResult(
                    success=True,
                    data=info,
                    source=self.name,
                    fields=available_fields,
                )

            return ProviderResult(
                success=False,
                data=None,
                error="yt-dlp returned no data",
                source=self.name,
            )

        except yt_dlp.utils.DownloadError as e:
            error_msg = self._parse_download_error(e)
            logger.warning(
                "ytdlp_download_error",
                provider=self.name,
                video_id=video_id,
                error=error_msg,
            )
            return ProviderResult(
                success=False,
                data=None,
                error=error_msg,
                source=self.name,
            )

        except yt_dlp.utils.ExtractorError as e:
            error_msg = f"Extraction failed: {e}"
            logger.warning(
                "ytdlp_extractor_error",
                provider=self.name,
                video_id=video_id,
                error=error_msg,
            )
            return ProviderResult(
                success=False,
                data=None,
                error=error_msg,
                source=self.name,
            )

        except Exception as e:
            error_msg = f"yt-dlp error: {e}"
            logger.exception(
                "ytdlp_error",
                provider=self.name,
                video_id=video_id,
                error=str(e),
            )
            return ProviderResult(
                success=False,
                data=None,
                error=error_msg,
                source=self.name,
            )

    def _extract_info(
        self, video_url: str, opts: dict[str, Any]
    ) -> dict[str, Any] | None:
        """Extract video info using yt-dlp (blocking).

        Args:
            video_url: YouTube video URL
            opts: yt-dlp options

        Returns:
            Video info dict or None
        """
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                return ydl.extract_info(video_url, download=False)
        except Exception:
            return None

    def _get_available_fields(self, info: dict[str, Any]) -> list[str]:
        """Get list of fields that have non-null values.

        Args:
            info: yt-dlp info dict

        Returns:
            List of available field names
        """
        return [f for f in self.SUPPORTED_FIELDS if info.get(f) is not None]

    def _parse_download_error(self, error: yt_dlp.utils.DownloadError) -> str:
        """Parse download error to user-friendly message.

        Args:
            error: DownloadError from yt-dlp

        Returns:
            User-friendly error message
        """
        error_str = str(error).lower()

        if "private" in error_str:
            return "Video is private"
        if "unavailable" in error_str or "removed" in error_str:
            return "Video is unavailable or has been removed"
        if "age" in error_str or "age-restricted" in error_str:
            return "Video is age-restricted"
        if "member" in error_str:
            return "Video is members-only content"
        if "region" in error_str or "country" in error_str:
            return "Video is not available in your region"
        if "live" in error_str:
            return "Live stream handling not supported"

        return f"Video unavailable: {error}"

    def extract_transcript(
        self, info: dict[str, Any], language_preference: list[str] | None = None
    ) -> TranscriptResult:
        """Extract transcript from yt-dlp info.

        Args:
            info: yt-dlp info dict
            language_preference: Preferred languages for transcript

        Returns:
            TranscriptResult with transcript data
        """
        langs = language_preference or self.DEFAULT_SUBTITLE_LANGS

        # Try manual subtitles first, then auto-generated
        subtitles = info.get("subtitles", {})
        auto_captions = info.get("automatic_captions", {})

        # Combine with preference
        all_subs = {**subtitles, **auto_captions}

        if not all_subs:
            return TranscriptResult(
                success=False,
                error="No subtitles available",
                source=self.name,
            )

        # Select language
        selected_lang = None
        selected_subs = None
        is_auto = False

        for lang in langs:
            if lang in subtitles:
                selected_lang = lang
                selected_subs = subtitles[lang]
                is_auto = False
                break
            if lang in auto_captions:
                selected_lang = lang
                selected_subs = auto_captions[lang]
                is_auto = True
                break

        # Fallback to first available
        if not selected_subs:
            if subtitles:
                selected_lang = list(subtitles.keys())[0]
                selected_subs = subtitles[selected_lang]
                is_auto = False
            elif auto_captions:
                selected_lang = list(auto_captions.keys())[0]
                selected_subs = auto_captions[selected_lang]
                is_auto = True

        if not selected_subs:
            return TranscriptResult(
                success=False,
                error="Could not find usable subtitles",
                source=self.name,
            )

        # Parse subtitle data
        try:
            segments = self._parse_subtitle_data(selected_subs)
            full_text = " ".join(seg.get("text", "") for seg in segments)

            return TranscriptResult(
                success=True,
                text=full_text,
                segments=segments,
                language=selected_lang,
                is_auto_generated=is_auto,
                source=self.name,
            )

        except Exception as e:
            return TranscriptResult(
                success=False,
                error=f"Failed to parse subtitles: {e}",
                source=self.name,
            )

    def _parse_subtitle_data(
        self, subtitle_data: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Parse subtitle data into normalized format.

        Args:
            subtitle_data: Raw subtitle data from yt-dlp

        Returns:
            List of normalized subtitle segments
        """
        segments = []

        for sub in subtitle_data:
            text = sub.get("text", "").strip()
            if not text:
                continue

            start = sub.get("start", 0)
            duration = sub.get("duration", 0)

            segments.append({
                "text": text,
                "start_ms": int(start * 1000),
                "end_ms": int((start + duration) * 1000),
                "speaker": None,
            })

        return segments