"""Unified API envelope for all parser responses.

This module defines the standard response wrapper that all parser
services must use for consistent API responses.
"""

from typing import Generic, TypeVar

from pydantic import BaseModel, Field

from app.contract.error_codes import ErrorCode

T = TypeVar("T")

PARSER_VERSION = "0.1.0"


class ErrorDetail(BaseModel):
    """Error detail structure for failed responses."""

    code: ErrorCode = Field(..., description="Error code for programmatic handling")
    message: str = Field(..., description="Human-readable error message")
    retryable: bool = Field(default=False, description="Whether the request can be retried")


class ResponseMeta(BaseModel):
    """Metadata included in every response."""

    request_id: str = Field(..., alias="requestId", description="Unique request identifier")
    parser_version: str = Field(
        default=PARSER_VERSION,
        alias="parserVersion",
        description="Current parser version",
    )

    model_config = {"populate_by_name": True}


class ApiEnvelope(BaseModel, Generic[T]):
    """Unified API response envelope.

    All parser endpoints must return this structure for consistency.

    Success example:
    {
        "success": true,
        "data": {...},
        "error": null,
        "meta": {"requestId": "...", "parserVersion": "..."}
    }

    Error example:
    {
        "success": false,
        "data": null,
        "error": {"code": "...", "message": "...", "retryable": false},
        "meta": {"requestId": "...", "parserVersion": "..."}
    }
    """

    success: bool = Field(..., description="Whether the request succeeded")
    data: T | None = Field(default=None, description="Response data on success")
    error: ErrorDetail | None = Field(default=None, description="Error details on failure")
    meta: ResponseMeta = Field(..., description="Response metadata")

    model_config = {"populate_by_name": True}


def success_response(data: T, request_id: str) -> ApiEnvelope[T]:
    """Create a successful response envelope.

    Args:
        data: The response data
        request_id: The request identifier

    Returns:
        A successful ApiEnvelope containing the data
    """
    return ApiEnvelope(
        success=True,
        data=data,
        error=None,
        meta=ResponseMeta(request_id=request_id),
    )


def error_response(
    code: ErrorCode,
    message: str,
    request_id: str,
    retryable: bool = False,
) -> ApiEnvelope[None]:
    """Create an error response envelope.

    Args:
        code: The error code
        message: Human-readable error message
        request_id: The request identifier
        retryable: Whether the request can be retried

    Returns:
        An error ApiEnvelope
    """
    return ApiEnvelope(
        success=False,
        data=None,
        error=ErrorDetail(
            code=code,
            message=message,
            retryable=retryable,
        ),
        meta=ResponseMeta(request_id=request_id),
    )