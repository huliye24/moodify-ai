import { getDb } from "@/db";
import { sql } from "drizzle-orm";
import { users, contributionTasks, contributionSubmissions, reputationEvents, rewardEvents } from "@/db/schema";

export async function GET(request: Request) {
  try {
    const db = getDb();

    // Metrics timestamp
    const generatedAt = new Date().toISOString();

    // Network health check
    const healthStatus = await getNetworkHealth(db);

    // Calculate all metrics
    const [
      residentMetrics,
      taskMetrics,
      submissionMetrics,
      reputationMetrics,
      rewardMetrics
    ] = await Promise.all([
      getResidentMetrics(db),
      getTaskMetrics(db),
      getSubmissionMetrics(db),
      getReputationMetrics(db),
      getRewardMetrics(db)
    ]);

    // Generate network overview response
    const overview = {
      status: healthStatus,
      generatedAt,
      metrics: {
        // Residents
        residents: {
          value: residentMetrics.active,
          state: "available" as const,
          source: "users",
          updatedAt: residentMetrics.updatedAt,
          definition: "Active residents with verified identity"
        },
        totalResidents: {
          value: residentMetrics.total,
          state: "available" as const,
          source: "users",
          updatedAt: residentMetrics.updatedAt,
          definition: "Total registered residents"
        },
        newResidents: {
          value: residentMetrics.new30d,
          state: "available" as const,
          source: "users",
          updatedAt: residentMetrics.updatedAt,
          definition: "New residents in last 30 days"
        },

        // Contributors
        contributors: {
          value: residentMetrics.contributors,
          state: "available" as const,
          source: "contributionSubmissions",
          updatedAt: submissionMetrics.updatedAt,
          definition: "Active contributors with submitted work"
        },
        approvedContributors: {
          value: residentMetrics.approvedContributors,
          state: "available" as const,
          source: "contributionSubmissions",
          updatedAt: submissionMetrics.updatedAt,
          definition: "Contributors with approved work"
        },

        // Tasks
        openTasks: {
          value: taskMetrics.active,
          state: "available" as const,
          source: "contributionTasks",
          updatedAt: taskMetrics.updatedAt,
          definition: "Currently open for submissions"
        },
        totalTasks: {
          value: taskMetrics.total,
          state: "available" as const,
          source: "contributionTasks",
          updatedAt: taskMetrics.updatedAt,
          definition: "All-time task count"
        },
        draftTasks: {
          value: taskMetrics.draft,
          state: "available" as const,
          source: "contributionTasks",
          updatedAt: taskMetrics.updatedAt,
          definition: "Tasks not yet published"
        },
        pausedTasks: {
          value: taskMetrics.paused,
          state: "available" as const,
          source: "contributionTasks",
          updatedAt: taskMetrics.updatedAt,
          definition: "Temporarily closed tasks"
        },

        // Submissions
        submissions: {
          value: submissionMetrics.total,
          state: "available" as const,
          source: "contributionSubmissions",
          updatedAt: submissionMetrics.updatedAt,
          definition: "All-time submission count"
        },
        pendingReview: {
          value: submissionMetrics.pending,
          state: "available" as const,
          source: "contributionSubmissions",
          updatedAt: submissionMetrics.updatedAt,
          definition: "Submissions awaiting review"
        },
        approvedContributions: {
          value: submissionMetrics.approved,
          state: "available" as const,
          source: "contributionSubmissions",
          updatedAt: submissionMetrics.updatedAt,
          definition: "Successfully approved contributions"
        },
        rejectedSubmissions: {
          value: submissionMetrics.rejected,
          state: "available" as const,
          source: "contributionSubmissions",
          updatedAt: submissionMetrics.updatedAt,
          definition: "Rejected submissions"
        },
        withdrawnSubmissions: {
          value: submissionMetrics.withdrawn,
          state: "available" as const,
          source: "contributionSubmissions",
          updatedAt: submissionMetrics.updatedAt,
          definition: "Withdrawn submissions"
        },

        // Reputation
        reputationEvents: {
          value: reputationMetrics.totalEvents,
          state: "available" as const,
          source: "reputationEvents",
          updatedAt: reputationMetrics.updatedAt,
          definition: "Total reputation events"
        },
        totalReputation: {
          value: reputationMetrics.totalPoints,
          state: "available" as const,
          source: "reputationEvents",
          updatedAt: reputationMetrics.updatedAt,
          definition: "Total reputation points issued"
        },

        // Rewards
        pendingRewards: {
          value: rewardMetrics.pending,
          state: rewardMetrics.pending > 0 ? "available" : "unavailable",
          source: "rewardEvents",
          updatedAt: rewardMetrics.updatedAt,
          definition: "Awards awaiting distribution"
        },
        pendingRewardMood: {
          value: rewardMetrics.pendingMood,
          state: rewardMetrics.pendingMood > 0 ? "available" : "unavailable",
          source: "rewardEvents",
          updatedAt: rewardMetrics.updatedAt,
          definition: "Total MOOD pending distribution"
        },
        cancelledRewards: {
          value: rewardMetrics.cancelled,
          state: "available" as const,
          source: "rewardEvents",
          updatedAt: rewardMetrics.updatedAt,
          definition: "Cancelled rewards"
        },

        // Future metrics (coming soon)
        agents: {
          value: null,
          state: "coming-soon" as const,
          source: "MOOD-AGENTS-018",
          definition: "Registered agents (Package 018)"
        },
        nodes: {
          value: null,
          state: "coming-soon" as const,
          source: "MOOD-NODES-019",
          definition: "Network nodes (Package 019)"
        },
        governance: {
          value: null,
          state: "coming-soon" as const,
          source: "MOOD-GOVERNANCE-020",
          definition: "Governance proposals (Package 020)"
        },
        treasury: {
          value: null,
          state: "available" as const,
          source: "MOOD-TREASURY-021",
          definition: "Treasury status (Package 021)",
          subMetrics: await getTreasurySubMetrics(),
        }
      }
    };

    return Response.json(overview);
  } catch (error) {
    console.error("Network overview API error:", error);
    return Response.json(
      {
        error: "Failed to fetch network overview",
        status: "error"
      },
      { status: 500 }
    );
  }
}

// Helper functions for metrics calculation

async function getResidentMetrics(db: ReturnType<typeof getDb>) {
  const now = new Date();
  const thirtyDaysAgo = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000);

  const [activeCount, totalCount, newCount] = await Promise.all([
    // Active residents (status = 'active')
    db.select({ count: sql<number>`COUNT(*)` })
      .from(users)
      .where(sql`${users.status} = 'active'`),

    // Total residents
    db.select({ count: sql<number>`COUNT(*)` })
      .from(users),

    // New residents (last 30 days)
    db.select({ count: sql<number>`COUNT(*)` })
      .from(users)
      .where(sql`${users.createdAt} >= ${thirtyDaysAgo.toISOString()}`)
  ]);

  // Active contributors (distinct users with active submissions)
  const contributorCount = await db
    .select({
      count: sql<number>`COUNT(DISTINCT ${contributionSubmissions.userId})`
    })
    .from(contributionSubmissions)
    .join(users, sql`${contributionSubmissions.userId} = ${users.id}`)
    .where(sql`${users.status} = 'active' AND ${contributionSubmissions.status} IN ('submitted', 'under_review', 'changes_requested', 'approved')`);

  // Approved contributors (distinct users with approved submissions)
  const approvedContributorCount = await db
    .select({
      count: sql<number>`COUNT(DISTINCT ${contributionSubmissions.userId})`
    })
    .from(contributionSubmissions)
    .join(users, sql`${contributionSubmissions.userId} = ${users.id}`)
    .where(sql`${users.status} = 'active' AND ${contributionSubmissions.status} = 'approved'`);

  return {
    active: activeCount[0].count,
    total: totalCount[0].count,
    new30d: newCount[0].count,
    contributors: contributorCount[0].count,
    approvedContributors: approvedContributorCount[0].count,
    updatedAt: now.toISOString()
  };
}

async function getTaskMetrics(db: ReturnType<typeof getDb>) {
  const now = new Date();

  const taskCounts = await db
    .select({
      status: contributionTasks.status,
      total: sql<number>`COUNT(*)`
    })
    .from(contributionTasks)
    .groupBy(contributionTasks.status);

  const metrics: Record<string, number> = taskCounts.reduce((acc, row) => {
    acc[row.status] = row.total;
    return acc;
  }, {} as Record<string, number>);

  return {
    active: metrics.active || 0,
    total: metrics.active + metrics.draft + metrics.paused + metrics.completed || 0,
    draft: metrics.draft || 0,
    paused: metrics.paused || 0,
    completed: metrics.completed || 0,
    updatedAt: now.toISOString()
  };
}

async function getSubmissionMetrics(db: ReturnType<typeof getDb>) {
  const now = new Date();

  const submissionCounts = await db
    .select({
      status: contributionSubmissions.status,
      total: sql<number>`COUNT(*)`
    })
    .from(contributionSubmissions)
    .groupBy(contributionSubmissions.status);

  const metrics: Record<string, number> = submissionCounts.reduce((acc, row) => {
    acc[row.status] = row.total;
    return acc;
  }, {} as Record<string, number>);

  return {
    total: metrics.submitted + metrics.under_review + metrics.changes_requested + metrics.approved + metrics.rejected + metrics.withdrawn || 0,
    pending: (metrics.submitted || 0) + (metrics.under_review || 0) + (metrics.changes_requested || 0),
    approved: metrics.approved || 0,
    rejected: metrics.rejected || 0,
    withdrawn: metrics.withdrawn || 0,
    updatedAt: now.toISOString()
  };
}

async function getReputationMetrics(db: ReturnType<typeof getDb>) {
  const now = new Date();

  const reputationStats = await db
    .select({
      totalEvents: sql<number>`COUNT(*)`,
      totalPoints: sql<number>`COALESCE(SUM(pointsDelta), 0)`
    })
    .from(reputationEvents);

  return {
    totalEvents: reputationStats[0].totalEvents || 0,
    totalPoints: reputationStats[0].totalPoints || 0,
    updatedAt: now.toISOString()
  };
}

async function getRewardMetrics(db: ReturnType<typeof getDb>) {
  const now = new Date();

  const [rewardCounts, pendingRewards] = await Promise.all([
    // Reward counts by status
    db.select({
      status: rewardEvents.status,
      total: sql<number>`COUNT(*)`
    })
    .from(rewardEvents)
    .groupBy(rewardEvents.status),

    // Pending rewards details
    db.select({
      count: sql<number>`COUNT(*)`,
      totalMood: sql<number>`COALESCE(SUM(rewardMood), 0)`,
      totalAtomic: sql<number>`COALESCE(SUM(rewardAtomic), 0)`
    })
    .from(rewardEvents)
    .where(sql`${rewardEvents.status} = 'pending'`)
  ]);

  const metrics: Record<string, number> = rewardCounts.reduce((acc, row) => {
    acc[row.status] = row.total;
    return acc;
  }, {} as Record<string, number>);

  return {
    pending: pendingRewards[0].count || 0,
    pendingMood: pendingRewards[0].totalMood || 0,
    pendingAtomic: pendingRewards[0].totalAtomic || 0,
    cancelled: metrics.cancelled || 0,
    updatedAt: now.toISOString()
  };
}

async function getNetworkHealth(db: ReturnType<typeof getDb>): Promise<"operational" | "degraded" | "partial" | "maintenance" | "unknown"> {
  try {
    // Check database connectivity
    const start = Date.now();
    await db.select({ count: sql<number>`COUNT(*)` }).from(users).limit(1);
    const dbLatency = Date.now() - start;

    // Check API endpoint health
    const apiHealthy = dbLatency < 1000; // Response within 1 second

    if (!apiHealthy) {
      return "degraded";
    }

    // Additional health checks could be added here
    // - Contribution service availability
    // - Identity service status
    // - External dependencies

    return "operational";
  } catch (error) {
    console.error("Health check failed:", error);
    return "unknown";
  }
}

/**
 * Treasury sub-metrics for /network integration.
 * Reads from the treasury model directly (in-process) to avoid extra HTTP.
 * Falls back to "unavailable" on error.
 */
async function getTreasurySubMetrics() {
  try {
    // Lazy import to avoid circular dependency
    const { buildTreasuryStatusPayload } = await import(
      "../../../../lib/treasury/model"
    );
    const payload = buildTreasuryStatusPayload();
    return {
      treasuryStatus: payload.treasuryStatus,
      verifiedAccounts: payload.verifiedAccounts,
      lastReport: payload.lastReport,
      lastActivity: payload.lastActivity,
      economics: payload.economics,
      disabledSlots: payload.disabledSlots,
    };
  } catch (error) {
    return {
      treasuryStatus: "unavailable",
      verifiedAccounts: 0,
      lastReport: null,
      lastActivity: null,
      economics: "Unknown",
      disabledSlots: [],
    };
  }
}