/**
 * MOOD CONTRIBUTION 016 — Reputation
 *
 * Append-only Reputation event log + cached aggregate.
 * Authority: MOOD-CONTRIBUTION-016 TASK.md Phase G.
 *
 * Invariants:
 * - ReputationEvent is append-only. Never mutated, never deleted.
 * - Cached aggregate MUST equal sum of events.pointsDelta for resident.
 * - Profile never directly writes the total.
 */

import type {
  ReputationEvent,
  ResidentReputation,
  ReputationSource,
} from "./types.ts";
import type { ResidentId } from "../passport/types.ts";

export class ReputationRegistry {
  private events: ReputationEvent[] = [];
  // idempotency cache: submissionId -> reputationEventId
  private bySubmission: Map<string, string> = new Map();

  recordEvent(input: {
    residentId: ResidentId;
    submissionId?: string;
    pointsDelta: number;
    reason: string;
    source: ReputationSource;
    createdByResidentId: ResidentId;
    createdAt?: string;
  }): ReputationEvent {
    // INV-016-04: Approved submission only grants reputation once.
    if (input.submissionId) {
      if (this.bySubmission.has(input.submissionId)) {
        throw new Error("INV-016-04: reputation already granted for submission");
      }
    }

    const event: ReputationEvent = {
      id: `re_${this.events.length + 1}`,
      residentId: input.residentId,
      submissionId: input.submissionId,
      pointsDelta: input.pointsDelta,
      reason: input.reason,
      source: input.source,
      createdAt: input.createdAt ?? new Date().toISOString(),
      createdByResidentId: input.createdByResidentId,
    };

    this.events.push(event);
    if (input.submissionId) {
      this.bySubmission.set(input.submissionId, event.id);
    }
    return event;
  }

  /**
   * Adjustment: creates a NEW compensating event rather than mutating the original.
   * INV-016-07: corrections only via new adjustment events.
   */
  adjust(input: {
    residentId: ResidentId;
    reason: string;
    pointsDelta: number;
    createdByResidentId: ResidentId;
  }): ReputationEvent {
    return this.recordEvent({
      residentId: input.residentId,
      pointsDelta: input.pointsDelta,
      reason: input.reason,
      source: "system-adjustment",
      createdByResidentId: input.createdByResidentId,
    });
  }

  /**
   * INV-016-07: cached total MUST equal sum of events.
   */
  aggregateFor(residentId: ResidentId): ResidentReputation {
    const residentEvents = this.events.filter(
      (e) => e.residentId === residentId,
    );
    if (residentEvents.length === 0) {
      return {
        residentId,
        score: 0,
        lastEventAt: null,
        contributionCount: 0,
        approvedContributionCount: 0,
        source: "no-contributions-yet",
      };
    }
    const score = residentEvents.reduce(
      (acc, e) => acc + e.pointsDelta,
      0,
    );
    const lastEventAt = residentEvents.reduce((acc, e) => {
      if (!acc) return e.createdAt;
      return e.createdAt > acc ? e.createdAt : acc;
    }, "");
    const contributionCount = new Set(
      residentEvents
        .filter((e) => !!e.submissionId)
        .map((e) => e.submissionId as string),
    ).size;
    const approvedContributionCount = residentEvents.filter(
      (e) => e.source === "contribution" && e.pointsDelta > 0,
    ).length;
    return {
      residentId,
      score,
      lastEventAt: lastEventAt || null,
      contributionCount,
      approvedContributionCount,
      source: "events",
    };
  }

  /** Public aggregate: positive total + event count only (no private fields). */
  publicAggregate(): {
    totalEventCount: number;
    totalPositivePoints: number;
  } {
    return {
      totalEventCount: this.events.length,
      totalPositivePoints: this.events
        .filter((e) => e.pointsDelta > 0)
        .reduce((acc, e) => acc + e.pointsDelta, 0),
    };
  }

  hasGrantForSubmission(submissionId: string): boolean {
    return this.bySubmission.has(submissionId);
  }

  allEvents(): ReadonlyArray<ReputationEvent> {
    return this.events.slice();
  }
}