"""Parse service for orchestrating YouTube content parsing.

This service coordinates the parsing pipeline:
1. URL normalization
2. Metadata fetching (via providers)
3. Transcript fetching (via providers)
4. Mapping to contract schema
"""

import dataclasses
from dataclasses import dataclass
from typing import Self

import structlog

from app.contract import ErrorCode, ParsedContentPayload, ParserParseRequest
from app.youtube.domain.models import YoutubeVideo
from app.youtube.mapper.parsed_content_mapper import ParsedContentMapper
from app.youtube.normalization.url_normalizer import YoutubeUrlNormalizer

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
            logger.warning("no_url_in_input")
            return ParseResult.err(
                code=ErrorCode.INVALID_INPUT,
                message="No URL provided in input. Provide sourceUrl or sourceText with a YouTube URL.",
            )

        # Step 2: Normalize the URL
        url_info = self.url_normalizer.normalize(url)
        if url_info is None:
            logger.warning("invalid_youtube_url", url=url)
            return ParseResult.err(
                code=ErrorCode.UNSUPPORTED_URL,
                message=f"The URL '{url}' is not a valid YouTube video URL.",
            )

        logger.info(
            "url_normalized",
            video_id=url_info.video_id,
            url_type=url_info.url_type.value,
            canonical_url=url_info.canonical_url,
        )

        # Step 3: Build the video object
        # For now, we only have URL normalization
        # Metadata and transcript providers will be added in phase 3
        video = YoutubeVideo(
            video_id=url_info.video_id,
            canonical_url=url_info.canonical_url,
            title=None,  # Will be filled by metadata provider
            description=None,
            raw_data={
                "matchedSourceUrl": url,
                "resolvedVideoId": url_info.video_id,
                "urlType": url_info.url_type.value,
            },
        )

        # Step 4: Add placeholder warnings for missing features
        video.warnings.append("METADATA_UNAVAILABLE: Metadata provider not yet implemented")
        if request.options.fetch_transcript:
            video.warnings.append("TRANSCRIPT_UNAVAILABLE: Transcript provider not yet implemented")

        return ParseResult.ok(video)

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

    def map_to_payload(self, video: YoutubeVideo) -> ParsedContentPayload:
        """Map video to contract payload.

        Args:
            video: Parsed video

        Returns:
            ParsedContentPayload conforming to contract
        """
        return self.mapper.map(video)