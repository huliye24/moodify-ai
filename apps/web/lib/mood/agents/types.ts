/**
 * MOOD AGENTS 018 — Domain Types
 *
 * Canonical types for the MOOD AI Agent Registry.
 * Authority: MOOD-AGENTS-018 TASK.md Phases C..I.
 *
 * Principles:
 * - Agent ID is stable and decoupled from any API key, model provider, or
 *   runtime endpoint.
 * - Public record MUST NOT contain API keys, system prompts, secret endpoints,
 *   or any credentials.
 * - Status comes from real heartbeats or operator declaration. Default is
 *   `Registered` (no heartbeat == no claim of "Online").
 * - Agent NEVER holds funds. No treasury / wallet / signer permissions.
 */

export type AgentStatus =
  | "draft"
  | "active"
  | "paused"
  | "degraded"
  | "offline"
  | "retired";

export type AgentCapability =
  | "audio-analysis"
  | "research"
  | "documentation"
  | "code-assistance"
  | "proof-verification"
  | "curation"
  | "task-assistance"
  | "node-operations"
  | "other";

export interface AgentRecord {
  id: string;                   // stable ID, decoupled from API key
  slug: string;
  name: string;
  description: string;
  status: AgentStatus;
  capabilities: AgentCapability[];
  runtimeType?: string;         // public-safe label, not implementation
  modelProvider?: string;       // public-safe label, not secret
  modelName?: string;           // public-safe label, not weights/keys
  version?: string;
  operatorResidentId?: string;
  operatorOrganizationId?: string;
  public: boolean;              // opt-in to public registry
  createdAt: string;
  updatedAt: string;
  // Real heartbeat fields:
  lastSeenAt?: string;
  lastTaskAt?: string;
  lastSuccessAt?: string;
  lastErrorAt?: string;
  healthSummary?: string;       // operator-authored summary
}

export interface AgentHeartbeat {
  agentId: string;
  observedAt: string;
  status: "ok" | "degraded" | "error";
  message?: string;
}

export type AgentTaskRunStatus =
  | "queued"
  | "running"
  | "completed"
  | "failed"
  | "cancelled";

export interface AgentTaskRun {
  id: string;
  agentId: string;
  taskType: string;
  externalTaskId?: string;
  status: AgentTaskRunStatus;
  startedAt?: string;
  completedAt?: string;
  resultRef?: string;
}

export type AgentProofType =
  | "artifact"
  | "report"
  | "commit"
  | "analysis"
  | "verification"
  | "other";

export interface AgentProof {
  id: string;
  agentId: string;
  taskRunId?: string;
  proofType: AgentProofType;
  uri?: string;
  hash?: string;
  summary: string;
  createdAt: string;
}

/** Public-safe agent serializer output (no secrets). */
export type PublicAgent = Omit<
  AgentRecord,
  "operatorResidentId" | "operatorOrganizationId" | "healthSummary"
> & {
  operatorLabel?: string;       // public-safe label like "Resident M7Q4K2" or "Org"
};