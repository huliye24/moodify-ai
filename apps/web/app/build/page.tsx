"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

type TaskSummary = {
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
  createdAt: string;
  updatedAt: string;
};

export default function BuildPage() {
  const [tasks, setTasks] = useState<TaskSummary[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch("/api/contribution/tasks")
      .then((r) => r.json())
      .then((j) => {
        if (j.error) {
          setError(j.error.message);
        } else {
          setTasks(j.tasks ?? []);
        }
      })
      .catch((e) => setError((e as Error).message));
  }, []);

  return (
    <main style={{ padding: "48px 24px", maxWidth: 960, margin: "0 auto" }}>
      <p style={{ color: "rgba(0,0,0,0.55)", letterSpacing: "0.12em", fontSize: 13 }}>
        MOOD / BUILD
      </p>
      <h1 style={{ fontSize: 40, margin: "8px 0 24px" }}>Build MOOD</h1>
      <p style={{ fontSize: 16, lineHeight: 1.6, color: "rgba(0,0,0,0.7)" }}>
        Contribution is the second action after Play. Anyone with a MOOD Passport
        can browse open tasks, submit evidence, and earn Reputation. Pending
        Rewards are recorded but never converted to an on-chain claim.
      </p>

      <section style={{ marginTop: 32 }}>
        <h2 style={{ fontSize: 24, marginBottom: 16 }}>Open Tasks</h2>
        {error ? (
          <p style={{ color: "#a33" }}>Failed to load tasks: {error}</p>
        ) : tasks === null ? (
          <p style={{ color: "rgba(0,0,0,0.5)" }}>Loading…</p>
        ) : tasks.length === 0 ? (
          <p style={{ color: "rgba(0,0,0,0.5)" }}>
            No open tasks yet. Open contributions will appear here.
          </p>
        ) : (
          <ul style={{ listStyle: "none", padding: 0, margin: 0 }}>
            {tasks.map((t) => (
              <li
                key={t.id}
                style={{
                  padding: 20,
                  marginBottom: 12,
                  border: "1px solid rgba(0,0,0,0.12)",
                  borderRadius: 12,
                  background: "rgba(255,255,255,0.6)",
                }}
              >
                <Link
                  href={`/build/${t.slug}`}
                  style={{
                    fontSize: 20,
                    fontWeight: 600,
                    color: "#1a1340",
                    textDecoration: "none",
                  }}
                >
                  {t.title}
                </Link>
                <p style={{ margin: "8px 0 4px", color: "rgba(0,0,0,0.7)" }}>
                  {t.summary}
                </p>
                <p style={{ margin: 0, fontSize: 13, color: "rgba(0,0,0,0.55)" }}>
                  {t.category} · +{t.defaultReputationPoints} reputation
                  {t.defaultRewardUnits ? ` · ${t.defaultRewardUnits} pending units (not on-chain)` : ""}
                  {t.deadline ? ` · deadline ${t.deadline}` : ""}
                </p>
              </li>
            ))}
          </ul>
        )}
      </section>

      <section style={{ marginTop: 48 }}>
        <h2 style={{ fontSize: 20, marginBottom: 12 }}>How Contribution Works</h2>
        <ol style={{ paddingLeft: 24, lineHeight: 1.8, color: "rgba(0,0,0,0.75)" }}>
          <li>Browse open tasks. Each task lists required evidence.</li>
          <li>Connect your wallet and sign in with MOOD Passport.</li>
          <li>Submit your evidence. Human reviewers review every submission.</li>
          <li>Approved submissions grant Reputation. Pending Reward Units are recorded but never converted on-chain.</li>
        </ol>
      </section>

      <section style={{ marginTop: 32, padding: 16, border: "1px solid rgba(0,0,0,0.08)", borderRadius: 12, background: "rgba(0,0,0,0.02)" }}>
        <p style={{ margin: 0, fontSize: 13, color: "rgba(0,0,0,0.6)" }}>
          No token price, no USD estimate, no APY, no guaranteed payout. Reputation is earned through verified Contribution. Pending Reward Units are historical field naming — they are not an on-chain entitlement.
        </p>
      </section>
    </main>
  );
}