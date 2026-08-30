import { NextResponse } from "next/server";
import { networkObservatory } from "../../../../lib/mood/network/observatory.ts";

export const dynamic = "force-dynamic";

export async function GET() {
  return NextResponse.json(networkObservatory.overview());
}