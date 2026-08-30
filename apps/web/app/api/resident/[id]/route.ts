/**
 * MOOD PASSPORT 015 — GET /api/resident/[id]
 *
 * Public-by-default-disabled route.
 *
 * PASS POLICY:
 *   - ProfileVisibility must be "public" (not "minimal" / "private").
 *   - Feature flag: when MOOD_PASSPORT_PUBLIC_PROFILE is not "1", the route
 *     returns 404 (privacy hard default is OFF in foundation state).
 *
 * Response shape — only fields the Resident has chosen to expose:
 *   {
 *     residentId, displayName, roles, verifiedRoles,
 *     badges, joinedMonth, reputation, contributionCount
 *   }
 */

import {
  defaultResidentRegistry,
  derivePublicProfile,
} from "../../../lib/mood/passport/index.ts";
import { jsonError } from "../identity/_helpers.ts";

export const dynamic = "force-dynamic";

export async function GET(request: Request): Promise<Response> {
  try {
    if (process.env.MOOD_PASSPORT_PUBLIC_PROFILE !== "1") {
      return jsonError(404, "DISABLED", "public profile is disabled");
    }
    const url = new URL(request.url);
    const segments = url.pathname.split("/").filter(Boolean);
    const idIndex = segments.indexOf("resident");
    const id = idIndex >= 0 && segments.length > idIndex + 1
      ? segments[idIndex + 1] ?? ""
      : "";
    if (!id) return jsonError(400, "VALIDATION", "id required");

    const resident = defaultResidentRegistry.getResident(id);
    if (!resident) return jsonError(404, "NOT_FOUND", "no such resident");

    const privacy = defaultResidentRegistry.getPrivacy(resident.id);
    if (!privacy) return jsonError(404, "NOT_FOUND", "no privacy record");

    const profile = defaultResidentRegistry.getProfile(resident.id);
    const selfDeclared = defaultResidentRegistry.listSelfDeclaredRoles(
      resident.id,
    );
    const verified = defaultResidentRegistry.listVerifiedRoles(resident.id);
    const badges = defaultResidentRegistry.listBadges(resident.id);
    const reputation = defaultResidentRegistry.getReputation(resident.id)
      ?? defaultResidentRegistry.emptyReputation(resident.id);

    const publicView = derivePublicProfile({
      resident,
      selfDeclaredRoles: selfDeclared,
      verifiedRoles: verified,
      badges,
      reputation,
      contributionCount: reputation.contributionCount,
      displayName: profile?.displayName ?? null,
      privacy,
    });
    if (!publicView) return jsonError(403, "PRIVATE", "profile is private");

    return Response.json(publicView);
  } catch (err) {
    console.error("resident/[id] error", err);
    return jsonError(500, "INTERNAL", "resident lookup failed");
  }
}
