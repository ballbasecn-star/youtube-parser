"""Contract module for youtube-parser.

This module contains the unified parser contract definitions
including envelope, schemas, and error codes.
"""

from app.contract.envelope import ApiEnvelope, error_response, success_response
from app.contract.error_codes import ErrorCode
from app.contract.schemas import (
    AuthorInfo,
    ContentInfo,
    CoverImage,
    MediaInfo,
    MetricsInfo,
    Options,
    ParsedContentPayload,
    ParserParseRequest,
    ParserInput,
    Warning,
)

__all__ = [
    # Envelope
    "ApiEnvelope",
    "success_response",
    "error_response",
    # Error codes
    "ErrorCode",
    # Schemas
    "ParserParseRequest",
    "ParserInput",
    "Options",
    "ParsedContentPayload",
    "AuthorInfo",
    "ContentInfo",
    "CoverImage",
    "MediaInfo",
    "MetricsInfo",
    "Warning",
]