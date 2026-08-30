/**
 * MOOD NODES 019 — Node Registry
 *
 * In-memory authoritative registry for NodeRecord + heartbeat + service proofs.
 * Distinct from 018 AgentRegistry.
 *
 * Authority: MOOD-NODES-019 TASK.md Phases B..L.
 */

import type {
  NodeCapacity,
  NodeHeartbeat,
  NodeRecord,
  NodeRole,
  NodeServiceProof,
  NodeServiceProofType,
  NodeStatus,
  PublicNode,
} from "./types.ts";

const STALE_HEARTBEAT_MS = 30 * 60 * 1000; // 30 min

function nowIso(): string {
  return new Date().toISOString();
}

function publicNode(n: NodeRecord): PublicNode {
  return {
    id: n.id,
    slug: n.slug,
    name: n.name,
    role: n.role,
    status: n.status,
    capabilities: n.capabilities,
    publicRegion: n.publicRegion,
    version: n.version,
    capacity: n.capacity,
    publicEndpoint: n.publicEndpoint,
    createdAt: n.createdAt,
    updatedAt: n.updatedAt,
    lastSeenAt: n.lastSeenAt,
    lastHeartbeatAt: n.lastHeartbeatAt,
    operatorLabel: n.operatorResidentId
      ? `Resident ${n.operatorResidentId}`
      : n.operatorOrganizationId
        ? `Org ${n.operatorOrganizationId}`
        : undefined,
  };
}

export class NodeRegistry {
  private nodes: Map<string, NodeRecord> = new Map();
  private bySlugMap: Map<string, string> = new Map();
  private heartbeats: Map<string, NodeHeartbeat[]> = new Map();
  private proofs: Map<string, NodeServiceProof[]> = new Map();

  // ─── Registration ──────────────────────────────────────────────────────────

  register(input: {
    slug: string;
    name: string;
    role: NodeRole;
    capabilities: string[];
    operatorResidentId?: string;
    operatorOrganizationId?: string;
    publicRegion?: string;
    version?: string;
    capacity?: NodeCapacity;
    publicEndpoint?: string;
  }): NodeRecord {
    if (!input.operatorResidentId && !input.operatorOrganizationId) {
      throw new Error("INV-019-02: node requires operator");
    }
    if (this.bySlugMap.has(input.slug)) {
      throw new Error(`node-slug-exists:${input.slug}`);
    }
    const now = nowIso();
    const id = `node_${this.nodes.size + 1}`;
    const node: NodeRecord = {
      id,
      slug: input.slug,
      name: input.name,
      role: input.role,
      status: "draft",
      capabilities: input.capabilities,
      operatorResidentId: input.operatorResidentId,
      operatorOrganizationId: input.operatorOrganizationId,
      publicRegion: input.publicRegion,
      version: input.version,
      capacity: input.capacity,
      publicEndpoint: input.publicEndpoint,
      createdAt: now,
      updatedAt: now,
    };
    this.nodes.set(id, node);
    this.bySlugMap.set(input.slug, id);
    this.heartbeats.set(id, []);
    this.proofs.set(id, []);
    return node;
  }

  activate(nodeId: string, actorResidentId?: string): NodeRecord {
    const n = this.requireNode(nodeId);
    if (actorResidentId && n.operatorResidentId !== actorResidentId) {
      throw new Error("not-operator");
    }
    n.status = "active";
    n.updatedAt = nowIso();
    return n;
  }

  setMaintenance(nodeId: string, actorResidentId?: string): NodeRecord {
    const n = this.requireNode(nodeId);
    if (actorResidentId && n.operatorResidentId !== actorResidentId) {
      throw new Error("not-operator");
    }
    n.status = "maintenance";
    n.updatedAt = nowIso();
    return n;
  }

  retire(nodeId: string, actorResidentId?: string): NodeRecord {
    const n = this.requireNode(nodeId);
    if (actorResidentId && n.operatorResidentId !== actorResidentId) {
      throw new Error("not-operator");
    }
    n.status = "retired";
    n.updatedAt = nowIso();
    return n;
  }

  // ─── Heartbeat ─────────────────────────────────────────────────────────────

  recordHeartbeat(input: NodeHeartbeat): void {
    const n = this.requireNode(input.nodeId);
    n.lastSeenAt = input.observedAt;
    n.lastHeartbeatAt = input.observedAt;
    if (input.version) n.version = input.version;
    n.updatedAt = nowIso();
    this.heartbeats.get(n.id)?.push(input);
  }

  effectiveStatus(nodeId: string): NodeStatus {
    const n = this.requireNode(nodeId);
    if (n.status === "retired" || n.status === "draft") return n.status;
    if (n.status === "maintenance") return "maintenance";
    // active/degraded/offline derived from heartbeat
    if (!n.lastSeenAt) return "offline";
    const age = Date.now() - new Date(n.lastSeenAt).getTime();
    if (Number.isNaN(age) || age > STALE_HEARTBEAT_MS) return "offline";
    return n.status === "active" ? "active" : "degraded";
  }

  // ─── Service Proof ────────────────────────────────────────────────────────

  recordProof(input: {
    nodeId: string;
    proofType: NodeServiceProofType;
    startedAt?: string;
    artifactUri?: string;
    artifactHash?: string;
    summary: string;
  }): NodeServiceProof {
    const n = this.requireNode(input.nodeId);
    const proof: NodeServiceProof = {
      id: `proof_${this.proofs.get(n.id)?.length ?? 0}_${Date.now()}`,
      nodeId: n.id,
      proofType: input.proofType,
      startedAt: input.startedAt,
      completedAt: nowIso(),
      status: "passed",
      artifactUri: input.artifactUri,
      artifactHash: input.artifactHash,
      summary: input.summary,
    };
    this.proofs.get(n.id)?.push(proof);
    n.updatedAt = proof.completedAt;
    return proof;
  }

  // ─── Reads ─────────────────────────────────────────────────────────────────

  requireNode(id: string): NodeRecord {
    const n = this.nodes.get(id);
    if (!n) throw new Error("node-not-found");
    return n;
  }

  bySlug(slug: string): NodeRecord | undefined {
    const id = this.bySlugMap.get(slug);
    return id ? this.nodes.get(id) : undefined;
  }

  list(filter?: { role?: NodeRole; status?: NodeStatus }): NodeRecord[] {
    const out: NodeRecord[] = [];
    for (const n of this.nodes.values()) {
      if (filter?.role && n.role !== filter.role) continue;
      if (filter?.status && n.status !== filter.status) continue;
      out.push(n);
    }
    return out;
  }

  publicList(): PublicNode[] {
    return this.list().map(publicNode);
  }

  publicBySlug(slug: string): PublicNode | undefined {
    const id = this.bySlugMap.get(slug);
    if (!id) return undefined;
    const n = this.nodes.get(id);
    if (!n) return undefined;
    return publicNode(n);
  }

  proofsFor(nodeId: string): NodeServiceProof[] {
    return this.proofs.get(nodeId) ?? [];
  }

  /**
   * Counts for /network. Returns real data only.
   */
  counts(): {
    total: number;
    active: number;
    degraded: number;
    offline: number;
    byRole: Record<NodeRole, number>;
  } {
    let active = 0;
    let degraded = 0;
    let offline = 0;
    const byRole: Record<NodeRole, number> = {
      compute: 0,
      ai: 0,
      storage: 0,
      verification: 0,
    };
    for (const n of this.nodes.values()) {
      const s = this.effectiveStatus(n.id);
      if (s === "active") active++;
      else if (s === "degraded") degraded++;
      else if (s === "offline") offline++;
      byRole[n.role]++;
    }
    return { total: this.nodes.size, active, degraded, offline, byRole };
  }
}

export const nodeRegistry = new NodeRegistry();
