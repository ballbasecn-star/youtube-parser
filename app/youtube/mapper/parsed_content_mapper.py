"""Mapper for converting YouTube domain models to contract payloads.

This module is responsible for mapping internal domain models
to the unified ParsedContentPayload defined in the contract.
"""

from app.contract import (
    AuthorInfo,
    ContentInfo,
    CoverImage,
    MediaInfo,
    MetricsInfo,
    ParsedContentPayload,
    Warning,
)
from app.youtube.domain.models import YoutubeVideo


class ParsedContentMapper:
    """Mapper for converting YoutubeVideo to ParsedContentPayload."""

    @staticmethod
    def map(video: YoutubeVideo) -> ParsedContentPayload:
        """Map a YoutubeVideo to ParsedContentPayload.

        Args:
            video: The YouTube video to map

        Returns:
            ParsedContentPayload conforming to the contract
        """
        # Map author info
        author = None
        if video.channel:
            author = AuthorInfo(
                external_author_id=video.channel.channel_id,
                name=video.channel.name,
                handle=video.channel.handle,
                profile_url=video.channel.profile_url,
                avatar_url=video.channel.avatar_url,
            )

        # Map content info
        content = ContentInfo(
            raw_text=video.description,
            transcript=video.transcript.text if video.transcript else None,
            segments=[
                {
                    "text": seg.text,
                    "startMs": seg.start_ms,
                    "endMs": seg.end_ms,
                    "speaker": seg.speaker,
                }
                for seg in (video.transcript.segments if video.transcript else [])
            ],
        )

        # Map metrics
        metrics = MetricsInfo()
        if video.metrics:
            metrics = MetricsInfo(
                views=video.metrics.views,
                likes=video.metrics.likes,
                comments=video.metrics.comments,
            )

        # Map media (thumbnails as covers)
        covers = [
            CoverImage(url=thumb.url, width=thumb.width, height=thumb.height)
            for thumb in video.thumbnails
        ]

        # If no thumbnails, use YouTube's default thumbnail URL pattern
        if not covers:
            covers = [
                CoverImage(
                    url=f"https://img.youtube.com/vi/{video.video_id}/maxresdefault.jpg",
                    width=None,
                    height=None,
                ),
                CoverImage(
                    url=f"https://img.youtube.com/vi/{video.video_id}/hqdefault.jpg",
                    width=None,
                    height=None,
                ),
            ]

        media = MediaInfo(covers=covers)

        # Map warnings
        warnings = [
            Warning(code=w.split(":")[0], message=w.split(": ")[1] if ": " in w else w)
            for w in video.warnings
            if w
        ]

        return ParsedContentPayload(
            platform="youtube",
            source_type="video",
            external_id=video.video_id,
            canonical_url=video.canonical_url,
            title=video.title,
            summary=video.description,
            author=author,
            published_at=video.published_at,
            language=video.language,
            content=content,
            metrics=metrics,
            tags=video.tags,
            media=media,
            raw_payload=video.raw_data,
            warnings=warnings,
        )