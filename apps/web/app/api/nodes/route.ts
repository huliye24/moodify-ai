import { NextResponse } from "next/server";
import { nodeRegistry } from "@/lib/mood/nodes/registry.ts";

export const dynamic = "force-dynamic";

export async function GET() {
  return NextResponse.json({
    nodes: nodeRegistry.publicList(),
    counts: nodeRegistry.counts(),
  });
}