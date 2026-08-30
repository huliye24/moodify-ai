import { NextResponse } from "next/server";
import {
  contributionRegistry,
  type ContributionCategory,
} from "../../../../lib/mood/contribution/registry.ts";

export const dynamic = "force-dynamic";

/**
 * GET /api/contribution/tasks
 *
 * Public task catalog. Returns only active tasks by default.
 * No private metadata exposed.
 */
export async function GET(req: Request) {
  const url = new URL(req.url);
  const status = url.searchParams.get("status") ?? "active";
  const allowed = ["draft", "active", "paused", "completed", "archived"];
  if (!allowed.includes(status)) {
    return NextResponse.json(
      { error: { code: "invalid-status", message: "invalid status" } },
      { status: 400 },
    );
  }
  const tasks = contributionRegistry.listTasks({
    status: status as ContributionCategory extends never ? never : Parameters<
      typeof contributionRegistry.listTasks
    >[0] extends { status?: infer S }
      ? S
      : never,
  });
  // Public list excludes private fields (none currently, but pattern for future).
  const publicTasks = tasks.map((t) => ({
    id: t.id,
    slug: t.slug,
    title: t.title,
    summary: t.summary,
    description: t.description,
    category: t.category,
    status: t.status,
    evidenceRequirements: t.evidenceRequirements,
    defaultReputationPoints: t.defaultReputationPoints,
    defaultRewardUnits: t.defaultRewardUnits,
    deadline: t.deadline,
    maxApprovals: t.maxApprovals,
    createdAt: t.createdAt,
    updatedAt: t.updatedAt,
  }));
  return NextResponse.json({ tasks: publicTasks, count: publicTasks.length });
}

/**
 * POST /api/contribution/tasks
 *
 * Creates a new task. Requires authenticated Resident (admin or task-creator).
 * 016 in-memory only — no auth layer is fully wired yet; we treat the
 * "X-Resident-Id" header as the actor for the bridge build.
 */
export async function POST(req: Request) {
  let body: unknown;
  try {
    body = await req.json();
  } catch {
    return NextResponse.json(
      { error: { code: "invalid-json", message: "invalid JSON body" } },
      { status: 400 },
    );
  }
  if (!body || typeof body !== "object") {
    return NextResponse.json(
      { error: { code: "invalid-body", message: "invalid body" } },
      { status: 400 },
    );
  }
  const input = body as Record<string, unknown>;
  const required = [
    "slug",
    "title",
    "summary",
    "description",
    "category",
    "defaultReputationPoints",
    "createdByResidentId",
  ];
  for (const k of required) {
    if (!input[k]) {
      return NextResponse.json(
        { error: { code: "missing-field", message: `missing ${k}` } },
        { status: 400 },
      );
    }
  }
  try {
    const task = contributionRegistry.createTask({
      slug: input.slug as string,
      title: input.title as string,
      summary: input.summary as string,
      description: input.description as string,
      category: input.category as ContributionCategory,
      evidenceRequirements: (input.evidenceRequirements as string[]) ?? [],
      defaultReputationPoints: input.defaultReputationPoints as number,
      defaultRewardUnits: input.defaultRewardUnits as string | undefined,
      deadline: input.deadline as string | undefined,
      maxApprovals: input.maxApprovals as number | undefined,
      createdByResidentId: input.createdByResidentId as string,
    });
    return NextResponse.json({ task }, { status: 201 });
  } catch (e) {
    return NextResponse.json(
      {
        error: {
          code: "create-task-failed",
          message: (e as Error).message,
        },
      },
      { status: 400 },
    );
  }
}