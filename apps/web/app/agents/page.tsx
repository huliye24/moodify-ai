"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

type Agent = {
  id: string;
  slug: string;
  name: string;
  description: string;
  status: string;
  capabilities: string[];
  version?: string;
  lastSeenAt?: string;
  operatorLabel?: string;
};

type Counts = {
  total: number;
  active: number;
  degraded: number;
  offline: number;
};

export default function AgentsPage() {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [counts, setCounts] = useState<Counts | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch("/api/agents")
      .then((r) => r.json())
      .then((j) => {
        if (j.error) setError(j.error.message);
        else {
          setAgents(j.agents ?? []);
          setCounts(j.counts ?? null);
        }
      })
      .catch((e) => setError((e as Error).message));
  }, []);

  return (
    <main style={{ padding: "48px 24px", maxWidth: 960, margin: "0 auto" }}>
      <p style={{ color: "rgba(0,0,0,0.55)", letterSpacing: "0.12em", fontSize: 13 }}>
        MOOD / AGENTS
      </p>
      <h1 style={{ fontSize: 40, margin: "8px 0 16px" }}>MOOD Agent Network</h1>
      <p style={{ fontSize: 16, color: "rgba(0,0,0,0.7)", maxWidth: 640, lineHeight: 1.6 }}>
        AI Agents registered on the MOOD network. Each agent is bound to a real
        operator. Status comes from heartbeats — agents without heartbeats are
        never shown as &quot;Online&quot;.
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
          <Stat label="Registered" value={counts.total} />
          <Stat label="Active" value={counts.active} />
          <Stat label="Degraded" value={counts.degraded} />
          <Stat label="Offline" value={counts.offline} />
        </div>
      )}

      {error && <p style={{ color: "#a33" }}>{error}</p>}

      {agents.length === 0 && !error ? (
        <p style={{ color: "rgba(0,0,0,0.5)" }}>
          No agents registered yet. Operators can register via the admin flow.
        </p>
      ) : (
        <ul style={{ listStyle: "none", padding: 0 }}>
          {agents.map((a) => (
            <li
              key={a.id}
              style={{
                padding: 20,
                marginBottom: 12,
                border: "1px solid rgba(0,0,0,0.1)",
                borderRadius: 12,
              }}
            >
              <Link
                href={`/agents/${a.slug}`}
                style={{
                  fontSize: 20,
                  fontWeight: 600,
                  color: "#1a1340",
                  textDecoration: "none",
                }}
              >
                {a.name}
              </Link>
              <p style={{ margin: "8px 0 4px", color: "rgba(0,0,0,0.7)" }}>
                {a.description}
              </p>
              <p style={{ margin: 0, fontSize: 13, color: "rgba(0,0,0,0.55)" }}>
                Status: <strong>{a.status}</strong>
                {a.version ? ` · v${a.version}` : ""}
                {a.operatorLabel ? ` · ${a.operatorLabel}` : ""}
              </p>
              <div style={{ marginTop: 8 }}>
                {a.capabilities.map((c) => (
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
          Agents do not hold funds. They have no Treasury signer, no production
          wallet private key, and no automatic transfer tool. API keys, system
          prompts, and secret endpoints are never exposed in this registry.
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