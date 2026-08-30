/**
 * MOOD PASSPORT 015 — GET /api/resident/me/badges
 *
 * Owner-only. Returns the badges awarded to the current Resident.
 */

import { defaultResidentRegistry } from "@/lib/mood/passport/index.ts";
import { jsonError, requireResident } from "@/app/api/identity/_helpers.ts";

export const dynamic = "force-dynamic";

export async function GET(request: Request): Promise<Response> {
  try {
    const resident = requireResident(request);
    if (!resident) return jsonError(401, "UNAUTHORIZED", "no session");
    return Response.json({
      badges: defaultResidentRegistry.listBadges(resident.id).map((b) => b.badge),
    });
  } catch (err) {
    console.error("resident/me/badges error", err);
    return jsonError(500, "INTERNAL", "badges failed");
  }
}
