/**
 * MOOD NETWORK 017 — Observatory Types
 *
 * Authority: MOOD-NETWORK-017 TASK.md Phases C/D/E.
 *
 * Every metric carries:
 * - value or null (real | unknown)
 * - state: available | unavailable | coming-soon | stale
 * - source (provenance)
 * - updatedAt
 * - definition
 */

export type MetricState =
  | "available"
  | "unavailable"
  | "coming-soon"
  | "stale";

export interface MetricValue<T = number | null> {
  value: T | null;
  state: MetricState;
  source: string;
  updatedAt?: string;
  definition?: string;
}

export interface NetworkOverview {
  status: NetworkStatus;
  generatedAt: string;
  sourceUpdatedAt: string;
  metrics: {
    residents?: MetricValue;
    contributors?: MetricValue;
    openTasks?: MetricValue;
    submissions?: MetricValue;
    approvedContributions?: MetricValue;
    reputationEvents?: MetricValue;
    pendingReward?: MetricValue;
    applications?: MetricValue;
    agents?: MetricValue;
    nodes?: MetricValue;
    mips?: MetricValue;
  };
}

export type NetworkStatus =
  | "operational"
  | "degraded"
  | "partial"
  | "maintenance"
  | "unknown";

export type ActivityKind =
  | "ResidentJoined"
  | "TaskPublished"
  | "SubmissionSubmitted"
  | "SubmissionApproved"
  | "SubmissionRejected"
  | "ReputationGranted"
  | "ApplicationRegistered"
  | "AgentRegistered"
  | "AgentTaskCompleted"
  | "NodeRegistered"
  | "MIPPublished"
  | "MIPReviewStarted"
  | "MIPAccepted"
  | "MIPImplemented";

export interface PublicActivityEvent {
  type: ActivityKind;
  timestamp: string;
  residentShortId?: string;
  taskSlug?: string;
  submissionId?: string;
  reputationDelta?: number;
}
