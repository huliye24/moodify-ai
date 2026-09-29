/* Moodify Skeleton component — MFY_SHARED_DESIGN_SYSTEM_AND_SHELL_001 */

import type { CSSProperties } from "react";
import { forwardRef } from "react";

export interface SkeletonProps {
  className?: string;
  style?: CSSProperties;
  variant?: "text" | "circular" | "rectangular";
  width?: number | string;
  height?: number | string;
}

export const Skeleton = forwardRef<HTMLDivElement, SkeletonProps>(({
  className = "",
  style = {},
  variant = "rectangular",
  width,
  height,
  ...props
}, ref) => {
  const variantStyles: Record<string, CSSProperties> = {
    text: {
      borderRadius: "var(--radius-sm)",
    },
    circular: {
      borderRadius: "50%",
    },
    rectangular: {
      borderRadius: "var(--radius-md)",
    },
  };

  const defaultWidth = variant === "circular" ? 40 : "100%";
  const defaultHeight = variant === "circular" ? 40 : 16;

  return (
    <div
      ref={ref}
      className={className}
      style={{
        background: "linear-gradient(90deg, var(--surface-subtle) 25%, var(--surface) 50%, var(--surface-subtle) 75%)",
        backgroundSize: "200% 100%",
        animation: "skeleton-loading 1.5s ease-in-out infinite",
        ...variantStyles[variant],
        width: width ?? defaultWidth,
        height: height ?? defaultHeight,
        ...style,
      }}
      {...props}
    />
  );
});

Skeleton.displayName = "Skeleton";

// Add CSS animation for skeleton loading
if (typeof document !== "undefined" && !document.getElementById("skeleton-styles")) {
  const style = document.createElement("style");
  style.id = "skeleton-styles";
  style.textContent = `
    @keyframes skeleton-loading {
      0% {
        background-position: 200% 0;
      }
      100% {
        background-position: -200% 0;
      }
    }
  `;
  document.head.appendChild(style);
}