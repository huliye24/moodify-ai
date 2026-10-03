/* GET /api/contribution/admin/metrics — contribution network dashboard metrics */

import { jsonError } from "@/lib/api";
import { requireAdminActor } from "@/lib/admin-auth";
import { getOverviewMetrics } from "@/lib/contribution-service";

export async function GET() {
  try {
    await requireAdminActor({} as Request);
    const metrics = await getOverviewMetrics();
    return Response.json({ metrics });
  } catch (error) { return jsonError(error); }
}
