/**
 * MOOD GOVERNANCE 020 — MIP Governance Types
 *
 * Canonical type definitions for MIP (MOOD Improvement Proposal) records,
 * decisions, implementations, and audit events.
 *
 * Authority: MOOD-GOVERNANCE-020 TASK.md Phases D/E/F/J.
 */

export type MipStatus =
  | "draft"
  | "discussion"
  | "review"
  | "accepted"
  | "rejected"
  | "implemented"
  | "withdrawn"
  | "superseded"
  | "archived";

export type MipCategory =
  | "core"
  | "governance"
  | "identity"
  | "contribution"
  | "agents"
  | "nodes"
  | "security"
  | "economics"
  | "treasury"
  | "token"
  | "other";

export type MipDecisionMethod =
  | "maintainer-consensus"
  | "resident-signal"
  | "future-token-vote"
  | "emergency";

export interface MipRecord {
  id: string; // MIP-000
  slug: string;
  title: string;
  summary: string;
  category: MipCategory;
  status: MipStatus;
  authorResidentIds: string[];
  sponsorResidentIds?: string[];
  createdAt: string;
  updatedAt: string;
  discussionUrl?: string;
  sourcePath?: string;
  sourceSha?: string;
  implementationRefs?: string[];
  supersedes?: string[];
  supersededBy?: string;
  decisionMethod?: MipDecisionMethod;
}

export interface MipDecision {
  id: string;
  mipId: string;
  decision: "accepted" | "rejected" | "returned-for-revision";
  decidedBy: string[];
  decidedAt: string;
  rationale: string;
}

export interface MipImplementation {
  id: string;
  mipId: string;
  ref: string; // commit / PR / deployed route / policy doc
  recordedAt: string;
  recordedBy: string;
  note?: string;
}

export interface MipAuditEvent {
  id: string;
  type:
    | "MipCreated"
    | "MipUpdated"
    | "DiscussionOpened"
    | "ReviewStarted"
    | "RevisionRequested"
    | "MipAccepted"
    | "MipRejected"
    | "MipWithdrawn"
    | "MipImplemented"
    | "MipSuperseded"
    | "MipArchived";
  mipId: string;
  actorResidentId: string;
  timestamp: string;
  previousStatus?: MipStatus;
  nextStatus?: MipStatus;
  reason?: string;
}

export interface PublicMip {
  id: string;
  slug: string;
  title: string;
  summary: string;
  category: MipCategory;
  status: MipStatus;
  authorCount: number;
  sponsorCount: number;
  createdAt: string;
  updatedAt: string;
  discussionUrl?: string;
  decisionMethod?: MipDecisionMethod;
  implementationCount: number;
}

export interface PublicMipDetail extends PublicMip {
  authorResidentIds: string[];
  sponsorResidentIds?: string[];
  implementationRefs?: string[];
  supersedes?: string[];
  supersededBy?: string;
  sourcePath?: string;
  sourceSha?: string;
  decisions: MipDecision[];
  implementationRecords: MipImplementation[];
  auditEvents: MipAuditEvent[];
}

// Lifecycle transition validation
export const ALLOWED_TRANSITIONS: Record<MipStatus, MipStatus[]> = {
  draft: ["discussion", "withdrawn", "archived"],
  discussion: ["review", "draft", "withdrawn", "archived"],
  review: ["accepted", "rejected", "draft", "withdrawn", "archived"],
  accepted: ["implemented", "superseded", "withdrawn"],
  rejected: ["archived"],
  implemented: ["superseded", "archived"],
  withdrawn: ["archived"],
  superseded: ["archived"],
  archived: [],
};

// Statuses that allow public visibility (no internal reviewer notes)
export const PUBLIC_STATUSES: MipStatus[] = [
  "discussion",
  "review",
  "accepted",
  "rejected",
  "implemented",
  "withdrawn",
  "superseded",
  "archived",
];
