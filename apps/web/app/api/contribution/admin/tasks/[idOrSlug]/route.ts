/* GET /api/contribution/admin/tasks/[idOrSlug] — admin task detail
 * PUT /api/contribution/admin/tasks/[idOrSlug] — update task */

import { jsonError } from "@/lib/api";
import { requireAdminActor } from "@/lib/admin-auth";
import { getAdminTask, updateTask } from "@/lib/contribution-service";

export async function GET(
  _request: Request,
  { params }: { params: Promise<{ idOrSlug: string }> },
) {
  try {
    await requireAdminActor({} as Request);
    const { idOrSlug } = await params;
    const task = await getAdminTask(idOrSlug);
    if (!task) return Response.json({ error: { code: "NOT_FOUND", message: "任务不存在" } }, { status: 404 });
    return Response.json({ task });
  } catch (error) { return jsonError(error); }
}

export async function PUT(
  request: Request,
  { params }: { params: Promise<{ idOrSlug: string }> },
) {
  try {
    const admin = await requireAdminActor(request);
    const { idOrSlug } = await params;
    const body = (await request.json().catch(() => null)) as Record<string, unknown> | null;
    if (!body) throw new Error("请求体格式不正确");
    const task = await updateTask(
      idOrSlug,
      {
        title: body.title as string | undefined,
        summary: body.summary as string | undefined,
        description: body.description as string | undefined,
        category: body.category as string | undefined,
        status: body.status as "draft" | "active" | "paused" | "completed" | "archived" | undefined,
        requirements: body.requirements as string | undefined,
        evidenceInstructions: body.evidenceInstructions as string | undefined,
        rewardPointsDefault: body.rewardPointsDefault as number | undefined,
        rewardMoodDefault: body.rewardMoodDefault as string | null | undefined,
        deadline: body.deadline as string | null | undefined,
        maxApprovals: body.maxApprovals as number | null | undefined,
        allowDuplicateSubmissions: body.allowDuplicateSubmissions as boolean | undefined,
      },
      admin.displayId,
    );
    return Response.json({ task });
  } catch (error) { return jsonError(error); }
}
