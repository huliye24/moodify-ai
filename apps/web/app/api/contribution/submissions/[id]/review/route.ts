import { NextResponse } from "next/server";
import { contributionRegistry } from "../../../../../lib/mood/contribution/registry.ts";

export const dynamic = "force-dynamic";

/**
 * POST /api/contribution/submissions/[id]/review
 *
 * Reviewer-only action. Requires X-Resident-Id header.
 *
 * Body: { decision: "approve" | "request-changes" | "reject", note?: string }
 */
export async function POST(
  req: Request,
  { params }: { params: { id: string } },
) {
  const reviewerResidentId = req.headers.get("x-resident-id");
  if (!reviewerResidentId) {
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

  let body: unknown;
  try {
    body = await req.json();
  } catch {
    return NextResponse.json(
      { error: { code: "invalid-json", message: "invalid JSON body" } },
      { status: 400 },
    );
  }
  if (!body || typeof body !== "object") {
    return NextResponse.json(
      { error: { code: "invalid-body", message: "invalid body" } },
      { status: 400 },
    );
  }
  const input = body as Record<string, unknown>;
  const decision = input.decision;
  if (
    decision !== "approve" &&
    decision !== "request-changes" &&
    decision !== "reject"
  ) {
    return NextResponse.json(
      {
        error: {
          code: "invalid-decision",
          message: 'decision must be "approve" | "request-changes" | "reject"',
        },
      },
      { status: 400 },
    );
  }

  const result = contributionRegistry.review({
    submissionId: params.id,
    decision: decision as "approve" | "request-changes" | "reject",
    reviewerResidentId,
    note: input.note as string | undefined,
  });
  if (!result.ok) {
    const status = result.reason?.startsWith("INV-016-02") ? 403 : 400;
    return NextResponse.json(
      { error: { code: "review-failed", message: result.reason ?? "review failed" } },
      { status },
    );
  }
  // INV-016-10: reviewer note NEVER appears in public response.
  const sub = result.submission!;
  return NextResponse.json({
    submission: {
      id: sub.id,
      taskId: sub.taskId,
      residentId: sub.residentId,
      summary: sub.summary,
      status: sub.status,
      revision: sub.revision,
      reviewedByResidentId: sub.reviewedByResidentId,
      reviewedAt: sub.reviewedAt,
      createdAt: sub.createdAt,
      updatedAt: sub.updatedAt,
    },
    reputationEventId: result.reputationEventId,
    pendingRewardId: result.pendingRewardId,
    auditEventIds: result.auditEventIds,
  });
}