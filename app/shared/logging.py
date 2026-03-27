"""Structured logging configuration using structlog.

Provides JSON logging for production and human-readable output for development.
"""

import logging
import sys

import structlog
from structlog.types import Processor

from app.shared.settings import Settings


def setup_logging(settings: Settings | None = None) -> None:
    """Configure structured logging.

    Args:
        settings: Application settings. If None, uses default settings.
    """
    if settings is None:
        from app.shared.settings import get_settings

        settings = get_settings()

    # Choose processors based on log format
    if settings.log_format == "console":
        # Human-readable output for development
        processors: list[Processor] = [
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.dev.set_exc_info,
            structlog.dev.ConsoleRenderer(colors=True),
        ]
    else:
        # JSON output for production
        processors = [
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ]

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(
            logging.getLevelName(settings.log_level)
        ),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Configure standard logging to use structlog
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=logging.getLevelName(settings.log_level),
    )


def get_logger(name: str | None = None) -> structlog.stdlib.BoundLogger:
    """Get a structured logger instance.

    Args:
        name: Logger name, typically __name__

    Returns:
        A structlog logger instance
    """
    return structlog.get_logger(name)