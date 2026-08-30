import { NextResponse } from "next/server";
import { networkObservatory } from "@/lib/mood/network/observatory.ts";

export const dynamic = "force-dynamic";

export async function GET(req: Request) {
  const url = new URL(req.url);
  const limit = Math.max(
    1,
    Math.min(100, Number(url.searchParams.get("limit") ?? "25")),
  );
  return NextResponse.json({
    events: networkObservatory.activity(limit),
    count: Math.min(limit, networkObservatory.activity(limit).length),
  });
}