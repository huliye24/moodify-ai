/* Moodify status components — MFY_SHARED_DESIGN_SYSTEM_AND_SHELL_001.
   Accept state via props only. Semantic discipline (design_tokens_v1 §5):
   amber = human attention only, red = blocking failure only. */

import type { CSSProperties, ReactNode } from "react";

/* ---------- StateLabel ---------- */

export type SystemState =
  | "ready"
  | "processing"
  | "human_required"
  | "inconclusive"
  | "pending"
  | "failed"
  | "empty"
  | "offline";

export interface StateLabelProps {
  state: SystemState;
  label?: string;
}

const stateStyle: Record<SystemState, { color: string; bg: string }> = {
  ready: { color: "var(--text-muted)", bg: "var(--surface-subtle)" },
  processing: { color: "var(--evidence)", bg: "var(--evidence-soft)" },
  human_required: { color: "var(--attention)", bg: "var(--attention-soft)" },
  inconclusive: { color: "var(--text-muted)", bg: "var(--surface-subtle)" },
  pending: { color: "var(--text-muted)", bg: "var(--surface-subtle)" },
  failed: { color: "var(--blocking)", bg: "var(--blocking-soft)" },
  empty: { color: "var(--text-faint)", bg: "var(--surface-subtle)" },
  offline: { color: "var(--text-faint)", bg: "var(--surface-subtle)" },
};

const stateDefaultLabel: Record<SystemState, string> = {
  ready: "Ready",
  processing: "Processing",
  human_required: "Human required",
  inconclusive: "Inconclusive",
  pending: "Pending",
  failed: "Failed",
  empty: "Empty",
  offline: "Offline",
};

export function StateLabel({ state, label }: StateLabelProps) {
  const palette = stateStyle[state];
  return (
    <span
      style={{
        display: "inline-flex",
        alignItems: "center",
        gap: "var(--space-2)",
        padding: "var(--space-1) var(--space-3)",
        borderRadius: "var(--radius-pill)",
        background: palette.bg,
        color: palette.color,
        fontSize: "var(--text-xs)",
        fontWeight: 600,
        letterSpacing: "0.08em",
        textTransform: "uppercase" as const,
      }}
    >
      <span aria-hidden style={{ width: 6, height: 6, borderRadius: "50%", background: palette.color }} />
      {label ?? stateDefaultLabel[state]}
    </span>
  );
}

/* ---------- EvidenceBadge (claim maturity, per governance freeze) ---------- */

export type ClaimMaturity = "concept" | "experimental" | "verified" | "human_reviewed";

export interface EvidenceBadgeProps {
  maturity: ClaimMaturity;
  scope?: string;
}

const maturityStyle: Record<ClaimMaturity, { color: string; bg: string }> = {
  concept: { color: "var(--text-muted)", bg: "var(--surface-subtle)" },
  experimental: { color: "var(--attention)", bg: "var(--attention-soft)" },
  verified: { color: "var(--evidence)", bg: "var(--evidence-soft)" },
  human_reviewed: { color: "var(--text)", bg: "var(--surface-subtle)" },
};

const maturityLabel: Record<ClaimMaturity, string> = {
  concept: "Concept",
  experimental: "Experimental",
  verified: "Verified",
  human_reviewed: "Human-reviewed",
};

export function EvidenceBadge({ maturity, scope }: EvidenceBadgeProps) {
  const palette = maturityStyle[maturity];
  return (
    <span
      title={scope ? `Scope: ${scope}` : undefined}
      style={{
        display: "inline-flex",
        alignItems: "center",
        gap: "var(--space-2)",
        padding: "2px var(--space-2)",
        borderRadius: "var(--radius-sm)",
        border: `1px solid ${palette.color}`,
        background: palette.bg,
        color: palette.color,
        fontSize: "var(--text-xs)",
        fontVariantNumeric: "tabular-nums",
      }}
    >
      {maturityLabel[maturity]}
      {scope ? <span style={{ opacity: 0.7 }}>· {scope}</span> : null}
    </span>
  );
}

/* ---------- ProgressStepper ---------- */

export type StepState = "done" | "active" | "pending" | "failed" | "human";

export interface ProgressStep {
  label: string;
  state: StepState;
}

export interface ProgressStepperProps {
  steps: ProgressStep[];
  ariaLabel?: string;
}

const stepColor: Record<StepState, string> = {
  done: "var(--evidence)",
  active: "var(--evidence)",
  pending: "var(--text-faint)",
  failed: "var(--blocking)",
  human: "var(--attention)",
};

export function ProgressStepper({ steps, ariaLabel }: ProgressStepperProps) {
  return (
    <ol
      aria-label={ariaLabel ?? "Progress"}
      style={{
        listStyle: "none",
        margin: 0,
        padding: 0,
        display: "flex",
        gap: "var(--space-2)",
        alignItems: "center",
        flexWrap: "wrap",
      }}
    >
      {steps.map((step, index) => {
        const color = stepColor[step.state];
        return (
          <li key={index} style={{ display: "flex", alignItems: "center", gap: "var(--space-2)" }}>
            <span
              aria-current={step.state === "active" ? "step" : undefined}
              style={{
                display: "inline-flex",
                alignItems: "center",
                gap: "var(--space-2)",
                padding: "var(--space-1) var(--space-3)",
                borderRadius: "var(--radius-pill)",
                background: step.state === "pending" ? "var(--surface-subtle)" : "transparent",
                border: `1px solid ${step.state === "pending" ? "var(--line)" : color}`,
                color: step.state === "pending" ? "var(--text-faint)" : color,
                fontSize: "var(--text-xs)",
                fontWeight: 600,
              }}
            >
              <span aria-hidden>{step.state === "done" ? "✓" : step.state === "failed" ? "✕" : step.state === "human" ? "◐" : index + 1}</span>
              {step.label}
            </span>
            {index < steps.length - 1 ? <span aria-hidden style={{ color: "var(--line)", fontSize: "var(--text-sm)" }}>→</span> : null}
          </li>
        );
      })}
    </ol>
  );
}

/* ---------- Panel ---------- */

export interface PanelProps {
  title?: string;
  children: ReactNode;
  aside?: ReactNode;
}

export function Panel({ title, children, aside }: PanelProps) {
  return (
    <section
      style={{
        border: "1px solid var(--line)",
        borderRadius: "var(--radius-md)",
        background: "var(--surface-subtle)",
        padding: "var(--space-6)",
        display: "grid",
        gap: "var(--space-4)",
      }}
    >
      {title || aside ? (
        <header style={{ display: "flex", alignItems: "center", justifyContent: "space-between", gap: "var(--space-3)" }}>
          {title ? <h3 style={{ margin: 0, fontSize: "var(--text-lg)", fontWeight: 600 }}>{title}</h3> : null}
          {aside}
        </header>
      ) : null}
      {children}
    </section>
  );
}

/* style helper for consumers */
export const statusStyles: Record<string, CSSProperties> = stateStyle;
