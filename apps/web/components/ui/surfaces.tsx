/* Moodify page shell components — MFY_SHARED_DESIGN_SYSTEM_AND_SHELL_001.
   Navigation and shell only; never derives product state. */

import type { ReactNode } from "react";

/* ---------- BrandMark ---------- */

export interface BrandMarkProps {
  size?: "sm" | "md" | "lg";
  wordmark?: string;
}

export function BrandMark({ size = "md", wordmark = "MOODIFY" }: BrandMarkProps) {
  const fontSize = size === "lg" ? "var(--text-2xl)" : size === "sm" ? "var(--text-md)" : "var(--text-xl)";
  return (
    <span
      style={{
        display: "inline-flex",
        alignItems: "center",
        gap: "var(--space-2)",
        fontWeight: 700,
        fontSize,
        letterSpacing: "0.04em",
        color: "var(--text)",
        fontFamily: "var(--font-body)",
      }}
    >
      <span
        aria-hidden
        style={{
          width: size === "lg" ? 40 : size === "sm" ? 22 : 30,
          height: size === "lg" ? 40 : size === "sm" ? 22 : 30,
          borderRadius: "var(--radius-sm)",
          background: "linear-gradient(135deg, var(--brand-violet), var(--brand-cyan))",
          display: "grid",
          placeItems: "center",
          fontSize: size === "lg" ? 16 : size === "sm" ? 9 : 12,
          color: "var(--on-accent)",
        }}
      >
        M
      </span>
      {wordmark}
    </span>
  );
}

/* ---------- ProductSwitcher ---------- */

export type ProductEntry = "website" | "ear" | "music";

export interface ProductSwitcherProps {
  current: ProductEntry;
  onNavigate?: (product: ProductEntry) => void;
}

const productLabel: Record<ProductEntry, string> = {
  website: "Website",
  ear: "Moodify Ear",
  music: "Moodify Music",
};

export function ProductSwitcher({ current, onNavigate }: ProductSwitcherProps) {
  return (
    <nav aria-label="Product" style={{ display: "inline-flex", gap: "var(--space-1)", padding: 3, background: "var(--surface-subtle)", borderRadius: "var(--radius-pill)", border: "1px solid var(--line)" }}>
      {(Object.keys(productLabel) as ProductEntry[]).map((entry) => {
        const active = entry === current;
        return (
          <button
            key={entry}
            type="button"
            aria-current={active ? "page" : undefined}
            onClick={() => onNavigate?.(entry)}
            style={{
              padding: "var(--space-1) var(--space-4)",
              borderRadius: "var(--radius-pill)",
              border: 0,
              background: active ? "var(--surface)" : "transparent",
              color: active ? "var(--text)" : "var(--text-muted)",
              fontSize: "var(--text-xs)",
              fontWeight: active ? 600 : 400,
              cursor: "pointer",
            }}
          >
            {productLabel[entry]}
          </button>
        );
      })}
    </nav>
  );
}

/* ---------- NavLink ---------- */

export interface NavLinkProps {
  href: string;
  active?: boolean;
  children: ReactNode;
}

export function NavLink({ href, active, children }: NavLinkProps) {
  return (
    <a
      href={href}
      aria-current={active ? "page" : undefined}
      style={{
        display: "block",
        padding: "var(--space-2) var(--space-3)",
        borderRadius: "var(--radius-sm)",
        color: active ? "var(--text)" : "var(--text-muted)",
        background: active ? "var(--surface-subtle)" : "transparent",
        borderLeft: active ? `2px solid var(--evidence)` : "2px solid transparent",
        textDecoration: "none",
        fontSize: "var(--text-md)",
      }}
    >
      {children}
    </a>
  );
}

/* ---------- PageShell ---------- */

export interface PageShellProps {
  header?: ReactNode;
  nav?: ReactNode;
  footer?: ReactNode;
  maxWidth?: number;
  children: ReactNode;
}

export function PageShell({ header, nav, footer, maxWidth = 1080, children }: PageShellProps) {
  return (
    <div style={{ minHeight: "100vh", display: "flex", flexDirection: "column", background: "var(--bg)" }}>
      {header ? (
        <header
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            gap: "var(--space-4)",
            padding: "var(--space-4) clamp(16px, 4vw, 48px)",
            borderBottom: "1px solid var(--line)",
          }}
        >
          {header}
        </header>
      ) : null}
      {nav ? <nav style={{ padding: "0 clamp(16px, 4vw, 48px)" }}>{nav}</nav> : null}
      <main style={{ flex: 1, width: "100%", maxWidth, margin: "0 auto", padding: "var(--space-8) clamp(16px, 4vw, 48px)" }}>{children}</main>
      {footer ? (
        <footer style={{ borderTop: "1px solid var(--line)", padding: "var(--space-8) clamp(16px, 4vw, 48px)", color: "var(--text-faint)", fontSize: "var(--text-sm)" }}>
          {footer}
        </footer>
      ) : null}
    </div>
  );
}
