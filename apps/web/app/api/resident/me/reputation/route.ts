/**
 * MOOD PASSPORT 015 — GET /api/resident/me/reputation
 *
 * Returns the reputation summary for the current Resident. The summary
 * is read-only and may be `null` (no contributions yet) — never a fake
 * number.
 *
 * The data is sourced either from 016 (CONTRIBUTION_NETWORK) when present,
 * or computed locally as "no contributions yet" otherwise.
 *
 * This endpoint shape is the contract for 016's push path.
 */

import { defaultResidentRegistry } from "../../../../lib/mood/passport/index.ts";
import { jsonError, requireResident } from "../../identity/_helpers.ts";

export const dynamic = "force-dynamic";

export async function GET(request: Request): Promise<Response> {
  try {
    const resident = requireResident(request);
    if (!resident) return jsonError(401, "UNAUTHORIZED", "no session");
    const reputation =
      defaultResidentRegistry.getReputation(resident.id)
        ?? defaultResidentRegistry.emptyReputation(resident.id);
    return Response.json({ reputation });
  } catch (err) {
    console.error("resident/me/reputation error", err);
    return jsonError(500, "INTERNAL", "reputation failed");
  }
}
