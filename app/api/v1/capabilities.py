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
            "transcript": False,  # Will be enabled when transcript provider is ready
            "images": True,  # Thumbnail images are available
            "metrics": False,  # Will be enabled when metrics provider is ready
            "authorProfile": False,  # Will be enabled when author provider is ready
            "deepAnalysis": False,  # Not in current scope
            "batchParse": False,  # Not in current scope
            "asyncParse": False,  # Not in current scope
        },
    )