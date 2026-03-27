"""Error codes for youtube-parser.

This module defines all error codes that the parser service can return.
These codes are designed for programmatic handling by calling services.
"""

from enum import Enum


class ErrorCode(str, Enum):
    """Unified error codes for parser services.

    Categories:
    - Input errors: INVALID_INPUT, UNSUPPORTED_URL
    - Upstream access errors: AUTH_REQUIRED, RATE_LIMITED, PARSER_TIMEOUT
    - Upstream structure errors: UPSTREAM_CHANGED
    - Internal errors: INTERNAL_ERROR
    """

    # Input errors (4xx equivalent)
    INVALID_INPUT = "INVALID_INPUT"
    UNSUPPORTED_URL = "UNSUPPORTED_URL"

    # Upstream access errors
    AUTH_REQUIRED = "AUTH_REQUIRED"
    RATE_LIMITED = "RATE_LIMITED"
    PARSER_TIMEOUT = "PARSER_TIMEOUT"

    # Upstream structure errors
    UPSTREAM_CHANGED = "UPSTREAM_CHANGED"

    # Internal errors (5xx equivalent)
    INTERNAL_ERROR = "INTERNAL_ERROR"

    def is_retryable(self) -> bool:
        """Check if this error type is retryable.

        Returns:
            True if the error is transient and can be retried
        """
        retryable_codes = {
            ErrorCode.RATE_LIMITED,
            ErrorCode.PARSER_TIMEOUT,
        }
        return self in retryable_codes

    def http_status(self) -> int:
        """Get the recommended HTTP status code for this error.

        Returns:
            HTTP status code
        """
        status_map = {
            ErrorCode.INVALID_INPUT: 400,
            ErrorCode.UNSUPPORTED_URL: 400,
            ErrorCode.AUTH_REQUIRED: 401,
            ErrorCode.RATE_LIMITED: 429,
            ErrorCode.PARSER_TIMEOUT: 504,
            ErrorCode.UPSTREAM_CHANGED: 500,
            ErrorCode.INTERNAL_ERROR: 500,
        }
        return status_map.get(self, 500)


class WarningCode(str, Enum):
    """Warning codes for partial success scenarios.

    Warnings indicate successful parsing with incomplete data.
    They should not cause the request to fail.
    """

    TRANSCRIPT_UNAVAILABLE = "TRANSCRIPT_UNAVAILABLE"
    METRICS_UNAVAILABLE = "METRICS_UNAVAILABLE"
    DESCRIPTION_PARTIAL = "DESCRIPTION_PARTIAL"
    AUTHOR_PARTIAL = "AUTHOR_PARTIAL"