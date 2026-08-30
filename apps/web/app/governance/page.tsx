"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

type MipSummary = {
  id: string;
  slug: string;
  title: string;
  summary: string;
  category: string;
  status: string;
  authorCount: number;
  createdAt: string;
  updatedAt: string;
  discussionUrl?: string;
  decisionMethod?: string;
  implementationCount: number;
};

type Counts = {
  total: number;
  byStatus: Record<string, number>;
  byCategory: Record<string, number>;
  lastActivityAt: string | null;
};

const STATUS_LABELS: Record<string, string> = {
  draft: "Draft",
  discussion: "Discussion",
  review: "Review",
  accepted: "Accepted",
  rejected: "Rejected",
  implemented: "Implemented",
  withdrawn: "Withdrawn",
  superseded: "Superseded",
  archived: "Archived",
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

export default function GovernancePage() {
  const [mips, setMips] = useState<MipSummary[]>([]);
  const [counts, setCounts] = useState<Counts | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch("/api/governance/mips")
      .then((r) => r.json())
      .then((j: any) => {
        if (j.error) setError(j.error.message);
        else {
          setMips(j.mips ?? []);
          setCounts(j.counts ?? null);
        }
      })
      .catch((e) => setError((e as Error).message));
  }, []);

  return (
    <main style={{ padding: "48px 24px", maxWidth: 960, margin: "0 auto" }}>
      <p style={{ color: "rgba(0,0,0,0.55)", letterSpacing: "0.12em", fontSize: 13 }}>
        MOOD / GOVERNANCE
      </p>
      <h1 style={{ fontSize: 40, margin: "8px 0 16px" }}>MOOD Governance</h1>
      <p style={{ fontSize: 16, color: "rgba(0,0,0,0.7)", maxWidth: 720, lineHeight: 1.6 }}>
        How decisions are made in MOOD. Every change to the canonical protocol
        is recorded as a MOOD Improvement Proposal (MIP). MOOD Governance v1 is
        transparent and versioned — it is process-transparent but not yet
        fully decentralized.
      </p>

      {counts && (
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(140px, 1fr))",
            gap: 12,
            margin: "24px 0",
          }}
        >
          <Stat label="Total MIPs" value={counts.total} />
          <Stat label="In Discussion" value={counts.byStatus.discussion ?? 0} />
          <Stat label="In Review" value={counts.byStatus.review ?? 0} />
          <Stat label="Accepted" value={counts.byStatus.accepted ?? 0} />
          <Stat label="Implemented" value={counts.byStatus.implemented ?? 0} />
        </div>
      )}

      {error && <p style={{ color: "#a33" }}>{error}</p>}

      {mips.length === 0 && !error ? (
        <p style={{ color: "rgba(0,0,0,0.5)" }}>No MIPs registered yet.</p>
      ) : (
        <ul style={{ listStyle: "none", padding: 0, marginTop: 24 }}>
          {mips.map((m) => (
            <li
              key={m.id}
              style={{
                padding: 20,
                marginBottom: 12,
                border: "1px solid rgba(0,0,0,0.1)",
                borderRadius: 12,
                background: "rgba(255,255,255,0.6)",
              }}
            >
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: 12,
                  flexWrap: "wrap",
                }}
              >
                <Link
                  href={`/governance/mips/${m.id.toLowerCase()}`}
                  style={{
                    fontSize: 20,
                    fontWeight: 600,
                    color: "#1a1340",
                    textDecoration: "none",
                  }}
                >
                  {m.id} — {m.title}
                </Link>
                <span
                  style={{
                    display: "inline-block",
                    padding: "2px 10px",
                    border: `1px solid ${STATUS_COLORS[m.status] ?? "rgba(0,0,0,0.2)"}`,
                    borderRadius: 999,
                    fontSize: 12,
                    color: STATUS_COLORS[m.status] ?? "rgba(0,0,0,0.7)",
                  }}
                >
                  {STATUS_LABELS[m.status] ?? m.status}
                </span>
                <span
                  style={{
                    fontSize: 12,
                    color: "rgba(0,0,0,0.55)",
                    textTransform: "uppercase",
                    letterSpacing: "0.08em",
                  }}
                >
                  {m.category}
                </span>
              </div>
              <p style={{ margin: "8px 0 0", color: "rgba(0,0,0,0.7)" }}>
                {m.summary}
              </p>
              <p
                style={{
                  margin: "8px 0 0",
                  fontSize: 13,
                  color: "rgba(0,0,0,0.55)",
                }}
              >
                {m.authorCount} author{m.authorCount === 1 ? "" : "s"}
                {m.implementationCount > 0
                  ? ` · ${m.implementationCount} implementation ref${m.implementationCount === 1 ? "" : "s"}`
                  : ""}
              </p>
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
        <h2 style={{ marginTop: 0, fontSize: 18 }}>Governance Principles</h2>
        <ul style={{ margin: 0, paddingLeft: 20, lineHeight: 1.7, color: "rgba(0,0,0,0.7)" }}>
          <li>
            <strong>Maintainer-reviewed governance.</strong> 020 uses explicit
            decisions by authorized reviewers. It is process-transparent but
            not yet fully decentralized.
          </li>
          <li>
            <strong>No token voting.</strong> Future-token-vote is reserved as
            a decision method but is currently disabled. No MOOD balance, no
            delegation by stake.
          </li>
          <li>
            <strong>No canon auto-rewrite.</strong> An Accepted MIP does not
            automatically rewrite <code>CURRENT_CANON.md</code>. Canon updates
            require an explicit implementation PR reviewed by humans.
          </li>
          <li>
            <strong>Append-only audit.</strong> Every state change produces an
            audit event with actor, timestamp, and reason. Superseded MIPs
            remain readable forever.
          </li>
          <li>
            <strong>Emergency policy.</strong> Critical security issues may be
            paused without a full MIP cycle, but the action must be logged
            with actor, reason, and time, and followed by a retrospective
            MIP / incident report.
          </li>
        </ul>
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
          fontSize: 11,
          color: "rgba(0,0,0,0.55)",
          letterSpacing: "0.08em",
          textTransform: "uppercase",
        }}
      >
        {label}
      </p>
      <p style={{ margin: "6px 0 0", fontSize: 22, fontWeight: 700 }}>{value}</p>
    </div>
  );
}
