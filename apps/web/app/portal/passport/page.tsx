"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";

type MeResponse = {
  resident: { id: string; createdAt: string; status: "active" | "suspended" | "deleted" };
  profile: {
    residentId: string;
    displayName: string | null;
    bio: string | null;
    avatarUrl: string | null;
    preferredLanguage: "zh" | "en" | null;
    updatedAt: string;
  } | null;
  wallets: Array<{
    id: string;
    address: string;
    truncated: string;
    isPrimary: boolean;
    verifiedAt: string;
    addedAt: string;
  }>;
  roles: { selfDeclared: string[]; verified: string[] };
  badges: Array<{
    id: string;
    slug: string;
    title: string;
    description: string;
    source: "system" | "governance" | "manual-review";
    issuedAt: string;
    evidenceUrl?: string;
  }>;
  privacy: {
    profileVisibility: "public" | "minimal" | "private";
    showFullWalletAddress: boolean;
    showContributionHistory: boolean;
    showRoles: boolean;
    showReputation: boolean;
  };
  reputation: {
    residentId: string;
    score: number | null;
    contributionCount: number;
    approvedContributionCount: number;
    lastEventAt: string | null;
    source: string;
  };
};

type SignInStep =
  | { kind: "idle" }
  | { kind: "address-entered"; address: string }
  | { kind: "awaiting-signature"; messageText: string }
  | { kind: "verifying"; messageText: string; signature: string }
  | { kind: "error"; reason: string };

export default function PassportPage() {
  const [me, setMe] = useState<MeResponse | null>(null);
  const [bootError, setBootError] = useState<string | null>(null);
  const [signInStep, setSignInStep] = useState<SignInStep>({ kind: "idle" });
  const [address, setAddress] = useState("");
  const [developmentMode, setDevelopmentMode] = useState<boolean>(false);

  async function refreshMe() {
    try {
      const res = await fetch("/api/resident/me", { credentials: "same-origin" });
      if (res.status === 401) {
        setMe(null);
        return;
      }
      if (!res.ok) {
        setBootError(`me-error:${res.status}`);
        return;
      }
      const body = (await res.json()) as MeResponse;
      setMe(body);
    } catch (err) {
      setBootError((err as Error).message);
    }
  }

  useEffect(() => {
    void refreshMe();
  }, []);

  async function handleConnect() {
    setSignInStep({ kind: "error", reason: "" });
    const cleaned = address.trim();
    if (!/^0x[a-fA-F0-9]{40}$/.test(cleaned)) {
      setSignInStep({ kind: "error", reason: "Enter a valid 0x address" });
      return;
    }
    setSignInStep({ kind: "address-entered", address: cleaned });
    try {
      // 1) Issue nonce + SIWE message.
      const nonceRes = await fetch(
        `/api/identity/nonce?address=${encodeURIComponent(cleaned)}`,
        { credentials: "same-origin" },
      );
      if (!nonceRes.ok) {
        setSignInStep({ kind: "error", reason: `nonce-failed:${nonceRes.status}` });
        return;
      }
      const nonceBody = (await nonceRes.json()) as {
        message: unknown;
        messageText: string;
        expiresAt: string;
      };
      setSignInStep({
        kind: "awaiting-signature",
        messageText: nonceBody.messageText,
      });

      // 2) Sign with wallet. Browser only.
      const ethereum = (window as unknown as {
        ethereum?: { request: (args: { method: string; params: unknown[] }) => Promise<string> };
      }).ethereum;
      let signature: string;
      if (ethereum && typeof ethereum.request === "function") {
        try {
          signature = await ethereum.request({
            method: "personal_sign",
            params: [nonceBody.messageText, cleaned],
          });
        } catch (err) {
          setSignInStep({ kind: "error", reason: `sign-failed:${(err as Error).message}` });
          return;
        }
      } else if (developmentMode) {
        // Dev-mode stub: produces a syntactically valid signature. Production
        // does NOT enable this; the verifier will reject it.
        signature = "0x" + "ab".repeat(64) + "1b";
      } else {
        setSignInStep({
          kind: "error",
          reason: "no-wallet-detected-install-metamask-or-enable-dev-mode",
        });
        return;
      }

      setSignInStep({
        kind: "verifying",
        messageText: nonceBody.messageText,
        signature,
      });
      const verifyRes = await fetch("/api/identity/verify", {
        method: "POST",
        credentials: "same-origin",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({
          messageText: nonceBody.messageText,
          signature,
        }),
      });
      if (!verifyRes.ok) {
        const err = (await verifyRes.json().catch(() => null)) as
          | { error?: { code?: string; message?: string } }
          | null;
        setSignInStep({
          kind: "error",
          reason: err?.error?.message ?? `verify-failed:${verifyRes.status}`,
        });
        return;
      }
      setSignInStep({ kind: "idle" });
      await refreshMe();
    } catch (err) {
      setSignInStep({ kind: "error", reason: (err as Error).message });
    }
  }

  async function handleLogout() {
    await fetch("/api/identity/logout", {
      method: "POST",
      credentials: "same-origin",
    });
    setMe(null);
  }

  return (
    <main className="passport-surface">
      <div className="passport-container">
        <Link href="/portal" className="passport-link">← /portal</Link>
        <p className="passport-eyebrow" style={{ marginTop: 24 }}>MOOD PASSPORT</p>
        <h1 className="passport-title">Resident Identity</h1>
        <p className="passport-subtitle">
          Wallet is the key. Identity is the person. Reputation is earned, not bought.
        </p>

        {bootError ? (
          <div className="passport-card passport-banner-warn">Passport boot failed: {bootError}</div>
        ) : null}

        {!me ? (
          <SignInPanel
            address={address}
            onAddressChange={setAddress}
            onConnect={handleConnect}
            step={signInStep}
            developmentMode={developmentMode}
            onToggleDevMode={() => setDevelopmentMode((v) => !v)}
          />
        ) : (
          <PassportCard me={me} onLogout={handleLogout} />
        )}

        <p className="passport-disclaimer">
          MOOD Passport is independent of the future MOOD Token. No holdings,
          balance, or holding tier influences identity, roles, or reputation.
        </p>
      </div>
    </main>
  );
}

function SignInPanel({
  address,
  onAddressChange,
  onConnect,
  step,
  developmentMode,
  onToggleDevMode,
}: {
  address: string;
  onAddressChange: (v: string) => void;
  onConnect: () => void;
  step: SignInStep;
  developmentMode: boolean;
  onToggleDevMode: () => void;
}) {
  return (
    <div className="passport-card passport-card--accent">
      <p className="passport-eyebrow">Sign in with your wallet</p>
      <h2 className="passport-title" style={{ fontSize: 32, color: "#fff" }}>
        Connect to MOOD
      </h2>
      <p
        className="passport-subtitle"
        style={{ marginBottom: 32, color: "rgba(255,255,255,0.85)" }}
      >
        Your wallet is a key — not your full identity. You will sign a
        human-readable message to begin.
      </p>
      <label style={{ display: "block" }}>
        <span className="passport-stat-label" style={{ color: "rgba(255,255,255,0.85)" }}>
          Wallet address
        </span>
        <input
          className="passport-input"
          style={{ marginTop: 8 }}
          placeholder="0xABCD…1234"
          value={address}
          onChange={(e) => onAddressChange(e.target.value)}
          autoComplete="off"
          spellCheck={false}
        />
      </label>
      <div style={{ display: "flex", gap: 12, marginTop: 24, flexWrap: "wrap" }}>
        <button
          type="button"
          className="passport-cta"
          style={{ background: "#ffffff", color: "#4a3a8c" }}
          onClick={onConnect}
          disabled={step.kind === "verifying"}
        >
          {step.kind === "verifying" ? "Verifying…" : "Connect Wallet"}
        </button>
        <label style={{ display: "flex", gap: 8, alignItems: "center", color: "rgba(255,255,255,0.9)" }}>
          <input type="checkbox" checked={developmentMode} onChange={onToggleDevMode} />
          <span style={{ fontSize: 13 }}>Dev mode (browser wallet required for real signing)</span>
        </label>
      </div>
      {step.kind === "awaiting-signature" && (
        <div style={{ marginTop: 24, color: "#fff" }}>
          <p className="passport-stat-label" style={{ color: "rgba(255,255,255,0.85)" }}>
            Awaiting wallet signature
          </p>
          <pre
            style={{
              background: "rgba(0,0,0,0.2)",
              padding: 16,
              borderRadius: 12,
              overflow: "auto",
              fontSize: 12,
              marginTop: 12,
            }}
          >
            {step.messageText}
          </pre>
        </div>
      )}
      {step.kind === "error" && step.reason && (
        <div className="passport-banner-warn" style={{ marginTop: 24 }}>
          {step.reason}
        </div>
      )}
    </div>
  );
}

function PassportCard({ me, onLogout }: { me: MeResponse; onLogout: () => void }) {
  const profile = me.profile;
  const reputation = me.reputation;
  const joinedMonth = useMemo(() => {
    const d = new Date(me.resident.createdAt);
    if (Number.isNaN(d.getTime())) return "—";
    const month = d.toLocaleString("en-US", { month: "short" });
    return `${month} ${d.getUTCFullYear()}`;
  }, [me.resident.createdAt]);

  const primaryWallet = me.wallets.find((w) => w.isPrimary) ?? me.wallets[0];
  const displayName = profile?.displayName && profile.displayName.trim().length > 0
    ? profile.displayName
    : `Resident ${me.resident.id}`;

  return (
    <>
      <section className="passport-card passport-card--accent">
        <p className="passport-eyebrow">MOOD PASSPORT</p>
        <h2 style={{ fontSize: 28, margin: "0 0 8px", color: "#fff" }}>
          {displayName}
        </h2>
        <p style={{ margin: 0, fontSize: 14, color: "rgba(255,255,255,0.85)" }}>
          {primaryWallet ? primaryWallet.truncated : "no wallet"}
        </p>
        <p style={{ margin: 0, fontSize: 13, color: "rgba(255,255,255,0.7)" }}>
          Resident {me.resident.id} · Joined {joinedMonth}
        </p>

        <div className="passport-grid" style={{ marginTop: 24 }}>
          <div>
            <p className="passport-stat-label" style={{ color: "rgba(255,255,255,0.85)" }}>
              Reputation
            </p>
            <p className="passport-stat-value" style={{ color: "#fff" }}>
              {reputation.score == null ? "—" : reputation.score}
            </p>
          </div>
          <div>
            <p className="passport-stat-label" style={{ color: "rgba(255,255,255,0.85)" }}>
              Contributions
            </p>
            <p className="passport-stat-value" style={{ color: "#fff" }}>
              {reputation.contributionCount}
            </p>
          </div>
          <div>
            <p className="passport-stat-label" style={{ color: "rgba(255,255,255,0.85)" }}>
              Approved
            </p>
            <p className="passport-stat-value" style={{ color: "#fff" }}>
              {reputation.approvedContributionCount}
            </p>
          </div>
        </div>

        <div style={{ marginTop: 24, display: "flex", gap: 12, flexWrap: "wrap" }}>
          <Link href="/portal/passport/settings" className="passport-cta" style={{ background: "#fff", color: "#4a3a8c" }}>
            Privacy & Settings
          </Link>
          <button
            type="button"
            onClick={onLogout}
            className="passport-cta passport-cta--ghost"
            style={{ background: "transparent", color: "#fff", borderColor: "rgba(255,255,255,0.5)" }}
          >
            Sign out
          </button>
        </div>
      </section>

      <RolesAndBadges me={me} />
      <ReputationPanel reputation={reputation} />
    </>
  );
}

function RolesAndBadges({ me }: { me: MeResponse }) {
  return (
    <section className="passport-card">
      <p className="passport-section-title">Identity</p>
      <p style={{ marginTop: 0, fontSize: 14 }}>
        Wallet: <code>{me.wallets[0]?.truncated ?? "—"}</code>
        {me.wallets.length > 1 && (
          <span style={{ marginLeft: 8, color: "rgba(0,0,0,0.55)" }}>
            + {me.wallets.length - 1} bound
          </span>
        )}
      </p>

      <p className="passport-section-title">Roles</p>
      <div className="passport-row">
        {me.roles.selfDeclared.length === 0 && me.roles.verified.length === 0 ? (
          <span className="passport-status-empty">No roles yet.</span>
        ) : (
          <>
            {me.roles.selfDeclared.map((r) => (
              <span key={r} className="passport-pill">{r}</span>
            ))}
            {me.roles.verified.map((r) => (
              <span key={r} className="passport-pill passport-pill--verified">
                ✓ {r}
              </span>
            ))}
          </>
        )}
      </div>

      <p className="passport-section-title">Badges</p>
      <div className="passport-row">
        {me.badges.length === 0 ? (
          <span className="passport-status-empty">No badges yet.</span>
        ) : (
          me.badges.map((b) => (
            <span key={b.id} className="passport-pill passport-pill--verified">
              {b.title}
            </span>
          ))
        )}
      </div>
    </section>
  );
}

function ReputationPanel({
  reputation,
}: {
  reputation: MeResponse["reputation"];
}) {
  return (
    <section className="passport-card">
      <p className="passport-section-title">Reputation</p>
      {reputation.source === "no-contributions-yet" ? (
        <p className="passport-status-empty">No contributions yet.</p>
      ) : (
        <>
          <p style={{ margin: 0, fontSize: 14 }}>
            Score <strong>{reputation.score ?? "—"}</strong> · Last event{" "}
            {reputation.lastEventAt
              ? new Date(reputation.lastEventAt).toLocaleDateString()
              : "—"}
          </p>
          <p className="passport-disclaimer">
            Reputation comes from verified Contribution activity (see /contribute). It is not
            influenced by Token balance or holdings.
          </p>
        </>
      )}
    </section>
  );
}
