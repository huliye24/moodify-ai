import { NextResponse } from "next/server";
import { mipRegistry } from "@/lib/mood/governance/registry.ts";

export const dynamic = "force-dynamic";

export async function GET() {
  return NextResponse.json({
    mips: mipRegistry.publicList(),
    counts: mipRegistry.counts(),
  });
}
