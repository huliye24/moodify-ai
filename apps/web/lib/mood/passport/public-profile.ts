/**
 * MOOD PASSPORT 015 — Public Passport Derivation
 *
 * Derives the publicly-visible profile for a Resident from the
 * Resident's privacy settings. Default = minimal; never reveals:
 *   - full wallet address (only truncated display name)
 *   - consent history
 *   - session history
 *   - admin notes
 *   - DB-internal IDs
 */

import type {
  Resident,
  ResidentBadge,
  ResidentSession,
  PublicResidentProfile,
} from "./types.ts";

export interface DerivePublicInput {
  resident: Resident;
  selfDeclaredRoles: import("./types.ts").SelfDeclaredRole[];
  verifiedRoles: import("./types.ts").VerifiedRole[];
  badges: ResidentBadge[];
  reputation: import("./types.ts").ReputationSummary | null;
  contributionCount: number;
  displayName: string | null;
  privacy: {
    profileVisibility: "public" | "minimal" | "private";
    showRoles: boolean;
    showReputation: boolean;
    showContributionHistory: boolean;
  };
}

/**
 * Derive the public profile according to privacy settings.
 * Returns `null` when the Resident has chosen `private`.
 */
export function derivePublicProfile(
  input: DerivePublicInput,
): PublicResidentProfile | null {
  if (input.privacy.profileVisibility === "private") return null;

  const includeAll =
    input.privacy.profileVisibility === "public" &&
    input.privacy.showRoles &&
    input.privacy.showReputation &&
    input.privacy.showContributionHistory;

  return {
    residentId: input.resident.id,
    displayName: input.displayName,
    roles: includeAll || input.privacy.showRoles ? input.selfDeclaredRoles : [],
    verifiedRoles: includeAll || input.privacy.showRoles ? input.verifiedRoles : [],
    badges: includeAll
      ? input.badges.map((b) => b.badge)
      : input.privacy.showRoles
        ? input.badges.map((b) => b.badge)
        : [],
    joinedMonth: joinedMonth(input.resident.createdAt),
    reputation: includeAll || input.privacy.showReputation
      ? input.reputation
      : null,
    contributionCount: includeAll || input.privacy.showContributionHistory
      ? input.contributionCount
      : 0,
  };
}

function joinedMonth(iso: string): string {
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return "—";
  const month = d.toLocaleString("en-US", { month: "short" });
  return `${month} ${d.getUTCFullYear()}`;
}

/**
 * Strip internal fields from a ResidentSession before exposing it to the
 * client. We never want to leak the underlying `walletId` or DB IDs.
 */
export function deriveClientSession(session: ResidentSession) {
  return {
    id: session.id,
    residentId: session.residentId,
    walletAddressTruncated: `${session.walletAddress.slice(0, 6)}…${session.walletAddress.slice(-4)}`,
    issuedAt: session.issuedAt,
    expiresAt: session.expiresAt,
  };
}

/**
 * Display helpers — kept pure so they can be reused in UI as well as tests.
 */
export function displayNameOrFallback(profile: {
  displayName: string | null;
}): string {
  return profile.displayName ?? "Anonymous Resident";
}
