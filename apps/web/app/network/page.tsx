"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

type MetricValue = {
  value: number | null;
  state: "available" | "unavailable" | "coming-soon" | "stale";
  source: string;
  definition?: string;
  updatedAt?: string;
};

type Overview = {
  status: string;
  generatedAt: string;
  sourceUpdatedAt: string;
  metrics: Record<string, MetricValue | undefined>;
};

type Activity = {
  type: string;
  timestamp: string;
  taskSlug?: string;
  submissionId?: string;
  reputationDelta?: number;
};

const METRIC_LABELS: Record<string, { label: string; group: string }> = {
  residents: { label: "Residents", group: "Identity" },
  contributors: { label: "Contributors", group: "Identity" },
  openTasks: { label: "Open Tasks", group: "Contribution" },
  submissions: { label: "Submissions", group: "Contribution" },
  approvedContributions: { label: "Approved", group: "Contribution" },
  reputationEvents: { label: "Reputation Events", group: "Contribution" },
  pendingReward: { label: "Pending Reward Records", group: "Contribution" },
  applications: { label: "Applications", group: "Network" },
  agents: { label: "Agents", group: "Network" },
  nodes: { label: "Nodes", group: "Network" },
  mips: { label: "MIPs", group: "Network" },
};

function formatValue(m: MetricValue | undefined): string {
  if (!m) return "—";
  if (m.state === "coming-soon") return "Coming Soon";
  if (m.state === "unavailable") return "Unavailable";
  if (m.state === "stale") return "Stale";
  if (m.value === null) return "—";
  return String(m.value);
}

export default function NetworkPage() {
  const [overview, setOverview] = useState<Overview | null>(null);
  const [activity, setActivity] = useState<Activity[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch("/api/network/overview")
      .then((r) => r.json())
      .then((j) => setOverview(j))
      .catch((e) => setError((e as Error).message));
    fetch("/api/network/activity?limit=20")
      .then((r) => r.json())
      .then((j) => setActivity(j.events ?? []))
      .catch((e) => setError((e as Error).message));
  }, []);

  const groups: Record<string, Array<{ key: string; metric: MetricValue | undefined }>> = {};
  if (overview) {
    for (const [key, m] of Object.entries(overview.metrics)) {
      const g = METRIC_LABELS[key]?.group ?? "Other";
      if (!groups[g]) groups[g] = [];
      groups[g].push({ key, metric: m });
    }
  }

  return (
    <main style={{ padding: "48px 24px", maxWidth: 1080, margin: "0 auto" }}>
      <p style={{ color: "rgba(0,0,0,0.55)", letterSpacing: "0.12em", fontSize: 13 }}>
        MOOD / NETWORK
      </p>
      <h1 style={{ fontSize: 40, margin: "8px 0 8px" }}>MOOD Network</h1>
      <p style={{ fontSize: 16, color: "rgba(0,0,0,0.7)", maxWidth: 640, lineHeight: 1.6 }}>
        A living view of the world being built. Numbers here come from real
        registries — not from a marketing dashboard.
      </p>
      {overview && (
        <p style={{ marginTop: 16, fontSize: 13, color: "rgba(0,0,0,0.55)" }}>
          Status: <strong>{overview.status}</strong> · Updated:{" "}
          {new Date(overview.generatedAt).toLocaleString()}
        </p>
      )}

      {error && (
        <p style={{ color: "#a33", marginTop: 16 }}>{error}</p>
      )}

      {overview && (
        <div style={{ display: "grid", gap: 24, marginTop: 32 }}>
          {Object.entries(groups).map(([group, items]) => (
            <section key={group}>
              <h2 style={{ fontSize: 20, margin: "0 0 12px" }}>{group}</h2>
              <div
                style={{
                  display: "grid",
                  gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))",
                  gap: 12,
                }}
              >
                {items.map(({ key, metric }) => (
                  <div
                    key={key}
                    style={{
                      padding: 16,
                      border: "1px solid rgba(0,0,0,0.1)",
                      borderRadius: 12,
                      background:
                        metric?.state === "available"
                          ? "rgba(255,255,255,0.7)"
                          : "rgba(0,0,0,0.03)",
                    }}
                  >
                    <p
                      style={{
                        margin: 0,
                        fontSize: 12,
                        color: "rgba(0,0,0,0.55)",
                        letterSpacing: "0.08em",
                        textTransform: "uppercase",
                      }}
                    >
                      {METRIC_LABELS[key]?.label ?? key}
                    </p>
                    <p
                      style={{
                        margin: "6px 0 0",
                        fontSize: 28,
                        fontWeight: 700,
                        color:
                          metric?.state === "coming-soon"
                            ? "rgba(0,0,0,0.4)"
                            : "#1a1340",
                      }}
                    >
                      {formatValue(metric)}
                    </p>
                    {metric?.definition && (
                      <p
                        style={{
                          margin: "6px 0 0",
                          fontSize: 11,
                          color: "rgba(0,0,0,0.5)",
                        }}
                      >
                        {metric.definition}
                      </p>
                    )}
                  </div>
                ))}
              </div>
            </section>
          ))}
        </div>
      )}

      <section style={{ marginTop: 48 }}>
        <h2 style={{ fontSize: 22, marginBottom: 12 }}>Activity</h2>
        {activity.length === 0 ? (
          <p style={{ color: "rgba(0,0,0,0.5)" }}>
            No public activity yet.
          </p>
        ) : (
          <ul style={{ listStyle: "none", padding: 0, margin: 0 }}>
            {activity.map((a, i) => (
              <li
                key={i}
                style={{
                  padding: 12,
                  borderBottom: "1px solid rgba(0,0,0,0.08)",
                  fontSize: 14,
                }}
              >
                <strong>{a.type}</strong>
                {a.taskSlug ? (
                  <>
                    {" · "}
                    <Link href={`/build/${a.taskSlug}`}>{a.taskSlug}</Link>
                  </>
                ) : null}
                {typeof a.reputationDelta === "number" ? (
                  ` · ${a.reputationDelta > 0 ? "+" : ""}${a.reputationDelta} reputation`
                ) : null}
                <span style={{ color: "rgba(0,0,0,0.5)", marginLeft: 8 }}>
                  {new Date(a.timestamp).toLocaleString()}
                </span>
              </li>
            ))}
          </ul>
        )}
      </section>

      <section style={{ marginTop: 48, padding: 16, border: "1px solid rgba(0,0,0,0.08)", borderRadius: 12, background: "rgba(0,0,0,0.02)" }}>
        <p style={{ margin: 0, fontSize: 13, color: "rgba(0,0,0,0.6)" }}>
          This page observes the MOOD Foundation Network. It does not display Token price,
          market cap, volume, liquidity, holder counts, or Flap tax. Those belong to
          future Token / Economics layers and are intentionally absent.
        </p>
      </section>
    </main>
  );
}