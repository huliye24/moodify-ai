"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";

type Agent = {
  id: string;
  slug: string;
  name: string;
  description: string;
  status: string;
  capabilities: string[];
  runtimeType?: string;
  modelProvider?: string;
  modelName?: string;
  version?: string;
  lastSeenAt?: string;
  lastTaskAt?: string;
  lastSuccessAt?: string;
  lastErrorAt?: string;
  createdAt: string;
  updatedAt: string;
  operatorLabel?: string;
};

export default function AgentDetailPage() {
  const params = useParams<{ slug: string }>();
  const slug = params?.slug;
  const [agent, setAgent] = useState<Agent | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!slug) return;
    fetch(`/api/agents/${slug}`)
      .then((r) => r.json())
      .then((j) => {
        if (j.error) setError(j.error.message);
        else setAgent(j.agent);
      })
      .catch((e) => setError((e as Error).message));
  }, [slug]);

  if (error) {
    return (
      <main style={{ padding: 48, maxWidth: 720, margin: "0 auto" }}>
        <p style={{ color: "#a33" }}>{error}</p>
        <Link href="/agents">← back to /agents</Link>
      </main>
    );
  }
  if (!agent) {
    return (
      <main style={{ padding: 48, maxWidth: 720, margin: "0 auto" }}>
        <p>Loading…</p>
      </main>
    );
  }

  return (
    <main style={{ padding: "48px 24px", maxWidth: 720, margin: "0 auto" }}>
      <Link href="/agents" style={{ fontSize: 13, color: "rgba(0,0,0,0.55)" }}>
        ← /agents
      </Link>
      <p
        style={{
          marginTop: 24,
          color: "rgba(0,0,0,0.55)",
          letterSpacing: "0.12em",
          fontSize: 13,
        }}
      >
        MOOD / AGENT / {agent.status.toUpperCase()}
      </p>
      <h1 style={{ fontSize: 36, margin: "8px 0 8px" }}>{agent.name}</h1>
      <p style={{ fontSize: 16, color: "rgba(0,0,0,0.7)", lineHeight: 1.6 }}>
        {agent.description}
      </p>

      <section
        style={{
          marginTop: 24,
          padding: 16,
          border: "1px solid rgba(0,0,0,0.1)",
          borderRadius: 12,
        }}
      >
        <Row label="Operator" value={agent.operatorLabel ?? "—"} />
        <Row label="Version" value={agent.version ?? "—"} />
        <Row label="Runtime" value={agent.runtimeType ?? "—"} />
        <Row label="Model" value={`${agent.modelProvider ?? "—"} ${agent.modelName ?? ""}`.trim()} />
        <Row label="Capabilities" value={agent.capabilities.join(", ")} />
        <Row label="Created" value={new Date(agent.createdAt).toLocaleString()} />
        <Row label="Last seen" value={agent.lastSeenAt ? new Date(agent.lastSeenAt).toLocaleString() : "—"} />
        <Row label="Last task" value={agent.lastTaskAt ? new Date(agent.lastTaskAt).toLocaleString() : "—"} />
        <Row label="Last success" value={agent.lastSuccessAt ? new Date(agent.lastSuccessAt).toLocaleString() : "—"} />
        <Row label="Last error" value={agent.lastErrorAt ? new Date(agent.lastErrorAt).toLocaleString() : "—"} />
      </section>

      <section
        style={{
          marginTop: 24,
          padding: 16,
          border: "1px solid rgba(0,0,0,0.08)",
          borderRadius: 12,
          background: "rgba(0,0,0,0.02)",
        }}
      >
        <p style={{ margin: 0, fontSize: 13, color: "rgba(0,0,0,0.6)" }}>
          Agents do not hold funds. API keys, system prompts, and secret
          endpoints are never exposed in this registry.
        </p>
      </section>
    </main>
  );
}

function Row({ label, value }: { label: string; value: string }) {
  return (
    <div
      style={{
        display: "grid",
        gridTemplateColumns: "120px 1fr",
        padding: "8px 0",
        borderBottom: "1px solid rgba(0,0,0,0.06)",
      }}
    >
      <span style={{ fontSize: 13, color: "rgba(0,0,0,0.55)" }}>{label}</span>
      <span style={{ fontSize: 14, color: "rgba(0,0,0,0.85)" }}>{value}</span>
    </div>
  );
}