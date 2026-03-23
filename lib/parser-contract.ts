import { NextResponse } from "next/server";
import type { NextResponse as TypedNextResponse } from "next/server";

export const PARSER_VERSION = "0.1.0";

export interface ApiErrorPayload {
  code: string;
  message: string;
  retryable: boolean;
  details?: Record<string, unknown>;
}

export interface EnvelopeMeta {
  requestId: string;
  parserVersion: string;
}

export interface ApiEnvelope<T> {
  success: boolean;
  data: T | null;
  error: ApiErrorPayload | null;
  meta: EnvelopeMeta;
}

export interface ParserParseRequest {
  requestId?: string;
  input?: {
    sourceText?: string;
    sourceUrl?: string;
    platformHint?: string;
  };
  options?: {
    fetchTranscript?: boolean;
    fetchMedia?: boolean;
    fetchMetrics?: boolean;
    deepAnalysis?: boolean;
    languageHint?: string;
  };
}

export function createRequestId() {
  return `req_${crypto.randomUUID().replaceAll("-", "")}`;
}

export function buildSuccessEnvelope<T>(requestId: string, data: T): ApiEnvelope<T> {
  return {
    success: true,
    data,
    error: null,
    meta: {
      requestId,
      parserVersion: PARSER_VERSION
    }
  };
}

export function buildErrorEnvelope(
  requestId: string,
  error: ApiErrorPayload
): ApiEnvelope<null> {
  return {
    success: false,
    data: null,
    error,
    meta: {
      requestId,
      parserVersion: PARSER_VERSION
    }
  };
}

export function successResponse<T>(requestId: string, data: T): TypedNextResponse<ApiEnvelope<T>> {
  return NextResponse.json(buildSuccessEnvelope(requestId, data));
}

export function errorResponse(
  requestId: string,
  status: number,
  error: ApiErrorPayload
): TypedNextResponse<ApiEnvelope<null>> {
  return NextResponse.json(buildErrorEnvelope(requestId, error), { status });
}
