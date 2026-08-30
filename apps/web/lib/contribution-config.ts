/* MOOD-GENESIS-006: Contribution Network — canonical configuration.
 *
 * Single source of truth for:
 *   - Contribution categories (controlled enum)
 *   - Task / submission / reward status enums (mirrors Drizzle column enums)
 *   - Submission status transition table (validated server-side)
 *   - Reputation / Reward exact arithmetic parameters
 *
 * IMPORTANT: This module never performs token transfer, wallet signing,
 * private-key handling, or contract deployment. It is configuration only.
 *
 * See docs/protocol/CONTRIBUTION_NETWORK.md for full specification.
 */

import { MOOD_TOKEN } from "./mood-token";

/** Contribution categories (controlled enum, do not add free-form values). */
export const CONTRIBUTION_CATEGORIES = [
  "code",
  "audio-testing",
  "dataset",
  "research",
  "documentation",
  "translation",
  "bug-report",
  "community",
  "other",
] as const;

export type ContributionCategory = typeof CONTRIBUTION_CATEGORIES[number];

/** Task status enum — mirrors contribution_tasks.status in schema.ts. */
export const TASK_STATUSES = [
  "draft",
  "active",
  "paused",
  "completed",
  "archived",
] as const;

export type TaskStatus = typeof TASK_STATUSES[number];

/** Submission status enum — mirrors contribution_submissions.status. */
export const SUBMISSION_STATUSES = [
  "submitted",
  "under_review",
  "changes_requested",
  "approved",
  "rejected",
  "withdrawn",
] as const;

export type SubmissionStatus = typeof SUBMISSION_STATUSES[number];

/** Reward event status enum — mirrors reward_events.status. */
export const REWARD_STATUSES = [
  "pending",
  "included_in_snapshot",
  "distributed",
  "cancelled",
] as const;

export type RewardStatus = typeof REWARD_STATUSES[number];

/** Public-facing subset of task statuses (draft is hidden from public). */
export const PUBLIC_TASK_STATUSES: readonly TaskStatus[] = ["active", "paused", "completed"] as const;

/** Submission statuses a contributor may transition into themselves. */
export const SELF_TRANSITIONABLE_SUBMISSION_STATUSES: readonly SubmissionStatus[] = ["withdrawn"] as const;

/** Submission lifecycle — server-validated transition table.
 *
 * Keys are the FROM status; values are the set of legal next statuses.
 * Any transition outside this table must be rejected by the server with
 * SUBMISSION_INVALID_TRANSITION. */
export const SUBMISSION_TRANSITIONS: Readonly<Record<SubmissionStatus, readonly SubmissionStatus[]>> = {
  submitted: ["under_review", "withdrawn"],
  under_review: ["changes_requested", "approved", "rejected"],
  changes_requested: ["submitted", "withdrawn"],
  approved: [], // Terminal until manual rollback appends a negative event.
  rejected: [], // Terminal unless explicitly restored by audit action.
  withdrawn: [], // Terminal; contributor can submit again to a new submission id.
};

/** Reputation event types (append-only ledger). */
export const REPUTATION_EVENT_TYPES = [
  "approval",
  "rollback",
  "manual_adjust",
] as const;

export type ReputationEventType = typeof REPUTATION_EVENT_TYPES[number];

/** Review event types (append-only review history). */
export const REVIEW_EVENT_TYPES = [
  "created",
  "status_change",
  "changes_requested",
  "approved",
  "rejected",
  "withdrawn",
  "reopened",
  "reward_change",
] as const;

export type ReviewEventType = typeof REVIEW_EVENT_TYPES[number];

/** Canonical configuration object — exported as a single source of truth. */
export const CONTRIBUTION_CONFIG = {
  /** Schema version for the contribution task/submission/reward JSON envelopes. */
  schemaVersion: "moodify-contribution-v1",
  /** Single source for the protocol token metadata. */
  chainId: MOOD_TOKEN.chainId,
  network: MOOD_TOKEN.network,
  tokenName: MOOD_TOKEN.name,
  tokenSymbol: MOOD_TOKEN.symbol,
  tokenAddress: MOOD_TOKEN.address,
  tokenDecimals: MOOD_TOKEN.decimals,
  /** Atomic multiplier — 1 MOOD = 10^18 atomic units. */
  atomicMultiplier: 10n ** 18n,
  /** Categories allowed at task creation time. */
  categories: CONTRIBUTION_CATEGORIES,
  taskStatuses: TASK_STATUSES,
  publicTaskStatuses: PUBLIC_TASK_STATUSES,
  submissionStatuses: SUBMISSION_STATUSES,
  rewardStatuses: REWARD_STATUSES,
  reviewEventTypes: REVIEW_EVENT_TYPES,
  reputationEventTypes: REPUTATION_EVENT_TYPES,
  submissionTransitions: SUBMISSION_TRANSITIONS,
  /** Maximum length of summary text. */
  summaryMaxLength: 400,
  /** Maximum length of free-form evidence text. */
  evidenceTextMaxLength: 4000,
  /** Maximum number of URLs in a single submission. */
  evidenceUrlMaxCount: 10,
  /** Maximum length of a reason/note string. */
  reasonMaxLength: 500,
  /** Maximum length of the task description text. */
  descriptionMaxLength: 8000,
  /** Maximum length of requirements/evidence instructions text. */
  blockTextMaxLength: 4000,
  /** Maximum allowed default reward points. */
  maxRewardPoints: 1_000_000,
  /** Maximum allowed default reward MOOD (decimal string length cap, not amount cap). */
  maxRewardDecimalLength: 30,
  /** Maximum deadline window (days from now). Past deadlines must be rejected. */
  maxDeadlineDays: 365,
  /** Maximum total pending reward budget allowed across the network (in atomic units).
   *  Set to a clearly-labelled local-development cap. Production deployment must
   *  override this via canonical human approval; otherwise production publishing
   *  must remain disabled. */
  genesisPoolCeilingAtomic: (10_000_000n * 10n ** 18n).toString(),
  /** Soft ceiling for total pending rewards (atomic). When exceeded, server-side
   *  approval endpoints refuse additional pending approvals. */
} as const;

export type ContributionConfig = typeof CONTRIBUTION_CONFIG;

/** Type guard helpers. */
export function isContributionCategory(value: string): value is ContributionCategory {
  return (CONTRIBUTION_CATEGORIES as readonly string[]).includes(value);
}

export function isTaskStatus(value: string): value is TaskStatus {
  return (TASK_STATUSES as readonly string[]).includes(value);
}

export function isSubmissionStatus(value: string): value is SubmissionStatus {
  return (SUBMISSION_STATUSES as readonly string[]).includes(value);
}

export function isRewardStatus(value: string): value is RewardStatus {
  return (REWARD_STATUSES as readonly string[]).includes(value);
}

export function isPublicTaskStatus(value: string): value is TaskStatus {
  return (PUBLIC_TASK_STATUSES as readonly string[]).includes(value);
}

/** Returns true if `from -> to` is an allowed submission transition. */
export function isAllowedSubmissionTransition(from: SubmissionStatus, to: SubmissionStatus): boolean {
  const allowed = SUBMISSION_TRANSITIONS[from];
  return allowed.includes(to);
}

/** Convert a plain user-typed URL string to a normalized https URL.
 *  Accepts "https://", "http://", or bare "github.com/..." forms. Bare hosts
 *  are normalized to https:// for canonical storage. */
export function normalizeEvidenceUrl(raw: string): string | null {
  const value = raw.trim();
  if (!value) return null;
  let candidate = value;
  if (!/^https?:\/\//i.test(candidate)) {
    if (/^[a-z0-9.-]+\.[a-z]{2,}/i.test(candidate)) {
      candidate = `https://${candidate}`;
    } else {
      return null;
    }
  }
  let parsed: URL;
  try {
    parsed = new URL(candidate);
  } catch {
    return null;
  }
  if (parsed.protocol !== "https:" && parsed.protocol !== "http:") return null;
  return parsed.toString();
}

/** Crude GitHub PR/commit URL detector for evidence normalization. */
export function isGitHubPrOrCommitUrl(value: string): boolean {
  try {
    const url = new URL(value);
    if (!/(^|\.)github\.com$/i.test(url.hostname)) return false;
    return /\/(pull|pulls|commit|commits)\/\d+/.test(url.pathname);
  } catch {
    return false;
  }
}
