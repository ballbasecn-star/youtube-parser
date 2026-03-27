"""OEmbed provider for YouTube metadata.

Uses YouTube's oEmbed API to fetch basic video metadata.
This is a free, no-authentication-required API that provides
basic information about YouTube videos.

Pros:
- Free, no API key required
- Fast response
- Stable official API

Cons:
- Limited fields (no description, no metrics, no channel_id)
"""

import structlog

from app.shared.http_client import get_http_client
from app.youtube.providers.base import BaseProvider, ProviderResult

logger = structlog.get_logger(__name__)


class OEmbedProvider(BaseProvider):
    """YouTube oEmbed API provider.

    Fetches basic video metadata from YouTube's oEmbed endpoint.
    This is the primary (fast) provider for metadata.

    API Documentation: https://oembed.com/
    YouTube oEmbed endpoint: https://www.youtube.com/oembed
    """

    name = "oembed"
    OEMBED_URL = "https://www.youtube.com/oembed"

    # Fields that oEmbed API returns
    SUPPORTED_FIELDS = [
        "title",
        "author_name",
        "author_url",
        "thumbnail_url",
        "thumbnail_width",
        "thumbnail_height",
        "type",
        "html",
    ]

    # Fields we actually use from oEmbed
    USABLE_FIELDS = [
        "title",
        "author_name",
        "author_url",
        "thumbnail_url",
    ]

    @property
    def supported_fields(self) -> list[str]:
        """Return list of fields this provider can retrieve."""
        return self.USABLE_FIELDS

    async def fetch(self, video_id: str) -> ProviderResult:
        """Fetch video metadata from oEmbed API.

        Args:
            video_id: YouTube video ID

        Returns:
            ProviderResult with oEmbed data or error
        """
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        params = {"url": video_url, "format": "json"}

        logger.debug(
            "oembed_fetch_start",
            provider=self.name,
            video_id=video_id,
        )

        try:
            async with get_http_client() as client:
                response = await client.get(
                    self.OEMBED_URL,
                    params=params,
                    timeout=10.0,
                )

                if response.status_code == 200:
                    data = response.json()
                    logger.info(
                        "oembed_fetch_success",
                        provider=self.name,
                        video_id=video_id,
                        title=data.get("title", "")[:50],
                    )
                    return ProviderResult(
                        success=True,
                        data=data,
                        source=self.name,
                        fields=self._get_available_fields(data),
                    )

                if response.status_code == 404:
                    error_msg = "Video not found or unavailable"
                elif response.status_code == 401:
                    error_msg = "Video is private or restricted"
                else:
                    error_msg = f"oEmbed request failed with status {response.status_code}"

                logger.warning(
                    "oembed_fetch_failed",
                    provider=self.name,
                    video_id=video_id,
                    status_code=response.status_code,
                    error=error_msg,
                )

                return ProviderResult(
                    success=False,
                    data=None,
                    error=error_msg,
                    source=self.name,
                )

        except TimeoutError:
            error_msg = "oEmbed request timed out"
            logger.warning(
                "oembed_timeout",
                provider=self.name,
                video_id=video_id,
            )
            return ProviderResult(
                success=False,
                data=None,
                error=error_msg,
                source=self.name,
            )

        except Exception as e:
            error_msg = f"oEmbed request error: {e}"
            logger.exception(
                "oembed_error",
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

    def _get_available_fields(self, data: dict) -> list[str]:
        """Get list of fields that have non-null values.

        Args:
            data: oEmbed response data

        Returns:
            List of available field names
        """
        return [f for f in self.USABLE_FIELDS if data.get(f) is not None]