/**
 * MOOD AGENTS 018 — Agent metrics for /network Observatory.
 *
 * Extends the 017 NetworkObservatory with:
 * - agents.total / active / degraded / offline
 * - agents.lastActivity
 * - activity events: AgentRegistered / AgentStatusChanged / AgentTaskCompleted / AgentProofSubmitted
 *
 * Authority: MOOD-AGENTS-018 TASK.md Phase N.
 */

import type { MetricValue, PublicActivityEvent } from "../network/types.ts";
import { agentRegistry } from "./registry.ts";

function nowIso(): string {
  return new Date().toISOString();
}

export class AgentMetrics {
  /** /network "Agents" card group. */
  summary(): {
    total: MetricValue;
    active: MetricValue;
    degraded: MetricValue;
    offline: MetricValue;
    lastActivity: MetricValue;
  } {
    const c = agentRegistry.counts();
    return {
      total: {
        value: c.total,
        state: "available",
        source: "agent-registry:018",
        definition: "Total registered AI Agents.",
        updatedAt: nowIso(),
      },
      active: {
        value: c.active,
        state: "available",
        source: "agent-registry:018",
        definition: "Agents with recent OK heartbeat.",
        updatedAt: nowIso(),
      },
      degraded: {
        value: c.degraded,
        state: "available",
        source: "agent-registry:018",
        definition: "Agents with recent error heartbeat but still registered.",
        updatedAt: nowIso(),
      },
      offline: {
        value: c.offline,
        state: "available",
        source: "agent-registry:018",
        definition: "Active agents whose heartbeat is stale or absent.",
        updatedAt: nowIso(),
      },
      lastActivity: {
        value: null,
        state: c.total === 0 ? "unavailable" : "available",
        source: "agent-registry:018",
        definition: "Most recent agent task timestamp (epoch ms).",
        updatedAt: nowIso(),
      },
    };
  }

  /** Recent activity events for /network feed. */
  activityEvents(limit = 10): PublicActivityEvent[] {
    const events: PublicActivityEvent[] = [];
    for (const a of agentRegistry.list()) {
      // Initial registration event.
      events.push({
        type: "AgentRegistered",
        timestamp: a.createdAt,
        // agent slug exposed via additional field if added later; for now
        // leave taskSlug undefined to keep serializer small.
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

export const agentMetrics = new AgentMetrics();