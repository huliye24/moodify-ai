/* Moodify Badge component — MFY_SHARED_DESIGN_SYSTEM_AND_SHELL_001 */

import type { CSSProperties, ReactNode } from "react";
import { forwardRef } from "react";

export interface BadgeProps {
  children: ReactNode;
  variant?: "default" | "secondary" | "outline" | "success" | "warning" | "error";
  size?: "sm" | "md";
  className?: string;
  style?: CSSProperties;
}

export const Badge = forwardRef<HTMLSpanElement, BadgeProps>(({
  children,
  variant = "default",
  size = "md",
  className = "",
  style = {},
  ...props
}, ref) => {
  const variantStyles: Record<string, CSSProperties> = {
    default: {
      background: "var(--evidence)",
      color: "var(--on-contrast)",
      border: "1px solid var(--evidence)",
    },
    secondary: {
      background: "var(--surface-subtle)",
      color: "var(--text)",
      border: "1px solid var(--line)",
    },
    outline: {
      background: "transparent",
      color: "var(--text)",
      border: "1px solid var(--line)",
    },
    success: {
      background: "var(--success)",
      color: "var(--on-contrast)",
      border: "1px solid var(--success)",
    },
    warning: {
      background: "var(--attention)",
      color: "var(--on-contrast)",
      border: "1px solid var(--attention)",
    },
    error: {
      background: "var(--blocking)",
      color: "var(--on-contrast)",
      border: "1px solid var(--blocking)",
    },
  };

  const sizeStyles: Record<string, CSSProperties> = {
    sm: {
      fontSize: "var(--text-xs)",
      padding: "2px 8px",
      height: 20,
    },
    md: {
      fontSize: "var(--text-sm)",
      padding: "2px 12px",
      height: 24,
    },
  };

  return (
    <span
      ref={ref}
      className={className}
      style={{
        display: "inline-flex",
        alignItems: "center",
        justifyContent: "center",
        borderRadius: "var(--radius-pill)",
        fontWeight: 500,
        fontFamily: "inherit",
        lineHeight: 1,
        ...variantStyles[variant],
        ...sizeStyles[size],
        ...style,
      }}
      {...props}
    >
      {children}
    </span>
  );
});

Badge.displayName = "Badge";