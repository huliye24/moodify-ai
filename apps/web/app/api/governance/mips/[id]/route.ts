import { NextResponse } from "next/server";
import { mipRegistry } from "@/lib/mood/governance/registry.ts";

export const dynamic = "force-dynamic";

export async function GET(
  _req: Request,
  { params }: { params: { id: string } },
) {
  // Accept either id (MIP-NNN) or slug
  const decoded = decodeURIComponent(params.id);
  const mip =
    mipRegistry.publicDetailById(decoded) ?? mipRegistry.publicDetailById(
      // try slug fallback
      (mipRegistry.bySlug(decoded)?.id ?? ""),
    );
  if (!mip) {
    return NextResponse.json(
      { error: { code: "mip-not-found", message: "MIP not found" } },
      { status: 404 },
    );
  }
  return NextResponse.json({ mip });
}
