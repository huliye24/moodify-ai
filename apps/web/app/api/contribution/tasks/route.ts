/* GET /api/contribution/tasks — public task catalog (active tasks only)
 * POST /api/contribution/tasks — admin: create a new task */

import { jsonError } from "@/lib/api";
import { requireAdminActor } from "@/lib/admin-auth";
import { listPublicTasks, createTask } from "@/lib/contribution-service";

export async function GET() {
  try {
    const tasks = await listPublicTasks();
    return Response.json({ tasks });
  } catch (error) { return jsonError(error); }
}

export async function POST(request: Request) {
  try {
    const admin = await requireAdminActor(request);
    const body = (await request.json().catch(() => null)) as Record<string, unknown> | null;
    if (!body) throw new Error("请求体格式不正确");
    const task = await createTask(
      {
        slug: typeof body.slug === "string" ? body.slug : "",
        title: typeof body.title === "string" ? body.title : "",
        summary: body.summary as string | undefined,
        description: body.description as string | undefined,
        category: typeof body.category === "string" ? body.category : "",
        status: body.status as "draft" | "active" | undefined,
        requirements: body.requirements as string | undefined,
        evidenceInstructions: body.evidenceInstructions as string | undefined,
        rewardPointsDefault: body.rewardPointsDefault as number | undefined,
        rewardMoodDefault: body.rewardMoodDefault as string | undefined,
        deadline: body.deadline as string | undefined,
        maxApprovals: body.maxApprovals as number | undefined,
        allowDuplicateSubmissions: body.allowDuplicateSubmissions as boolean | undefined,
      },
      admin.displayId,
    );
    return Response.json({ task }, { status: 201 });
  } catch (error) { return jsonError(error); }
}
