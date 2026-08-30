/**
 * MOOD CONTRIBUTION 016 — Contribution Registry
 *
 * In-memory registries for tasks / submissions + review orchestration.
 * Authority: MOOD-CONTRIBUTION-016 TASK.md Phases C..P.
 *
 * This is the single authoritative server-side state machine host.
 * All transitions go through this registry; the API routes must NOT
 * mutate records directly.
 */

import type { ResidentId } from "../passport/types.ts";
import {
  isAlreadyReviewed,
  isSelfReview,
  countOpenSubmissions,
} from "./anti-abuse.ts";
import { AuditLog } from "./audit.ts";
import {
  isValidEvidenceArray,
  validateEvidence,
} from "./evidence.ts";
import { PendingRewardRegistry } from "./pending-reward.ts";
import { ReputationRegistry } from "./reputation.ts";
import {
  assertTransition,
  isTransitionAllowed,
} from "./state-machine.ts";
import type {
  ContributionCategory,
  ContributionEvidence,
  ContributionSubmission,
  ContributionTask,
  ReviewActionInput,
  ReviewActionResult,
} from "./types.ts";

const SYSTEM_ACTOR: ResidentId = "system";

export class ContributionRegistry {
  tasks: Map<string, ContributionTask> = new Map();
  submissions: Map<string, ContributionSubmission> = new Map();
  evidence: Map<string, ContributionEvidence[]> = new Map(); // submissionId -> list
  reputation: ReputationRegistry = new ReputationRegistry();
  pendingReward: PendingRewardRegistry = new PendingRewardRegistry();
  audit: AuditLog = new AuditLog();

  // ─── Tasks ────────────────────────────────────────────────────────────────

  createTask(input: {
    slug: string;
    title: string;
    summary: string;
    description: string;
    category: ContributionCategory;
    evidenceRequirements: string[];
    defaultReputationPoints: number;
    defaultRewardUnits?: string;
    deadline?: string;
    maxApprovals?: number;
    createdByResidentId: ResidentId;
  }): ContributionTask {
    if (this.findTaskBySlug(input.slug)) {
      throw new Error(`task-slug-exists:${input.slug}`);
    }
    const now = new Date().toISOString();
    const task: ContributionTask = {
      id: `task_${this.tasks.size + 1}`,
      slug: input.slug,
      title: input.title,
      summary: input.summary,
      description: input.description,
      category: input.category,
      status: "active",
      evidenceRequirements: input.evidenceRequirements,
      defaultReputationPoints: input.defaultReputationPoints,
      defaultRewardUnits: input.defaultRewardUnits,
      deadline: input.deadline,
      maxApprovals: input.maxApprovals,
      createdByResidentId: input.createdByResidentId,
      createdAt: now,
      updatedAt: now,
    };
    this.tasks.set(task.id, task);
    this.audit.record({
      type: "TaskCreated",
      actorResidentId: input.createdByResidentId,
      taskId: task.id,
    });
    return task;
  }

  setTaskStatus(
    taskId: string,
    nextStatus: ContributionTask["status"],
    actor: ResidentId,
  ): ContributionTask {
    const task = this.tasks.get(taskId);
    if (!task) throw new Error("task-not-found");
    const previous = task.status;
    task.status = nextStatus;
    task.updatedAt = new Date().toISOString();
    this.audit.record({
      type: "TaskStatusChanged",
      actorResidentId: actor,
      taskId,
      previousStatus: previous,
      nextStatus,
    });
    return task;
  }

  findTaskBySlug(slug: string): ContributionTask | undefined {
    for (const t of this.tasks.values()) if (t.slug === slug) return t;
    return undefined;
  }

  listTasks(filter?: { status?: ContributionTask["status"] }): ContributionTask[] {
    const out: ContributionTask[] = [];
    for (const t of this.tasks.values()) {
      if (filter?.status && t.status !== filter.status) continue;
      out.push(t);
    }
    return out;
  }

  // ─── Submissions ──────────────────────────────────────────────────────────

  createSubmission(input: {
    taskId: string;
    residentId: ResidentId;
    summary: string;
    evidenceText?: string;
    evidenceItems?: Array<{
      type: ContributionEvidence["type"];
      value: string;
      label?: string;
    }>;
  }): ContributionSubmission {
    const task = this.tasks.get(input.taskId);
    if (!task) throw new Error("task-not-found");
    if (task.status !== "active") throw new Error("task-not-active");
    const open = countOpenSubmissions(
      Array.from(this.submissions.values()),
      input.residentId,
    );
    if (!open.allowed) {
      throw new Error(
        `anti-abuse:too-many-open-submissions:${open.count}`,
      );
    }
    if (!input.summary || input.summary.length < 10) {
      throw new Error("summary too short (min 10 chars)");
    }
    if (input.evidenceItems) {
      const v = isValidEvidenceArray(input.evidenceItems);
      if (!v.ok) throw new Error(`evidence:${v.code}:${v.message}`);
    }
    const now = new Date().toISOString();
    const submission: ContributionSubmission = {
      id: `sub_${this.submissions.size + 1}`,
      taskId: input.taskId,
      residentId: input.residentId,
      summary: input.summary,
      evidenceText: input.evidenceText,
      status: "submitted",
      revision: 1,
      createdAt: now,
      updatedAt: now,
    };
    this.submissions.set(submission.id, submission);
    this.evidence.set(
      submission.id,
      (input.evidenceItems ?? []).map((e, i) => {
        // re-validate each (defensive — already validated, but tests rely on it)
        const v = validateEvidence(e);
        if (!v.ok) throw new Error(`evidence:${v.code}:${v.message}`);
        return {
          id: `ev_${submission.id}_${i + 1}`,
          submissionId: submission.id,
          type: e.type,
          value: e.value,
          label: e.label,
          createdAt: now,
        };
      }),
    );
    this.audit.record({
      type: "SubmissionCreated",
      actorResidentId: input.residentId,
      submissionId: submission.id,
      taskId: input.taskId,
    });
    return submission;
  }

  /** Resubmit a submission after changes were requested. */
  resubmit(input: {
    submissionId: string;
    actorResidentId: ResidentId;
    summary?: string;
    additionalEvidence?: Array<{
      type: ContributionEvidence["type"];
      value: string;
      label?: string;
    }>;
  }): ContributionSubmission {
    const sub = this.submissions.get(input.submissionId);
    if (!sub) throw new Error("submission-not-found");
    if (sub.residentId !== input.actorResidentId) {
      throw new Error("only-owner-may-resubmit");
    }
    assertTransition(sub.status, "submitted");
    sub.status = "submitted";
    sub.revision = sub.revision + 1;
    sub.updatedAt = new Date().toISOString();
    if (input.summary) sub.summary = input.summary;
    if (input.additionalEvidence) {
      const v = isValidEvidenceArray(input.additionalEvidence);
      if (!v.ok) throw new Error(`evidence:${v.code}:${v.message}`);
      const existing = this.evidence.get(sub.id) ?? [];
      const merged = [...existing, ...input.additionalEvidence].slice(0, 20);
      this.evidence.set(sub.id, merged as ContributionEvidence[]);
    }
    this.audit.record({
      type: "SubmissionResubmitted",
      actorResidentId: input.actorResidentId,
      submissionId: sub.id,
      taskId: sub.taskId,
      previousStatus: "changes_requested",
      nextStatus: "submitted",
    });
    return sub;
  }

  withdraw(input: {
    submissionId: string;
    actorResidentId: ResidentId;
  }): ContributionSubmission {
    const sub = this.submissions.get(input.submissionId);
    if (!sub) throw new Error("submission-not-found");
    if (sub.residentId !== input.actorResidentId) {
      throw new Error("only-owner-may-withdraw");
    }
    assertTransition(sub.status, "withdrawn");
    sub.status = "withdrawn";
    sub.updatedAt = new Date().toISOString();
    this.audit.record({
      type: "SubmissionWithdrawn",
      actorResidentId: input.actorResidentId,
      submissionId: sub.id,
      taskId: sub.taskId,
      previousStatus: "submitted",
      nextStatus: "withdrawn",
    });
    return sub;
  }

  listSubmissionsForResident(residentId: ResidentId): ContributionSubmission[] {
    const out: ContributionSubmission[] = [];
    for (const s of this.submissions.values()) {
      if (s.residentId === residentId) out.push(s);
    }
    return out;
  }

  listSubmissionsForTask(taskId: string): ContributionSubmission[] {
    const out: ContributionSubmission[] = [];
    for (const s of this.submissions.values()) {
      if (s.taskId === taskId) out.push(s);
    }
    return out;
  }

  listReviewQueue(): ContributionSubmission[] {
    const out: ContributionSubmission[] = [];
    for (const s of this.submissions.values()) {
      if (s.status === "submitted" || s.status === "under_review") out.push(s);
    }
    return out;
  }

  // ─── Review ───────────────────────────────────────────────────────────────

  startReview(input: {
    submissionId: string;
    reviewerResidentId: ResidentId;
  }): ContributionSubmission {
    const sub = this.submissions.get(input.submissionId);
    if (!sub) throw new Error("submission-not-found");
    if (isSelfReview(sub, input.reviewerResidentId)) {
      throw new Error("INV-016-02: cannot review own submission");
    }
    if (!isTransitionAllowed(sub.status, "under_review")) {
      throw new Error(`INV-016-03: cannot start review from ${sub.status}`);
    }
    sub.status = "under_review";
    sub.updatedAt = new Date().toISOString();
    sub.reviewedByResidentId = input.reviewerResidentId;
    this.audit.record({
      type: "ReviewStarted",
      actorResidentId: input.reviewerResidentId,
      submissionId: sub.id,
      taskId: sub.taskId,
      previousStatus: "submitted",
      nextStatus: "under_review",
    });
    return sub;
  }

  review(input: ReviewActionInput & { submissionId: string }): ReviewActionResult {
    const sub = this.submissions.get(input.submissionId);
    if (!sub) return { ok: false, reason: "submission-not-found", auditEventIds: [] };
    if (isSelfReview(sub, input.reviewerResidentId)) {
      return { ok: false, reason: "INV-016-02: cannot review own submission", auditEventIds: [] };
    }
    if (isAlreadyReviewed(sub)) {
      // INV-016-09: idempotent — already-reviewed submissions return the
      // existing state without producing new audit/reputation/reward events.
      return {
        ok: true,
        submission: sub,
        reputationEventId: undefined,
        pendingRewardId: undefined,
        auditEventIds: [],
      };
    }
    if (sub.status !== "under_review" && sub.status !== "submitted") {
      return {
        ok: false,
        reason: `INV-016-03: review only allowed from submitted/under_review, got ${sub.status}`,
        auditEventIds: [],
      };
    }
    // Move to under_review if currently submitted (without producing extra events).
    if (sub.status === "submitted") {
      assertTransition("submitted", "under_review");
      sub.status = "under_review";
      sub.reviewedByResidentId = input.reviewerResidentId;
      const startEv = this.audit.record({
        type: "ReviewStarted",
        actorResidentId: input.reviewerResidentId,
        submissionId: sub.id,
        taskId: sub.taskId,
        previousStatus: "submitted",
        nextStatus: "under_review",
      });
      const auditIds: string[] = [startEv.id];
      return this.applyDecision(sub, input, auditIds);
    }
    return this.applyDecision(sub, input, []);
  }

  private applyDecision(
    sub: ContributionSubmission,
    input: ReviewActionInput & { submissionId: string },
    auditIds: string[],
  ): ReviewActionResult {
    const task = this.tasks.get(sub.taskId);
    if (!task) return { ok: false, reason: "task-not-found", auditEventIds: auditIds };

    if (input.decision === "request-changes") {
      assertTransition(sub.status, "changes_requested");
      sub.status = "changes_requested";
      sub.reviewerNote = input.note;
      sub.updatedAt = new Date().toISOString();
      const ev = this.audit.record({
        type: "ChangesRequested",
        actorResidentId: input.reviewerResidentId,
        submissionId: sub.id,
        taskId: sub.taskId,
        previousStatus: "under_review",
        nextStatus: "changes_requested",
        note: input.note,
      });
      auditIds.push(ev.id);
      return { ok: true, submission: sub, auditEventIds: auditIds };
    }

    if (input.decision === "approve") {
      assertTransition(sub.status, "approved");
      sub.status = "approved";
      sub.reviewerNote = input.note;
      sub.updatedAt = new Date().toISOString();
      const approvedEv = this.audit.record({
        type: "SubmissionApproved",
        actorResidentId: input.reviewerResidentId,
        submissionId: sub.id,
        taskId: sub.taskId,
        previousStatus: "under_review",
        nextStatus: "approved",
        note: input.note,
      });
      auditIds.push(approvedEv.id);

      // Reputation grant — INV-016-04 enforced inside registry.
      let reputationEventId: string | undefined;
      try {
        const repEv = this.reputation.recordEvent({
          residentId: sub.residentId,
          submissionId: sub.id,
          pointsDelta: task.defaultReputationPoints,
          reason: `Approved contribution for task ${task.slug}`,
          source: "contribution",
          createdByResidentId: input.reviewerResidentId,
        });
        reputationEventId = repEv.id;
        const auditRep = this.audit.record({
          type: "ReputationGranted",
          actorResidentId: input.reviewerResidentId,
          submissionId: sub.id,
          taskId: sub.taskId,
          reputationEventId: repEv.id,
        });
        auditIds.push(auditRep.id);
      } catch (e) {
        // Already-granted: idempotent — no new event.
      }

      // Pending reward — INV-016-05 enforced inside registry.
      let pendingRewardId: string | undefined;
      if (task.defaultRewardUnits) {
        try {
          const prEv = this.pendingReward.record({
            residentId: sub.residentId,
            submissionId: sub.id,
            rewardUnits: task.defaultRewardUnits,
            reason: `Approved contribution for task ${task.slug}; historical field naming — not an on-chain entitlement.`,
          });
          pendingRewardId = prEv.id;
          const auditPr = this.audit.record({
            type: "PendingRewardRecorded",
            actorResidentId: input.reviewerResidentId,
            submissionId: sub.id,
            taskId: sub.taskId,
            pendingRewardId: prEv.id,
          });
          auditIds.push(auditPr.id);
        } catch (e) {
          // Already-recorded: idempotent — no new event.
        }
      }

      return {
        ok: true,
        submission: sub,
        reputationEventId,
        pendingRewardId,
        auditEventIds: auditIds,
      };
    }

    if (input.decision === "reject") {
      assertTransition(sub.status, "rejected");
      sub.status = "rejected";
      sub.reviewerNote = input.note;
      sub.updatedAt = new Date().toISOString();
      const ev = this.audit.record({
        type: "SubmissionRejected",
        actorResidentId: input.reviewerResidentId,
        submissionId: sub.id,
        taskId: sub.taskId,
        previousStatus: "under_review",
        nextStatus: "rejected",
        note: input.note,
      });
      auditIds.push(ev.id);
      return { ok: true, submission: sub, auditEventIds: auditIds };
    }

    return { ok: false, reason: "unknown-decision", auditEventIds: auditIds };
  }
}

/** Process-wide singleton — same pattern as passport registry. */
export const contributionRegistry = new ContributionRegistry();