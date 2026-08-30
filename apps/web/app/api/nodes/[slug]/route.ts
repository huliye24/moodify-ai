import { NextResponse } from "next/server";
import { nodeRegistry } from "@/lib/mood/nodes/registry.ts";

export const dynamic = "force-dynamic";

export async function GET(
  _req: Request,
  { params }: { params: { slug: string } },
) {
  const node = nodeRegistry.publicBySlug(params.slug);
  if (!node) {
    return NextResponse.json(
      { error: { code: "node-not-found", message: "node not found" } },
      { status: 404 },
    );
  }
  return NextResponse.json({ node });
}