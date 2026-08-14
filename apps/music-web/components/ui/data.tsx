/* Moodify data display components — MFY_SHARED_DESIGN_SYSTEM_AND_SHELL_001.
   Render-only: tables, definition lists, single-question chart frames. */

import type { ReactNode } from "react";

/* ---------- DataTable ---------- */

export interface DataColumn<T> {
  key: string;
  header: string;
  render?: (row: T) => ReactNode;
  numeric?: boolean;
}

export interface DataTableProps<T> {
  columns: DataColumn<T>[];
  rows: T[];
  emptyLabel?: string;
}

export function DataTable<T>({ columns, rows, emptyLabel = "No records" }: DataTableProps<T>) {
  if (rows.length === 0) {
    return <p style={{ color: "var(--text-faint)", fontSize: "var(--text-sm)" }}>{emptyLabel}</p>;
  }
  return (
    <div style={{ overflowX: "auto", border: "1px solid var(--line)", borderRadius: "var(--radius-md)" }}>
      <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "var(--text-md)" }}>
        <thead>
          <tr style={{ textAlign: "left", background: "var(--surface-subtle)" }}>
            {columns.map((col) => (
              <th
                key={col.key}
                scope="col"
                style={{
                  padding: "var(--space-3)",
                  color: "var(--text-muted)",
                  fontSize: "var(--text-xs)",
                  textTransform: "uppercase",
                  letterSpacing: "0.08em",
                  fontWeight: 600,
                }}
              >
                {col.header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, index) => (
            <tr key={index} style={{ borderTop: "1px solid var(--line)" }}>
              {columns.map((col) => (
                <td
                  key={col.key}
                  style={{
                    padding: "var(--space-3)",
                    color: "var(--text)",
                    fontVariantNumeric: col.numeric ? "tabular-nums" : undefined,
                  }}
                >
                  {col.render ? col.render(row) : String((row as Record<string, unknown>)[col.key] ?? "")}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

/* ---------- DefinitionList ---------- */

export interface DefinitionItem {
  term: string;
  detail: ReactNode;
}

export function DefinitionList({ items }: { items: DefinitionItem[] }) {
  return (
    <dl style={{ margin: 0, display: "grid", gap: "var(--space-3)" }}>
      {items.map((item, index) => (
        <div key={index} style={{ display: "grid", gridTemplateColumns: "minmax(120px, 180px) 1fr", gap: "var(--space-4)" }}>
          <dt style={{ color: "var(--text-muted)", fontSize: "var(--text-sm)" }}>{item.term}</dt>
          <dd style={{ margin: 0, color: "var(--text)", fontSize: "var(--text-md)", fontVariantNumeric: "tabular-nums" }}>{item.detail}</dd>
        </div>
      ))}
    </dl>
  );
}

/* ---------- ChartFrame (single-question chart) ---------- */

export interface ChartFrameProps {
  title: string;
  question?: string;
  children: ReactNode;
  note?: string;
}

export function ChartFrame({ title, question, children, note }: ChartFrameProps) {
  return (
    <figure style={{ margin: 0, border: "1px solid var(--line)", borderRadius: "var(--radius-md)", padding: "var(--space-6)", display: "grid", gap: "var(--space-3)" }}>
      <figcaption>
        <div style={{ fontWeight: 600, fontSize: "var(--text-md)", color: "var(--text)" }}>{title}</div>
        {question ? <div style={{ fontSize: "var(--text-sm)", color: "var(--text-muted)" }}>{question}</div> : null}
      </figcaption>
      {children}
      {note ? (
        <div style={{ fontSize: "var(--text-xs)", color: "var(--text-faint)", borderTop: "1px solid var(--line)", paddingTop: "var(--space-2)" }}>{note}</div>
      ) : null}
    </figure>
  );
}
