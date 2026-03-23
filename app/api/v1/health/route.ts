import { NextResponse } from "next/server";

export function GET() {
  return NextResponse.json({
    service: "youtube-parser",
    status: "UP",
    checkedAt: new Date().toISOString()
  });
}
