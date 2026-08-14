/* Moodify UI primitives — MFY_SHARED_DESIGN_SYSTEM_AND_SHELL_001.
   Presentational only: accept state via props, never derive Ear judgment or
   Music publication conclusions. All colors/spacing from tokens.css. */

import type { CSSProperties, ReactNode } from "react";
import {
  type ButtonHTMLAttributes,
  type AnchorHTMLAttributes,
  type InputHTMLAttributes,
  type SelectHTMLAttributes,
  type TextareaHTMLAttributes,
  useEffect,
  useId,
  useRef,
} from "react";

/* ---------- Button ---------- */

type ButtonVariant = "primary" | "ghost" | "danger" | "brand";
type ButtonSize = "sm" | "md";

export interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
  size?: ButtonSize;
  loading?: boolean;
}

const buttonVariantStyle: Record<ButtonVariant, CSSProperties> = {
  primary: { background: "var(--evidence)", color: "var(--on-contrast)" },
  ghost: { background: "var(--surface-subtle)", border: "1px solid var(--line)", color: "var(--text)" },
  danger: { background: "var(--blocking)", color: "var(--on-contrast)" },
  brand: { background: "linear-gradient(100deg, var(--brand-violet), var(--brand-cyan))", color: "var(--on-accent)" },
};

const buttonSizeStyle: Record<ButtonSize, CSSProperties> = {
  sm: { padding: "0 var(--space-4)", height: 36, fontSize: "var(--text-sm)" },
  md: { padding: "0 var(--space-6)", height: 44, fontSize: "var(--text-md)" },
};

export function Button({
  variant = "primary",
  size = "md",
  loading = false,
  className = "",
  style,
  disabled,
  children,
  ...rest
}: ButtonProps) {
  return (
    <button
      className={className}
      style={{
        display: "inline-flex",
        alignItems: "center",
        justifyContent: "center",
        gap: "var(--space-2)",
        border: 0,
        borderRadius: "var(--radius-pill)",
        fontWeight: 600,
        fontFamily: "inherit",
        cursor: "pointer",
        opacity: disabled || loading ? 0.45 : 1,
        transition: "opacity var(--duration-fast) var(--ease-out)",
        ...buttonVariantStyle[variant],
        ...buttonSizeStyle[size],
        ...style,
      }}
      disabled={disabled || loading}
      aria-busy={loading || undefined}
      {...rest}
    >
      {loading ? <span aria-hidden>…</span> : children}
    </button>
  );
}

/* ---------- Link (styled anchor) ---------- */

export interface LinkProps extends AnchorHTMLAttributes<HTMLAnchorElement> {
  variant?: "default" | "muted" | "evidence";
}

const linkVariantStyle: Record<string, CSSProperties> = {
  default: { color: "var(--text)" },
  muted: { color: "var(--text-muted)" },
  evidence: { color: "var(--evidence)" },
};

export function Link({ variant = "default", className = "", style, ...rest }: LinkProps) {
  return (
    <a
      className={className}
      style={{
        textDecoration: "none",
        transition: "opacity var(--duration-fast) var(--ease-out)",
        ...linkVariantStyle[variant],
        ...style,
      }}
      {...rest}
    />
  );
}

/* ---------- Field ---------- */

export interface FieldProps {
  label: string;
  hint?: string;
  error?: string;
  required?: boolean;
  htmlFor?: string;
  children: ReactNode;
}

export function Field({ label, hint, error, required, htmlFor, children }: FieldProps) {
  const id = useId();
  const controlId = htmlFor ?? id;
  return (
    <div style={{ display: "grid", gap: "var(--space-2)" }}>
      <label htmlFor={controlId} style={{ fontSize: "var(--text-sm)", color: "var(--text-muted)" }}>
        {label}
        {required ? <span style={{ color: "var(--blocking)" }}> *</span> : null}
      </label>
      {children}
      {error ? (
        <output htmlFor={controlId} role="alert" style={{ fontSize: "var(--text-sm)", color: "var(--blocking)" }}>
          {error}
        </output>
      ) : hint ? (
        <span style={{ fontSize: "var(--text-sm)", color: "var(--text-faint)" }}>{hint}</span>
      ) : null}
    </div>
  );
}

const controlStyle: CSSProperties = {
  width: "100%",
  border: "1px solid var(--line)",
  borderRadius: "var(--radius-sm)",
  background: "var(--surface)",
  color: "var(--text)",
  padding: "var(--space-3)",
  fontSize: "var(--text-md)",
  outline: "none",
  fontFamily: "inherit",
};

export function TextInput(props: InputHTMLAttributes<HTMLInputElement>) {
  return <input {...props} style={{ ...controlStyle, ...props.style }} />;
}

export function TextArea(props: TextareaHTMLAttributes<HTMLTextAreaElement>) {
  const { rows = 3, ...rest } = props;
  return <textarea {...rest} rows={rows} style={{ ...controlStyle, resize: "vertical", ...props.style }} />;
}

export function Select(props: SelectHTMLAttributes<HTMLSelectElement>) {
  return <select {...props} style={{ ...controlStyle, ...props.style }} />;
}

/* ---------- Dialog ---------- */

export interface DialogProps {
  open: boolean;
  onClose: () => void;
  title: string;
  children: ReactNode;
  footer?: ReactNode;
}

export function Dialog({ open, onClose, title, children, footer }: DialogProps) {
  const titleId = useId();
  const ref = useRef<HTMLDivElement>(null);
  useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    document.addEventListener("keydown", onKey);
    ref.current?.focus();
    return () => document.removeEventListener("keydown", onKey);
  }, [open, onClose]);
  if (!open) return null;
  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby={titleId}
      tabIndex={-1}
      ref={ref}
      style={{
        position: "fixed",
        inset: 0,
        display: "grid",
        placeItems: "center",
        background: "rgba(5,8,30,.72)",
        zIndex: 60,
      }}
      onClick={(e) => {
        if (e.target === e.currentTarget) onClose();
      }}
    >
      <div
        style={{
          width: "min(560px, calc(100vw - 32px))",
          background: "var(--surface)",
          border: "1px solid var(--line)",
          borderRadius: "var(--radius-lg)",
          padding: "var(--space-6)",
          display: "grid",
          gap: "var(--space-4)",
        }}
      >
        <h2 id={titleId} style={{ margin: 0, fontSize: "var(--text-xl)", fontWeight: 600 }}>
          {title}
        </h2>
        <div>{children}</div>
        {footer ? <div style={{ display: "flex", gap: "var(--space-3)", justifyContent: "flex-end" }}>{footer}</div> : null}
      </div>
    </div>
  );
}

/* ---------- Toast ---------- */

export type ToastTone = "info" | "success" | "attention" | "error";

export interface ToastProps {
  tone?: ToastTone;
  message: string;
  onDismiss: () => void;
}

const toastColor: Record<ToastTone, string> = {
  info: "var(--text-muted)",
  success: "var(--evidence)",
  attention: "var(--attention)",
  error: "var(--blocking)",
};

export function Toast({ tone = "info", message, onDismiss }: ToastProps) {
  return (
    <div
      role={tone === "error" ? "alert" : "status"}
      aria-live={tone === "error" ? "assertive" : "polite"}
      style={{
        display: "flex",
        alignItems: "center",
        gap: "var(--space-3)",
        padding: "var(--space-3) var(--space-4)",
        background: "var(--surface)",
        border: `1px solid ${toastColor[tone]}`,
        borderLeft: `3px solid ${toastColor[tone]}`,
        borderRadius: "var(--radius-md)",
        fontSize: "var(--text-md)",
        color: "var(--text)",
      }}
    >
      <span style={{ width: 8, height: 8, borderRadius: "50%", background: toastColor[tone], flex: "none" }} aria-hidden />
      <span>{message}</span>
      <button
        type="button"
        aria-label="Dismiss"
        onClick={onDismiss}
        style={{ marginLeft: "auto", background: "none", border: 0, color: "var(--text-muted)", cursor: "pointer", fontSize: "var(--text-md)" }}
      >
        ×
      </button>
    </div>
  );
}
