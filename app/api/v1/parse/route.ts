import {
  createRequestId,
  errorResponse,
  successResponse,
  type ParserParseRequest
} from "@/lib/parser-contract";
import { parseYoutubeSource } from "@/lib/youtube-parse";

export async function POST(request: Request) {
  let requestBody: ParserParseRequest | null = null;

  try {
    requestBody = (await request.json()) as ParserParseRequest;
  } catch {
    const requestId = createRequestId();
    return errorResponse(requestId, 400, {
      code: "INVALID_INPUT",
      message: "Request body must be valid JSON.",
      retryable: false
    });
  }

  const requestId = requestBody.requestId?.trim() || createRequestId();
  const sourceText = requestBody.input?.sourceText?.trim();
  const sourceUrl = requestBody.input?.sourceUrl?.trim();

  if (!sourceText && !sourceUrl) {
    return errorResponse(requestId, 400, {
      code: "INVALID_INPUT",
      message: "sourceText and sourceUrl cannot both be empty.",
      retryable: false
    });
  }

  try {
    const result = parseYoutubeSource({
      sourceText,
      sourceUrl,
      languageHint: requestBody.options?.languageHint?.trim()
    });

    return successResponse(requestId, result.payload);
  } catch (error) {
    if (error instanceof Error) {
      if (error.message === "MISSING_SOURCE") {
        return errorResponse(requestId, 400, {
          code: "INVALID_INPUT",
          message: "Unable to resolve a YouTube URL from the provided input.",
          retryable: false
        });
      }

      if (error.message === "INVALID_URL") {
        return errorResponse(requestId, 400, {
          code: "INVALID_INPUT",
          message: "The resolved sourceUrl is not a valid URL.",
          retryable: false
        });
      }

      if (error.message === "UNSUPPORTED_URL") {
        return errorResponse(requestId, 400, {
          code: "UNSUPPORTED_URL",
          message: "The provided URL is not a supported YouTube video URL.",
          retryable: false
        });
      }
    }

    return errorResponse(requestId, 500, {
      code: "INTERNAL_ERROR",
      message: "Unexpected parser error.",
      retryable: true
    });
  }
}
