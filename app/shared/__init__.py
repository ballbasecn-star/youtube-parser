"""Shared utilities and configuration.

This module contains shared components used across the application.
"""

from app.shared.logging import get_logger, setup_logging
from app.shared.settings import Settings, get_settings

__all__ = [
    "Settings",
    "get_settings",
    "get_logger",
    "setup_logging",
]