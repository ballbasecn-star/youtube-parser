"""Parse service for orchestrating YouTube content parsing.

This service coordinates the parsing pipeline:
1. URL normalization
2. Metadata fetching (via providers)
3. Transcript fetching (via providers)
4. Mapping to contract schema
"""

from dataclasses import dataclass
from typing import Self

import structlog

from app.contract import ErrorCode, ParsedContentPayload, ParserParseRequest
from app.youtube.domain.models import YoutubeVideo
from app.youtube.mapper.parsed_content_mapper import ParsedContentMapper
from app.youtube.normalization.metadata_normalizer import MetadataNormalizer
from app.youtube.normalization.transcript_normalizer import TranscriptNormalizer
from app.youtube.normalization.url_normalizer import YoutubeUrlNormalizer
from app.youtube.providers.base import ProviderResult, TranscriptResult
from app.youtube.providers.orchestrator import MetadataOrchestrator

logger = structlog.get_logger(__name__)


@dataclass
class ParseError:
    """Parse error with code and message."""

    code: ErrorCode
    message: str


@dataclass
class ParseResult:
    """Result of a parse operation.

    Uses a Result pattern to handle success/failure without exceptions.
    """

    _value: YoutubeVideo | None = None
    _error: ParseError | None = None

    @classmethod
    def ok(cls, value: YoutubeVideo) -> Self:
        """Create a successful result.

        Args:
            value: The parsed video

        Returns:
            Successful ParseResult
        """
        return cls(_value=value, _error=None)

    @classmethod
    def err(cls, code: ErrorCode, message: str) -> Self:
        """Create an error result.

        Args:
            code: Error code
            message: Error message

        Returns:
            Error ParseResult
        """
        return cls(_value=None, _error=ParseError(code=code, message=message))

    def is_ok(self) -> bool:
        """Check if result is successful."""
        return self._value is not None

    def is_err(self) -> bool:
        """Check if result is an error."""
        return self._error is not None

    def unwrap(self) -> YoutubeVideo:
        """Get the value (raises if error).

        Returns:
            The parsed video

        Raises:
            ValueError: If result is an error
        """
        if self._value is None:
            raise ValueError("Cannot unwrap error result")
        return self._value

    def unwrap_err(self) -> ParseError:
        """Get the error (raises if success).

        Returns:
            The parse error

        Raises:
            ValueError: If result is successful
        """
        if self._error is None:
            raise ValueError("Cannot unwrap success result")
        return self._error


class ParseYoutubeService:
    """Service for parsing YouTube content.

    This service orchestrates the entire parsing pipeline,
    coordinating between URL normalization, providers, and mapping.
    """

    def __init__(self) -> None:
        """Initialize the parse service."""
        self.url_normalizer = YoutubeUrlNormalizer()
        self.provider_orchestrator = MetadataOrchestrator()
        self.mapper = ParsedContentMapper()

    async def parse(
        self,
        request: ParserParseRequest,
        request_id: str,
    ) -> ParseResult:
        """Parse YouTube content from the request.

        Args:
            request: Parse request
            request_id: Request ID for tracing

        Returns:
            ParseResult containing either the parsed video or an error
        """
        # Step 1: Get the URL from input
        url = self._get_url_from_input(request)
        if not url:
            logger.warning("no_url_in_input", request_id=request_id)
            return ParseResult.err(
                code=ErrorCode.INVALID_INPUT,
                message="No URL provided in input. Provide sourceUrl or sourceText with a YouTube URL.",
            )

        # Step 2: Normalize the URL
        url_info = self.url_normalizer.normalize(url)
        if url_info is None:
            logger.warning("invalid_youtube_url", url=url, request_id=request_id)
            return ParseResult.err(
                code=ErrorCode.UNSUPPORTED_URL,
                message=f"The URL '{url}' is not a valid YouTube video URL.",
            )

        logger.info(
            "url_normalized",
            request_id=request_id,
            video_id=url_info.video_id,
            url_type=url_info.url_type.value,
            canonical_url=url_info.canonical_url,
        )

        # Step 3: Fetch metadata from providers
        metadata_result, provider_used = await self.provider_orchestrator.fetch_with_fallback(
            video_id=url_info.video_id,
            required_fields=["title"],
        )

        if not metadata_result.success:
            error_msg = metadata_result.error or "Failed to fetch video metadata"
            logger.error(
                "metadata_fetch_failed",
                request_id=request_id,
                video_id=url_info.video_id,
                error=error_msg,
            )

            # Determine appropriate error code
            error_code = self._determine_error_code(metadata_result)
            return ParseResult.err(code=error_code, message=error_msg)

        logger.info(
            "metadata_fetch_success",
            request_id=request_id,
            video_id=url_info.video_id,
            provider=provider_used,
            fields=metadata_result.fields,
        )

        # Step 4: Normalize metadata to domain model
        video = MetadataNormalizer.normalize_from_result(
            result=metadata_result,
            video_id=url_info.video_id,
            canonical_url=url_info.canonical_url,
        )

        if video is None:
            return ParseResult.err(
                code=ErrorCode.INTERNAL_ERROR,
                message="Failed to normalize video metadata",
            )

        # Step 5: Fetch transcript if requested
        if request.options.fetch_transcript:
            await self._fetch_and_attach_transcript(
                video=video,
                video_id=url_info.video_id,
                metadata_result=metadata_result,
                language_hint=request.options.language_hint,
                request_id=request_id,
            )

        # Step 6: Attach raw data for debugging
        video.raw_data.update({
            "matchedSourceUrl": url,
            "resolvedVideoId": url_info.video_id,
            "urlType": url_info.url_type.value,
            "metadataProvider": provider_used,
        })

        return ParseResult.ok(video)

    async def _fetch_and_attach_transcript(
        self,
        video: YoutubeVideo,
        video_id: str,
        metadata_result: ProviderResult,
        language_hint: str | None,
        request_id: str,
    ) -> None:
        """Fetch and attach transcript to video.

        This is a best-effort operation - failure doesn't block parsing.

        Args:
            video: Video to attach transcript to
            video_id: YouTube video ID
            metadata_result: Metadata result (may contain yt-dlp data)
            language_hint: Preferred language for transcript
            request_id: Request ID for tracing
        """
        langs = None
        if language_hint:
            langs = [language_hint, "en"]

        transcript_result: TranscriptResult | None = None

        # If metadata came from yt-dlp, try to extract transcript from it
        if metadata_result.data and metadata_result.source in ("yt_dlp", "merged_oembed_ytdlp"):
            transcript_result = self.provider_orchestrator.ytdlp_provider.extract_transcript(
                metadata_result.data, langs
            )

        # Otherwise, fetch transcript separately
        if transcript_result is None or not transcript_result.success:
            transcript_result = await self.provider_orchestrator.fetch_transcript(
                video_id, langs
            )

        if transcript_result.success:
            logger.info(
                "transcript_fetch_success",
                request_id=request_id,
                video_id=video_id,
                language=transcript_result.language,
                is_auto=transcript_result.is_auto_generated,
                segment_count=len(transcript_result.segments),
            )

            # Normalize and attach
            video.transcript = TranscriptNormalizer.normalize_from_provider(transcript_result)
            video.raw_data["transcriptProvider"] = transcript_result.source
            video.raw_data["transcriptLanguage"] = transcript_result.language

        else:
            logger.info(
                "transcript_unavailable",
                request_id=request_id,
                video_id=video_id,
                error=transcript_result.error,
            )
            video.warnings.append(f"TRANSCRIPT_UNAVAILABLE: {transcript_result.error}")
            video.raw_data["transcriptProvider"] = "none"

    def _get_url_from_input(self, request: ParserParseRequest) -> str | None:
        """Extract URL from request input.

        Args:
            request: Parse request

        Returns:
            URL if found, None otherwise
        """
        # Priority 1: Direct URL
        if request.input.source_url:
            return request.input.source_url

        # Priority 2: Extract from text
        if request.input.source_text:
            return self.url_normalizer.extract_url_from_text(request.input.source_text)

        return None

    def _determine_error_code(self, result: ProviderResult) -> ErrorCode:
        """Determine appropriate error code from provider result.

        Args:
            result: Failed provider result

        Returns:
            Appropriate ErrorCode
        """
        error = (result.error or "").lower()

        if "private" in error:
            return ErrorCode.AUTH_REQUIRED
        if "unavailable" in error or "removed" in error:
            return ErrorCode.UPSTREAM_CHANGED
        if "age" in error or "restricted" in error:
            return ErrorCode.AUTH_REQUIRED
        if "region" in error or "country" in error:
            return ErrorCode.AUTH_REQUIRED
        if "timeout" in error:
            return ErrorCode.PARSER_TIMEOUT
        if "rate" in error or "limit" in error:
            return ErrorCode.RATE_LIMITED

        return ErrorCode.UPSTREAM_CHANGED

    def map_to_payload(self, video: YoutubeVideo) -> ParsedContentPayload:
        """Map video to contract payload.

        Args:
            video: Parsed video

        Returns:
            ParsedContentPayload conforming to contract
        """
        return self.mapper.map(video)