"""FastAPI application entry point.

Run with: uvicorn app.main:app --reload
"""

import uvicorn

from app.bootstrap import create_app
from app.shared.settings import get_settings

# Create the application instance
app = create_app()


def main() -> None:
    """Run the application using uvicorn."""
    settings = get_settings()

    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_config=None,  # Use structlog configuration
    )


if __name__ == "__main__":
    main()