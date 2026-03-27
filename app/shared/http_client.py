"""HTTP client configuration.

Provides a shared httpx async client with proper configuration.
"""

from contextlib import asynccontextmanager

import httpx

from app.shared.settings import Settings, get_settings


@asynccontextmanager
async def get_http_client(settings: Settings | None = None):
    """Get an HTTP client context manager.

    Args:
        settings: Application settings. If None, uses default settings.

    Yields:
        Configured httpx AsyncClient
    """
    if settings is None:
        settings = get_settings()

    async with httpx.AsyncClient(
        timeout=httpx.Timeout(
            connect=settings.http_connect_timeout,
            read=settings.http_timeout,
            write=settings.http_timeout,
            pool=settings.http_connect_timeout,
        ),
        follow_redirects=True,
        headers={
            "User-Agent": f"{settings.app_name}/{settings.app_version}",
            "Accept-Language": "en-US,en;q=0.9",
        },
    ) as client:
        yield client