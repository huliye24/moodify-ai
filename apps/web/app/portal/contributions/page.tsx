"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

type MySubmission = {
  id: string;
  taskId: string;
  residentId: string;
  summary: string;
  status: string;
  revision: number;
  createdAt: string;
  updatedAt: string;
};

type MeResponse = {
  resident: { id: string };
  reputation: { score: number | null; contributionCount: number; approvedContributionCount: number };
};

export default function MyContributionsPage() {
  const [me, setMe] = useState<MeResponse | null>(null);
  const [subs, setSubs] = useState<MySubmission[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch("/api/resident/me", { credentials: "same-origin" })
      .then(async (r) => {
        if (r.status === 401) return null;
        return r.json();
      })
      .then((j: any) => {
        if (j) setMe(j);
      })
      .catch(() => {/* not signed in */});
  }, []);

  async function load() {
    if (!me) return;
    try {
      const res = await fetch("/api/resident/me/contributions", {
        credentials: "same-origin",
      });
      const j: any = await res.json();
      if (j.error) setError(j.error.message);
      else setSubs(j.submissions ?? []);
    } catch (e) {
      setError((e as Error).message);
    }
  }

  useEffect(() => {
    void load();
  }, [me]);

  if (!me) {
    return (
      <main style={{ padding: 48, maxWidth: 720, margin: "0 auto" }}>
        <p>
          <Link href="/portal/passport">Sign in with MOOD Passport</Link> to view
          your submissions.
        </p>
      </main>
    );
  }

  const rep = me.reputation;

  return (
    <main style={{ padding: 48, maxWidth: 960, margin: "0 auto" }}>
      <p style={{ color: "rgba(0,0,0,0.55)", letterSpacing: "0.12em", fontSize: 13 }}>
        MOOD / PORTAL / CONTRIBUTIONS
      </p>
      <h1 style={{ fontSize: 36, margin: "8px 0 16px" }}>My Contributions</h1>
      <p style={{ color: "rgba(0,0,0,0.6)" }}>
        Resident {me.resident.id} · Reputation {rep.score ?? "—"} · {rep.approvedContributionCount} approved
      </p>

      <section style={{ marginTop: 24 }}>
        <h2 style={{ fontSize: 22 }}>My Submissions</h2>
        {error ? (
          <p style={{ color: "#a33" }}>{error}</p>
        ) : subs.length === 0 ? (
          <p style={{ color: "rgba(0,0,0,0.5)" }}>
            No submissions yet.{" "}
            <Link href="/build">Browse open tasks</Link>.
          </p>
        ) : (
          <ul style={{ listStyle: "none", padding: 0 }}>
            {subs.map((s) => (
              <li
                key={s.id}
                style={{
                  padding: 16,
                  border: "1px solid rgba(0,0,0,0.1)",
                  borderRadius: 10,
                  marginBottom: 8,
                }}
              >
                <p style={{ margin: 0, fontWeight: 600 }}>
                  {s.id} · revision {s.revision} · status: {s.status}
                </p>
                <p style={{ margin: "4px 0 0", color: "rgba(0,0,0,0.7)" }}>{s.summary}</p>
              </li>
            ))}
          </ul>
        )}
      </section>
    </main>
  );
}