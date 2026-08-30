/**
 * MOOD PASSPORT 015 — Resident Registry
 *
 * Core identity store. In-memory; same rationale as NonceRegistry.
 *
 * Authoritative concepts:
 *   - Resident          : stable person record (no wallet address inside).
 *   - WalletIdentity    : bound wallet → resident, with primary flag.
 *   - ResidentProfile   : optional display, bio, avatar, language.
 *   - ResidentRoleRecord: self-declared or verified role.
 *   - ResidentBadge     : badges awarded by system/governance/manual.
 *   - ResidentConsent   : policy version acceptance record.
 *   - ResidentPrivacySettings: default-minimal privacy posture.
 *   - ReputationSummary : read-only cache pulled from 016.
 *
 * Tested in tests/passport-invariants.test.mjs.
 */

import { normalizeEvmAddress } from "./evm-address.ts";
import { generateResidentId } from "./resident-id.ts";
import type {
  Resident,
  ResidentProfile,
  WalletIdentity,
  ResidentRoleRecord,
  ResidentBadge,
  Badge,
  ResidentConsent,
  ResidentPrivacySettings,
  ResidentSession,
  PreferredLanguage,
  SelfDeclaredRole,
  VerifiedRole,
  ResidentRole,
  BadgeSource,
  ReputationSummary,
  ProfileVisibility,
  WalletDisplayPreference,
} from "./types.ts";

const DEFAULT_PRIVACY: Omit<ResidentPrivacySettings, "residentId"> = {
  profileVisibility: "minimal",
  showFullWalletAddress: false,
  showContributionHistory: true,
  showRoles: true,
  showReputation: true,
};

function isValidSelfDeclaredRole(r: unknown): r is SelfDeclaredRole {
  return ["creator", "developer", "researcher", "node-operator", "agent-builder"].includes(
    r as string,
  );
}

function isValidVerifiedRole(r: unknown): r is VerifiedRole {
  return [
    "verified-contributor",
    "verified-developer",
    "genesis-builder",
    "node-operator-verified",
  ].includes(r as string);
}

function isValidRole(r: unknown): r is ResidentRole {
  return isValidSelfDeclaredRole(r) || isValidVerifiedRole(r);
}

function isoNow(): string {
  return new Date().toISOString();
}

function newId(): string {
  return globalThis.crypto.randomUUID();
}

export class ResidentRegistry {
  private residents: Map<string, Resident> = new Map();
  private wallets: Map<string, WalletIdentity> = new Map(); // by wallet.id
  private walletsByAddress: Map<string, WalletIdentity> = new Map(); // by normalized address
  private profiles: Map<string, ResidentProfile> = new Map(); // by residentId
  private roles: ResidentRoleRecord[] = [];
  private badges: ResidentBadge[] = [];
  private consents: ResidentConsent[] = [];
  private privacy: Map<string, ResidentPrivacySettings> = new Map();
  private sessions: Map<string, ResidentSession> = new Map(); // by session.id
  private reputations: Map<string, ReputationSummary> = new Map();

  // ─── Resident ──────────────────────────────────────────────────────────────

  /**
   * Find a Resident by ID.
   */
  getResident(id: string): Resident | null {
    if (!id) return null;
    return this.residents.get(id) ?? null;
  }

  /**
   * Find a Resident by their primary wallet address.
   * Returns null if no Resident is bound.
   */
  getResidentByAddress(address: string): Resident | null {
    const normalized = normalizeEvmAddress(address);
    if (!normalized) return null;
    const wallet = this.walletsByAddress.get(normalized);
    if (!wallet) return null;
    return this.residents.get(wallet.residentId) ?? null;
  }

  /**
   * List all wallet identities bound to a Resident.
   */
  listWallets(residentId: string): WalletIdentity[] {
    return [...this.wallets.values()].filter((w) => w.residentId === residentId);
  }

  /**
   * Bind a verified wallet address to a Resident.
   * If the wallet is already bound to a different Resident, returns
   * { ok: false, reason } and does not mutate.
   * If the wallet was previously bound to a deleted Resident, allows re-bind.
   */
  bindWallet(params: {
    residentId: string;
    address: string;
    markPrimary?: boolean;
  }): { ok: boolean; identity?: WalletIdentity; reason?: string } {
    const resident = this.residents.get(params.residentId);
    if (!resident) return { ok: false, reason: "unknown-resident" };
    if (resident.status !== "active") {
      return { ok: false, reason: "resident-not-active" };
    }
    const address = normalizeEvmAddress(params.address);
    if (!address) return { ok: false, reason: "invalid-address" };

    // Already bound to the same resident → no-op.
    const existing = this.walletsByAddress.get(address);
    if (existing && existing.residentId === params.residentId) {
      if (params.markPrimary) this.markPrimary(existing.id);
      return { ok: true, identity: existing };
    }
    if (existing) {
      // Only allow re-bind if the previous resident is deleted.
      const previousResident = this.residents.get(existing.residentId);
      if (!previousResident || previousResident.status !== "deleted") {
        return { ok: false, reason: "address-bound-to-other-resident" };
      }
      // Mark old wallet deleted.
      existing.address = "";
      this.walletsByAddress.delete(address);
    }

    const identity: WalletIdentity = {
      id: newId(),
      residentId: params.residentId,
      address,
      chainFamily: "evm",
      isPrimary: false,
      verifiedAt: isoNow(),
      addedAt: isoNow(),
    };
    this.wallets.set(identity.id, identity);
    this.walletsByAddress.set(address, identity);

    if (params.markPrimary) this.markPrimary(identity.id);

    // Always ensure at least one primary wallet.
    const residentWallets = this.listWallets(params.residentId);
    if (!residentWallets.some((w) => w.isPrimary)) {
      this.markPrimary(identity.id);
    }

    return { ok: true, identity: this.wallets.get(identity.id)! };
  }

  /**
   * Mark a wallet as the primary. Demotes any other primary for the same Resident.
   */
  markPrimary(walletId: string): boolean {
    const wallet = this.wallets.get(walletId);
    if (!wallet) return false;
    for (const w of this.listWallets(wallet.residentId)) {
      w.isPrimary = w.id === walletId;
    }
    return true;
  }

  // ─── Resident Create / Resolve ──────────────────────────────────────────────

  /**
   * Idempotent: if the address is not yet bound, create a new Resident +
   * WalletIdentity. If the address is already bound, return the existing
   * Resident.
   *
   * This is the central "first-login / repeat-login" collision resolver.
   * It does NOT couple to any Token config.
   */
  resolveOrCreateByWallet(address: string): {
    resident: Resident;
    wallet: WalletIdentity;
    created: boolean;
  } {
    const existing = this.getResidentByAddress(address);
    if (existing) {
      const wallet = this.listWallets(existing.id).find((w) => w.isPrimary)
        ?? this.listWallets(existing.id)[0]
        ?? null;
      if (!wallet) {
        // Should not happen: resident has no wallets.
        const w = this.bindWallet({ residentId: existing.id, address, markPrimary: true });
        if (!w.ok || !w.identity) throw new Error("failed to re-bind wallet");
        return { resident: existing, wallet: w.identity, created: false };
      }
      return { resident: existing, wallet, created: false };
    }

    const residentId = generateResidentId();
    const createdAt = isoNow();
    const resident: Resident = {
      id: residentId,
      createdAt,
      updatedAt: createdAt,
      status: "active",
    };
    this.residents.set(residentId, resident);

    // Initialize default profile (all-null).
    this.profiles.set(residentId, {
      residentId,
      displayName: null,
      bio: null,
      avatarUrl: null,
      preferredLanguage: null,
      updatedAt: createdAt,
    });

    // Initialize default privacy.
    this.privacy.set(residentId, { residentId, ...DEFAULT_PRIVACY });

    // Bind wallet.
    const bind = this.bindWallet({
      residentId,
      address,
      markPrimary: true,
    });
    if (!bind.ok || !bind.identity) {
      throw new Error(`failed to bind wallet: ${bind.reason}`);
    }
    return { resident, wallet: bind.identity, created: true };
  }

  // ─── Profile ───────────────────────────────────────────────────────────────

  getProfile(residentId: string): ResidentProfile | null {
    return this.profiles.get(residentId) ?? null;
  }

  /**
   * Update profile. Owner-only enforced by caller; here we just validate.
   */
  updateProfile(
    residentId: string,
    patch: Partial<{
      displayName: string | null;
      bio: string | null;
      avatarUrl: string | null;
      preferredLanguage: PreferredLanguage | null;
    }>,
  ): { ok: boolean; profile?: ResidentProfile; reason?: string } {
    const resident = this.residents.get(residentId);
    if (!resident) return { ok: false, reason: "unknown-resident" };
    const profile = this.profiles.get(residentId);
    if (!profile) return { ok: false, reason: "no-profile" };

    // Field validation: length caps to prevent XSS / DoS / wall-of-text.
    if (patch.displayName !== undefined) {
      if (
        patch.displayName === null ||
        (typeof patch.displayName === "string" && patch.displayName.length <= 32)
      ) {
        profile.displayName = patch.displayName;
      } else {
        return { ok: false, reason: "displayName-too-long" };
      }
    }
    if (patch.bio !== undefined) {
      if (
        patch.bio === null ||
        (typeof patch.bio === "string" && patch.bio.length <= 280)
      ) {
        profile.bio = patch.bio;
      } else {
        return { ok: false, reason: "bio-too-long" };
      }
    }
    if (patch.avatarUrl !== undefined) {
      if (
        patch.avatarUrl === null ||
        (typeof patch.avatarUrl === "string" && patch.avatarUrl.length <= 256)
      ) {
        profile.avatarUrl = patch.avatarUrl;
      } else {
        return { ok: false, reason: "avatarUrl-too-long" };
      }
    }
    if (patch.preferredLanguage !== undefined) {
      if (
        patch.preferredLanguage === null ||
        patch.preferredLanguage === "zh" ||
        patch.preferredLanguage === "en"
      ) {
        profile.preferredLanguage = patch.preferredLanguage;
      } else {
        return { ok: false, reason: "invalid-preferredLanguage" };
      }
    }

    profile.updatedAt = isoNow();
    resident.updatedAt = profile.updatedAt;
    return { ok: true, profile: { ...profile } };
  }

  // ─── Roles ─────────────────────────────────────────────────────────────────

  listRoles(residentId: string): ResidentRoleRecord[] {
    return this.roles.filter((r) => r.residentId === residentId);
  }

  listSelfDeclaredRoles(residentId: string): SelfDeclaredRole[] {
    const out = new Set<SelfDeclaredRole>();
    for (const r of this.roles) {
      if (r.residentId === residentId && !r.verifiedAt && isValidSelfDeclaredRole(r.role)) {
        out.add(r.role);
      }
    }
    return [...out];
  }

  listVerifiedRoles(residentId: string): VerifiedRole[] {
    const out = new Set<VerifiedRole>();
    for (const r of this.roles) {
      if (r.residentId === residentId && r.verifiedAt && isValidVerifiedRole(r.role)) {
        out.add(r.role);
      }
    }
    return [...out];
  }

  /**
   * Self-declared role registration. Always available to the resident.
   * Idempotent.
   */
  addSelfDeclaredRole(
    residentId: string,
    role: SelfDeclaredRole,
  ): { ok: boolean; reason?: string } {
    const resident = this.residents.get(residentId);
    if (!resident) return { ok: false, reason: "unknown-resident" };
    if (!isValidSelfDeclaredRole(role)) return { ok: false, reason: "invalid-role" };
    const existing = this.roles.find(
      (r) => r.residentId === residentId && r.role === role && !r.verifiedAt,
    );
    if (existing) return { ok: true };
    this.roles.push({
      residentId,
      role,
      declaredAt: isoNow(),
    });
    return { ok: true };
  }

  /**
   * Verified role authorization.
   * REQUIRES an evidence source. Used by admin/governance tooling, NOT
   * exposed to a public self-issue endpoint.
   */
  awardVerifiedRole(
    residentId: string,
    role: VerifiedRole,
    source: string,
  ): { ok: boolean; reason?: string } {
    const resident = this.residents.get(residentId);
    if (!resident) return { ok: false, reason: "unknown-resident" };
    if (!isValidVerifiedRole(role)) return { ok: false, reason: "invalid-role" };
    if (!source || typeof source !== "string" || source.length > 256) {
      return { ok: false, reason: "missing-or-invalid-source" };
    }
    const existing = this.roles.find(
      (r) => r.residentId === residentId && r.role === role && r.verifiedAt,
    );
    if (existing) {
      existing.source = source; // Update evidence reference.
      return { ok: true };
    }
    // Strip any prior self-declared claim (verifying supersedes).
    for (let i = this.roles.length - 1; i >= 0; i--) {
      const r = this.roles[i];
      if (r && r.residentId === residentId && r.role === role && !r.verifiedAt) {
        this.roles.splice(i, 1);
      }
    }
    this.roles.push({
      residentId,
      role,
      declaredAt: isoNow(),
      verifiedAt: isoNow(),
      source,
    });
    return { ok: true };
  }

  // ─── Badges ────────────────────────────────────────────────────────────────

  listBadges(residentId: string): ResidentBadge[] {
    return this.badges.filter((b) => b.residentId === residentId);
  }

  /**
   * Award a badge to a Resident. Badges may NEVER be self-issued.
   * The caller (governance / system code) must enforce that this is only
   * invoked from authority-paths.
   */
  awardBadge(
    residentId: string,
    params: {
      slug: string;
      title: string;
      description: string;
      source: BadgeSource;
      evidenceUrl?: string;
    },
  ): { ok: boolean; badge?: ResidentBadge; reason?: string } {
    const resident = this.residents.get(residentId);
    if (!resident) return { ok: false, reason: "unknown-resident" };
    if (!params.slug || typeof params.slug !== "string") {
      return { ok: false, reason: "missing-slug" };
    }
    if (params.evidenceUrl && params.evidenceUrl.length > 256) {
      return { ok: false, reason: "evidenceUrl-too-long" };
    }
    const id = newId();
    const badge: Badge = {
      id,
      slug: params.slug,
      title: params.title,
      description: params.description,
      source: params.source,
      issuedAt: isoNow(),
      evidenceUrl: params.evidenceUrl,
    };
    const record: ResidentBadge = {
      residentId,
      badge,
      awardedAt: isoNow(),
    };
    this.badges.push(record);
    return { ok: true, badge: record };
  }

  // ─── Consent ───────────────────────────────────────────────────────────────

  listConsents(residentId: string): ResidentConsent[] {
    return this.consents.filter((c) => c.residentId === residentId);
  }

  /**
   * Record consent acceptance. `policyStatus` MUST be "active" (caller
   * MUST check that the policy is not Draft before invoking).
   */
  recordConsent(
    residentId: string,
    policySlug: string,
    policyVersion: string,
    policyStatus: "draft" | "active" | "superseded" | "archived",
  ): { ok: boolean; consent?: ResidentConsent; reason?: string } {
    if (policyStatus !== "active") {
      return { ok: false, reason: "policy-not-active" };
    }
    const resident = this.residents.get(residentId);
    if (!resident) return { ok: false, reason: "unknown-resident" };
    if (!policySlug || !policyVersion) {
      return { ok: false, reason: "missing-fields" };
    }
    // Idempotent: same slug+version + already accepted → no-op.
    const existing = this.consents.find(
      (c) =>
        c.residentId === residentId &&
        c.policySlug === policySlug &&
        c.policyVersion === policyVersion &&
        c.status === "accepted",
    );
    if (existing) return { ok: true, consent: existing };

    // If a previous (different-version) consent exists, mark withdrawn.
    for (const c of this.consents) {
      if (
        c.residentId === residentId &&
        c.policySlug === policySlug &&
        c.status === "accepted"
      ) {
        c.status = "withdrawn";
        c.withdrawnAt = isoNow();
      }
    }
    const consent: ResidentConsent = {
      residentId,
      policySlug,
      policyVersion,
      acceptedAt: isoNow(),
      status: "accepted",
    };
    this.consents.push(consent);
    return { ok: true, consent };
  }

  withdrawConsent(
    residentId: string,
    policySlug: string,
    policyVersion: string,
  ): { ok: boolean; reason?: string } {
    const consent = this.consents.find(
      (c) =>
        c.residentId === residentId &&
        c.policySlug === policySlug &&
        c.policyVersion === policyVersion &&
        c.status === "accepted",
    );
    if (!consent) return { ok: false, reason: "not-found" };
    consent.status = "withdrawn";
    consent.withdrawnAt = isoNow();
    return { ok: true };
  }

  // ─── Privacy ──────────────────────────────────────────────────────────────

  getPrivacy(residentId: string): ResidentPrivacySettings | null {
    return this.privacy.get(residentId) ?? null;
  }

  updatePrivacy(
    residentId: string,
    patch: Partial<{
      profileVisibility: ProfileVisibility;
      showFullWalletAddress: boolean;
      showContributionHistory: boolean;
      showRoles: boolean;
      showReputation: boolean;
    }>,
  ): { ok: boolean; privacy?: ResidentPrivacySettings; reason?: string } {
    const existing = this.privacy.get(residentId);
    if (!existing) return { ok: false, reason: "no-privacy" };
    const next: ResidentPrivacySettings = { ...existing, ...patch };
    if (
      next.profileVisibility !== "public" &&
      next.profileVisibility !== "minimal" &&
      next.profileVisibility !== "private"
    ) {
      return { ok: false, reason: "invalid-visibility" };
    }
    this.privacy.set(residentId, next);
    return { ok: true, privacy: next };
  }

  // ─── Sessions ──────────────────────────────────────────────────────────────

  issueSession(params: {
    residentId: string;
    walletAddress: string;
    ttlMs: number;
  }): { ok: boolean; session?: ResidentSession; reason?: string } {
    const resident = this.residents.get(params.residentId);
    if (!resident) return { ok: false, reason: "unknown-resident" };
    const address = normalizeEvmAddress(params.walletAddress);
    if (!address) return { ok: false, reason: "invalid-address" };
    const now = Date.now();
    const session: ResidentSession = {
      id: globalThis.crypto.randomUUID(),
      residentId: params.residentId,
      walletAddress: address,
      issuedAt: new Date(now).toISOString(),
      expiresAt: new Date(now + params.ttlMs).toISOString(),
      lastActiveAt: new Date(now).toISOString(),
    };
    this.sessions.set(session.id, session);
    return { ok: true, session };
  }

  getSession(id: string): ResidentSession | null {
    const session = this.sessions.get(id);
    if (!session) return null;
    if (new Date(session.expiresAt).getTime() < Date.now()) return null;
    return session;
  }

  revokeSession(id: string): boolean {
    return this.sessions.delete(id);
  }

  revokeAllSessions(residentId: string): number {
    let n = 0;
    for (const [id, s] of this.sessions) {
      if (s.residentId === residentId) {
        this.sessions.delete(id);
        n++;
      }
    }
    return n;
  }

  // ─── Reputation Cache ──────────────────────────────────────────────────────

  /**
   * Cache a reputation summary pushed by 016 (or initialize the empty form).
   * This is a read-only cache from the Passport's perspective.
   */
  setReputation(summary: ReputationSummary): void {
    if (!summary.residentId) return;
    this.reputations.set(summary.residentId, summary);
  }

  getReputation(residentId: string): ReputationSummary | null {
    return this.reputations.get(residentId) ?? null;
  }

  /**
   * Returns the "honest empty" reputation summary for a Resident.
   * Used when no 016 data exists. Never a fake number.
   */
  emptyReputation(residentId: string): ReputationSummary {
    return {
      residentId,
      score: null,
      contributionCount: 0,
      approvedContributionCount: 0,
      lastEventAt: null,
      source: "no-contributions-yet",
    };
  }

  // ─── Inspection ────────────────────────────────────────────────────────────

  residentCount(): number {
    return this.residents.size;
  }

  walletCount(): number {
    return this.wallets.size;
  }

  activeResidentCount(): number {
    let n = 0;
    for (const r of this.residents.values()) if (r.status === "active") n++;
    return n;
  }

  reset(): void {
    this.residents.clear();
    this.wallets.clear();
    this.walletsByAddress.clear();
    this.profiles.clear();
    this.roles = [];
    this.badges = [];
    this.consents = [];
    this.privacy.clear();
    this.sessions.clear();
    this.reputations.clear();
  }

  // For tests only.
  __allRoles(): ResidentRoleRecord[] {
    return [...this.roles];
  }
  __allConsents(): ResidentConsent[] {
    return [...this.consents];
  }
}

/**
 * Default singleton.
 */
export const defaultResidentRegistry = new ResidentRegistry();
