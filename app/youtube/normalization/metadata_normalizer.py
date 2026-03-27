"""Metadata normalization module.

Normalizes raw provider data into standardized domain models.
"""

from datetime import datetime

from app.youtube.domain.models import YoutubeChannel, YoutubeMetrics, YoutubeThumbnail, YoutubeVideo


class MetadataNormalizer:
    """Normalizes metadata from various providers.

    Converts raw provider data (oEmbed, yt-dlp) into standardized
    YoutubeVideo domain models.
    """

    @staticmethod
    def normalize_oembed(
        data: dict, video_id: str, canonical_url: str
    ) -> YoutubeVideo:
        """Normalize oEmbed data to YoutubeVideo.

        Args:
            data: oEmbed response data
            video_id: YouTube video ID
            canonical_url: Canonical URL for the video

        Returns:
            YoutubeVideo with oEmbed data
        """
        # Extract thumbnail
        thumbnails = []
        if data.get("thumbnail_url"):
            thumbnails.append(
                YoutubeThumbnail(
                    url=data["thumbnail_url"],
                    width=data.get("thumbnail_width"),
                    height=data.get("thumbnail_height"),
                )
            )

        # Extract channel info
        channel = None
        if data.get("author_name"):
            channel = YoutubeChannel(
                name=data["author_name"],
                profile_url=data.get("author_url"),
            )

        return YoutubeVideo(
            video_id=video_id,
            canonical_url=canonical_url,
            title=data.get("title"),
            description=None,  # oEmbed doesn't provide this
            channel=channel,
            thumbnails=thumbnails,
            raw_data={
                "source": "oembed",
                "author_name": data.get("author_name"),
                "author_url": data.get("author_url"),
            },
        )

    @staticmethod
    def normalize_ytdlp(
        data: dict, video_id: str, canonical_url: str
    ) -> YoutubeVideo:
        """Normalize yt-dlp data to YoutubeVideo.

        Args:
            data: yt-dlp info dict
            video_id: YouTube video ID
            canonical_url: Canonical URL for the video

        Returns:
            YoutubeVideo with yt-dlp data
        """
        # Parse upload date
        published_at = None
        if data.get("upload_date"):
            try:
                published_at = datetime.strptime(data["upload_date"], "%Y%m%d")
            except ValueError:
                pass

        # Extract thumbnails
        thumbnails = []
        for t in data.get("thumbnails", []):
            if t.get("url"):
                thumbnails.append(
                    YoutubeThumbnail(
                        url=t["url"],
                        width=t.get("width"),
                        height=t.get("height"),
                    )
                )

        # Fallback to single thumbnail
        if not thumbnails and data.get("thumbnail"):
            thumbnails.append(
                YoutubeThumbnail(url=data["thumbnail"])
            )

        # Extract channel info
        channel = None
        if data.get("uploader") or data.get("channel_id"):
            channel = YoutubeChannel(
                channel_id=data.get("channel_id"),
                name=data.get("uploader"),
                profile_url=data.get("channel_url"),
            )

        # Extract metrics
        metrics = None
        if any(
            data.get(f) is not None
            for f in ["view_count", "like_count", "comment_count"]
        ):
            metrics = YoutubeMetrics(
                views=data.get("view_count"),
                likes=data.get("like_count"),
                comments=data.get("comment_count"),
            )

        return YoutubeVideo(
            video_id=video_id,
            canonical_url=canonical_url,
            title=data.get("title"),
            description=data.get("description"),
            published_at=published_at,
            duration_seconds=data.get("duration"),
            language=data.get("language"),
            tags=data.get("tags", []),
            channel=channel,
            thumbnails=thumbnails,
            metrics=metrics,
            raw_data={
                "source": "yt_dlp",
                "view_count": data.get("view_count"),
                "like_count": data.get("like_count"),
                "comment_count": data.get("comment_count"),
                "duration": data.get("duration"),
                "upload_date": data.get("upload_date"),
            },
        )

    @staticmethod
    def merge_oembed_ytdlp(
        oembed_data: dict, ytdlp_data: dict, video_id: str, canonical_url: str
    ) -> YoutubeVideo:
        """Merge oEmbed and yt-dlp data.

        Prefers yt-dlp for completeness, uses oEmbed as fallback.

        Args:
            oembed_data: oEmbed response data
            ytdlp_data: yt-dlp info dict
            video_id: YouTube video ID
            canonical_url: Canonical URL for the video

        Returns:
            YoutubeVideo with merged data
        """
        # Start with yt-dlp normalization
        video = MetadataNormalizer.normalize_ytdlp(ytdlp_data, video_id, canonical_url)

        # Fill in missing fields from oEmbed
        if not video.title and oembed_data.get("title"):
            video.title = oembed_data["title"]

        if not video.channel and oembed_data.get("author_name"):
            video.channel = YoutubeChannel(
                name=oembed_data["author_name"],
                profile_url=oembed_data.get("author_url"),
            )

        if not video.thumbnails and oembed_data.get("thumbnail_url"):
            video.thumbnails = [
                YoutubeThumbnail(
                    url=oembed_data["thumbnail_url"],
                    width=oembed_data.get("thumbnail_width"),
                    height=oembed_data.get("thumbnail_height"),
                )
            ]

        # Update raw_data to show merge
        video.raw_data["source"] = "merged_oembed_ytdlp"
        video.raw_data["oembed_author_name"] = oembed_data.get("author_name")

        return video

    @staticmethod
    def normalize_from_result(
        result: "ProviderResult",
        video_id: str,
        canonical_url: str,
        oembed_result: "ProviderResult | None" = None,
    ) -> YoutubeVideo | None:
        """Normalize provider result to YoutubeVideo.

        Handles different source types (oembed, yt_dlp, merged).

        Args:
            result: Provider result to normalize
            video_id: YouTube video ID
            canonical_url: Canonical URL for the video
            oembed_result: Optional oEmbed result for merging

        Returns:
            YoutubeVideo or None if result is not successful
        """
        if not result.success or not result.data:
            return None

        source = result.source

        if source == "oembed":
            return MetadataNormalizer.normalize_oembed(
                result.data, video_id, canonical_url
            )

        if source == "yt_dlp":
            # Check if we should merge with oEmbed
            if oembed_result and oembed_result.success and oembed_result.data:
                return MetadataNormalizer.merge_oembed_ytdlp(
                    oembed_result.data, result.data, video_id, canonical_url
                )
            return MetadataNormalizer.normalize_ytdlp(
                result.data, video_id, canonical_url
            )

        if source == "merged_oembed_ytdlp":
            return MetadataNormalizer.normalize_ytdlp(
                result.data, video_id, canonical_url
            )

        # Unknown source, try to use yt-dlp normalization
        return MetadataNormalizer.normalize_ytdlp(
            result.data, video_id, canonical_url
        )