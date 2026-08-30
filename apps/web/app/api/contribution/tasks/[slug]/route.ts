import { NextResponse } from "next/server";
import { contributionRegistry } from "@/lib/mood/contribution/registry.ts";

export const dynamic = "force-dynamic";

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
  return NextResponse.json({
    task: {
      id: task.id,
      slug: task.slug,
      title: task.title,
      summary: task.summary,
      description: task.description,
      category: task.category,
      status: task.status,
      evidenceRequirements: task.evidenceRequirements,
      defaultReputationPoints: task.defaultReputationPoints,
      defaultRewardUnits: task.defaultRewardUnits,
      deadline: task.deadline,
      maxApprovals: task.maxApprovals,
      createdAt: task.createdAt,
      updatedAt: task.updatedAt,
    },
  });
}