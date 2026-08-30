/**
 * MOOD PASSPORT 015 — GET /api/resident/me/contributions
 *
 * Returns the Resident's contributions summary. In foundation state this
 * is sourced from 016 once available; otherwise an honest empty shape.
 *
 * This endpoint intentionally lists *contributions* (private to the
 * resident). Public listing of contribution history is governed by
 * the resident's `showContributionHistory` privacy setting, and lives
 * behind the public profile route when privacy allows.
 */

import { defaultResidentRegistry } from "../../../../lib/mood/passport/index.ts";
import { jsonError, requireResident } from "../../identity/_helpers.ts";

export const dynamic = "force-dynamic";

export interface ResidentContributionsResponse {
  contributionCount: number;
  approvedContributionCount: number;
  recent: Array<{
    id: string;
    title: string;
    status: string;
    submittedAt: string;
    approvedAt: string | null;
  }>;
  source: "016-contribution-network" | "no-contributions-yet";
}

export async function GET(request: Request): Promise<Response> {
  try {
    const resident = requireResident(request);
    if (!resident) return jsonError(401, "UNAUTHORIZED", "no session");
    const reputation = defaultResidentRegistry.getReputation(resident.id)
      ?? defaultResidentRegistry.emptyReputation(resident.id);
    const body: ResidentContributionsResponse = {
      contributionCount: reputation.contributionCount,
      approvedContributionCount: reputation.approvedContributionCount,
      recent: [], // Foundation: 016 not yet integrated. Always empty.
      source: reputation.source,
    };
    return Response.json(body);
  } catch (err) {
    console.error("resident/me/contributions error", err);
    return jsonError(500, "INTERNAL", "contributions failed");
  }
}
