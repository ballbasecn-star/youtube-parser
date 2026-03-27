"""Capabilities endpoint.

Declares the platform, supported source types, and available features.
"""

from fastapi import APIRouter

from app.contract.schemas import CapabilitiesResponse

router = APIRouter()


@router.get(
    "/capabilities",
    response_model=CapabilitiesResponse,
    summary="Get capabilities",
    description="Get the platform, supported source types, and available features",
)
async def get_capabilities() -> CapabilitiesResponse:
    """Capabilities declaration endpoint.

    Returns information about what the parser supports, including:
    - Platform identifier
    - Supported source types (video, share_text)
    - Available features (transcript, metrics, etc.)

    Returns:
        CapabilitiesResponse with current capabilities
    """
    return CapabilitiesResponse(
        platform="youtube",
        supported_source_types=["video", "share_text"],
        features={
            "transcript": True,  # Available via yt-dlp
            "images": True,  # Thumbnail images are available
            "metrics": True,  # Available via yt-dlp (views, likes, comments)
            "authorProfile": True,  # Channel info available
            "deepAnalysis": False,  # Not in current scope
            "batchParse": False,  # Not in current scope
            "asyncParse": False,  # Not in current scope
        },
    )