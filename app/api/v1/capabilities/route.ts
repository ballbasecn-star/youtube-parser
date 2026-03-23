import { NextResponse } from "next/server";

export function GET() {
  return NextResponse.json({
    service: "youtube-parser",
    parserType: "YOUTUBE",
    version: "0.1.0",
    capabilities: {
      parseUrl: false,
      parseShareText: false,
      transcript: false,
      metadata: true,
      health: true
    }
  });
}
