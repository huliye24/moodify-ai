import { NextResponse } from "next/server";
import { networkObservatory } from "@/lib/mood/network/observatory.ts";

export const dynamic = "force-dynamic";

export async function GET() {
  const overview = networkObservatory.overview();
  return NextResponse.json({
    status: overview.status,
    timestamp: overview.generatedAt,
    components: {
      contribution: overview.metrics.submissions?.state ?? "unknown",
      reputation: overview.metrics.reputationEvents?.state ?? "unknown",
      pendingReward: overview.metrics.pendingReward?.state ?? "unknown",
      agents: overview.metrics.agents?.state ?? "unknown",
      nodes: overview.metrics.nodes?.state ?? "unknown",
    },
    // Public-safe surface only. No DB host, no stack trace, no secrets.
  });
}