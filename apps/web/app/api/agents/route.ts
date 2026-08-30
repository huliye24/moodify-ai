import { NextResponse } from "next/server";
import { agentRegistry } from "../../../../lib/mood/agents/registry.ts";

export const dynamic = "force-dynamic";

export async function GET() {
  const agents = agentRegistry.publicList();
  const counts = agentRegistry.counts();
  return NextResponse.json({
    agents,
    counts,
  });
}