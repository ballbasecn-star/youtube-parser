import { createRequestId, successResponse } from "@/lib/parser-contract";

export function GET() {
  const requestId = createRequestId();

  return successResponse(requestId, {
    platform: "youtube",
    supportedSourceTypes: ["video", "share_text"],
    features: {
      transcript: false,
      images: false,
      metrics: false,
      authorProfile: false,
      deepAnalysis: false,
      batchParse: false,
      asyncParse: false
    }
  });
}
