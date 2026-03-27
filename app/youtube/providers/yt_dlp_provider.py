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
import os
import re
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
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

    async def fetch_transcript(
        self, video_id: str, language_preference: list[str] | None = None
    ) -> TranscriptResult:
        """Fetch transcript by downloading subtitle file.

        This method downloads the actual subtitle file and parses it,
        rather than just getting metadata.

        Args:
            video_id: YouTube video ID
            language_preference: Preferred languages for transcript

        Returns:
            TranscriptResult with transcript data
        """
        langs = language_preference or self.DEFAULT_SUBTITLE_LANGS

        # Create temp directory for subtitle files
        with tempfile.TemporaryDirectory() as tmpdir:
            video_url = f"https://www.youtube.com/watch?v={video_id}"

            ydl_opts = {
                "quiet": True,
                "no_warnings": True,
                "writesubtitles": True,
                "writeautomaticsub": True,
                "subtitleslangs": langs,
                "skip_download": True,
                "outtmpl": os.path.join(tmpdir, "video"),
                "socket_timeout": 30,
                "retries": 2,
                "ignoreerrors": True,  # Don't fail on subtitle download errors
            }

            try:
                loop = asyncio.get_event_loop()
                info = await loop.run_in_executor(
                    _executor,
                    lambda: self._download_subtitles(video_url, ydl_opts, tmpdir),
                )

                # Find and parse subtitle file (info may be None but files might exist)
                return self._find_and_parse_subtitle(tmpdir, langs, info)

            except Exception as e:
                logger.exception(
                    "transcript_fetch_error",
                    video_id=video_id,
                    error=str(e),
                )
                return TranscriptResult(
                    success=False,
                    error=f"Failed to fetch transcript: {e}",
                    source=self.name,
                )

    def _download_subtitles(
        self, video_url: str, opts: dict[str, Any], tmpdir: str
    ) -> dict[str, Any] | None:
        """Download subtitles using yt-dlp.

        Args:
            video_url: YouTube video URL
            opts: yt-dlp options
            tmpdir: Temporary directory for files

        Returns:
            Video info dict or None
        """
        try:
            logger.debug(
                "ytdlp_download_subs_start",
                video_url=video_url,
                tmpdir=tmpdir,
            )
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(video_url, download=True)
                logger.debug(
                    "ytdlp_download_subs_done",
                    info_keys=list(info.keys()) if info else None,
                )
                return info
        except Exception as e:
            logger.exception(
                "ytdlp_download_subs_error",
                error=str(e),
            )
            return None

    def _find_and_parse_subtitle(
        self, tmpdir: str, langs: list[str], info: dict[str, Any]
    ) -> TranscriptResult:
        """Find and parse downloaded subtitle file.

        Args:
            tmpdir: Temporary directory containing subtitle files
            langs: Preferred languages
            info: Video info dict

        Returns:
            TranscriptResult with parsed transcript
        """
        # List files in temp dir
        files = list(Path(tmpdir).glob("video.*.vtt"))
        files.extend(Path(tmpdir).glob("video.*.srt"))

        logger.debug(
            "subtitle_files_search",
            tmpdir=tmpdir,
            files=[f.name for f in files],
            langs=langs,
        )

        if not files:
            logger.warning("no_subtitle_files_found", tmpdir=tmpdir)
            return TranscriptResult(
                success=False,
                error="No subtitle files downloaded",
                source=self.name,
            )

        # Find best matching file by language preference
        selected_file = None
        selected_lang = None
        is_auto = False

        auto_captions = info.get("automatic_captions", {}) if info else {}
        subtitles = info.get("subtitles", {}) if info else {}

        for lang in langs:
            # Check for matching file
            for f in files:
                if f".{lang}." in f.name:
                    selected_file = f
                    selected_lang = lang
                    is_auto = lang in auto_captions and lang not in subtitles
                    break
            if selected_file:
                break

        # Fallback to first available
        if not selected_file and files:
            selected_file = files[0]
            # Extract language from filename (video.en.vtt -> en)
            match = re.search(r"\.([a-z]{2}(?:-[A-Z]{2})?)\.", selected_file.name)
            if match:
                selected_lang = match.group(1)
                is_auto = selected_lang in auto_captions if info else True

        if not selected_file:
            return TranscriptResult(
                success=False,
                error="Could not find matching subtitle file",
                source=self.name,
            )

        # Parse the subtitle file
        try:
            segments = self._parse_vtt_file(selected_file)
            full_text = " ".join(seg.get("text", "") for seg in segments)

            logger.info(
                "subtitle_parsed",
                language=selected_lang,
                segment_count=len(segments),
                text_length=len(full_text),
            )

            return TranscriptResult(
                success=True,
                text=full_text,
                segments=segments,
                language=selected_lang,
                is_auto_generated=is_auto,
                source=self.name,
            )

        except Exception as e:
            logger.exception(
                "subtitle_parse_error",
                file=selected_file.name,
                error=str(e),
            )
            return TranscriptResult(
                success=False,
                error=f"Failed to parse subtitle file: {e}",
                source=self.name,
            )

    def _parse_vtt_file(self, file_path: Path) -> list[dict[str, Any]]:
        """Parse VTT subtitle file.

        Args:
            file_path: Path to VTT file

        Returns:
            List of subtitle segments
        """
        segments = []

        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        # VTT time format: 00:00:00.000 --> 00:00:00.000
        time_pattern = re.compile(
            r"(\d{2}):(\d{2}):(\d{2})\.(\d{3})\s*-->\s*(\d{2}):(\d{2}):(\d{2})\.(\d{3})"
        )

        lines = content.split("\n")
        current_start_ms = 0
        current_end_ms = 0

        for line in lines:
            line = line.strip()

            # Skip empty lines and headers
            if not line or line.startswith("WEBVTT") or line.startswith("Kind:") or line.startswith("Language:"):
                continue

            # Check for timing line
            match = time_pattern.match(line)
            if match:
                # Parse start time
                current_start_ms = (
                    int(match.group(1)) * 3600000
                    + int(match.group(2)) * 60000
                    + int(match.group(3)) * 1000
                    + int(match.group(4))
                )
                # Parse end time
                current_end_ms = (
                    int(match.group(5)) * 3600000
                    + int(match.group(6)) * 60000
                    + int(match.group(7)) * 1000
                    + int(match.group(8))
                )
                continue

            # This is a text line
            # Clean up VTT formatting tags
            text = re.sub(r"<[^>]+>", "", line).strip()
            if text and current_start_ms < current_end_ms:
                segments.append({
                    "text": text,
                    "start_ms": current_start_ms,
                    "end_ms": current_end_ms,
                    "speaker": None,
                })
                # Reset timing to avoid duplicate entries
                current_start_ms = 0
                current_end_ms = 0

        return segments

    def extract_transcript(
        self, info: dict[str, Any], language_preference: list[str] | None = None
    ) -> TranscriptResult:
        """Extract transcript from yt-dlp info (metadata only).

        Note: This method only returns metadata about available subtitles.
        Use fetch_transcript() to actually download and parse subtitles.

        Args:
            info: yt-dlp info dict
            language_preference: Preferred languages for transcript

        Returns:
            TranscriptResult indicating available subtitles
        """
        langs = language_preference or self.DEFAULT_SUBTITLE_LANGS

        subtitles = info.get("subtitles", {})
        auto_captions = info.get("automatic_captions", {})

        available_langs = list(subtitles.keys()) + list(auto_captions.keys())

        if not available_langs:
            return TranscriptResult(
                success=False,
                error="No subtitles available",
                source=self.name,
            )

        # Check if any preferred language is available
        found_lang = None
        for lang in langs:
            if lang in subtitles or lang in auto_captions:
                found_lang = lang
                break

        if not found_lang:
            found_lang = available_langs[0]

        # Return placeholder - caller should use fetch_transcript
        return TranscriptResult(
            success=True,
            text="",  # Will be filled by fetch_transcript
            segments=[],
            language=found_lang,
            is_auto_generated=found_lang in auto_captions,
            source=self.name,
        )