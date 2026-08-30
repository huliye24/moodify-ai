/**
 * MOOD NETWORK 017 + MOOD AGENTS 018 — Observatory
 *
 * 018 extends 017's NetworkObservatory with agent metrics + activity.
 *
 * Authority: MOOD-NETWORK-017 TASK.md + MOOD-AGENTS-018 TASK.md Phase N.
 */

import { agentRegistry } from "../agents/registry.ts";
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
const SOURCE_AGENT = "agent-registry:018";

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
  applications(): MetricValue {
    return makeMetric(
      1,
      "constant:moodify-genesis-application",
      "Moodify — registered as Genesis Application.",
    );
  }

  residents(): MetricValue {
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
    const count = contributionRegistry.listTasks({ status: "active" }).length;
    return makeMetric(count, SOURCE_CONTRIBUTION, "Active ContributionTasks.");
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

  // ─── Agent metrics (018) ───────────────────────────────────────────────────

  agents(): MetricValue {
    const c = agentRegistry.counts();
    return makeMetric(
      c.total,
      SOURCE_AGENT,
      "Registered AI Agents.",
    );
  }

  agentsActive(): MetricValue {
    const c = agentRegistry.counts();
    return makeMetric(c.active, SOURCE_AGENT, "Agents with active status.");
  }

  agentsDegraded(): MetricValue {
    const c = agentRegistry.counts();
    return makeMetric(c.degraded, SOURCE_AGENT, "Agents with degraded status.");
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

  status(): NetworkStatus {
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

  /** Privacy-safe activity feed (extends 017 with agent events). */
  activity(limit = 25): PublicActivityEvent[] {
    const events: PublicActivityEvent[] = [];
    // Contribution events
    for (const audit of contributionRegistry.audit.all()) {
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
          if (audit.reputationEventId) {
            const rep = contributionRegistry.reputation
              .allEvents()
              .find((e) => e.id === audit.reputationEventId);
            if (rep) delta = rep.pointsDelta;
          }
          break;
        default:
          type = null;
      }
      if (!type) continue;
      const task = audit.taskId
        ? contributionRegistry.tasks.get(audit.taskId)
        : undefined;
      events.push({
        type,
        timestamp: audit.createdAt,
        taskSlug: task?.slug,
        submissionId: audit.submissionId,
        reputationDelta: delta,
      });
    }
    // Agent events (018)
    for (const a of agentRegistry.list()) {
      events.push({
        type: "AgentRegistered",
        timestamp: a.createdAt,
      });
      if (a.lastTaskAt) {
        events.push({
          type: "AgentTaskCompleted",
          timestamp: a.lastTaskAt,
        });
      }
    }
    events.sort((x, y) => (x.timestamp < y.timestamp ? 1 : -1));
    return events.slice(0, limit);
  }
}

export const networkObservatory = new NetworkObservatory();