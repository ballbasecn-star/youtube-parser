"""YouTube data providers.

This module contains providers for fetching YouTube video data
from various sources with fallback logic.

Provider hierarchy:
- OEmbedProvider: Fast, reliable, limited fields (primary)
- YtDlpProvider: Complete, slower (fallback)
- MetadataOrchestrator: Coordinates providers with fallback logic
"""

from app.youtube.providers.base import BaseProvider, ProviderResult, TranscriptResult
from app.youtube.providers.oembed_provider import OEmbedProvider
from app.youtube.providers.orchestrator import MetadataOrchestrator
from app.youtube.providers.yt_dlp_provider import YtDlpProvider

__all__ = [
    # Base classes
    "BaseProvider",
    "ProviderResult",
    "TranscriptResult",
    # Providers
    "OEmbedProvider",
    "YtDlpProvider",
    # Orchestrator
    "MetadataOrchestrator",
]