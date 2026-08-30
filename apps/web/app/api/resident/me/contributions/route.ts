import { NextResponse } from "next/server";
import { contributionRegistry } from "@/lib/mood/contribution/registry.ts";

export const dynamic = "force-dynamic";

/**
 * GET /api/resident/me/contributions
 *
 * Lists submissions owned by the authenticated Resident.
 * Uses X-Resident-Id header (bridge build); production must derive from session.
 */
export async function GET(req: Request) {
  const residentId = req.headers.get("x-resident-id");
  if (!residentId) {
    return NextResponse.json(
      {
        error: {
          code: "unauthenticated",
          message: "X-Resident-Id header required (bridge build)",
        },
      },
      { status: 401 },
    );
  }
  const subs = contributionRegistry.listSubmissionsForResident(residentId);
  return NextResponse.json({
    submissions: subs.map((s) => ({
      id: s.id,
      taskId: s.taskId,
      residentId: s.residentId,
      summary: s.summary,
      status: s.status,
      revision: s.revision,
      createdAt: s.createdAt,
      updatedAt: s.updatedAt,
    })),
    count: subs.length,
  });
}