"""Parse endpoint.

The main endpoint for parsing YouTube content.
"""

import uuid

import structlog
from fastapi import APIRouter, HTTPException, status

from app.contract import (
    ApiEnvelope,
    ErrorCode,
    ParsedContentPayload,
    ParserParseRequest,
    error_response,
    success_response,
)
from app.youtube.application.parse_youtube_service import ParseYoutubeService

router = APIRouter()
logger = structlog.get_logger(__name__)

# Service instance (will be injected properly in production)
_parse_service: ParseYoutubeService | None = None


def get_parse_service() -> ParseYoutubeService:
    """Get or create the parse service instance.

    Returns:
        ParseYoutubeService instance
    """
    global _parse_service
    if _parse_service is None:
        _parse_service = ParseYoutubeService()
    return _parse_service


@router.post(
    "/parse",
    response_model=ApiEnvelope[ParsedContentPayload],
    summary="Parse YouTube content",
    description="Parse a YouTube video URL or share text and extract content information",
    responses={
        200: {"description": "Successfully parsed content"},
        400: {"description": "Invalid input or unsupported URL"},
        500: {"description": "Internal error"},
    },
)
async def parse_content(request: ParserParseRequest) -> ApiEnvelope[ParsedContentPayload]:
    """Parse YouTube content endpoint.

    Accepts a YouTube URL or share text and returns parsed content including:
    - Video metadata (title, author, description)
    - Transcript (if available and requested)
    - Metrics (if available)
    - Media information (thumbnails)

    Args:
        request: Parse request containing input and options

    Returns:
        ApiEnvelope with ParsedContentPayload on success,
        or error details on failure

    Raises:
        HTTPException: For input errors (400) or internal errors (500)
    """
    # Generate or use existing request ID
    request_id = request.request_id or f"req_{uuid.uuid4().hex[:12]}"

    # Set request context for logging
    structlog.contextvars.bind_contextvars(request_id=request_id)

    try:
        logger.info("parse_request_received", input=request.input.model_dump())

        # Get the parse service
        service = get_parse_service()

        # Execute parsing
        result = await service.parse(request, request_id)

        if result.is_err():
            error = result.unwrap_err()
            logger.warning(
                "parse_failed",
                error_code=error.code,
                error_message=error.message,
            )

            # Map error code to HTTP status
            http_status = error.code.http_status()

            raise HTTPException(
                status_code=http_status,
                detail=error_response(
                    code=error.code,
                    message=error.message,
                    request_id=request_id,
                    retryable=error.code.is_retryable(),
                ).model_dump(),
            )

        # Success - map to contract payload
        video = result.unwrap()
        payload = service.map_to_payload(video)
        logger.info(
            "parse_success",
            external_id=payload.external_id,
            has_title=payload.title is not None,
            has_transcript=payload.content.transcript is not None,
        )

        return success_response(data=payload, request_id=request_id)

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("parse_unexpected_error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_response(
                code=ErrorCode.INTERNAL_ERROR,
                message="An unexpected error occurred",
                request_id=request_id,
            ).model_dump(),
        )
    finally:
        structlog.contextvars.unbind_contextvars("request_id")