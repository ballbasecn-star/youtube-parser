import { successResponse, createRequestId } from "@/lib/parser-contract";

export function GET() {
  const requestId = createRequestId();
  return successResponse(requestId, {
    status: "UP"
  });
}
