/* GET /api/contribution/admin/tasks — admin task list */

import { jsonError } from "@/lib/api";
import { requireAdminActor } from "@/lib/admin-auth";
import { listAdminTasks } from "@/lib/contribution-service";

export async function GET() {
  try {
    await requireAdminActor({} as Request);
    const tasks = await listAdminTasks();
    return Response.json({ tasks });
  } catch (error) { return jsonError(error); }
}
