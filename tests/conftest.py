"""Pytest configuration for YouTube parser tests."""

import pytest


@pytest.fixture(autouse=True)
def reset_contextvars():
    """Reset structlog contextvars before each test."""
    import structlog.contextvars

    structlog.contextvars.clear_contextvars()
    yield
    structlog.contextvars.clear_contextvars()