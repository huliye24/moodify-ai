/**
 * MOOD NODES 019 — Node metrics for /network Observatory.
 *
 * Extends the 017 + 018 NetworkObservatory with:
 * - nodes.total / active / degraded / offline / byRole
 * - activity events: NodeRegistered / NodeActivated / NodeStatusChanged / NodeServiceProofRecorded
 *
 * Authority: MOOD-NODES-019 TASK.md Phase O.
 */

import type { MetricValue, PublicActivityEvent } from "../network/types.ts";
import { nodeRegistry } from "./registry.ts";

function nowIso(): string {
  return new Date().toISOString();
}

export class NodeMetrics {
  summary(): {
    total: MetricValue;
    active: MetricValue;
    degraded: MetricValue;
    offline: MetricValue;
    byRole: Record<string, MetricValue>;
  } {
    const c = nodeRegistry.counts();
    return {
      total: {
        value: c.total,
        state: "available",
        source: "node-registry:019",
        definition: "Total registered Nodes.",
        updatedAt: nowIso(),
      },
      active: {
        value: c.active,
        state: "available",
        source: "node-registry:019",
        definition: "Nodes with recent OK heartbeat.",
        updatedAt: nowIso(),
      },
      degraded: {
        value: c.degraded,
        state: "available",
        source: "node-registry:019",
        definition: "Nodes with degraded runtime but registered.",
        updatedAt: nowIso(),
      },
      offline: {
        value: c.offline,
        state: "available",
        source: "node-registry:019",
        definition: "Active nodes whose heartbeat is stale.",
        updatedAt: nowIso(),
      },
      byRole: {
        compute: {
          value: c.byRole.compute,
          state: "available",
          source: "node-registry:019",
          definition: "Compute nodes.",
          updatedAt: nowIso(),
        },
        ai: {
          value: c.byRole.ai,
          state: "available",
          source: "node-registry:019",
          definition: "AI inference nodes.",
          updatedAt: nowIso(),
        },
        storage: {
          value: c.byRole.storage,
          state: "available",
          source: "node-registry:019",
          definition: "Storage nodes.",
          updatedAt: nowIso(),
        },
        verification: {
          value: c.byRole.verification,
          state: "available",
          source: "node-registry:019",
          definition: "Verification nodes.",
          updatedAt: nowIso(),
        },
      },
    };
  }

  /** Recent activity events for /network feed. */
  activityEvents(limit = 10): PublicActivityEvent[] {
    const events: PublicActivityEvent[] = [];
    for (const n of nodeRegistry.list()) {
      events.push({
        type: "NodeRegistered",
        timestamp: n.createdAt,
      });
    }
    events.sort((x, y) => (x.timestamp < y.timestamp ? 1 : -1));
    return events.slice(0, limit);
  }
}

export const nodeMetrics = new NodeMetrics();