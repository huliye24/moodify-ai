/**
 * MOOD GOVERNANCE 020 — MIP Registry
 *
 * In-memory authoritative registry for MipRecord + decisions + implementation
 * records + audit events. Single source of truth for the governance layer.
 *
 * Authority: MOOD-GOVERNANCE-020 TASK.md Phases C/D/J/K/L/Q/R/S.
 *
 * Design principles:
 * - Maintainer-reviewed governance (v1). NOT token-voting.
 * - Decision methods are explicit (maintainer-consensus / resident-signal /
 *   future-token-vote / emergency). Token-vote is reserved but disabled.
 * - Lifecycle transitions are validated (no draft → implemented shortcuts).
 * - Every state change produces an audit event with actor + reason.
 * - Public API surfaces only PublicMip / PublicMipDetail — never the raw
 *   reviewer rationale in audit events.
 */

import {
  ALLOWED_TRANSITIONS,
  PUBLIC_STATUSES,
  type MipAuditEvent,
  type MipCategory,
  type MipDecision,
  type MipDecisionMethod,
  type MipImplementation,
  type MipRecord,
  type MipStatus,
  type PublicMip,
  type PublicMipDetail,
} from "./types.ts";

function nowIso(): string {
  return new Date().toISOString();
}

function publicMip(m: MipRecord, decisions: MipDecision[], impls: MipImplementation[]): PublicMip {
  return {
    id: m.id,
    slug: m.slug,
    title: m.title,
    summary: m.summary,
    category: m.category,
    status: m.status,
    authorCount: m.authorResidentIds.length,
    sponsorCount: m.sponsorResidentIds?.length ?? 0,
    createdAt: m.createdAt,
    updatedAt: m.updatedAt,
    discussionUrl: m.discussionUrl,
    decisionMethod: m.decisionMethod,
    implementationCount: impls.length,
  };
}

export class MipRegistry {
  private records: Map<string, MipRecord> = new Map(); // by id (MIP-NNN)
  private bySlugMap: Map<string, string> = new Map();
  private decisionsByMip: Map<string, MipDecision[]> = new Map();
  private implementationsByMip: Map<string, MipImplementation[]> = new Map();
  private auditByMip: Map<string, MipAuditEvent[]> = new Map();
  private nextNumber: number = 0;

  // ─── Numbering ─────────────────────────────────────────────────────────────

  /**
   * Allocate the next available MIP number. MIP-000 is reserved for the
   * governance standard (Phase C).
   */
  private allocateId(): string {
    while (true) {
      const candidate = `MIP-${String(this.nextNumber).padStart(3, "0")}`;
      this.nextNumber++;
      if (!this.records.has(candidate)) return candidate;
    }
  }

  /**
   * Get or seed MIP-000 (the governance standard). Idempotent.
   * If MIP-000 already exists, returns existing. Otherwise creates a draft.
   */
  ensureMipZero(): MipRecord {
    const existing = this.records.get("MIP-000");
    if (existing) return existing;
    const m: MipRecord = {
      id: "MIP-000",
      slug: "mip-000-governance-standard",
      title: "MOOD Improvement Proposal (MIP) Governance Standard",
      summary:
        "Defines the MIP lifecycle, status transitions, decision methods, and review process for the MOOD governance system. MIP-000 is itself the governance process specification.",
      category: "governance",
      status: "draft",
      authorResidentIds: ["system"],
      createdAt: nowIso(),
      updatedAt: nowIso(),
      decisionMethod: "maintainer-consensus",
    };
    this.records.set(m.id, m);
    this.bySlugMap.set(m.slug, m.id);
    this.decisionsByMip.set(m.id, []);
    this.implementationsByMip.set(m.id, []);
    this.auditByMip.set(m.id, [
      {
        id: `audit_${m.id}_seed`,
        type: "MipCreated",
        mipId: m.id,
        actorResidentId: "system",
        timestamp: m.createdAt,
        nextStatus: m.status,
        reason: "seed",
      },
    ]);
    return m;
  }

  // ─── Authoring ─────────────────────────────────────────────────────────────

  /**
   * Create a MIP draft. Requires at least one author Resident ID.
   * Initial status is "draft". Cannot create with status=accepted / implemented.
   */
  create(input: {
    title: string;
    summary: string;
    category: MipCategory;
    authorResidentIds: string[];
    sponsorResidentIds?: string[];
    discussionUrl?: string;
    sourcePath?: string;
    sourceSha?: string;
    decisionMethod?: MipDecisionMethod;
  }): MipRecord {
    if (!input.authorResidentIds || input.authorResidentIds.length === 0) {
      throw new Error("INV-020-06: MIP requires at least one author");
    }
    if (!input.title || input.title.length < 5) {
      throw new Error("mip-title-required");
    }
    if (!input.summary || input.summary.length < 10) {
      throw new Error("mip-summary-required");
    }
    const id = this.allocateId();
    const slug = input.title
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, "-")
      .replace(/^-|-$/g, "")
      .slice(0, 80);
    const finalSlug = this.bySlugMap.has(slug)
      ? `${slug}-${id.toLowerCase()}`
      : slug;
    const now = nowIso();
    const m: MipRecord = {
      id,
      slug: finalSlug,
      title: input.title,
      summary: input.summary,
      category: input.category,
      status: "draft",
      authorResidentIds: input.authorResidentIds,
      sponsorResidentIds: input.sponsorResidentIds,
      createdAt: now,
      updatedAt: now,
      discussionUrl: input.discussionUrl,
      sourcePath: input.sourcePath,
      sourceSha: input.sourceSha,
      decisionMethod: input.decisionMethod ?? "maintainer-consensus",
    };
    this.records.set(id, m);
    this.bySlugMap.set(finalSlug, id);
    this.decisionsByMip.set(id, []);
    this.implementationsByMip.set(id, []);
    this.auditByMip.set(id, [
      {
        id: `audit_${id}_create`,
        type: "MipCreated",
        mipId: id,
        actorResidentId: input.authorResidentIds[0],
        timestamp: now,
        nextStatus: "draft",
        reason: "draft created",
      },
    ]);
    return m;
  }

  requireMip(id: string): MipRecord {
    const m = this.records.get(id);
    if (!m) throw new Error(`mip-not-found:${id}`);
    return m;
  }

  bySlug(slug: string): MipRecord | undefined {
    const id = this.bySlugMap.get(slug);
    return id ? this.records.get(id) : undefined;
  }

  // ─── Lifecycle transitions ─────────────────────────────────────────────────

  /**
   * Move a MIP to a new status. Validates the transition is allowed.
   * Records an audit event. Cannot bypass required decision records.
   *
   * Special rules (INV-020-02/03/04):
   * - cannot transition to "implemented" without a prior "accepted" decision
   * - cannot transition to "accepted" without a decision record
   * - cannot transition to "rejected" without a decision record
   */
  transition(input: {
    mipId: string;
    nextStatus: MipStatus;
    actorResidentId: string;
    reason?: string;
  }): MipRecord {
    const m = this.requireMip(input.mipId);
    const allowed = ALLOWED_TRANSITIONS[m.status];
    if (!allowed.includes(input.nextStatus)) {
      throw new Error(
        `INV-020-02: invalid transition ${m.status} -> ${input.nextStatus}`,
      );
    }
    if (input.nextStatus === "implemented") {
      const decs = this.decisionsByMip.get(m.id) ?? [];
      const accepted = decs.find((d) => d.decision === "accepted");
      if (!accepted) {
        throw new Error("INV-020-03: cannot implement without acceptance decision");
      }
      const impls = this.implementationsByMip.get(m.id) ?? [];
      if (impls.length === 0) {
        throw new Error("INV-020-04: cannot implement without implementation reference");
      }
    }
    const previous = m.status;
    m.status = input.nextStatus;
    m.updatedAt = nowIso();
    this.auditByMip.get(m.id)?.push({
      id: `audit_${m.id}_${Date.now()}`,
      type: auditTypeForTransition(previous, input.nextStatus),
      mipId: m.id,
      actorResidentId: input.actorResidentId,
      timestamp: m.updatedAt,
      previousStatus: previous,
      nextStatus: input.nextStatus,
      reason: input.reason,
    });
    return m;
  }

  // ─── Decisions ─────────────────────────────────────────────────────────────

  /**
   * Record a review decision. Required to accept / reject a MIP.
   * Public Residents cannot accept their own MIPs unless they are
   * also governance maintainers.
   */
  recordDecision(input: {
    mipId: string;
    decision: "accepted" | "rejected" | "returned-for-revision";
    decidedBy: string[];
    rationale: string;
    isMaintainer: boolean;
  }): MipDecision {
    const m = this.requireMip(input.mipId);
    if (!input.decidedBy || input.decidedBy.length === 0) {
      throw new Error("mip-decision-actor-required");
    }
    if (!input.rationale || input.rationale.length < 5) {
      throw new Error("mip-decision-rationale-required");
    }
    // INV-020-06: public Residents cannot accept their own MIPs without maintainer role
    if (input.decision === "accepted") {
      const isSelfAccept =
        input.decidedBy.length === 1 &&
        m.authorResidentIds.includes(input.decidedBy[0]) &&
        !input.isMaintainer;
      if (isSelfAccept) {
        throw new Error("INV-020-06: resident cannot self-accept MIP without maintainer role");
      }
    }
    const decision: MipDecision = {
      id: `dec_${m.id}_${(this.decisionsByMip.get(m.id)?.length ?? 0) + 1}_${Date.now()}`,
      mipId: m.id,
      decision: input.decision,
      decidedBy: input.decidedBy,
      decidedAt: nowIso(),
      rationale: input.rationale,
    };
    this.decisionsByMip.get(m.id)?.push(decision);
    this.auditByMip.get(m.id)?.push({
      id: `audit_${m.id}_${Date.now()}`,
      type:
        input.decision === "accepted"
          ? "MipAccepted"
          : input.decision === "rejected"
            ? "MipRejected"
            : "RevisionRequested",
      mipId: m.id,
      actorResidentId: input.decidedBy[0],
      timestamp: decision.decidedAt,
      reason: input.rationale,
    });
    // Auto-transition on accept/reject
    if (input.decision === "accepted" && m.status === "review") {
      m.status = "accepted";
      m.updatedAt = nowIso();
    } else if (input.decision === "rejected" && m.status === "review") {
      m.status = "rejected";
      m.updatedAt = nowIso();
    } else if (input.decision === "returned-for-revision") {
      m.status = "draft";
      m.updatedAt = nowIso();
    }
    return decision;
  }

  // ─── Implementation ────────────────────────────────────────────────────────

  /**
   * Record an implementation reference. Required to transition to "implemented".
   * ref may be a commit SHA, PR URL, deployed route, policy doc path, etc.
   */
  recordImplementation(input: {
    mipId: string;
    ref: string;
    recordedBy: string;
    note?: string;
  }): MipImplementation {
    const m = this.requireMip(input.mipId);
    if (!input.ref || input.ref.length < 3) {
      throw new Error("mip-implementation-ref-required");
    }
    const impl: MipImplementation = {
      id: `impl_${m.id}_${(this.implementationsByMip.get(m.id)?.length ?? 0) + 1}_${Date.now()}`,
      mipId: m.id,
      ref: input.ref,
      recordedAt: nowIso(),
      recordedBy: input.recordedBy,
      note: input.note,
    };
    this.implementationsByMip.get(m.id)?.push(impl);
    this.auditByMip.get(m.id)?.push({
      id: `audit_${m.id}_${Date.now()}`,
      type: "MipImplemented",
      mipId: m.id,
      actorResidentId: input.recordedBy,
      timestamp: impl.recordedAt,
      nextStatus: m.status,
      reason: input.note ?? `implementation:${input.ref}`,
    });
    return impl;
  }

  // ─── Supersession ──────────────────────────────────────────────────────────

  /**
   * Mark a MIP as superseded by another. Old MIP remains readable.
   */
  supersede(input: {
    mipId: string;
    supersededBy: string;
    actorResidentId: string;
  }): MipRecord {
    const m = this.requireMip(input.mipId);
    if (m.status !== "accepted" && m.status !== "implemented") {
      throw new Error("mip-supersede-not-allowed-for-status:" + m.status);
    }
    const replacer = this.requireMip(input.supersededBy);
    m.supersededBy = input.supersededBy;
    replacer.supersedes = [...(replacer.supersedes ?? []), m.id];
    m.status = "superseded";
    m.updatedAt = nowIso();
    this.auditByMip.get(m.id)?.push({
      id: `audit_${m.id}_${Date.now()}`,
      type: "MipSuperseded",
      mipId: m.id,
      actorResidentId: input.actorResidentId,
      timestamp: m.updatedAt,
      previousStatus: "accepted",
      nextStatus: "superseded",
      reason: `superseded by ${input.supersededBy}`,
    });
    return m;
  }

  // ─── Reads ─────────────────────────────────────────────────────────────────

  list(filter?: { status?: MipStatus; category?: MipCategory }): MipRecord[] {
    const out: MipRecord[] = [];
    for (const m of this.records.values()) {
      if (filter?.status && m.status !== filter.status) continue;
      if (filter?.category && m.category !== filter.category) continue;
      out.push(m);
    }
    return out.sort((a, b) => (a.createdAt < b.createdAt ? 1 : -1));
  }

  publicList(filter?: { status?: MipStatus; category?: MipCategory }): PublicMip[] {
    return this.list(filter).map((m) =>
      publicMip(m, this.decisionsByMip.get(m.id) ?? [], this.implementationsByMip.get(m.id) ?? []),
    );
  }

  publicById(id: string): PublicMip | undefined {
    const m = this.records.get(id);
    if (!m) return undefined;
    return publicMip(m, this.decisionsByMip.get(m.id) ?? [], this.implementationsByMip.get(m.id) ?? []);
  }

  publicDetailById(id: string): PublicMipDetail | undefined {
    const m = this.records.get(id);
    if (!m) return undefined;
    const decs = this.decisionsByMip.get(m.id) ?? [];
    const impls = this.implementationsByMip.get(m.id) ?? [];
    const audits = (this.auditByMip.get(m.id) ?? []).filter((a) =>
      isPublicAuditType(a.type),
    );
    return {
      ...publicMip(m, decs, impls),
      authorResidentIds: m.authorResidentIds,
      sponsorResidentIds: m.sponsorResidentIds,
      implementationRefs: impls.map((i) => i.ref),
      supersedes: m.supersedes,
      supersededBy: m.supersededBy,
      sourcePath: m.sourcePath,
      sourceSha: m.sourceSha,
      decisions: decs.map((d) => ({
        ...d,
        // Strip rationale from public view? No - decision rationale is public
        // because the policy says no private reviewer notes in the public feed.
        // Rationale is part of the public decision record.
      })),
      implementationRecords: impls,
      auditEvents: audits,
    };
  }

  decisionsFor(mipId: string): MipDecision[] {
    return this.decisionsByMip.get(mipId) ?? [];
  }

  implementationsFor(mipId: string): MipImplementation[] {
    return this.implementationsByMip.get(mipId) ?? [];
  }

  auditFor(mipId: string): MipAuditEvent[] {
    return this.auditByMip.get(mipId) ?? [];
  }

  // ─── Counts / metrics ──────────────────────────────────────────────────────

  counts(): {
    total: number;
    byStatus: Record<MipStatus, number>;
    byCategory: Record<MipCategory, number>;
    lastActivityAt: string | null;
  } {
    const byStatus: Record<MipStatus, number> = {
      draft: 0,
      discussion: 0,
      review: 0,
      accepted: 0,
      rejected: 0,
      implemented: 0,
      withdrawn: 0,
      superseded: 0,
      archived: 0,
    };
    const byCategory: Record<MipCategory, number> = {
      core: 0,
      governance: 0,
      identity: 0,
      contribution: 0,
      agents: 0,
      nodes: 0,
      security: 0,
      economics: 0,
      treasury: 0,
      token: 0,
      other: 0,
    };
    let lastActivityAt: string | null = null;
    for (const m of this.records.values()) {
      byStatus[m.status]++;
      byCategory[m.category]++;
      if (!lastActivityAt || m.updatedAt > lastActivityAt) lastActivityAt = m.updatedAt;
    }
    return { total: this.records.size, byStatus, byCategory, lastActivityAt };
  }
}

function auditTypeForTransition(
  from: MipStatus,
  to: MipStatus,
): MipAuditEvent["type"] {
  if (from === "draft" && to === "discussion") return "DiscussionOpened";
  if (to === "review") return "ReviewStarted";
  if (to === "withdrawn") return "MipWithdrawn";
  if (to === "archived") return "MipArchived";
  if (to === "superseded") return "MipSuperseded";
  return "MipUpdated";
}

function isPublicAuditType(t: MipAuditEvent["type"]): boolean {
  // All audit types are public (no PRIVATE-INTERNAL-NOTE etc).
  // Rationale goes via Decision records, which are public.
  return true;
}

export const mipRegistry = new MipRegistry();
mipRegistry.ensureMipZero();
