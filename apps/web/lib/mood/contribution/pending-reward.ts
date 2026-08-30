/**
 * MOOD CONTRIBUTION 016 — Pending Reward
 *
 * Append-only PendingRewardEvent log + idempotency.
 * Authority: MOOD-CONTRIBUTION-016 TASK.md Phase H.
 *
 * Hard rule: PendingRewardEvent has NO chain side effect.
 * rewardUnits is stringly-typed and never interpreted as on-chain entitlement.
 */

import type { PendingRewardEvent, PendingRewardStatus } from "./types.ts";
import type { ResidentId } from "../passport/types.ts";

export class PendingRewardRegistry {
  private events: PendingRewardEvent[] = [];
  private bySubmission: Map<string, string> = new Map();

  record(input: {
    residentId: ResidentId;
    submissionId: string;
    rewardUnits: string;
    reason?: string;
    createdAt?: string;
  }): PendingRewardEvent {
    // INV-016-05: one pending reward per approved submission.
    if (this.bySubmission.has(input.submissionId)) {
      throw new Error(
        "INV-016-05: pending reward already recorded for submission",
      );
    }
    const event: PendingRewardEvent = {
      id: `pr_${this.events.length + 1}`,
      residentId: input.residentId,
      submissionId: input.submissionId,
      rewardUnits: input.rewardUnits,
      status: "pending",
      createdAt: input.createdAt ?? new Date().toISOString(),
      updatedAt: input.createdAt ?? new Date().toISOString(),
      reason: input.reason,
    };
    this.events.push(event);
    this.bySubmission.set(input.submissionId, event.id);
    return event;
  }

  changeStatus(
    id: string,
    nextStatus: PendingRewardStatus,
    reason?: string,
  ): PendingRewardEvent {
    const ev = this.events.find((e) => e.id === id);
    if (!ev) throw new Error("pending reward not found");
    ev.status = nextStatus;
    ev.updatedAt = new Date().toISOString();
    if (reason) ev.reason = reason;
    return ev;
  }

  forResident(residentId: ResidentId): ReadonlyArray<PendingRewardEvent> {
    return this.events.filter((e) => e.residentId === residentId);
  }

  all(): ReadonlyArray<PendingRewardEvent> {
    return this.events.slice();
  }

  /**
   * For /network observatory. Returns total pending units + count.
   * No wallet addresses exposed.
   */
  publicAggregate(): {
    pendingCount: number;
    pendingByResidentCount: number;
  } {
    const pending = this.events.filter((e) => e.status === "pending");
    const residents = new Set(pending.map((e) => e.residentId));
    return {
      pendingCount: pending.length,
      pendingByResidentCount: residents.size,
    };
  }
}