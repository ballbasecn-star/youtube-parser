"""Provider orchestrator for metadata fetching.

Coordinates multiple providers with fallback logic to ensure
reliable metadata retrieval.
"""

import structlog

from app.youtube.providers.base import ProviderResult, TranscriptResult
from app.youtube.providers.oembed_provider import OEmbedProvider
from app.youtube.providers.yt_dlp_provider import YtDlpProvider

logger = structlog.get_logger(__name__)


class MetadataOrchestrator:
    """Orchestrates metadata providers with fallback logic.

    Provider priority:
    1. oEmbed (fast, reliable, limited fields)
    2. yt-dlp (complete, slower, fallback)

    The orchestrator tries providers in order and returns the first
    successful result. It can also combine data from multiple providers
    to get the most complete information.
    """

    def __init__(self) -> None:
        """Initialize providers."""
        self.oembed_provider = OEmbedProvider()
        self.ytdlp_provider = YtDlpProvider()

        # Provider chain in priority order
        self.metadata_providers = [
            self.oembed_provider,
            self.ytdlp_provider,
        ]

    async def fetch_metadata(self, video_id: str) -> tuple[ProviderResult, str]:
        """Fetch metadata using provider chain.

        Tries providers in order until one succeeds.

        Args:
            video_id: YouTube video ID

        Returns:
            Tuple of (ProviderResult, provider_name_used)
        """
        errors = []

        for provider in self.metadata_providers:
            logger.debug(
                "orchestrator_trying_provider",
                provider=provider.name,
                video_id=video_id,
            )

            result = await provider.fetch(video_id)

            if result.success:
                logger.info(
                    "orchestrator_provider_success",
                    provider=provider.name,
                    video_id=video_id,
                    fields=result.fields,
                )
                return result, provider.name

            errors.append(f"{provider.name}: {result.error}")
            logger.warning(
                "orchestrator_provider_failed",
                provider=provider.name,
                error=result.error,
                video_id=video_id,
            )

        # All providers failed
        error_msg = "; ".join(errors)
        logger.error(
            "orchestrator_all_providers_failed",
            video_id=video_id,
            errors=error_msg,
        )

        return ProviderResult(
            success=False,
            data=None,
            error=error_msg,
            source="orchestrator",
        ), "none"

    async def fetch_with_fallback(
        self, video_id: str, required_fields: list[str] | None = None
    ) -> tuple[ProviderResult, str]:
        """Fetch metadata, falling back if required fields are missing.

        This method tries oEmbed first for speed. If oEmbed succeeds
        but is missing required fields, it falls back to yt-dlp.

        Args:
            video_id: YouTube video ID
            required_fields: Fields that must be present (e.g., ["description"])

        Returns:
            Tuple of (ProviderResult, provider_name_used)
        """
        required = required_fields or []

        # Try oEmbed first (fast)
        oembed_result = await self.oembed_provider.fetch(video_id)

        if oembed_result.success:
            # Check if all required fields are present
            missing_fields = [
                f for f in required if f not in oembed_result.fields
            ]

            if not missing_fields:
                # oEmbed has everything we need
                return oembed_result, self.oembed_provider.name

            logger.info(
                "orchestrator_oembed_missing_fields",
                video_id=video_id,
                missing=missing_fields,
                falling_back_to="yt_dlp",
            )

            # Fall back to yt-dlp for missing fields
            ytdlp_result = await self.ytdlp_provider.fetch(video_id)

            if ytdlp_result.success:
                # Merge data: prefer yt-dlp for missing fields
                merged_data = {**oembed_result.data, **ytdlp_result.data}
                merged_fields = list(set(oembed_result.fields + ytdlp_result.fields))

                return ProviderResult(
                    success=True,
                    data=merged_data,
                    source="merged_oembed_ytdlp",
                    fields=merged_fields,
                ), "merged"

            # yt-dlp failed, use oEmbed with warnings
            return oembed_result, self.oembed_provider.name

        # oEmbed failed, try yt-dlp
        ytdlp_result = await self.ytdlp_provider.fetch(video_id)
        return ytdlp_result, self.ytdlp_provider.name if ytdlp_result.success else "none"

    async def fetch_transcript(
        self, video_id: str, language_preference: list[str] | None = None
    ) -> TranscriptResult:
        """Fetch transcript using yt-dlp.

        This downloads the actual subtitle file and parses it.

        Args:
            video_id: YouTube video ID
            language_preference: Preferred languages for transcript

        Returns:
            TranscriptResult with transcript data
        """
        logger.debug(
            "orchestrator_fetch_transcript",
            video_id=video_id,
            langs=language_preference,
        )

        # Use yt-dlp to fetch and parse transcript
        return await self.ytdlp_provider.fetch_transcript(video_id, language_preference)

    async def fetch_full(
        self,
        video_id: str,
        include_transcript: bool = True,
        language_preference: list[str] | None = None,
    ) -> tuple[ProviderResult, TranscriptResult | None, str]:
        """Fetch complete video data including transcript.

        This is the main entry point for fetching all available data.

        Args:
            video_id: YouTube video ID
            include_transcript: Whether to fetch transcript
            language_preference: Preferred languages for transcript

        Returns:
            Tuple of (metadata_result, transcript_result, provider_name)
        """
        # Fetch metadata with full fallback
        required_fields = ["title", "description"]
        metadata_result, provider = await self.fetch_with_fallback(
            video_id, required_fields
        )

        # Fetch transcript if requested
        transcript_result = None
        if include_transcript and metadata_result.success:
            # If we already have yt-dlp data, extract transcript from it
            if provider in ("yt_dlp", "merged") and metadata_result.data:
                transcript_result = self.ytdlp_provider.extract_transcript(
                    metadata_result.data, language_preference
                )
            else:
                # Need to fetch separately
                transcript_result = await self.fetch_transcript(
                    video_id, language_preference
                )

        return metadata_result, transcript_result, provider