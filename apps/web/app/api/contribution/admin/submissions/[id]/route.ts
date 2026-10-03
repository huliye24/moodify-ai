/* GET /api/contribution/admin/submissions/[id] — admin submission detail */

import { jsonError } from "@/lib/api";
import { requireAdminActor } from "@/lib/admin-auth";
import { getSubmissionForAdmin } from "@/lib/contribution-service";

export async function GET(
  _request: Request,
  { params }: { params: Promise<{ id: string }> },
) {
  try {
    await requireAdminActor({} as Request);
    const { id } = await params;
    const submission = await getSubmissionForAdmin(id);
    if (!submission) return Response.json({ error: { code: "NOT_FOUND", message: "提交不存在" } }, { status: 404 });
    return Response.json({ submission });
  } catch (error) { return jsonError(error); }
}
