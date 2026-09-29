/* Moodify Card component — MFY_SHARED_DESIGN_SYSTEM_AND_SHELL_001 */

import type { CSSProperties, ReactNode } from "react";
import { forwardRef } from "react";

export interface CardProps {
  children: ReactNode;
  className?: string;
  style?: CSSProperties;
}

export const Card = forwardRef<HTMLDivElement, CardProps>(({ children, className = "", style = {}, ...props }, ref) => {
  return (
    <div
      ref={ref}
      className={className}
      style={{
        background: "var(--surface)",
        border: "1px solid var(--line)",
        borderRadius: "var(--radius-lg)",
        padding: "var(--space-6)",
        ...style,
      }}
      {...props}
    >
      {children}
    </div>
  );
});

Card.displayName = "Card";