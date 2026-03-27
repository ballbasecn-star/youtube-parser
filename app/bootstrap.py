"""Application bootstrap.

Handles application initialization, lifecycle events, and dependency setup.
"""

import structlog
from fastapi import FastAPI

from app.api.v1 import capabilities, health, parse
from app.shared.logging import setup_logging
from app.shared.settings import get_settings

logger = structlog.get_logger(__name__)


def create_app() -> FastAPI:
    """Create and configure the FastAPI application.

    Returns:
        Configured FastAPI application instance
    """
    settings = get_settings()

    # Setup logging
    setup_logging(settings)

    # Create FastAPI app
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="YouTube content parsing service for linker-platform",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        debug=settings.debug,
    )

    # Include routers
    app.include_router(health.router, prefix="/api/v1", tags=["health"])
    app.include_router(capabilities.router, prefix="/api/v1", tags=["capabilities"])
    app.include_router(parse.router, prefix="/api/v1", tags=["parse"])

    @app.on_event("startup")
    async def startup_event() -> None:
        """Application startup event handler."""
        logger.info(
            "application_started",
            app_name=settings.app_name,
            version=settings.app_version,
            debug=settings.debug,
        )

    @app.on_event("shutdown")
    async def shutdown_event() -> None:
        """Application shutdown event handler."""
        logger.info("application_shutdown")

    return app