"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";

type Node = {
  id: string;
  slug: string;
  name: string;
  role: string;
  status: string;
  capabilities: string[];
  publicRegion?: string;
  version?: string;
  publicEndpoint?: string;
  capacity?: Record<string, unknown>;
  createdAt: string;
  updatedAt: string;
  lastSeenAt?: string;
  lastHeartbeatAt?: string;
  operatorLabel?: string;
};

export default function NodeDetailPage() {
  const params = useParams<{ slug: string }>();
  const slug = params?.slug;
  const [node, setNode] = useState<Node | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!slug) return;
    fetch(`/api/nodes/${slug}`)
      .then((r) => r.json())
      .then((j: any) => {
        if (j.error) setError(j.error.message);
        else setNode(j.node);
      })
      .catch((e) => setError((e as Error).message));
  }, [slug]);

  if (error) {
    return (
      <main style={{ padding: 48, maxWidth: 720, margin: "0 auto" }}>
        <p style={{ color: "#a33" }}>{error}</p>
        <Link href="/nodes">← back to /nodes</Link>
      </main>
    );
  }
  if (!node) {
    return (
      <main style={{ padding: 48, maxWidth: 720, margin: "0 auto" }}>
        <p>Loading…</p>
      </main>
    );
  }

  return (
    <main style={{ padding: "48px 24px", maxWidth: 720, margin: "0 auto" }}>
      <Link href="/nodes" style={{ fontSize: 13, color: "rgba(0,0,0,0.55)" }}>
        ← /nodes
      </Link>
      <p
        style={{
          marginTop: 24,
          color: "rgba(0,0,0,0.55)",
          letterSpacing: "0.12em",
          fontSize: 13,
        }}
      >
        MOOD / NODE / {node.role.toUpperCase()}
      </p>
      <h1 style={{ fontSize: 36, margin: "8px 0 8px" }}>{node.name}</h1>
      <p style={{ fontSize: 14, color: "rgba(0,0,0,0.55)" }}>
        Status: <strong>{node.status}</strong> · Operator: {node.operatorLabel ?? "—"}
      </p>

      <section
        style={{
          marginTop: 24,
          padding: 16,
          border: "1px solid rgba(0,0,0,0.1)",
          borderRadius: 12,
        }}
      >
        <Row label="Role" value={node.role} />
        <Row label="Region" value={node.publicRegion ?? "—"} />
        <Row label="Version" value={node.version ?? "—"} />
        <Row label="Public endpoint" value={node.publicEndpoint ?? "—"} />
        <Row label="Capabilities" value={node.capabilities.join(", ") || "—"} />
        <Row label="Created" value={new Date(node.createdAt).toLocaleString()} />
        <Row label="Last seen" value={node.lastSeenAt ? new Date(node.lastSeenAt).toLocaleString() : "—"} />
      </section>

      {node.capacity && Object.keys(node.capacity).length > 0 && (
        <section
          style={{
            marginTop: 24,
            padding: 16,
            border: "1px solid rgba(0,0,0,0.1)",
            borderRadius: 12,
          }}
        >
          <h2 style={{ fontSize: 18, margin: "0 0 12px" }}>Capacity</h2>
          {Object.entries(node.capacity).map(([k, v]) => (
            <Row key={k} label={k} value={String(v)} />
          ))}
        </section>
      )}

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
          Public node records never expose private IPs, SSH endpoints, cloud
          account IDs, database credentials, or internal hostnames. Operators
          may choose to expose a public service endpoint; if no safe endpoint
          exists, publicEndpoint is empty.
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