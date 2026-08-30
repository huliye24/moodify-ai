/**
 * MOOD NODES 019 — Domain Types
 *
 * Canonical types for the MOOD Node Registry.
 * Authority: MOOD-NODES-019 TASK.md Phases C..L.
 *
 * Distinct from 018 Agents (Node != Agent).
 * Agent = software actor; Node = infrastructure provider.
 *
 * Principles:
 * - Node ID is stable and decoupled from IP / cloud vendor / instance.
 * - Public record MUST NOT contain private IP, SSH, cloud account IDs,
 *   database credentials, internal hostnames, or secret endpoints.
 * - Status comes from heartbeat or operator declaration.
 * - No mining / staking / rewards.
 */

export type NodeRole =
  | "compute"
  | "ai"
  | "storage"
  | "verification";

export type NodeStatus =
  | "draft"
  | "active"
  | "degraded"
  | "offline"
  | "maintenance"
  | "retired";

export interface NodeCapacity {
  cpuCores?: number;
  memoryGb?: number;
  gpuModel?: string;
  gpuCount?: number;
  storageGb?: number;
  bandwidthMbps?: number;
  maxConcurrentJobs?: number;
}

export interface NodeRecord {
  id: string;                  // stable, decoupled from IP / instance
  slug: string;
  name: string;
  role: NodeRole;
  status: NodeStatus;
  capabilities: string[];
  operatorResidentId?: string;
  operatorOrganizationId?: string;
  publicRegion?: string;       // coarse-grained
  version?: string;
  capacity?: NodeCapacity;
  publicEndpoint?: string;     // safe service endpoint only
  createdAt: string;
  updatedAt: string;
  lastSeenAt?: string;
  lastHeartbeatAt?: string;
  healthSummary?: string;       // operator-internal
}

export interface NodeHeartbeat {
  nodeId: string;
  observedAt: string;
  status: "ok" | "degraded" | "error";
  currentJobs?: number;
  capacityAvailable?: number;
  version?: string;
}

export type NodeServiceProofType =
  | "health"
  | "compute-job"
  | "inference"
  | "storage-integrity"
  | "verification";

export interface NodeServiceProof {
  id: string;
  nodeId: string;
  proofType: NodeServiceProofType;
  startedAt?: string;
  completedAt: string;
  status: "passed" | "failed";
  artifactUri?: string;
  artifactHash?: string;
  summary: string;
}

/** Public-safe serializer (no secrets). */
export type PublicNode = Omit<
NodeRecord,
  "operatorResidentId" | "operatorOrganizationId" | "healthSummary"
> & {
  operatorLabel?: string;
};