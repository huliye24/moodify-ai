import { NextResponse } from "next/server";
import { contributionRegistry } from "@/lib/mood/contribution/registry.ts";

export const dynamic = "force-dynamic";

/**
 * POST /api/contribution/tasks/[slug]/submissions
 *
 * Authenticated Resident creates a submission for the task.
 * Resident ID is passed via X-Resident-Id header (bridge build).
 *
 * Body: { summary, evidenceText?, evidenceItems?[] }
 */
export async function POST(
  req: Request,
  { params }: { params: { slug: string } },
) {
  const residentId = req.headers.get("x-resident-id");
  if (!residentId) {
    return NextResponse.json(
      {
        error: {
          code: "unauthenticated",
          message: "X-Resident-Id header required (bridge build)",
        },
      },
      { status: 401 },
    );
  }

  const task = contributionRegistry.findTaskBySlug(params.slug);
  if (!task) {
    return NextResponse.json(
      { error: { code: "task-not-found", message: "task not found" } },
      { status: 404 },
    );
  }

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
  if (!input.summary || typeof input.summary !== "string") {
    return NextResponse.json(
      { error: { code: "missing-summary", message: "summary required" } },
      { status: 400 },
    );
  }

  try {
    const submission = contributionRegistry.createSubmission({
      taskId: task.id,
      residentId,
      summary: input.summary,
      evidenceText: input.evidenceText as string | undefined,
      evidenceItems: input.evidenceItems as
        | Array<{ type: "url" | "github-pr" | "github-commit" | "document" | "artifact" | "text"; value: string; label?: string }>
        | undefined,
    });
    return NextResponse.json({ submission }, { status: 201 });
  } catch (e) {
    const msg = (e as Error).message;
    const status = msg.startsWith("evidence:") ? 400 : 400;
    return NextResponse.json(
      { error: { code: "create-submission-failed", message: msg } },
      { status },
    );
  }
}

/**
 * GET /api/contribution/tasks/[slug]/submissions
 *
 * Lists submissions for a task. Public view excludes reviewer-only fields.
 */
export async function GET(
  _req: Request,
  { params }: { params: { slug: string } },
) {
  const task = contributionRegistry.findTaskBySlug(params.slug);
  if (!task) {
    return NextResponse.json(
      { error: { code: "task-not-found", message: "task not found" } },
      { status: 404 },
    );
  }
  const subs = contributionRegistry.listSubmissionsForTask(task.id);
  // Public view excludes reviewerNote.
  const publicSubs = subs.map((s) => ({
    id: s.id,
    taskId: s.taskId,
    residentId: s.residentId,
    summary: s.summary,
    status: s.status,
    revision: s.revision,
    createdAt: s.createdAt,
    updatedAt: s.updatedAt,
  }));
  return NextResponse.json({ submissions: publicSubs, count: publicSubs.length });
}