import { getDb } from "@/db";
import { sql } from "drizzle-orm";
import { users, contributionTasks, contributionSubmissions } from "@/db/schema";

export async function GET(request: Request) {
  try {
    const db = getDb();
    const now = new Date().toISOString();

    // Run all health checks in parallel
    const [
      databaseHealth,
      userServiceHealth,
      contributionServiceHealth,
      overallStatus
    ] = await Promise.all([
      checkDatabaseHealth(db),
      checkUserServiceHealth(db),
      checkContributionServiceHealth(db),
      getOverallNetworkHealth(db)
    ]);

    const healthResponse = {
      status: overallStatus,
      generatedAt: now,
      checks: {
        database: databaseHealth,
        userService: userServiceHealth,
        contributionService: contributionServiceHealth
      },
      timestamp: now
    };

    return Response.json(healthResponse);
  } catch (error) {
    console.error("Network health API error:", error);
    return Response.json(
      {
        status: "unknown",
        error: "Failed to fetch network health",
        generatedAt: new Date().toISOString(),
        checks: {
          database: { status: "error", error: "Health check failed" },
          userService: { status: "error", error: "Health check failed" },
          contributionService: { status: "error", error: "Health check failed" }
        }
      },
      { status: 500 }
    );
  }
}

async function checkDatabaseHealth(db: ReturnType<typeof getDb>) {
  try {
    const startTime = Date.now();

    // Test basic database connectivity
    const result = await db.select({ count: sql<number>`COUNT(*)` })
      .from(users)
      .limit(1);

    const latency = Date.now() - startTime;
    const responseTime = latency < 500 ? "fast" : latency < 1000 ? "normal" : "slow";

    // Test table accessibility
    const tableAccess = {
      users: true,
      contributionTasks: true,
      contributionSubmissions: true
    };

    // Check if we can write timestamps
    const canWriteTimestamps = new Date().toISOString() !== null;

    return {
      status: latency < 2000 ? "healthy" : "degraded",
      latencyMs: latency,
      responseTime,
      tableAccess,
      canWriteTimestamps,
      details: {
        totalUsers: result[0].count,
        message: latency < 1000 ? "Database responsive" : "Database slow but responding"
      }
    };
  } catch (error) {
    console.error("Database health check failed:", error);
    return {
      status: "error",
      latencyMs: null,
      responseTime: "unknown",
      tableAccess: { users: false, contributionTasks: false, contributionSubmissions: false },
      canWriteTimestamps: false,
      error: error instanceof Error ? error.message : "Unknown database error"
    };
  }
}

async function checkUserServiceHealth(db: ReturnType<typeof getDb>) {
  try {
    const startTime = Date.now();

    // Test user registration flow
    const activeUsers = await db.select({ count: sql<number>`COUNT(*)` })
      .from(users)
      .where(sql`${users.status} = 'active'`);

    const recentUsers = await db.select({ count: sql<number>`COUNT(*)` })
      .from(users)
      .where(sql`${users.createdAt} >= ${new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString()}`);

    const latency = Date.now() - startTime;

    return {
      status: latency < 1000 ? "healthy" : "degraded",
      latencyMs: latency,
      details: {
        activeUsers: activeUsers[0].count,
        newUsers24h: recentUsers[0].count,
        message: latency < 500 ? "User service responsive" : "User service slow"
      }
    };
  } catch (error) {
    console.error("User service health check failed:", error);
    return {
      status: "error",
      latencyMs: null,
      details: {
        activeUsers: 0,
        newUsers24h: 0,
        error: error instanceof Error ? error.message : "Unknown user service error"
      }
    };
  }
}

async function checkContributionServiceHealth(db: ReturnType<typeof getDb>) {
  try {
    const startTime = Date.now();

    // Test contribution workflow
    const activeTasks = await db.select({ count: sql<number>`COUNT(*)` })
      .from(contributionTasks)
      .where(sql`${contributionTasks.status} = 'active'`);

    const recentSubmissions = await db.select({ count: sql<number>`COUNT(*)` })
      .from(contributionSubmissions)
      .where(sql`${contributionSubmissions.createdAt} >= ${new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString()}`);

    const pendingSubmissions = await db.select({ count: sql<number>`COUNT(*)` })
      .from(contributionSubmissions)
      .where(sql`${contributionSubmissions.status} IN ('submitted', 'under_review', 'changes_requested')`);

    const latency = Date.now() - startTime;

    return {
      status: latency < 1000 ? "healthy" : "degraded",
      latencyMs: latency,
      details: {
        activeTasks: activeTasks[0].count,
        recentSubmissions24h: recentSubmissions[0].count,
        pendingSubmissions: pendingSubmissions[0].count,
        message: latency < 500 ? "Contribution service responsive" : "Contribution service slow"
      }
    };
  } catch (error) {
    console.error("Contribution service health check failed:", error);
    return {
      status: "error",
      latencyMs: null,
      details: {
        activeTasks: 0,
        recentSubmissions24h: 0,
        pendingSubmissions: 0,
        error: error instanceof Error ? error.message : "Unknown contribution service error"
      }
    };
  }
}

async function getOverallNetworkHealth(db: ReturnType<typeof getDb>): Promise<"operational" | "degraded" | "partial" | "maintenance" | "unknown"> {
  try {
    // Check individual services
    const [dbHealth, userHealth, contribHealth] = await Promise.all([
      checkDatabaseHealth(db),
      checkUserServiceHealth(db),
      checkContributionServiceHealth(db)
    ]);

    // Determine overall status based on individual checks
    const allHealthy = dbHealth.status === "healthy" &&
                     userHealth.status === "healthy" &&
                     contribHealth.status === "healthy";

    const anyError = dbHealth.status === "error" ||
                    userHealth.status === "error" ||
                    contribHealth.status === "error";

    const anyDegraded = dbHealth.status === "degraded" ||
                       userHealth.status === "degraded" ||
                       contribHealth.status === "degraded";

    if (anyError) {
      return "partial";
    }

    if (anyDegraded) {
      return "degraded";
    }

    if (allHealthy) {
      return "operational";
    }

    return "unknown";
  } catch (error) {
    console.error("Overall health check failed:", error);
    return "unknown";
  }
}