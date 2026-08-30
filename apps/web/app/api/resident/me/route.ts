/**
 * MOOD PASSPORT 015 — GET /api/resident/me
 *
 * Returns the current Resident + profile + privacy + (truncated) wallets +
 * roles + (empty) reputation. Owner-only.
 */

import {
  defaultResidentRegistry,
  derivePublicProfile,
} from "../../../lib/mood/passport/index.ts";
import { jsonError, requireResident } from "../identity/_helpers.ts";

export const dynamic = "force-dynamic";

export async function GET(request: Request): Promise<Response> {
  try {
    const resident = requireResident(request);
    if (!resident) return jsonError(401, "UNAUTHORIZED", "no session");

    const profile = defaultResidentRegistry.getProfile(resident.id);
    const wallets = defaultResidentRegistry
      .listWallets(resident.id)
      .map((w) => ({
        id: w.id,
        address: w.address,
        truncated: `${w.address.slice(0, 6)}…${w.address.slice(-4)}`,
        isPrimary: w.isPrimary,
        verifiedAt: w.verifiedAt,
        addedAt: w.addedAt,
      }));
    const selfDeclared = defaultResidentRegistry.listSelfDeclaredRoles(
      resident.id,
    );
    const verified = defaultResidentRegistry.listVerifiedRoles(resident.id);
    const badges = defaultResidentRegistry.listBadges(resident.id).map((b) => b.badge);
    const privacy = defaultResidentRegistry.getPrivacy(resident.id);
    const reputation =
      defaultResidentRegistry.getReputation(resident.id)
        ?? defaultResidentRegistry.emptyReputation(resident.id);

    return Response.json({
      resident: {
        id: resident.id,
        createdAt: resident.createdAt,
        status: resident.status,
      },
      profile: profile ?? null,
      wallets,
      roles: {
        selfDeclared,
        verified,
      },
      badges,
      privacy,
      reputation,
    });
  } catch (err) {
    console.error("resident/me error", err);
    return jsonError(500, "INTERNAL", "resident/me failed");
  }
}

/**
 * PATCH /api/resident/me — update profile / privacy fields.
 */
export async function PATCH(request: Request): Promise<Response> {
  try {
    const resident = requireResident(request);
    if (!resident) return jsonError(401, "UNAUTHORIZED", "no session");
    const body = (await request.json()) as Record<string, unknown>;
    const url = new URL(request.url);

    // Dispatch on a `kind` field:
    //   { kind: "profile", displayName, bio, avatarUrl, preferredLanguage }
    //   { kind: "privacy", profileVisibility, showFullWalletAddress, ... }
    const kind = typeof body.kind === "string" ? body.kind : "profile";
    if (kind === "privacy") {
      const result = defaultResidentRegistry.updatePrivacy(resident.id, {
        profileVisibility: typeof body.profileVisibility === "string"
          ? (body.profileVisibility as "public" | "minimal" | "private")
          : undefined,
        showFullWalletAddress: typeof body.showFullWalletAddress === "boolean"
          ? body.showFullWalletAddress
          : undefined,
        showContributionHistory: typeof body.showContributionHistory === "boolean"
          ? body.showContributionHistory
          : undefined,
        showRoles: typeof body.showRoles === "boolean"
          ? body.showRoles
          : undefined,
        showReputation: typeof body.showReputation === "boolean"
          ? body.showReputation
          : undefined,
      });
      if (!result.ok) return jsonError(400, "VALIDATION", result.reason ?? "bad-privacy-patch");
      return Response.json({ ok: true, privacy: result.privacy });
    }
    // Profile
    const result = defaultResidentRegistry.updateProfile(resident.id, {
      displayName: typeof body.displayName === "string"
        ? body.displayName.slice(0, 32)
        : body.displayName === null
          ? null
          : undefined,
      bio: typeof body.bio === "string"
        ? body.bio.slice(0, 280)
        : body.bio === null
          ? null
          : undefined,
      avatarUrl: typeof body.avatarUrl === "string"
        ? body.avatarUrl.slice(0, 256)
        : body.avatarUrl === null
          ? null
          : undefined,
      preferredLanguage: typeof body.preferredLanguage === "string"
          && (body.preferredLanguage === "zh" || body.preferredLanguage === "en")
        ? body.preferredLanguage
        : body.preferredLanguage === null
          ? null
          : undefined,
    });
    if (!result.ok) return jsonError(400, "VALIDATION", result.reason ?? "bad-profile-patch");
    return Response.json({ ok: true, profile: result.profile });
  } catch (err) {
    console.error("resident/me PATCH error", err);
    return jsonError(500, "INTERNAL", "resident/me PATCH failed");
  }
}

// used by server-side imports
export { defaultResidentRegistry, derivePublicProfile };
