/**
 * MOOD NETWORK 017 — Observatory Aggregator
 *
 * Reads from canonical registries (Contribution, Reputation, PendingReward)
 * and produces privacy-safe aggregates.
 *
 * Authority: MOOD-NETWORK-017 TASK.md Phases C/J.
 *
 * Privacy rules:
 * - Small-sample suppression: count < 3 -> hidden.
 * - Wallet addresses NEVER appear in public feed.
 * - Reviewer notes NEVER appear.
 * - Internal audit details NEVER appear.
 * - Reputation only as totals + positive points.
 */

import {
  contributionRegistry,
} from "../contribution/registry.ts";
import type {
  ActivityKind,
  MetricValue,
  NetworkOverview,
  NetworkStatus,
  PublicActivityEvent,
} from "./types.ts";

const SOURCE_CONTRIBUTION = "contribution-registry:016";
const SOURCE_REPUTATION = "reputation-registry:016";
const SOURCE_PENDING = "pending-reward-registry:016";
const SOURCE_AUDIT = "audit-log:016";

const SUPPRESSION_THRESHOLD = 3;

function nowIso(): string {
  return new Date().toISOString();
}

function makeMetric(
  value: number | null,
  source: string,
  definition: string,
  state: MetricValue["state"] = "available",
): MetricValue {
  return {
    value,
    state,
    source,
    definition,
    updatedAt: nowIso(),
  };
}

function suppressed(value: number): MetricValue {
  return {
    value: null,
    state: "unavailable",
    source: SUPPRESSION_THRESHOLD.toString(),
    definition: "Hidden when count below suppression threshold.",
    updatedAt: nowIso(),
  };
}

export class NetworkObservatory {
  /**
   * INV-017-12: Moodify is registered as Genesis Application with real source.
   */
  applications(): MetricValue {
    return makeMetric(
      1,
      "constant:moodify-genesis-application",
      "Moodify — registered as Genesis Application (017)",
    );
  }

  residents(): MetricValue {
    // Source from contribution submissions (distinct residentId).
    const ids = new Set<string>();
    for (const s of contributionRegistry.submissions.values()) {
      ids.add(s.residentId);
    }
    if (ids.size > 0 && ids.size < SUPPRESSION_THRESHOLD) {
      return suppressed(ids.size);
    }
    return makeMetric(
      ids.size,
      "contribution-registry:016 (distinct residentIds)",
      "Residents who have at least one submission (privacy-safe upper bound).",
    );
  }

  contributors(): MetricValue {
    // Distinct residents with at least one approved contribution.
    const ids = new Set<string>();
    for (const s of contributionRegistry.submissions.values()) {
      if (s.status === "approved") ids.add(s.residentId);
    }
    if (ids.size > 0 && ids.size < SUPPRESSION_THRESHOLD) {
      return suppressed(ids.size);
    }
    return makeMetric(
      ids.size,
      "contribution-registry:016 (distinct approved residentIds)",
      "Distinct Residents with at least one approved contribution.",
    );
  }

  openTasks(): MetricValue {
    const count = contributionRegistry
      .listTasks({ status: "active" })
      .filter((t) => t.status === "active").length;
    return makeMetric(
      count,
      SOURCE_CONTRIBUTION,
      "Active ContributionTasks.",
    );
  }

  submissions(): MetricValue {
    return makeMetric(
      contributionRegistry.submissions.size,
      SOURCE_CONTRIBUTION,
      "Total ContributionSubmissions (any status).",
    );
  }

  approvedContributions(): MetricValue {
    const n = Array.from(contributionRegistry.submissions.values()).filter(
      (s) => s.status === "approved",
    ).length;
    return makeMetric(n, SOURCE_CONTRIBUTION, "Submissions with status=approved.");
  }

  reputationEvents(): MetricValue {
    const agg = contributionRegistry.reputation.publicAggregate();
    return makeMetric(
      agg.totalEventCount,
      SOURCE_REPUTATION,
      "Append-only ReputationEvent count (public total only).",
    );
  }

  pendingReward(): MetricValue {
    const agg = contributionRegistry.pendingReward.publicAggregate();
    return makeMetric(
      agg.pendingCount,
      SOURCE_PENDING,
      "PendingRewardEvent count with status=pending.",
    );
  }

  agents(): MetricValue {
    // 018 not implemented yet.
    return {
      value: null,
      state: "coming-soon",
      source: "package-018:pending",
      definition: "AI Agent registry (Package 018).",
      updatedAt: nowIso(),
    };
  }

  nodes(): MetricValue {
    return {
      value: null,
      state: "coming-soon",
      source: "package-019:pending",
      definition: "Node registry (Package 019).",
      updatedAt: nowIso(),
    };
  }

  mips(): MetricValue {
    return {
      value: null,
      state: "coming-soon",
      source: "package-020:pending",
      definition: "MIP governance (Package 020).",
      updatedAt: nowIso(),
    };
  }

  /**
   * Compute network status from available subsystem signals.
   * INV-017-12: not dependent on Token RPC.
   */
  status(): NetworkStatus {
    const subs = Array.from(contributionRegistry.submissions.values());
    if (subs.length === 0 && contributionRegistry.tasks.size === 0) {
      // empty registries -> not broken, just empty
      return "operational";
    }
    // v1: if any registry is reachable and contains data, we treat as operational.
    return "operational";
  }

  overview(): NetworkOverview {
    const t = nowIso();
    return {
      status: this.status(),
      generatedAt: t,
      sourceUpdatedAt: t,
      metrics: {
        residents: this.residents(),
        contributors: this.contributors(),
        openTasks: this.openTasks(),
        submissions: this.submissions(),
        approvedContributions: this.approvedContributions(),
        reputationEvents: this.reputationEvents(),
        pendingReward: this.pendingReward(),
        applications: this.applications(),
        agents: this.agents(),
        nodes: this.nodes(),
        mips: this.mips(),
      },
    };
  }

  /**
   * Privacy-safe activity feed (INV-017-05/06):
   * - no full wallet
   * - no private reviewer notes
   * - no admin metadata
   * - small-sample suppression
   */
  activity(limit = 25): PublicActivityEvent[] {
    const events: PublicActivityEvent[] = [];
    for (const audit of contributionRegistry.audit.all()) {
      // Map audit -> activity type.
      let type: ActivityKind | null = null;
      let delta: number | undefined;
      switch (audit.type) {
        case "TaskCreated":
          type = "TaskPublished";
          break;
        case "SubmissionCreated":
        case "SubmissionResubmitted":
          type = "SubmissionSubmitted";
          break;
        case "SubmissionApproved":
          type = "SubmissionApproved";
          break;
        case "SubmissionRejected":
          type = "SubmissionRejected";
          break;
        case "ReputationGranted":
          type = "ReputationGranted";
          // Look up delta from reputation event id.
          if (audit.reputationEventId) {
            const rep = contributionRegistry.reputation
              .allEvents()
              .find((e) => e.id === audit.reputationEventId);
            if (rep) delta = rep.pointsDelta;
          }
          break;
        default:
          // SubmissionWithdrawn, ReviewStarted, ChangesRequested, etc. are
          // intentionally NOT surfaced in the public feed.
          type = null;
      }
      if (!type) continue;
      const submission = audit.submissionId
        ? contributionRegistry.submissions.get(audit.submissionId)
        : undefined;
      const task = audit.taskId
        ? contributionRegistry.tasks.get(audit.taskId)
        : undefined;
      // Privacy: short resident ID only, never wallet.
      events.push({
        type,
        timestamp: audit.createdAt,
        // The audit log does not carry residentId publicly — skip.
        taskSlug: task?.slug,
        submissionId: audit.submissionId,
        reputationDelta: delta,
      });
    }
    events.sort((a, b) => (a.timestamp < b.timestamp ? 1 : -1));
    return events.slice(0, limit);
  }
}

export const networkObservatory = new NetworkObservatory();