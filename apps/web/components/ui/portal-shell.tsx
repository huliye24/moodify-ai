/* MOOD Portal Shell Components — MOOD-PORTAL-013.
   Phase K: shared components for /world, /protocol, /portal routes.
   All colors from tokens.css design tokens. No new token introduction. */

import type { ReactNode } from "react";
import Link from "next/link";
import { BrandMark } from "./surfaces";

/* ─── StatusBadge ─────────────────────────────────────────────────────────── */

export type MoodStatus =
  | "Foundation"
  | "Active"
  | "Experimental"
  | "Coming Next"
  | "Launch-Gated";

export interface StatusBadgeProps {
  status: MoodStatus;
  since?: string; // e.g. "Package 012"
}

const STATUS_CONFIG: Record<
  MoodStatus,
  { color: string; bg: string; dot: string }
> = {
  Foundation: {
    color: "var(--text-muted)",
    bg: "var(--surface-subtle)",
    dot: "var(--text-faint)",
  },
  Active: {
    color: "var(--evidence)",
    bg: "var(--evidence-soft)",
    dot: "var(--evidence)",
  },
  Experimental: {
    color: "var(--attention)",
    bg: "var(--attention-soft)",
    dot: "var(--attention)",
  },
  "Coming Next": {
    color: "var(--text-muted)",
    bg: "var(--surface-subtle)",
    dot: "var(--text-faint)",
  },
  "Launch-Gated": {
    color: "var(--attention)",
    bg: "var(--attention-soft)",
    dot: "var(--attention)",
  },
};

export function StatusBadge({ status, since }: StatusBadgeProps) {
  const cfg = STATUS_CONFIG[status];
  return (
    <span
      style={{
        display: "inline-flex",
        alignItems: "center",
        gap: "var(--space-2)",
        padding: "var(--space-1) var(--space-3)",
        borderRadius: "var(--radius-pill)",
        background: cfg.bg,
        color: cfg.color,
        fontSize: "var(--text-xs)",
        fontWeight: 600,
        letterSpacing: "0.08em",
        textTransform: "uppercase" as const,
        border: `1px solid ${cfg.color}`,
      }}
    >
      <span
        aria-hidden
        style={{
          width: 6,
          height: 6,
          borderRadius: "50%",
          background: cfg.dot,
          flex: "none",
        }}
      />
      {status}
      {since ? (
        <span style={{ opacity: 0.65, fontWeight: 400 }}>
          · {since}
        </span>
      ) : null}
    </span>
  );
}

/* ─── ComingSoonModule ──────────────────────────────────────────────────────── */

export interface ComingSoonModuleProps {
  package: string; // e.g. "Package 015"
  label: string; // e.g. "Passport"
  description?: string;
  blocked?: boolean;
  blockedReason?: string;
}

export function ComingSoonModule({
  package: pkg,
  label,
  description,
  blocked,
  blockedReason,
}: ComingSoonModuleProps) {
  return (
    <div
      style={{
        border: "1px solid var(--line)",
        borderRadius: "var(--radius-md)",
        background: "var(--surface-subtle)",
        padding: "var(--space-6)",
        opacity: blocked ? 0.65 : 1,
      }}
    >
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: "var(--space-3)",
          marginBottom: "var(--space-3)",
        }}
      >
        <StatusBadge
          status={blocked ? "Launch-Gated" : "Coming Next"}
          since={pkg}
        />
      </div>
      <h3
        style={{
          margin: "0 0 var(--space-2)",
          fontSize: "var(--text-lg)",
          fontWeight: 600,
          color: "var(--text)",
        }}
      >
        {label}
      </h3>
      {description && (
        <p
          style={{
            margin: "0 0 var(--space-3)",
            color: "var(--text-muted)",
            fontSize: "var(--text-md)",
          }}
        >
          {description}
        </p>
      )}
      {blocked && blockedReason && (
        <p
          style={{
            margin: 0,
            fontSize: "var(--text-sm)",
            color: "var(--attention)",
          }}
        >
          {blockedReason}
        </p>
      )}
    </div>
  );
}

/* ─── MoodPublicHeader ──────────────────────────────────────────────────────── */

export type MoodArea = "home" | "world" | "protocol" | "portal" | "network" | "library";

const NAV_ITEMS: { label: string; href: string; area: MoodArea }[] = [
  { label: "World", href: "/world", area: "world" },
  { label: "Protocol", href: "/protocol", area: "protocol" },
  { label: "Network", href: "/network", area: "network" },
  { label: "Library", href: "/library", area: "library" },
  { label: "Portal", href: "/portal", area: "portal" },
];

export interface MoodPublicHeaderProps {
  activeArea?: MoodArea;
  walletState?: "disconnected" | "connected";
  walletAddress?: string;
}

export function MoodPublicHeader({
  activeArea,
  walletState = "disconnected",
  walletAddress,
}: MoodPublicHeaderProps) {
  return (
    <header
      style={{
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        padding: "var(--space-4) clamp(16px, 4vw, 48px)",
        borderBottom: "1px solid var(--line)",
        background: "var(--surface)",
        position: "sticky",
        top: 0,
        zIndex: 10,
      }}
    >
      {/* Left: MOOD wordmark */}
      <div style={{ display: "flex", alignItems: "center", gap: "var(--space-6)" }}>
        <Link
          href="/"
          style={{
            textDecoration: "none",
            color: "var(--text)",
            display: "flex",
            alignItems: "center",
            gap: "var(--space-2)",
          }}
        >
          <span
            aria-hidden
            style={{
              width: 32,
              height: 32,
              borderRadius: "var(--radius-sm)",
              background: "linear-gradient(135deg, var(--brand-violet), var(--brand-cyan))",
              display: "grid",
              placeItems: "center",
              fontSize: 14,
              color: "var(--on-accent)",
              fontWeight: 700,
            }}
          >
            M
          </span>
          <span
            style={{
              fontWeight: 700,
              fontSize: "var(--text-xl)",
              letterSpacing: "0.04em",
              fontFamily: "var(--font-body)",
            }}
          >
            MOOD
          </span>
        </Link>

        {/* Desktop nav */}
        <nav
          aria-label="MOOD main navigation"
          style={{
            display: "flex",
            gap: "var(--space-1)",
          }}
          className="mood-desktop-nav"
        >
          {NAV_ITEMS.map((item) => {
            const active = activeArea === item.area;
            return (
              <Link
                key={item.href}
                href={item.href}
                aria-current={active ? "page" : undefined}
                style={{
                  display: "flex",
                  alignItems: "center",
                  padding: "var(--space-2) var(--space-3)",
                  borderRadius: "var(--radius-sm)",
                  color: active ? "var(--text)" : "var(--text-muted)",
                  background: active ? "var(--surface-subtle)" : "transparent",
                  textDecoration: "none",
                  fontSize: "var(--text-md)",
                  fontWeight: active ? 600 : 400,
                  transition: "color var(--duration-fast), background var(--duration-fast)",
                }}
              >
                {item.label}
              </Link>
            );
          })}
        </nav>
      </div>

      {/* Right: Moodify + wallet state */}
      <div style={{ display: "flex", alignItems: "center", gap: "var(--space-4)" }}>
        <Link
          href="/"
          style={{
            display: "flex",
            alignItems: "center",
            gap: "var(--space-2)",
            textDecoration: "none",
            color: "var(--text-muted)",
            fontSize: "var(--text-sm)",
          }}
        >
          <BrandMark size="sm" wordmark="Moodify" />
          <span
            style={{
              fontSize: "var(--text-xs)",
              color: "var(--text-faint)",
              fontWeight: 600,
              letterSpacing: "0.08em",
              textTransform: "uppercase",
            }}
          >
            Genesis Application
          </span>
        </Link>

        {walletState === "connected" && walletAddress ? (
          <span
            style={{
              padding: "var(--space-1) var(--space-3)",
              borderRadius: "var(--radius-pill)",
              background: "var(--evidence-soft)",
              border: "1px solid var(--evidence)",
              color: "var(--evidence)",
              fontSize: "var(--text-xs)",
              fontWeight: 600,
              fontFamily: "monospace",
            }}
          >
            {walletAddress.slice(0, 6)}…{walletAddress.slice(-4)}
          </span>
        ) : (
          <span
            style={{
              padding: "var(--space-1) var(--space-3)",
              borderRadius: "var(--radius-pill)",
              background: "var(--surface-subtle)",
              border: "1px solid var(--line)",
              color: "var(--text-faint)",
              fontSize: "var(--text-xs)",
            }}
          >
            Visitor
          </span>
        )}
      </div>

      <style>{`
        @media (max-width: 768px) {
          .mood-desktop-nav { display: none !important; }
        }
      `}</style>
    </header>
  );
}

/* ─── MoodPublicFooter ──────────────────────────────────────────────────────── */

export function MoodPublicFooter() {
  const year = new Date().getFullYear();
  return (
    <footer
      style={{
        borderTop: "1px solid var(--line)",
        padding: "var(--space-8) clamp(16px, 4vw, 48px)",
        color: "var(--text-faint)",
        fontSize: "var(--text-sm)",
        display: "flex",
        flexDirection: "column",
        gap: "var(--space-4)",
        marginTop: "auto",
      }}
    >
      <div
        style={{
          display: "flex",
          flexWrap: "wrap",
          gap: "var(--space-6)",
          alignItems: "flex-start",
        }}
      >
        {/* Brand */}
        <div style={{ display: "flex", flexDirection: "column", gap: "var(--space-2)" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "var(--space-2)" }}>
            <span
              aria-hidden
              style={{
                width: 24,
                height: 24,
                borderRadius: 4,
                background: "linear-gradient(135deg, var(--brand-violet), var(--brand-cyan))",
                display: "grid",
                placeItems: "center",
                fontSize: 10,
                color: "white",
                fontWeight: 700,
              }}
            >
              M
            </span>
            <span style={{ fontWeight: 700, color: "var(--text-muted)" }}>MOOD</span>
          </div>
          <p style={{ margin: 0, maxWidth: 280, lineHeight: "var(--leading-normal)" }}>
            An open Web3 world built by people and AI.
          </p>
        </div>

        {/* Navigation */}
        <nav
          aria-label="Footer navigation"
          style={{
            display: "flex",
            flexWrap: "wrap",
            gap: "var(--space-2) var(--space-6)",
          }}
        >
          {[
            { label: "World", href: "/world" },
            { label: "Protocol", href: "/protocol" },
            { label: "Portal", href: "/portal" },
            { label: "Library", href: "/library" },
            { label: "Network", href: "/network" },
          ].map((item) => (
            <Link
              key={item.href}
              href={item.href}
              style={{
                color: "var(--text-faint)",
                textDecoration: "none",
                fontSize: "var(--text-sm)",
              }}
            >
              {item.label}
            </Link>
          ))}
        </nav>
      </div>

      <div
        style={{
          display: "flex",
          flexWrap: "wrap",
          gap: "var(--space-4)",
          alignItems: "center",
          paddingTop: "var(--space-4)",
          borderTop: "1px solid var(--line)",
        }}
      >
        <span>
          © {year} MOOD. No Token is currently active.
        </span>
        <span>·</span>
        <a
          href="https://github.com/huliye24/moodify-ai"
          target="_blank"
          rel="noopener noreferrer"
          style={{ color: "var(--text-faint)", textDecoration: "none" }}
        >
          GitHub
        </a>
        <span>·</span>
        <Link href="/protocol" style={{ color: "var(--text-faint)", textDecoration: "none" }}>
          Security
        </Link>
        <span>·</span>
        <Link href="/" style={{ color: "var(--text-faint)", textDecoration: "none" }}>
          Moodify
        </Link>
      </div>
    </footer>
  );
}

/* ─── PortalShell ───────────────────────────────────────────────────────────── */

export interface PortalShellProps {
  children: ReactNode;
  activeArea?: MoodArea;
  walletState?: "disconnected" | "connected";
  walletAddress?: string;
}

export function PortalShell({
  children,
  activeArea,
  walletState,
  walletAddress,
}: PortalShellProps) {
  return (
    <div
      style={{
        minHeight: "100vh",
        display: "flex",
        flexDirection: "column",
        background: "var(--bg)",
        color: "var(--text)",
        fontFamily: "var(--font-body)",
      }}
    >
      <MoodPublicHeader
        activeArea={activeArea}
        walletState={walletState}
        walletAddress={walletAddress}
      />
      <main
        style={{
          flex: 1,
          padding: "var(--space-12) clamp(16px, 4vw, 48px)",
          maxWidth: 1200,
          width: "100%",
          margin: "0 auto",
        }}
      >
        {children}
      </main>
      <MoodPublicFooter />
    </div>
  );
}

/* ─── SectionHeading ────────────────────────────────────────────────────────── */

export interface SectionHeadingProps {
  eyebrow?: string;
  title: string;
  description?: string;
  action?: ReactNode;
}

export function SectionHeading({
  eyebrow,
  title,
  description,
  action,
}: SectionHeadingProps) {
  return (
    <div
      style={{
        marginBottom: "var(--space-8)",
        display: "flex",
        alignItems: "flex-end",
        justifyContent: "space-between",
        flexWrap: "wrap",
        gap: "var(--space-4)",
      }}
    >
      <div>
        {eyebrow && (
          <p
            style={{
              margin: "0 0 var(--space-2)",
              fontSize: "var(--text-xs)",
              fontWeight: 700,
              letterSpacing: "0.12em",
              textTransform: "uppercase" as const,
              color: "var(--text-muted)",
            }}
          >
            {eyebrow}
          </p>
        )}
        <h2
          style={{
            margin: 0,
            fontSize: "var(--text-4xl)",
            fontWeight: 700,
            lineHeight: "var(--leading-tight)",
            color: "var(--text)",
            fontFamily: "var(--font-display)",
          }}
        >
          {title}
        </h2>
        {description && (
          <p
            style={{
              margin: "var(--space-3) 0 0",
              color: "var(--text-muted)",
              fontSize: "var(--text-lg)",
              maxWidth: 560,
            }}
          >
            {description}
          </p>
        )}
      </div>
      {action ? <div>{action}</div> : null}
    </div>
  );
}
