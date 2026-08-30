"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

type NodeSummary = {
  id: string;
  slug: string;
  name: string;
  role: "compute" | "ai" | "storage" | "verification";
  status: string;
  capabilities: string[];
  publicRegion?: string;
  version?: string;
  operatorLabel?: string;
  lastSeenAt?: string;
};

type Counts = {
  total: number;
  active: number;
  degraded: number;
  offline: number;
  byRole: Record<string, number>;
};

export default function NodesPage() {
  const [nodes, setNodes] = useState<NodeSummary[]>([]);
  const [counts, setCounts] = useState<Counts | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch("/api/nodes")
      .then((r) => r.json())
      .then((j) => {
        if (j.error) setError(j.error.message);
        else {
          setNodes(j.nodes ?? []);
          setCounts(j.counts ?? null);
        }
      })
      .catch((e) => setError((e as Error).message));
  }, []);

  return (
    <main style={{ padding: "48px 24px", maxWidth: 960, margin: "0 auto" }}>
      <p style={{ color: "rgba(0,0,0,0.55)", letterSpacing: "0.12em", fontSize: 13 }}>
        MOOD / NODES
      </p>
      <h1 style={{ fontSize: 40, margin: "8px 0 16px" }}>MOOD Node Network</h1>
      <p style={{ fontSize: 16, color: "rgba(0,0,0,0.7)", maxWidth: 640, lineHeight: 1.6 }}>
        Compute, AI inference, storage, and verification nodes powering the
        network. Each node has a real operator and a coarse-grained public
        region. Status comes from heartbeats — no heartbeat, no &quot;Online&quot;.
      </p>

      {counts && (
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(160px, 1fr))",
            gap: 12,
            margin: "24px 0",
          }}
        >
          <Stat label="Total" value={counts.total} />
          <Stat label="Active" value={counts.active} />
          <Stat label="Degraded" value={counts.degraded} />
          <Stat label="Offline" value={counts.offline} />
        </div>
      )}

      {counts && (
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(160px, 1fr))",
            gap: 12,
            marginBottom: 24,
          }}
        >
          <Stat label="Compute" value={counts.byRole.compute ?? 0} />
          <Stat label="AI" value={counts.byRole.ai ?? 0} />
          <Stat label="Storage" value={counts.byRole.storage ?? 0} />
          <Stat label="Verification" value={counts.byRole.verification ?? 0} />
        </div>
      )}

      {error && <p style={{ color: "#a33" }}>{error}</p>}

      {nodes.length === 0 && !error ? (
        <p style={{ color: "rgba(0,0,0,0.5)" }}>
          No nodes registered yet. Operators can register via the admin flow.
        </p>
      ) : (
        <ul style={{ listStyle: "none", padding: 0 }}>
          {nodes.map((n) => (
            <li
              key={n.id}
              style={{
                padding: 20,
                marginBottom: 12,
                border: "1px solid rgba(0,0,0,0.1)",
                borderRadius: 12,
              }}
            >
              <Link
                href={`/nodes/${n.slug}`}
                style={{
                  fontSize: 20,
                  fontWeight: 600,
                  color: "#1a1340",
                  textDecoration: "none",
                }}
              >
                {n.name}
              </Link>
              <p style={{ margin: "8px 0 4px", color: "rgba(0,0,0,0.7)" }}>
                Role: <strong>{n.role}</strong>
                {n.publicRegion ? ` · ${n.publicRegion}` : ""}
                {n.version ? ` · v${n.version}` : ""}
              </p>
              <p style={{ margin: 0, fontSize: 13, color: "rgba(0,0,0,0.55)" }}>
                Status: <strong>{n.status}</strong>
                {n.operatorLabel ? ` · ${n.operatorLabel}` : ""}
              </p>
              <div style={{ marginTop: 8 }}>
                {n.capabilities.map((c) => (
                  <span
                    key={c}
                    style={{
                      display: "inline-block",
                      padding: "2px 10px",
                      marginRight: 6,
                      border: "1px solid rgba(0,0,0,0.15)",
                      borderRadius: 999,
                      fontSize: 12,
                      color: "rgba(0,0,0,0.7)",
                    }}
                  >
                    {c}
                  </span>
                ))}
              </div>
            </li>
          ))}
        </ul>
      )}

      <section
        style={{
          marginTop: 48,
          padding: 16,
          border: "1px solid rgba(0,0,0,0.08)",
          borderRadius: 12,
          background: "rgba(0,0,0,0.02)",
        }}
      >
        <p style={{ margin: 0, fontSize: 13, color: "rgba(0,0,0,0.6)" }}>
          Public node records never expose private IPs, SSH endpoints, cloud
          account IDs, database credentials, or internal hostnames. There is
          no mining, staking, validator yield, or slashing in 019. Operators
          may choose to expose a public service endpoint; if no safe endpoint
          exists, publicEndpoint remains empty.
        </p>
      </section>
    </main>
  );
}

function Stat({ label, value }: { label: string; value: number }) {
  return (
    <div
      style={{
        padding: 12,
        border: "1px solid rgba(0,0,0,0.1)",
        borderRadius: 10,
        background: "rgba(255,255,255,0.7)",
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
        {label}
      </p>
      <p style={{ margin: "6px 0 0", fontSize: 24, fontWeight: 700 }}>{value}</p>
    </div>
  );
}