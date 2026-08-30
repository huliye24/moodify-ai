import { NextResponse } from "next/server";
import { contributionRegistry } from "@/lib/mood/contribution/registry.ts";

export const dynamic = "force-dynamic";

/**
 * GET /api/contribution/review/queue
 *
 * Reviewer queue. Public-safe: includes only summary + status, not reviewer notes.
 */
export async function GET() {
  const queue = contributionRegistry.listReviewQueue();
  return NextResponse.json({
    submissions: queue.map((s) => ({
      id: s.id,
      taskId: s.taskId,
      residentId: s.residentId,
      summary: s.summary,
      status: s.status,
      revision: s.revision,
      createdAt: s.createdAt,
      updatedAt: s.updatedAt,
    })),
    count: queue.length,
  });
}