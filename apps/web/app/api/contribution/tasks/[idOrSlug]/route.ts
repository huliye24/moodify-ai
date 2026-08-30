/* GET /api/contribution/tasks/[idOrSlug] — public single task (404 if hidden/draft) */

import { jsonError } from "@/lib/api";
import { getPublicTask } from "@/lib/contribution-service";

export async function GET(
  _request: Request,
  { params }: { params: Promise<{ idOrSlug: string }> },
) {
  try {
    const { idOrSlug } = await params;
    const task = await getPublicTask(idOrSlug);
    if (!task) return Response.json({ error: { code: "NOT_FOUND", message: "任务不存在" } }, { status: 404 });
    return Response.json({ task });
  } catch (error) { return jsonError(error); }
}
