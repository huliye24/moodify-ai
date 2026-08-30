/* POST /api/contribution/admin/submissions/[id]/transition — admin review action
 * Body: { action: "under_review" | "changes_requested" | "approved" | "rejected", reason, pointsDelta?, rewardMood? } */

import { jsonError } from "@/lib/api";
import { requireAdminActor } from "@/lib/admin-auth";
import { transitionSubmission } from "@/lib/contribution-service";
import { isSubmissionStatus } from "@/lib/contribution-config";

export async function POST(
  request: Request,
  { params }: { params: Promise<{ id: string }> },
) {
  try {
    const admin = await requireAdminActor(request);
    const { id } = await params;
    const body = (await request.json().catch(() => null)) as Record<string, unknown> | null;
    if (!body) throw new Error("请求体格式不正确");
    const action = typeof body.action === "string" ? body.action : "";
    if (!isSubmissionStatus(action)) {
      return Response.json({ error: { code: "ACTION_INVALID", message: "action 不合法" } }, { status: 400 });
    }
    const submission = await transitionSubmission(
      id,
      admin.displayId,
      action,
      {
        reason: typeof body.reason === "string" ? body.reason : "",
        pointsDelta: typeof body.pointsDelta === "number" ? body.pointsDelta : undefined,
        rewardMood: body.rewardMood as string | null | undefined,
      },
    );
    return Response.json({ submission });
  } catch (error) { return jsonError(error); }
}
