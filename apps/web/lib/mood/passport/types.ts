/**
 * MOOD PASSPORT 015 — Resident Identity Types
 *
 * Canonical types for the MOOD Resident Identity system.
 * These types are the single source of truth for all Passport-related code.
 *
 * Principles:
 * - Wallet is a key, not the person.
 * - Resident ID is stable and independent of wallet address.
 * - One Resident may have multiple WalletIdentity records.
 * - No token balance or holding tier affects Resident creation.
 * - Reputation is earned, not bought.
 */

// ─── Core Entities ────────────────────────────────────────────────────────────

export type ResidentStatus = "active" | "suspended" | "deleted";

export interface Resident {
  id: string;                // stable internal ID (e.g. "M7Q4K2")
  createdAt: string;         // ISO 8601
  updatedAt: string;         // ISO 8601
  status: ResidentStatus;
}

export type ChainFamily = "evm";

export interface WalletIdentity {
  id: string;                // primary key
  residentId: string;         // FK to Resident.id
  address: string;           // normalized EVM address (checksummed)
  chainFamily: ChainFamily;
  isPrimary: boolean;        // one wallet may be marked primary per resident
  verifiedAt: string;        // ISO 8601
  addedAt: string;           // ISO 8601
}

export type PreferredLanguage = "zh" | "en";

export interface ResidentProfile {
  residentId: string;        // FK to Resident.id
  displayName: string | null;
  bio: string | null;
  avatarUrl: string | null;
  preferredLanguage: PreferredLanguage | null;
  updatedAt: string;        // ISO 8601
}

// ─── Roles ────────────────────────────────────────────────────────────────────

export type SelfDeclaredRole =
  | "creator"
  | "developer"
  | "researcher"
  | "node-operator"
  | "agent-builder";

export type VerifiedRole =
  | "verified-contributor"
  | "verified-developer"
  | "genesis-builder"
  | "node-operator-verified";

export type ResidentRole = SelfDeclaredRole | VerifiedRole;

export interface ResidentRoleRecord {
  residentId: string;
  role: ResidentRole;
  declaredAt: string;        // ISO 8601
  verifiedAt?: string;      // ISO 8601 — only for VerifiedRole
  source?: string;          // evidence URL or authority reference
}

// ─── Badges ───────────────────────────────────────────────────────────────────

export type BadgeSource = "system" | "governance" | "manual-review";

export interface Badge {
  id: string;
  slug: string;
  title: string;
  description: string;
  source: BadgeSource;
  issuedAt: string;          // ISO 8601
  evidenceUrl?: string;
}

export interface ResidentBadge {
  residentId: string;
  badge: Badge;
  awardedAt: string;         // ISO 8601
}

// ─── Consent ──────────────────────────────────────────────────────────────────

export type ConsentStatus = "accepted" | "withdrawn";

export interface ResidentConsent {
  residentId: string;
  policySlug: string;        // matches LibraryDocument.slug
  policyVersion: string;     // exact version string
  acceptedAt: string;        // ISO 8601
  withdrawnAt?: string;       // ISO 8601 — if withdrawn
  status: ConsentStatus;
}

// ─── Session ──────────────────────────────────────────────────────────────────

export interface ResidentSession {
  id: string;                // opaque session token / session ID
  residentId: string;
  walletAddress: string;     // normalized
  issuedAt: string;          // ISO 8601
  expiresAt: string;         // ISO 8601 — short-lived
  lastActiveAt: string;      // ISO 8601
}

// ─── Privacy ─────────────────────────────────────────────────────────────────

export type WalletDisplayPreference = "truncated" | "full" | "hidden";
export type ProfileVisibility = "public" | "minimal" | "private";

export interface ResidentPrivacySettings {
  residentId: string;
  profileVisibility: ProfileVisibility;   // default: "minimal"
  showFullWalletAddress: boolean;          // default: false (truncated)
  showContributionHistory: boolean;         // default: true (if policy allows)
  showRoles: boolean;                     // default: true
  showReputation: boolean;                // default: true
}

// ─── Signature ────────────────────────────────────────────────────────────────

/**
 * SIWE (EIP-4361) compatible sign-in message.
 * See: https://eips.ethereum.org/EIPS/eip-4361
 */
export interface SiweMessage {
  domain: string;
  address: string;
  statement: string;
  uri: string;
  version: string;           // must be "1"
  chainId: number;
  nonce: string;
  issuedAt: string;          // ISO 8601
  expirationTime?: string;    // ISO 8601
  notBefore?: string;         // ISO 8601
  requestId?: string;
  resources?: string[];
}

/** Raw signature verification result */
export interface SignatureVerificationResult {
  valid: boolean;
  recoveredAddress?: string;  // checksummed
  error?: string;
}

// ─── Nonce ────────────────────────────────────────────────────────────────────

export interface NonceRecord {
  value: string;              // opaque random string
  address: string;           // bound to this address
  createdAt: string;         // ISO 8601
  expiresAt: string;         // ISO 8601 — must be short-lived (e.g. 10 min)
  used: boolean;             // consumed after single use
}

// ─── Reputation (read-only, from 012/016) ────────────────────────────────────

export interface ReputationSummary {
  residentId: string;
  score: number | null;      // null if no reputation yet
  contributionCount: number;
  approvedContributionCount: number;
  lastEventAt: string | null; // ISO 8601
  source: "016-contribution-network" | "no-contributions-yet";
}

// ─── Public Profile ───────────────────────────────────────────────────────────

/**
 * Fields that may be shown publicly when a Resident's profile is public.
 * Derived from Resident + ResidentProfile + WalletIdentity (truncated).
 */
export interface PublicResidentProfile {
  residentId: string;         // short ID e.g. "M7Q4K2"
  displayName: string | null;
  roles: SelfDeclaredRole[];
  verifiedRoles: VerifiedRole[];
  badges: Badge[];
  joinedMonth: string;        // e.g. "Aug 2026" — not exact date
  reputation: ReputationSummary | null;
  contributionCount: number;
}
