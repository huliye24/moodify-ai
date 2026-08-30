/**
 * MOOD CONTRIBUTION 016 — Audit Trail
 *
 * Append-only audit log for all contribution events.
 * Authority: MOOD-CONTRIBUTION-016 TASK.md Phase M.
 */

import type {
  ContributionAuditEvent,
  ContributionAuditType,
} from "./types.ts";
import type { ResidentId } from "../passport/types.ts";

export class AuditLog {
  private events: ContributionAuditEvent[] = [];

  record(input: {
    type: ContributionAuditType;
    actorResidentId: ResidentId;
    taskId?: string;
    submissionId?: string;
    reputationEventId?: string;
    pendingRewardId?: string;
    previousStatus?: string;
    nextStatus?: string;
    note?: string;
    createdAt?: string;
  }): ContributionAuditEvent {
    const event: ContributionAuditEvent = {
      id: `aud_${this.events.length + 1}`,
      type: input.type,
      actorResidentId: input.actorResidentId,
      taskId: input.taskId,
      submissionId: input.submissionId,
      reputationEventId: input.reputationEventId,
      pendingRewardId: input.pendingRewardId,
      previousStatus: input.previousStatus,
      nextStatus: input.nextStatus,
      note: input.note,
      createdAt: input.createdAt ?? new Date().toISOString(),
    };
    this.events.push(event);
    return event;
  }

  forSubmission(submissionId: string): ReadonlyArray<ContributionAuditEvent> {
    return this.events.filter((e) => e.submissionId === submissionId);
  }

  forTask(taskId: string): ReadonlyArray<ContributionAuditEvent> {
    return this.events.filter((e) => e.taskId === taskId);
  }

  all(): ReadonlyArray<ContributionAuditEvent> {
    return this.events.slice();
  }

  /** Public events for /network feed: no private fields. */
  publicEvents(): ReadonlyArray<{
    type: ContributionAuditType;
    submissionId?: string;
    taskId?: string;
    createdAt: string;
  }> {
    return this.events.map((e) => ({
      type: e.type,
      submissionId: e.submissionId,
      taskId: e.taskId,
      createdAt: e.createdAt,
    }));
  }
}