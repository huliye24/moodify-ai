"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";

type Decision = {
  id: string;
  decision: "accepted" | "rejected" | "returned-for-revision";
  decidedBy: string[];
  decidedAt: string;
  rationale: string;
};

type Implementation = {
  id: string;
  ref: string;
  recordedAt: string;
  recordedBy: string;
  note?: string;
};

type AuditEvent = {
  id: string;
  type: string;
  actorResidentId: string;
  timestamp: string;
  previousStatus?: string;
  nextStatus?: string;
  reason?: string;
};

type MipDetail = {
  id: string;
  slug: string;
  title: string;
  summary: string;
  category: string;
  status: string;
  authorCount: number;
  authorResidentIds: string[];
  sponsorCount: number;
  sponsorResidentIds?: string[];
  createdAt: string;
  updatedAt: string;
  discussionUrl?: string;
  decisionMethod?: string;
  implementationCount: number;
  implementationRefs?: string[];
  supersedes?: string[];
  supersededBy?: string;
  sourcePath?: string;
  sourceSha?: string;
  decisions: Decision[];
  implementationRecords: Implementation[];
  auditEvents: AuditEvent[];
};

const STATUS_COLORS: Record<string, string> = {
  draft: "rgba(0,0,0,0.45)",
  discussion: "#1a73e8",
  review: "#b45309",
  accepted: "#15803d",
  rejected: "#a33",
  implemented: "#0d9488",
  withdrawn: "rgba(0,0,0,0.55)",
  superseded: "rgba(0,0,0,0.55)",
  archived: "rgba(0,0,0,0.35)",
};

export default function MipDetailPage() {
  const params = useParams<{ id: string }>();
  const [mip, setMip] = useState<MipDetail | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!params?.id) return;
    fetch(`/api/governance/mips/${encodeURIComponent(params.id)}`)
      .then((r) => r.json())
      .then((j: any) => {
        if (j.error) setError(j.error.message);
        else setMip(j.mip ?? null);
      })
      .catch((e) => setError((e as Error).message));
  }, [params?.id]);

  if (error) {
    return (
      <main style={{ padding: "48px 24px", maxWidth: 880, margin: "0 auto" }}>
        <p style={{ color: "#a33" }}>{error}</p>
        <Link href="/governance" style={{ color: "#1a73e8" }}>
          ← Back to governance
        </Link>
      </main>
    );
  }
  if (!mip) {
    return (
      <main style={{ padding: "48px 24px", maxWidth: 880, margin: "0 auto" }}>
        <p>Loading…</p>
      </main>
    );
  }

  return (
    <main style={{ padding: "48px 24px", maxWidth: 880, margin: "0 auto" }}>
      <Link
        href="/governance"
        style={{ fontSize: 13, color: "rgba(0,0,0,0.6)", textDecoration: "none" }}
      >
        ← Back to governance
      </Link>
      <p style={{ color: "rgba(0,0,0,0.55)", letterSpacing: "0.12em", fontSize: 13, marginTop: 16 }}>
        MOOD GOVERNANCE / {mip.id}
      </p>
      <h1 style={{ fontSize: 32, margin: "8px 0 8px" }}>{mip.title}</h1>
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: 12,
          flexWrap: "wrap",
          marginBottom: 16,
        }}
      >
        <span
          style={{
            display: "inline-block",
            padding: "2px 10px",
            border: `1px solid ${STATUS_COLORS[mip.status] ?? "rgba(0,0,0,0.2)"}`,
            borderRadius: 999,
            fontSize: 12,
            color: STATUS_COLORS[mip.status] ?? "rgba(0,0,0,0.7)",
          }}
        >
          {mip.status}
        </span>
        <span
          style={{
            fontSize: 12,
            color: "rgba(0,0,0,0.55)",
            textTransform: "uppercase",
            letterSpacing: "0.08em",
          }}
        >
          {mip.category}
        </span>
        {mip.decisionMethod && (
          <span
            style={{
              fontSize: 12,
              color: "rgba(0,0,0,0.55)",
              letterSpacing: "0.06em",
            }}
          >
            · {mip.decisionMethod}
          </span>
        )}
      </div>
      <p style={{ fontSize: 16, color: "rgba(0,0,0,0.7)", lineHeight: 1.6 }}>
        {mip.summary}
      </p>

      <Section title="Authors">
        <p>{mip.authorResidentIds.join(", ") || "—"}</p>
      </Section>

      {mip.sponsorResidentIds && mip.sponsorResidentIds.length > 0 && (
        <Section title="Sponsors">
          <p>{mip.sponsorResidentIds.join(", ")}</p>
        </Section>
      )}

      <Section title="Timestamps">
        <p style={{ fontSize: 13, color: "rgba(0,0,0,0.7)" }}>
          Created: {mip.createdAt}
          <br />
          Updated: {mip.updatedAt}
        </p>
      </Section>

      {mip.discussionUrl ? (
        <Section title="Discussion">
          <p>
            <a href={mip.discussionUrl} target="_blank" rel="noopener noreferrer">
              {mip.discussionUrl}
            </a>
          </p>
        </Section>
      ) : (
        <Section title="Discussion">
          <p style={{ color: "rgba(0,0,0,0.5)" }}>Discussion not opened</p>
        </Section>
      )}

      {mip.supersedes && mip.supersedes.length > 0 && (
        <Section title="Supersedes">
          <ul>
            {mip.supersedes.map((s) => (
              <li key={s}>
                <Link href={`/governance/mips/${s.toLowerCase()}`}>{s}</Link>
              </li>
            ))}
          </ul>
        </Section>
      )}

      {mip.supersededBy && (
        <Section title="Superseded by">
          <p>
            <Link href={`/governance/mips/${mip.supersededBy.toLowerCase()}`}>
              {mip.supersededBy}
            </Link>
          </p>
        </Section>
      )}

      <Section title="Decisions">
        {mip.decisions.length === 0 ? (
          <p style={{ color: "rgba(0,0,0,0.5)" }}>No decisions yet.</p>
        ) : (
          <ul style={{ paddingLeft: 20 }}>
            {mip.decisions.map((d) => (
              <li key={d.id} style={{ marginBottom: 12 }}>
                <p style={{ margin: 0 }}>
                  <strong>{d.decision}</strong> · {d.decidedAt} · by{" "}
                  {d.decidedBy.join(", ")}
                </p>
                <p style={{ margin: "4px 0 0", color: "rgba(0,0,0,0.7)" }}>
                  {d.rationale}
                </p>
              </li>
            ))}
          </ul>
        )}
      </Section>

      <Section title="Implementation References">
        {mip.implementationRecords.length === 0 ? (
          <p style={{ color: "rgba(0,0,0,0.5)" }}>None recorded yet.</p>
        ) : (
          <ul style={{ paddingLeft: 20 }}>
            {mip.implementationRecords.map((i) => (
              <li key={i.id} style={{ marginBottom: 8 }}>
                <code>{i.ref}</code> · {i.recordedAt} · by {i.recordedBy}
                {i.note && (
                  <p style={{ margin: "4px 0 0", color: "rgba(0,0,0,0.7)" }}>
                    {i.note}
                  </p>
                )}
              </li>
            ))}
          </ul>
        )}
      </Section>

      <Section title="Audit Events">
        {mip.auditEvents.length === 0 ? (
          <p style={{ color: "rgba(0,0,0,0.5)" }}>No audit events.</p>
        ) : (
          <ul style={{ paddingLeft: 20 }}>
            {mip.auditEvents.map((a) => (
              <li key={a.id} style={{ marginBottom: 8, fontSize: 13 }}>
                <code>{a.type}</code> · {a.timestamp} · by {a.actorResidentId}
                {a.previousStatus && a.nextStatus && (
                  <span style={{ color: "rgba(0,0,0,0.55)" }}>
                    {" "}
                    ({a.previousStatus} → {a.nextStatus})
                  </span>
                )}
                {a.reason && (
                  <p
                    style={{
                      margin: "2px 0 0",
                      color: "rgba(0,0,0,0.6)",
                      fontSize: 12,
                    }}
                  >
                    {a.reason}
                  </p>
                )}
              </li>
            ))}
          </ul>
        )}
      </Section>

      {mip.sourcePath && (
        <Section title="Source">
          <p style={{ fontSize: 13, color: "rgba(0,0,0,0.7)" }}>
            <code>{mip.sourcePath}</code>
            {mip.sourceSha && <span> · sha {mip.sourceSha}</span>}
          </p>
        </Section>
      )}
    </main>
  );
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section style={{ marginTop: 24 }}>
      <h2 style={{ fontSize: 16, margin: "0 0 8px", color: "rgba(0,0,0,0.85)" }}>
        {title}
      </h2>
      <div style={{ fontSize: 14, color: "rgba(0,0,0,0.7)" }}>{children}</div>
    </section>
  );
}
