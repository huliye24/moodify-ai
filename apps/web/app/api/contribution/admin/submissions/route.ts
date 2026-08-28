/* GET /api/contribution/admin/submissions — review queue
 * Filter params: status, taskId, search, limit, offset */

import { jsonError } from "@/lib/api";
import { requireAdminActor } from "@/lib/admin-auth";
import { listAdminSubmissions } from "@/lib/contribution-service";
import { isSubmissionStatus } from "@/lib/contribution-config";

export async function GET(request: Request) {
  try {
    await requireAdminActor(request);
    const url = new URL(request.url);
    const rawStatus = url.searchParams.get("status");
    const status = rawStatus && isSubmissionStatus(rawStatus) ? rawStatus : undefined;
    const taskId = url.searchParams.get("taskId") || undefined;
    const search = url.searchParams.get("search") || undefined;
    const limit = Math.max(1, Math.min(Number(url.searchParams.get("limit") ?? 100), 500));
    const offset = Math.max(0, Number(url.searchParams.get("offset") ?? 0));
    const result = await listAdminSubmissions({ status, taskId, search, limit, offset });
    return Response.json(result);
  } catch (error) { return jsonError(error); }
}
