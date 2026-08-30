/**
 * MOOD GOVERNANCE 020 — Governance Metrics for /network Observatory.
 *
 * Extends the 017 + 018 + 019 NetworkObservatory with:
 * - mips.total / in-discussion / in-review / accepted / implemented
 * - lastActivityAt
 * - activity events: MIPPublished, MIPReviewStarted, MIPAccepted, MIPImplemented
 *
 * Authority: MOOD-GOVERNANCE-020 TASK.md Phase S.
 */

import type { MetricValue, PublicActivityEvent } from "../network/types.ts";
import { mipRegistry } from "./registry.ts";

function nowIso(): string {
  return new Date().toISOString();
}

export class GovernanceMetrics {
  summary(): {
    total: MetricValue;
    inDiscussion: MetricValue;
    inReview: MetricValue;
    accepted: MetricValue;
    implemented: MetricValue;
    byCategory: Record<string, MetricValue>;
    lastActivityAt: MetricValue;
  } {
    const c = mipRegistry.counts();
    return {
      total: {
        value: c.total,
        state: "available",
        source: "mip-registry:020",
        definition: "Total MIPs (any status, including MIP-000).",
        updatedAt: nowIso(),
      },
      inDiscussion: {
        value: c.byStatus.discussion,
        state: "available",
        source: "mip-registry:020",
        definition: "MIPs currently in Discussion.",
        updatedAt: nowIso(),
      },
      inReview: {
        value: c.byStatus.review,
        state: "available",
        source: "mip-registry:020",
        definition: "MIPs currently in Review.",
        updatedAt: nowIso(),
      },
      accepted: {
        value: c.byStatus.accepted,
        state: "available",
        source: "mip-registry:020",
        definition: "MIPs accepted but not yet Implemented.",
        updatedAt: nowIso(),
      },
      implemented: {
        value: c.byStatus.implemented,
        state: "available",
        source: "mip-registry:020",
        definition: "MIPs Implemented.",
        updatedAt: nowIso(),
      },
      byCategory: {
        core: {
          value: c.byCategory.core,
          state: "available",
          source: "mip-registry:020",
          definition: "MIPs in the core category.",
          updatedAt: nowIso(),
        },
        governance: {
          value: c.byCategory.governance,
          state: "available",
          source: "mip-registry:020",
          definition: "MIPs in the governance category.",
          updatedAt: nowIso(),
        },
        identity: {
          value: c.byCategory.identity,
          state: "available",
          source: "mip-registry:020",
          definition: "MIPs in the identity category.",
          updatedAt: nowIso(),
        },
        contribution: {
          value: c.byCategory.contribution,
          state: "available",
          source: "mip-registry:020",
          definition: "MIPs in the contribution category.",
          updatedAt: nowIso(),
        },
        agents: {
          value: c.byCategory.agents,
          state: "available",
          source: "mip-registry:020",
          definition: "MIPs in the agents category.",
          updatedAt: nowIso(),
        },
        nodes: {
          value: c.byCategory.nodes,
          state: "available",
          source: "mip-registry:020",
          definition: "MIPs in the nodes category.",
          updatedAt: nowIso(),
        },
        security: {
          value: c.byCategory.security,
          state: "available",
          source: "mip-registry:020",
          definition: "MIPs in the security category.",
          updatedAt: nowIso(),
        },
        economics: {
          value: c.byCategory.economics,
          state: "available",
          source: "mip-registry:020",
          definition: "MIPs in the economics category.",
          updatedAt: nowIso(),
        },
        treasury: {
          value: c.byCategory.treasury,
          state: "available",
          source: "mip-registry:020",
          definition: "MIPs in the treasury category.",
          updatedAt: nowIso(),
        },
        token: {
          value: c.byCategory.token,
          state: "available",
          source: "mip-registry:020",
          definition: "MIPs in the token category.",
          updatedAt: nowIso(),
        },
        other: {
          value: c.byCategory.other,
          state: "available",
          source: "mip-registry:020",
          definition: "MIPs in the other category.",
          updatedAt: nowIso(),
        },
      },
      lastActivityAt: {
        value: c.lastActivityAt ? 1 : 0,
        state: "available",
        source: "mip-registry:020",
        definition: "Whether any MIP activity exists.",
        updatedAt: nowIso(),
      },
    };
  }

  /** Recent activity events for /network feed. */
  activityEvents(limit = 10): PublicActivityEvent[] {
    const events: PublicActivityEvent[] = [];
    for (const m of mipRegistry.list()) {
      events.push({
        type: "MIPPublished",
        timestamp: m.createdAt,
        taskSlug: m.id.toLowerCase(),
      });
      // Last decision / implementation event timestamps map to other activity kinds.
      const decs = mipRegistry.decisionsFor(m.id);
      for (const d of decs) {
        if (d.decision === "accepted") {
          events.push({
            type: "MIPAccepted",
            timestamp: d.decidedAt,
            taskSlug: m.id.toLowerCase(),
          });
        }
      }
      const impls = mipRegistry.implementationsFor(m.id);
      for (const i of impls) {
        events.push({
          type: "MIPImplemented",
          timestamp: i.recordedAt,
          taskSlug: m.id.toLowerCase(),
        });
      }
    }
    events.sort((x, y) => (x.timestamp < y.timestamp ? 1 : -1));
    return events.slice(0, limit);
  }
}

export const governanceMetrics = new GovernanceMetrics();
