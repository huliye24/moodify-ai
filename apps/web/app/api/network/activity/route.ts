import { getDb } from "@/db";
import { sql } from "drizzle-orm";
import { users, contributionTasks, contributionSubmissions, reputationEvents } from "@/db/schema";
import { eq } from "drizzle-orm";

export async function GET(request: Request) {
  try {
    const db = getDb();
    const url = new URL(request.url);
    const limit = parseInt(url.searchParams.get('limit') || '20');
    const offset = parseInt(url.searchParams.get('offset') || '0');

    // Validate limit
    const validatedLimit = Math.min(Math.max(limit, 1), 100); // Between 1 and 100

    // Generate activity feed
    const activity = await getActivityFeed(db, validatedLimit, offset);

    return Response.json({
      generatedAt: new Date().toISOString(),
      limit: validatedLimit,
      offset,
      total: activity.length,
      events: activity
    });
  } catch (error) {
    console.error("Network activity API error:", error);
    return Response.json(
      {
        error: "Failed to fetch activity feed",
        status: "error"
      },
      { status: 500 }
    );
  }
}

async function getActivityFeed(db: ReturnType<typeof getDb>, limit: number, offset: number) {
  const now = new Date();
  const thirtyDaysAgo = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000);

  // Collect all possible events from the last 30 days
  const events: any[] = [];

  // 1. New Resident Events
  const newResidents = await db
    .select({
      id: users.id,
      displayName: users.displayName,
      createdAt: users.createdAt
    })
    .from(users)
    .where(sql`${users.createdAt} >= ${thirtyDaysAgo.toISOString()}`)
    .orderBy(sql`${users.createdAt} DESC`)
    .limit(limit);

  for (const resident of newResidents) {
    events.push({
      id: `resident_${resident.id}_${resident.createdAt}`,
      type: "ResidentJoined",
      timestamp: resident.createdAt,
      publicData: {
        shortId: resident.id.slice(-8),
        displayName: resident.displayName
      }
    });
  }

  // 2. Task Published Events
  const publishedTasks = await db
    .select({
      id: contributionTasks.id,
      title: contributionTasks.title,
      slug: contributionTasks.slug,
      createdAt: contributionTasks.createdAt
    })
    .from(contributionTasks)
    .where(sql`${contributionTasks.status} = 'active' AND ${contributionTasks.createdAt} >= ${thirtyDaysAgo.toISOString()}`)
    .orderBy(sql`${contributionTasks.createdAt} DESC`)
    .limit(limit);

  for (const task of publishedTasks) {
    events.push({
      id: `task_${task.id}_${task.createdAt}`,
      type: "TaskPublished",
      timestamp: task.createdAt,
      publicData: {
        taskId: task.id,
        title: task.title,
        slug: task.slug
      }
    });
  }

  // 3. Contribution Submitted Events
  const submittedSubmissions = await db
    .select({
      id: contributionSubmissions.id,
      taskId: contributionSubmissions.taskId,
      title: contributionTasks.title,
      user: {
        id: users.id,
        displayName: users.displayName
      },
      createdAt: contributionSubmissions.createdAt
    })
    .from(contributionSubmissions)
    .join(contributionTasks, sql`${contributionSubmissions.taskId} = ${contributionTasks.id}`)
    .join(users, sql`${contributionSubmissions.userId} = ${users.id}`)
    .where(sql`${contributionSubmissions.status} IN ('submitted', 'under_review') AND ${contributionSubmissions.createdAt} >= ${thirtyDaysAgo.toISOString()}`)
    .orderBy(sql`${contributionSubmissions.createdAt} DESC`)
    .limit(limit);

  for (const submission of submittedSubmissions) {
    events.push({
      id: `submission_${submission.id}_${submission.createdAt}`,
      type: "ContributionSubmitted",
      timestamp: submission.createdAt,
      publicData: {
        submissionId: submission.id,
        taskId: submission.taskId,
        taskTitle: submission.title,
        user: {
          shortId: submission.user.id.slice(-8),
          displayName: submission.user.displayName
        }
      }
    });
  }

  // 4. Submission Approved Events
  const approvedSubmissions = await db
    .select({
      id: contributionSubmissions.id,
      taskId: contributionSubmissions.taskId,
      title: contributionTasks.title,
      user: {
        id: users.id,
        displayName: users.displayName
      },
      createdAt: contributionSubmissions.createdAt
    })
    .from(contributionSubmissions)
    .join(contributionTasks, sql`${contributionSubmissions.taskId} = ${contributionTasks.id}`)
    .join(users, sql`${contributionSubmissions.userId} = ${users.id}`)
    .where(sql`${contributionSubmissions.status} = 'approved' AND ${contributionSubmissions.createdAt} >= ${thirtyDaysAgo.toISOString()}`)
    .orderBy(sql`${contributionSubmissions.createdAt} DESC`)
    .limit(limit);

  for (const submission of approvedSubmissions) {
    events.push({
      id: `approved_${submission.id}_${submission.createdAt}`,
      type: "SubmissionApproved",
      timestamp: submission.createdAt,
      publicData: {
        submissionId: submission.id,
        taskId: submission.taskId,
        taskTitle: submission.title,
        user: {
          shortId: submission.user.id.slice(-8),
          displayName: submission.user.displayName
        }
      }
    });
  }

  // 5. Reputation Granted Events (public only)
  const publicReputationEvents = await db
    .select({
      id: reputationEvents.id,
      pointsDelta: reputationEvents.pointsDelta,
      user: {
        id: users.id,
        displayName: users.displayName
      },
      createdAt: reputationEvents.createdAt,
      evidenceType: reputationEvents.evidenceType
    })
    .from(reputationEvents)
    .join(users, sql`${reputationEvents.userId} = ${users.id}`)
    .where(sql`${reputationEvents.pointsDelta} > 0 AND ${reputationEvents.createdAt} >= ${thirtyDaysAgo.toISOString()}`)
    .orderBy(sql`${reputationEvents.createdAt} DESC`)
    .limit(limit);

  for (const event of publicReputationEvents) {
    events.push({
      id: `reputation_${event.id}_${event.createdAt}`,
      type: "ReputationGranted",
      timestamp: event.createdAt,
      publicData: {
        points: event.pointsDelta,
        user: {
          shortId: event.user.id.slice(-8),
          displayName: event.user.displayName
        },
        evidenceType: event.evidenceType
      }
    });
  }

  // Sort all events by timestamp descending
  events.sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime());

  // Apply pagination
  const paginatedEvents = events.slice(offset, offset + validatedLimit);

  return paginatedEvents;
}

// Define event types
export type ActivityEvent = {
  id: string;
  type: "ResidentJoined" | "TaskPublished" | "ContributionSubmitted" | "SubmissionApproved" | "ReputationGranted";
  timestamp: string;
  publicData: {
    shortId?: string;
    displayName?: string;
    taskId?: string;
    taskTitle?: string;
    submissionId?: string;
    points?: number;
    evidenceType?: string;
  };
};