/**
 * MOOD CONTRIBUTION 016 — Domain Types
 *
 * Canonical types for the MOOD Contribution Network.
 * Authority: MOOD-CONTRIBUTION-016 TASK.md Phase C.
 *
 * Principles:
 * - Contribution belongs to a Resident, not a wallet address.
 * - State machine is single and authoritative (server-side).
 * - Reputation is append-only.
 * - Pending reward has NO chain side effect.
 */

import type { ResidentId } from "../passport/types.ts";

// ─── Task ─────────────────────────────────────────────────────────────────────

export type ContributionCategory =
  | "code"
  | "audio-testing"
  | "dataset"
  | "research"
  | "documentation"
  | "translation"
  | "bug-report"
  | "community"
  | "other";

export type ContributionTaskStatus =
  | "draft"
  | "active"
  | "paused"
  | "completed"
  | "archived";

export interface ContributionTask {
  id: string;
  slug: string;
  title: string;
  summary: string;
  description: string;
  category: ContributionCategory;
  status: ContributionTaskStatus;
  evidenceRequirements: string[];
  defaultReputationPoints: number;
  defaultRewardUnits?: string; // stringly-typed to decouple from any token
  deadline?: string;
  maxApprovals?: number;
  createdByResidentId: ResidentId;
  createdAt: string;
  updatedAt: string;
}

// ─── Submission ───────────────────────────────────────────────────────────────

export type SubmissionStatus =
  | "submitted"
  | "under_review"
  | "changes_requested"
  | "approved"
  | "rejected"
  | "withdrawn";

export interface ContributionSubmission {
  id: string;
  taskId: string;
  residentId: ResidentId;
  summary: string;
  evidenceText?: string;
  status: SubmissionStatus;
  revision: number;
  createdAt: string;
  updatedAt: string;
  reviewedByResidentId?: ResidentId;
  reviewedAt?: string;
  reviewerNote?: string;       // private to reviewer
}

// ─── Evidence ─────────────────────────────────────────────────────────────────

export type EvidenceType =
  | "url"
  | "github-pr"
  | "github-commit"
  | "document"
  | "artifact"
  | "text";

export interface ContributionEvidence {
  id: string;
  submissionId: string;
  type: EvidenceType;
  value: string;          // url or text
  label?: string;
  createdAt: string;
}

// ─── Reputation ───────────────────────────────────────────────────────────────

export type ReputationSource =
  | "contribution"
  | "governance"
  | "system-adjustment";

export interface ReputationEvent {
  id: string;
  residentId: ResidentId;
  submissionId?: string;
  pointsDelta: number; // can be negative for adjustments
  reason: string;
  source: ReputationSource;
  createdAt: string;
  createdByResidentId: ResidentId; // actor (reviewer or system)
}

// Cached aggregate - must equal sum of ReputationEvent pointsDelta for resident.
export interface ResidentReputation {
  residentId: ResidentId;
  score: number;
  lastEventAt: string | null;
  contributionCount: number;
  approvedContributionCount: number;
  source: "events" | "no-contributions-yet";
}

// ─── Pending Reward ───────────────────────────────────────────────────────────

export type PendingRewardStatus =
  | "pending"
  | "included_in_future_snapshot"
  | "cancelled";

export interface PendingRewardEvent {
  id: string;
  residentId: ResidentId;
  submissionId: string;
  rewardUnits: string; // stringly-typed; never interpreted as on-chain entitlement
  status: PendingRewardStatus;
  createdAt: string;
  updatedAt: string;
  reason?: string;
  // History: historical field naming; NOT a present on-chain entitlement.
}

// ─── Audit Trail ──────────────────────────────────────────────────────────────

export type ContributionAuditType =
  | "TaskCreated"
  | "TaskStatusChanged"
  | "SubmissionCreated"
  | "SubmissionResubmitted"
  | "SubmissionWithdrawn"
  | "ReviewStarted"
  | "ChangesRequested"
  | "SubmissionApproved"
  | "SubmissionRejected"
  | "ReputationGranted"
  | "ReputationAdjusted"
  | "PendingRewardRecorded"
  | "PendingRewardCancelled";

export interface ContributionAuditEvent {
  id: string;
  type: ContributionAuditType;
  actorResidentId: ResidentId; // "system" is the platform itself
  taskId?: string;
  submissionId?: string;
  reputationEventId?: string;
  pendingRewardId?: string;
  previousStatus?: string;
  nextStatus?: string;
  note?: string;
  createdAt: string;
}

// ─── Review Action ─────────────────────────────────────────────────────────────

export interface ReviewActionInput {
  decision: "approve" | "request-changes" | "reject";
  reviewerResidentId: ResidentId;
  note?: string;
}

export interface ReviewActionResult {
  ok: boolean;
  reason?: string;
  submission?: ContributionSubmission;
  reputationEventId?: string;
  pendingRewardId?: string;
  auditEventIds: string[];
}