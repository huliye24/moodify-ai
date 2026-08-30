/* POST /api/contribution/admin/submissions/[id]/note — append internal note (no status change) */

import { jsonError } from "@/lib/api";
import { requireAdminActor } from "@/lib/admin-auth";
import { appendAdminNote } from "@/lib/contribution-service";

export async function POST(
  request: Request,
  { params }: { params: Promise<{ id: string }> },
) {
  try {
    const admin = await requireAdminActor(request);
    const { id } = await params;
    const body = (await request.json().catch(() => null)) as Record<string, unknown> | null;
    if (!body) throw new Error("请求体格式不正确");
    const submission = await appendAdminNote(
      id,
      admin.displayId,
      typeof body.body === "string" ? body.body : "",
    );
    return Response.json({ submission });
  } catch (error) { return jsonError(error); }
}
