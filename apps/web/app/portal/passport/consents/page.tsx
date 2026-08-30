"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

type Policy = {
  slug: string;
  title: string;
  version: string;
  status: "draft" | "active" | "superseded" | "archived";
  mandatory: boolean;
  reason: string;
};

type Consents = Array<{
  residentId: string;
  policySlug: string;
  policyVersion: string;
  acceptedAt: string;
  withdrawnAt?: string;
  status: "accepted" | "withdrawn";
}>;

export default function ConsentsPage() {
  const [policies, setPolicies] = useState<Policy[]>([]);
  const [consents, setConsents] = useState<Consents>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    void (async () => {
      try {
        const [libRes, conRes] = await Promise.all([
          fetch("/api/library/policies", { credentials: "same-origin" }),
          fetch("/api/resident/me/consents", { credentials: "same-origin" }),
        ]);
        if (!libRes.ok) {
          setError(`library-error:${libRes.status}`);
          return;
        }
        const libBody = (await libRes.json()) as { policies: Policy[] };
        setPolicies(libBody.policies);
        if (conRes.ok) {
          const conBody = (await conRes.json()) as { consents: Consents };
          setConsents(conBody.consents);
        }
      } catch (err) {
        setError((err as Error).message);
      }
    })();
  }, []);

  async function accept(policy: Policy) {
    setError(null);
    const res = await fetch("/api/resident/me/consents", {
      method: "POST",
      credentials: "same-origin",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({
        policySlug: policy.slug,
        policyVersion: policy.version,
        policyStatus: policy.status,
      }),
    });
    if (!res.ok) {
      const err = (await res.json().catch(() => null)) as
        | { error?: { message?: string } }
        | null;
      setError(err?.error?.message ?? `accept-failed:${res.status}`);
      return;
    }
    const conRes = await fetch("/api/resident/me/consents", {
      credentials: "same-origin",
    });
    if (conRes.ok) {
      const body = (await conRes.json()) as { consents: Consents };
      setConsents(body.consents);
    }
  }

  return (
    <main className="passport-surface">
      <div className="passport-container">
        <Link href="/portal/passport" className="passport-link">← Passport</Link>
        <p className="passport-eyebrow" style={{ marginTop: 24 }}>POLICIES & CONSENT</p>
        <h1 className="passport-title">Documents &amp; Consent</h1>
        <p className="passport-subtitle">
          Only Active policies may be recorded as accepted. Draft policies are
          shown for transparency but cannot bind you.
        </p>

        {error && <div className="passport-banner-warn">{error}</div>}

        <section className="passport-card">
          {policies.length === 0 ? (
            <p className="passport-status-empty">
              No documents available. The Library is initializing…
            </p>
          ) : (
            <table className="passport-table">
              <thead>
                <tr>
                  <th>Title</th>
                  <th>Version</th>
                  <th>Status</th>
                  <th>Accepted</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {policies.map((p) => {
                  const accepted = consents.find(
                    (c) => c.policySlug === p.slug && c.status === "accepted",
                  );
                  return (
                    <tr key={p.slug}>
                      <td>
                        <strong>{p.title}</strong>
                        <br />
                        <code style={{ fontSize: 12, color: "rgba(0,0,0,0.55)" }}>
                          {p.slug}
                        </code>
                      </td>
                      <td>{p.version}</td>
                      <td>
                        {p.status === "active" ? (
                          <span className="passport-pill passport-pill--verified">{p.status}</span>
                        ) : p.status === "draft" ? (
                          <span className="passport-pill passport-pill--draft">Draft</span>
                        ) : (
                          <span className="passport-pill">{p.status}</span>
                        )}
                      </td>
                      <td>
                        {accepted ? (
                          accepted.acceptedAt.split("T")[0]
                        ) : (
                          <span className="passport-status-empty">—</span>
                        )}
                      </td>
                      <td>
                        {p.status === "active" ? (
                          <button
                            type="button"
                            className="passport-cta"
                            disabled={Boolean(accepted)}
                            onClick={() => accept(p)}
                          >
                            {accepted ? "Accepted" : "Accept"}
                          </button>
                        ) : (
                          <span className="passport-disclaimer">
                            not mandatory ({p.reason})
                          </span>
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          )}
        </section>

        <p className="passport-disclaimer">
          Consent history is private and not exposed via the public Passport.
        </p>
      </div>
    </main>
  );
}
