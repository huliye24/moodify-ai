/**
 * MOOD AGENTS 018 — Registry
 *
 * In-memory authoritative registry for AgentRecord + heartbeat + task runs +
 * proofs. The single source of truth that 017 (Network Observatory) reads
 * to populate the /network "agents" metric.
 *
 * Authority: MOOD-AGENTS-018 TASK.md Phases B..P.
 */

import type {
  AgentCapability,
  AgentHeartbeat,
  AgentProof,
  AgentRecord,
  AgentStatus,
  AgentTaskRun,
  AgentTaskRunStatus,
  PublicAgent,
} from "./types.ts";

const STALE_HEARTBEAT_MS = 30 * 60 * 1000; // 30 min

function nowIso(): string {
  return new Date().toISOString();
}

function publicAgent(a: AgentRecord): PublicAgent {
  return {
    id: a.id,
    slug: a.slug,
    name: a.name,
    description: a.description,
    status: a.status,
    capabilities: a.capabilities,
    runtimeType: a.runtimeType,
    modelProvider: a.modelProvider,
    modelName: a.modelName,
    version: a.version,
    public: a.public,
    createdAt: a.createdAt,
    updatedAt: a.updatedAt,
    lastSeenAt: a.lastSeenAt,
    lastTaskAt: a.lastTaskAt,
    lastSuccessAt: a.lastSuccessAt,
    lastErrorAt: a.lastErrorAt,
    operatorLabel: a.operatorResidentId
      ? `Resident ${a.operatorResidentId}`
      : a.operatorOrganizationId
        ? `Org ${a.operatorOrganizationId}`
        : undefined,
  };
}

export class AgentRegistry {
  private agents: Map<string, AgentRecord> = new Map();
  private bySlugMap: Map<string, string> = new Map();
  private heartbeats: Map<string, AgentHeartbeat[]> = new Map();
  private taskRuns: Map<string, AgentTaskRun[]> = new Map();
  private proofs: Map<string, AgentProof[]> = new Map();

  // ─── Registration ──────────────────────────────────────────────────────────

  register(input: {
    slug: string;
    name: string;
    description: string;
    capabilities: AgentCapability[];
    runtimeType?: string;
    modelProvider?: string;
    modelName?: string;
    version?: string;
    operatorResidentId?: string;
    operatorOrganizationId?: string;
    public: boolean;
  }): AgentRecord {
    if (!input.operatorResidentId && !input.operatorOrganizationId) {
      throw new Error("INV-018-02: agent requires operator");
    }
    if (this.bySlugMap.has(input.slug)) {
      throw new Error(`agent-slug-exists:${input.slug}`);
    }
    const now = nowIso();
    const id = `agent_${this.agents.size + 1}`;
    const agent: AgentRecord = {
      id,
      slug: input.slug,
      name: input.name,
      description: input.description,
      status: "draft",     // operator must explicitly activate
      capabilities: input.capabilities,
      runtimeType: input.runtimeType,
      modelProvider: input.modelProvider,
      modelName: input.modelName,
      version: input.version,
      operatorResidentId: input.operatorResidentId,
      operatorOrganizationId: input.operatorOrganizationId,
      public: input.public,
      createdAt: now,
      updatedAt: now,
    };
    this.agents.set(id, agent);
    this.bySlugMap.set(input.slug, id);
    this.heartbeats.set(id, []);
    this.taskRuns.set(id, []);
    this.proofs.set(id, []);
    return agent;
  }

  activate(agentId: string, actorResidentId?: string): AgentRecord {
    const a = this.requireAgent(agentId);
    if (actorResidentId && a.operatorResidentId !== actorResidentId) {
      throw new Error("not-operator");
    }
    a.status = "active";
    a.updatedAt = nowIso();
    return a;
  }

  pause(agentId: string, actorResidentId?: string): AgentRecord {
    const a = this.requireAgent(agentId);
    if (actorResidentId && a.operatorResidentId !== actorResidentId) {
      throw new Error("not-operator");
    }
    a.status = "paused";
    a.updatedAt = nowIso();
    return a;
  }

  retire(agentId: string, actorResidentId?: string): AgentRecord {
    const a = this.requireAgent(agentId);
    if (actorResidentId && a.operatorResidentId !== actorResidentId) {
      throw new Error("not-operator");
    }
    a.status = "retired";
    a.updatedAt = nowIso();
    return a;
  }

  // ─── Heartbeat ─────────────────────────────────────────────────────────────

  recordHeartbeat(input: AgentHeartbeat): void {
    const a = this.requireAgent(input.agentId);
    if (input.status === "ok") {
      a.lastSeenAt = input.observedAt;
    }
    if (input.status === "error") {
      a.lastErrorAt = input.observedAt;
    }
    if (input.message) {
      a.healthSummary = input.message;
    }
    a.updatedAt = nowIso();
    this.heartbeats.get(a.id)?.push(input);
  }

  /** Compute effective runtime status from heartbeat + declared state. */
  effectiveStatus(agentId: string): AgentStatus {
    const a = this.requireAgent(agentId);
    if (a.status === "retired" || a.status === "draft") return a.status;
    if (a.status === "paused") return "paused";
    // active or degraded depends on heartbeat freshness
    if (!a.lastSeenAt) {
      // No heartbeat -> never "online" until we have one.
      return "offline";
    }
    const ageMs = Date.now() - new Date(a.lastSeenAt).getTime();
    if (Number.isNaN(ageMs)) return "offline";
    if (ageMs > STALE_HEARTBEAT_MS) return "offline";
    // recent error overrides active
    if (a.lastErrorAt && a.lastErrorAt > (a.lastSuccessAt ?? "")) {
      return "degraded";
    }
    return "active";
  }

  // ─── Task runs ─────────────────────────────────────────────────────────────

  startTaskRun(input: {
    agentId: string;
    taskType: string;
    externalTaskId?: string;
  }): AgentTaskRun {
    const a = this.requireAgent(input.agentId);
    if (a.status === "retired" || a.status === "draft") {
      throw new Error("agent-not-active");
    }
    const run: AgentTaskRun = {
      id: `run_${this.taskRuns.get(a.id)?.length ?? 0}_${Date.now()}`,
      agentId: a.id,
      taskType: input.taskType,
      externalTaskId: input.externalTaskId,
      status: "running",
      startedAt: nowIso(),
    };
    this.taskRuns.get(a.id)?.push(run);
    a.lastTaskAt = run.startedAt;
    a.updatedAt = run.startedAt!;
    return run;
  }

  finishTaskRun(
    agentId: string,
    runId: string,
    status: AgentTaskRunStatus,
    resultRef?: string,
  ): AgentTaskRun {
    const a = this.requireAgent(agentId);
    const list = this.taskRuns.get(a.id);
    if (!list) throw new Error("task-run-not-found");
    const r = list.find((x) => x.id === runId);
    if (!r) throw new Error("task-run-not-found");
    r.status = status;
    r.completedAt = nowIso();
    if (resultRef) r.resultRef = resultRef;
    if (status === "completed") {
      a.lastSuccessAt = r.completedAt;
    } else if (status === "failed") {
      a.lastErrorAt = r.completedAt;
    }
    a.updatedAt = r.completedAt;
    return r;
  }

  // ─── Proofs ────────────────────────────────────────────────────────────────

  recordProof(input: Omit<AgentProof, "id" | "createdAt">): AgentProof {
    const a = this.requireAgent(input.agentId);
    const proof: AgentProof = {
      id: `proof_${this.proofs.get(a.id)?.length ?? 0}_${Date.now()}`,
      createdAt: nowIso(),
      ...input,
    };
    this.proofs.get(a.id)?.push(proof);
    a.updatedAt = proof.createdAt;
    return proof;
  }

  // ─── Reads ─────────────────────────────────────────────────────────────────

  requireAgent(id: string): AgentRecord {
    const a = this.agents.get(id);
    if (!a) throw new Error("agent-not-found");
    return a;
  }

  bySlug(slug: string): AgentRecord | undefined {
    const id = this.bySlugMap.get(slug);
    return id ? this.agents.get(id) : undefined;
  }

  list(filter?: { status?: AgentStatus }): AgentRecord[] {
    const out: AgentRecord[] = [];
    for (const a of this.agents.values()) {
      if (filter?.status && a.status !== filter.status) continue;
      out.push(a);
    }
    return out;
  }

  publicList(): PublicAgent[] {
    return this.list().filter((a) => a.public).map(publicAgent);
  }

  publicBySlug(slug: string): PublicAgent | undefined {
    const id = this.bySlugMap.get(slug);
    if (!id) return undefined;
    const a = this.agents.get(id);
    if (!a || !a.public) return undefined;
    return publicAgent(a);
  }

  proofsFor(agentId: string): AgentProof[] {
    return this.proofs.get(agentId) ?? [];
  }

  taskRunsFor(agentId: string): AgentTaskRun[] {
    return this.taskRuns.get(agentId) ?? [];
  }

  /**
   * Counts for /network. Returns real data only.
   */
  counts(): { total: number; active: number; degraded: number; offline: number } {
    let active = 0;
    let degraded = 0;
    let offline = 0;
    for (const a of this.agents.values()) {
      const s = this.effectiveStatus(a.id);
      if (s === "active") active++;
      else if (s === "degraded") degraded++;
      else if (s === "offline") offline++;
    }
    return { total: this.agents.size, active, degraded, offline };
  }
}

export const agentRegistry = new AgentRegistry();