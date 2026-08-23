/* Moodify empty/error/recovery surfaces — MFY_SHARED_DESIGN_SYSTEM_AND_SHELL_001.
   Honest states: no fake success, no spinner-only feedback. */

import type { ReactNode } from "react";

/* ---------- EmptyState ---------- */

export interface EmptyStateProps {
  title: string;
  hint?: string;
  action?: ReactNode;
}

export function EmptyState({ title, hint, action }: EmptyStateProps) {
  return (
    <div
      style={{
        border: "1px dashed var(--line)",
        borderRadius: "var(--radius-md)",
        padding: "var(--space-12) var(--space-6)",
        display: "grid",
        placeItems: "center",
        gap: "var(--space-3)",
        textAlign: "center",
      }}
    >
      <div style={{ fontSize: "var(--text-lg)", fontWeight: 600, color: "var(--text)" }}>{title}</div>
      {hint ? <div style={{ fontSize: "var(--text-sm)", color: "var(--text-faint)", maxWidth: 420 }}>{hint}</div> : null}
      {action ? <div>{action}</div> : null}
    </div>
  );
}

/* ---------- ErrorState ---------- */

export interface ErrorStateProps {
  title: string;
  detail?: string;
  requestId?: string;
  retryLabel?: string;
  onRetry?: () => void;
}

export function ErrorState({ title, detail, requestId, retryLabel = "Retry", onRetry }: ErrorStateProps) {
  return (
    <div
      role="alert"
      style={{
        border: "1px solid var(--blocking)",
        borderLeft: "3px solid var(--blocking)",
        borderRadius: "var(--radius-md)",
        padding: "var(--space-6)",
        display: "grid",
        gap: "var(--space-2)",
        background: "var(--blocking-soft)",
      }}
    >
      <div style={{ fontWeight: 600, color: "var(--blocking)", fontSize: "var(--text-md)" }}>{title}</div>
      {detail ? <div style={{ fontSize: "var(--text-sm)", color: "var(--text-muted)" }}>{detail}</div> : null}
      {requestId ? (
        <div style={{ fontSize: "var(--text-xs)", color: "var(--text-faint)", fontVariantNumeric: "tabular-nums" }}>
          Request ID: {requestId}
        </div>
      ) : null}
      {onRetry ? (
        <div style={{ marginTop: "var(--space-2)" }}>
          <button
            type="button"
            onClick={onRetry}
            style={{
              border: "1px solid var(--blocking)",
              background: "transparent",
              color: "var(--blocking)",
              borderRadius: "var(--radius-pill)",
              padding: "var(--space-1) var(--space-4)",
              cursor: "pointer",
              fontSize: "var(--text-sm)",
              fontWeight: 600,
            }}
          >
            {retryLabel}
          </button>
        </div>
      ) : null}
    </div>
  );
}

/* ---------- RecoverySurface ---------- */

export interface RecoveryStep {
  label: string;
  action?: string;
}

export interface RecoverySurfaceProps {
  title: string;
  description?: string;
  steps?: RecoveryStep[];
  requestId?: string;
}

export function RecoverySurface({ title, description, steps, requestId }: RecoverySurfaceProps) {
  return (
    <div
      style={{
        border: "1px solid var(--line)",
        borderRadius: "var(--radius-md)",
        padding: "var(--space-6)",
        display: "grid",
        gap: "var(--space-4)",
        background: "var(--surface-subtle)",
      }}
    >
      <div style={{ fontWeight: 600, fontSize: "var(--text-lg)", color: "var(--text)" }}>{title}</div>
      {description ? <div style={{ fontSize: "var(--text-sm)", color: "var(--text-muted)" }}>{description}</div> : null}
      {steps && steps.length > 0 ? (
        <ol style={{ margin: 0, paddingLeft: "var(--space-6)", display: "grid", gap: "var(--space-2)", fontSize: "var(--text-sm)", color: "var(--text-muted)" }}>
          {steps.map((step, index) => (
            <li key={index}>
              {step.label}
              {step.action ? <span style={{ color: "var(--evidence)" }}> — {step.action}</span> : null}
            </li>
          ))}
        </ol>
      ) : null}
      {requestId ? (
        <div style={{ fontSize: "var(--text-xs)", color: "var(--text-faint)", fontVariantNumeric: "tabular-nums" }}>
          Request ID: {requestId}
        </div>
      ) : null}
    </div>
  );
}
