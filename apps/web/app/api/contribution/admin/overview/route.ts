/* GET /api/contribution/admin/overview — admin contribution dashboard overview
 * Returns summary counts for the admin dashboard */

import { jsonError } from "@/lib/api";
import { requireAdminActor } from "@/lib/admin-auth";
import { getDb } from "@/db";
import { contributionTasks, contributionSubmissions, rewardEvents } from "@/db/schema";
import { eq, sql, inArray } from "drizzle-orm";

export async function GET() {
  try {
    await requireAdminActor({} as Request);
    const db = getDb();

    // Task counts by status
    const taskCounts = await db
      .select({ status: contributionTasks.status, total: sql<number>`COUNT(*)` })
      .from(contributionTasks)
      .groupBy(contributionTasks.status);

    // Submission counts by status
    const submissionCounts = await db
      .select({ status: contributionSubmissions.status, total: sql<number>`COUNT(*)` })
      .from(contributionSubmissions)
      .groupBy(contributionSubmissions.status);

    // Pending rewards
    const pendingRewards = await db
      .select({
        count: sql<number>`COUNT(*)`,
        total: sql<string>`COALESCE(SUM(${rewardEvents.rewardAtomic}), '0')`,
      })
      .from(rewardEvents)
      .where(eq(rewardEvents.status, "pending"));

    const overview = {
      tasks: {
        total: taskCounts.reduce((sum, t) => sum + Number(t.total), 0),
        draft: taskCounts.find((t) => t.status === "draft")?.total ?? 0,
        active: taskCounts.find((t) => t.status === "active")?.total ?? 0,
        paused: taskCounts.find((t) => t.status === "paused")?.total ?? 0,
        completed: taskCounts.find((t) => t.status === "completed")?.total ?? 0,
        archived: taskCounts.find((t) => t.status === "archived")?.total ?? 0,
      },
      submissions: {
        total: submissionCounts.reduce((sum, s) => sum + Number(s.total), 0),
        submitted: submissionCounts.find((s) => s.status === "submitted")?.total ?? 0,
        underReview: submissionCounts.find((s) => s.status === "under_review")?.total ?? 0,
        changesRequested: submissionCounts.find((s) => s.status === "changes_requested")?.total ?? 0,
        approved: submissionCounts.find((s) => s.status === "approved")?.total ?? 0,
        rejected: submissionCounts.find((s) => s.status === "rejected")?.total ?? 0,
        withdrawn: submissionCounts.find((s) => s.status === "withdrawn")?.total ?? 0,
      },
      pendingRewards: {
        count: pendingRewards[0]?.count ?? 0,
        totalAtomic: pendingRewards[0]?.total ?? "0",
      },
    };

    return Response.json({ overview });
  } catch (error) {
    return jsonError(error);
  }
}
