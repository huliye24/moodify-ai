"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

type MeResponse = {
  profile: {
    residentId: string;
    displayName: string | null;
    bio: string | null;
    avatarUrl: string | null;
    preferredLanguage: "zh" | "en" | null;
    updatedAt: string;
  } | null;
  privacy: {
    profileVisibility: "public" | "minimal" | "private";
    showFullWalletAddress: boolean;
    showContributionHistory: boolean;
    showRoles: boolean;
    showReputation: boolean;
  };
};

export default function SettingsPage() {
  const [me, setMe] = useState<MeResponse | null>(null);
  const [savingProfile, setSavingProfile] = useState(false);
  const [savingPrivacy, setSavingPrivacy] = useState(false);
  const [savedAt, setSavedAt] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const [displayName, setDisplayName] = useState("");
  const [bio, setBio] = useState("");
  const [avatarUrl, setAvatarUrl] = useState("");
  const [preferredLanguage, setPreferredLanguage] = useState<"zh" | "en" | "">("");

  const [visibility, setVisibility] = useState<"public" | "minimal" | "private">("minimal");
  const [showFullWallet, setShowFullWallet] = useState(false);
  const [showContribHistory, setShowContribHistory] = useState(true);
  const [showRoles, setShowRoles] = useState(true);
  const [showReputation, setShowReputation] = useState(true);

  useEffect(() => {
    void (async () => {
      const res = await fetch("/api/resident/me", { credentials: "same-origin" });
      if (res.status === 401) return;
      const body = (await res.json()) as MeResponse;
      setMe(body);
      setDisplayName(body.profile?.displayName ?? "");
      setBio(body.profile?.bio ?? "");
      setAvatarUrl(body.profile?.avatarUrl ?? "");
      setPreferredLanguage(body.profile?.preferredLanguage ?? "");
      setVisibility(body.privacy.profileVisibility);
      setShowFullWallet(body.privacy.showFullWalletAddress);
      setShowContribHistory(body.privacy.showContributionHistory);
      setShowRoles(body.privacy.showRoles);
      setShowReputation(body.privacy.showReputation);
    })();
  }, []);

  async function saveProfile() {
    setSavingProfile(true);
    setError(null);
    try {
      const body = {
        kind: "profile",
        displayName: displayName.trim().length === 0 ? null : displayName,
        bio: bio.trim().length === 0 ? null : bio,
        avatarUrl: avatarUrl.trim().length === 0 ? null : avatarUrl,
        preferredLanguage: preferredLanguage.length === 0 ? null : preferredLanguage,
      };
      const res = await fetch("/api/resident/me", {
        method: "PATCH",
        credentials: "same-origin",
        headers: { "content-type": "application/json" },
        body: JSON.stringify(body),
      });
      if (!res.ok) {
        const err = (await res.json().catch(() => null)) as
          | { error?: { message?: string } }
          | null;
        setError(err?.error?.message ?? `save-failed:${res.status}`);
        return;
      }
      setSavedAt(new Date().toISOString());
    } finally {
      setSavingProfile(false);
    }
  }

  async function savePrivacy() {
    setSavingPrivacy(true);
    setError(null);
    try {
      const body = {
        kind: "privacy",
        profileVisibility: visibility,
        showFullWalletAddress: showFullWallet,
        showContributionHistory: showContribHistory,
        showRoles,
        showReputation,
      };
      const res = await fetch("/api/resident/me", {
        method: "PATCH",
        credentials: "same-origin",
        headers: { "content-type": "application/json" },
        body: JSON.stringify(body),
      });
      if (!res.ok) {
        const err = (await res.json().catch(() => null)) as
          | { error?: { message?: string } }
          | null;
        setError(err?.error?.message ?? `save-failed:${res.status}`);
        return;
      }
      setSavedAt(new Date().toISOString());
    } finally {
      setSavingPrivacy(false);
    }
  }

  async function disconnect() {
    const confirmed = typeof window !== "undefined"
      ? window.confirm("Sign out and clear all current sessions?")
      : false;
    if (!confirmed) return;
    await fetch("/api/identity/logout", {
      method: "POST",
      credentials: "same-origin",
    });
    if (typeof window !== "undefined") {
      window.location.href = "/portal/passport";
    }
  }

  if (!me) {
    return (
      <main className="passport-surface">
        <div className="passport-container">
          <p>
            Please <Link href="/portal/passport" className="passport-link">sign in</Link> to access privacy controls.
          </p>
        </div>
      </main>
    );
  }

  return (
    <main className="passport-surface">
      <div className="passport-container">
        <Link href="/portal/passport" className="passport-link">← Passport</Link>
        <p className="passport-eyebrow" style={{ marginTop: 24 }}>PRIVACY & SETTINGS</p>
        <h1 className="passport-title">Settings</h1>
        <p className="passport-subtitle">
          Privacy by default. You choose what becomes public.
        </p>

        {error && <div className="passport-banner-warn">{error}</div>}
        {savedAt && (
          <p style={{ color: "#1b5e20", fontSize: 14 }}>
            Saved · {new Date(savedAt).toLocaleTimeString()}
          </p>
        )}

        {/* Profile */}
        <section className="passport-card">
          <p className="passport-section-title">Profile</p>
          <label>
            <span className="passport-stat-label">Display name (1–32 chars)</span>
            <input
              className="passport-input"
              value={displayName}
              maxLength={32}
              onChange={(e) => setDisplayName(e.target.value)}
            />
          </label>
          <div style={{ height: 16 }} />
          <label>
            <span className="passport-stat-label">Bio (max 280 chars)</span>
            <textarea
              className="passport-textarea"
              value={bio}
              maxLength={280}
              onChange={(e) => setBio(e.target.value)}
            />
          </label>
          <div style={{ height: 16 }} />
          <label>
            <span className="passport-stat-label">Avatar URL (optional)</span>
            <input
              className="passport-input"
              value={avatarUrl}
              onChange={(e) => setAvatarUrl(e.target.value)}
              placeholder="https://…"
              maxLength={256}
            />
          </label>
          <div style={{ height: 16 }} />
          <label>
            <span className="passport-stat-label">Preferred language</span>
            <select
              className="passport-input"
              value={preferredLanguage}
              onChange={(e) => setPreferredLanguage(e.target.value as "zh" | "en" | "")}
            >
              <option value="">— not set —</option>
              <option value="zh">中文</option>
              <option value="en">English</option>
            </select>
          </label>
          <p className="passport-disclaimer">
            We do not collect legal name, phone, government ID, or location.
          </p>
          <button
            type="button"
            className="passport-cta"
            disabled={savingProfile}
            onClick={saveProfile}
          >
            {savingProfile ? "Saving…" : "Save profile"}
          </button>
        </section>

        {/* Privacy */}
        <section className="passport-card">
          <p className="passport-section-title">Privacy</p>

          <div className="passport-radio-group">
            <p className="passport-stat-label">Profile visibility</p>
            <label>
              <input
                type="radio"
                name="visibility"
                checked={visibility === "private"}
                onChange={() => setVisibility("private")}
              />
              <span>
                <strong>Private</strong> — only you can see your profile.
                Public Passport <code>/resident/[id]</code> returns 403.
              </span>
            </label>
            <label>
              <input
                type="radio"
                name="visibility"
                checked={visibility === "minimal"}
                onChange={() => setVisibility("minimal")}
              />
              <span>
                <strong>Minimal</strong> (default) — short ID + joined month only.
                Public Passport disabled by default.
              </span>
            </label>
            <label>
              <input
                type="radio"
                name="visibility"
                checked={visibility === "public"}
                onChange={() => setVisibility("public")}
              />
              <span>
                <strong>Public</strong> — public profile is reachable via
                <code>/resident/[id]</code> (only when feature is globally enabled).
              </span>
            </label>
          </div>

          <div className="passport-divider" />

          <p className="passport-stat-label">Wallet address on public profile</p>
          <div className="passport-checkboxes">
            <label>
              <input
                type="checkbox"
                checked={showFullWallet}
                onChange={(e) => setShowFullWallet(e.target.checked)}
              />
              <span>
                Show full wallet address. (Off by default — we only show{" "}
                <code>0xABCD…1234</code>.)
              </span>
            </label>
          </div>

          <div className="passport-divider" />

          <p className="passport-stat-label">Show sections on public profile</p>
          <div className="passport-checkboxes">
            <label>
              <input
                type="checkbox"
                checked={showContribHistory}
                onChange={(e) => setShowContribHistory(e.target.checked)}
              />
              <span>Contribution history</span>
            </label>
            <label>
              <input
                type="checkbox"
                checked={showRoles}
                onChange={(e) => setShowRoles(e.target.checked)}
              />
              <span>Self-declared + verified roles</span>
            </label>
            <label>
              <input
                type="checkbox"
                checked={showReputation}
                onChange={(e) => setShowReputation(e.target.checked)}
              />
              <span>Reputation summary</span>
            </label>
          </div>

          <div style={{ marginTop: 16, display: "flex", gap: 12, flexWrap: "wrap" }}>
            <button
              type="button"
              className="passport-cta"
              disabled={savingPrivacy}
              onClick={savePrivacy}
            >
              {savingPrivacy ? "Saving…" : "Save privacy"}
            </button>
          </div>
        </section>

        {/* Sessions */}
        <section className="passport-card">
          <p className="passport-section-title">Sessions</p>
          <p style={{ fontSize: 14 }}>
            Your current session expires automatically. You can revoke it now.
          </p>
          <button
            type="button"
            className="passport-cta passport-cta--ghost"
            onClick={disconnect}
          >
            Sign out &amp; revoke session
          </button>
        </section>

        <p className="passport-disclaimer">
          Soft delete / full deletion requests will be handled by a separate
          governance package. Until that is in place, profile data is stored
          in-memory for the foundation launch.
        </p>
      </div>
    </main>
  );
}
