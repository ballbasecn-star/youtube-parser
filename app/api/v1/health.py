"""Health check endpoint.

Provides a simple endpoint for health probes and availability checks.
"""

from fastapi import APIRouter

from app.contract.schemas import HealthResponse

router = APIRouter()


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check",
    description="Check if the service is healthy and available",
)
async def health_check() -> HealthResponse:
    """Health check endpoint.

    Returns a simple status indicating the service is running.
    Does not check upstream provider health.

    Returns:
        HealthResponse with status "UP"
    """
    return HealthResponse(status="UP")