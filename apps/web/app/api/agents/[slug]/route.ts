import { NextResponse } from "next/server";
import { agentRegistry } from "@/lib/mood/agents/registry.ts";

export const dynamic = "force-dynamic";

export async function GET(
  _req: Request,
  { params }: { params: { slug: string } },
) {
  const agent = agentRegistry.publicBySlug(params.slug);
  if (!agent) {
    return NextResponse.json(
      { error: { code: "agent-not-found", message: "agent not found" } },
      { status: 404 },
    );
  }
  return NextResponse.json({ agent });
}