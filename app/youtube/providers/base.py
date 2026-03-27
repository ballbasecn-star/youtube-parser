"""Provider base classes and result types.

This module defines the abstract base class for all providers
and the standard result type they return.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ProviderResult:
    """Standard result type returned by all providers.

    Attributes:
        success: Whether the provider successfully fetched data
        data: The fetched data dictionary, or None on failure
        error: Error message if success is False
        source: Provider name for tracking data origin
        fields: List of fields that were successfully retrieved
    """

    success: bool
    data: dict[str, Any] | None
    error: str | None = None
    source: str = ""
    fields: list[str] = field(default_factory=list)

    def get(self, key: str, default: Any = None) -> Any:
        """Get a value from the data dictionary.

        Args:
            key: The key to look up
            default: Default value if key not found

        Returns:
            The value or default
        """
        if self.data is None:
            return default
        return self.data.get(key, default)


class BaseProvider(ABC):
    """Abstract base class for all providers.

    Providers are responsible for fetching data from a specific source.
    Each provider handles one data source and returns a standardized
    ProviderResult.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Provider name for logging and tracking.

        Returns:
            Provider identifier string
        """
        pass

    @property
    @abstractmethod
    def supported_fields(self) -> list[str]:
        """List of fields this provider can retrieve.

        Returns:
            List of supported field names
        """
        pass

    @abstractmethod
    async def fetch(self, video_id: str) -> ProviderResult:
        """Fetch data for a YouTube video.

        Args:
            video_id: YouTube video ID

        Returns:
            ProviderResult containing the fetched data or error
        """
        pass

    def supports_field(self, field: str) -> bool:
        """Check if this provider supports a specific field.

        Args:
            field: Field name to check

        Returns:
            True if the field is supported
        """
        return field in self.supported_fields

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name!r})"


@dataclass
class TranscriptResult:
    """Result from transcript extraction.

    Attributes:
        success: Whether transcript was successfully extracted
        text: Full transcript text
        segments: List of transcript segments with timing
        language: Language code of the transcript
        is_auto_generated: Whether this is an auto-generated caption
        source: Provider name that extracted the transcript
        error: Error message if success is False
    """

    success: bool
    text: str | None = None
    segments: list[dict[str, Any]] = field(default_factory=list)
    language: str | None = None
    is_auto_generated: bool = False
    source: str = ""
    error: str | None = None