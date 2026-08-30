"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";

type TaskDetail = {
  id: string;
  slug: string;
  title: string;
  summary: string;
  description: string;
  category: string;
  status: string;
  evidenceRequirements: string[];
  defaultReputationPoints: number;
  defaultRewardUnits?: string;
  deadline?: string;
  maxApprovals?: number;
};

export default function BuildTaskPage() {
  const params = useParams<{ slug: string }>();
  const slug = params?.slug;
  const [task, setTask] = useState<TaskDetail | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [me, setMe] = useState<{ resident: { id: string } } | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [summary, setSummary] = useState("");
  const [evidenceUrl, setEvidenceUrl] = useState("");
  const [evidenceLabel, setEvidenceLabel] = useState("");
  const [submitResult, setSubmitResult] = useState<{
    id: string;
    status: string;
  } | null>(null);

  useEffect(() => {
    if (!slug) return;
    fetch(`/api/contribution/tasks/${slug}`)
      .then((r) => r.json())
      .then((j: any) => {
        if (j.error) setError(j.error.message);
        else setTask(j.task);
      })
      .catch((e) => setError((e as Error).message));
    fetch("/api/resident/me", { credentials: "same-origin" })
      .then(async (r) => {
        if (r.status === 401) return null;
        return r.json();
      })
      .then((j: any) => {
        if (j) setMe(j);
      })
      .catch(() => {/* not signed in */});
  }, [slug]);

  async function handleSubmit() {
    if (!task || !me) return;
    setSubmitting(true);
    setError(null);
    setSubmitResult(null);
    try {
      const evidenceItems = evidenceUrl
        ? [
            {
              type: "url",
              value: evidenceUrl,
              label: evidenceLabel || undefined,
            },
          ]
        : [];
      const res = await fetch(
        `/api/contribution/tasks/${task.slug}/submissions`,
        {
          method: "POST",
          credentials: "same-origin",
          headers: {
            "content-type": "application/json",
            "x-resident-id": me.resident.id,
          },
          body: JSON.stringify({ summary, evidenceItems }),
        },
      );
      const j: any = await res.json();
      if (j.error) {
        setError(j.error.message);
      } else {
        setSubmitResult({ id: j.submission.id, status: j.submission.status });
        setSummary("");
        setEvidenceUrl("");
        setEvidenceLabel("");
      }
    } finally {
      setSubmitting(false);
    }
  }

  if (error) {
    return (
      <main style={{ padding: 48, maxWidth: 720, margin: "0 auto" }}>
        <p style={{ color: "#a33" }}>{error}</p>
        <Link href="/build">← back to /build</Link>
      </main>
    );
  }
  if (!task) {
    return (
      <main style={{ padding: 48, maxWidth: 720, margin: "0 auto" }}>
        <p>Loading…</p>
      </main>
    );
  }

  return (
    <main style={{ padding: "48px 24px", maxWidth: 720, margin: "0 auto" }}>
      <Link href="/build" style={{ fontSize: 13, color: "rgba(0,0,0,0.55)" }}>
        ← /build
      </Link>
      <p style={{ marginTop: 24, color: "rgba(0,0,0,0.55)", letterSpacing: "0.12em", fontSize: 13 }}>
        MOOD / BUILD / {task.category.toUpperCase()}
      </p>
      <h1 style={{ fontSize: 36, margin: "8px 0 16px" }}>{task.title}</h1>
      <p style={{ fontSize: 16, color: "rgba(0,0,0,0.7)", lineHeight: 1.6 }}>
        {task.description}
      </p>

      <section style={{ marginTop: 24, padding: 16, border: "1px solid rgba(0,0,0,0.1)", borderRadius: 12 }}>
        <p style={{ margin: "0 0 8px", fontSize: 14, color: "rgba(0,0,0,0.6)" }}>
          Reward on approval: +{task.defaultReputationPoints} reputation
          {task.defaultRewardUnits
            ? ` · ${task.defaultRewardUnits} pending units (not on-chain)`
            : ""}
        </p>
        <p style={{ margin: 0, fontSize: 13, color: "rgba(0,0,0,0.55)" }}>
          Evidence required:
        </p>
        <ul style={{ margin: "4px 0 0 16px", padding: 0 }}>
          {task.evidenceRequirements.map((r, i) => (
            <li key={i} style={{ fontSize: 13 }}>{r}</li>
          ))}
        </ul>
      </section>

      <section style={{ marginTop: 32 }}>
        {!me ? (
          <div style={{ padding: 24, border: "1px solid rgba(0,0,0,0.1)", borderRadius: 12 }}>
            <p style={{ margin: 0 }}>
              <Link href="/portal/passport">Connect with MOOD Passport</Link>{" "}
              to submit evidence.
            </p>
          </div>
        ) : (
          <form
            onSubmit={(e) => {
              e.preventDefault();
              void handleSubmit();
            }}
            style={{ display: "flex", flexDirection: "column", gap: 12 }}
          >
            <label>
              <span style={{ display: "block", fontSize: 13, color: "rgba(0,0,0,0.6)" }}>
                Summary
              </span>
              <textarea
                value={summary}
                onChange={(e) => setSummary(e.target.value)}
                required
                minLength={10}
                rows={4}
                style={{
                  display: "block",
                  width: "100%",
                  padding: 12,
                  marginTop: 4,
                  border: "1px solid rgba(0,0,0,0.15)",
                  borderRadius: 8,
                  fontSize: 14,
                  fontFamily: "inherit",
                }}
              />
            </label>
            <label>
              <span style={{ display: "block", fontSize: 13, color: "rgba(0,0,0,0.6)" }}>
                Evidence URL (http(s) only — javascript:, data:, file: rejected)
              </span>
              <input
                value={evidenceUrl}
                onChange={(e) => setEvidenceUrl(e.target.value)}
                type="url"
                placeholder="https://…"
                style={{
                  display: "block",
                  width: "100%",
                  padding: 12,
                  marginTop: 4,
                  border: "1px solid rgba(0,0,0,0.15)",
                  borderRadius: 8,
                  fontSize: 14,
                }}
              />
            </label>
            <label>
              <span style={{ display: "block", fontSize: 13, color: "rgba(0,0,0,0.6)" }}>
                Evidence label (optional)
              </span>
              <input
                value={evidenceLabel}
                onChange={(e) => setEvidenceLabel(e.target.value)}
                maxLength={200}
                style={{
                  display: "block",
                  width: "100%",
                  padding: 12,
                  marginTop: 4,
                  border: "1px solid rgba(0,0,0,0.15)",
                  borderRadius: 8,
                  fontSize: 14,
                }}
              />
            </label>
            <button
              type="submit"
              disabled={submitting}
              style={{
                padding: "12px 20px",
                background: "linear-gradient(100deg, #6a4cc4, #4ec6c6)",
                color: "#fff",
                border: 0,
                borderRadius: 999,
                fontSize: 15,
                fontWeight: 600,
                cursor: submitting ? "wait" : "pointer",
              }}
            >
              {submitting ? "Submitting…" : "Submit Contribution"}
            </button>
          </form>
        )}

        {submitResult && (
          <p
            style={{
              marginTop: 16,
              padding: 12,
              border: "1px solid rgba(0,128,0,0.25)",
              borderRadius: 8,
              background: "rgba(0,128,0,0.06)",
              color: "#0a4",
            }}
          >
            Submission {submitResult.id} created (status: {submitResult.status}).
            A reviewer will respond shortly.
          </p>
        )}
      </section>
    </main>
  );
}