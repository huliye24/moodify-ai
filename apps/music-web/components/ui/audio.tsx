/* Moodify audio transport primitives — MFY_SHARED_DESIGN_SYSTEM_AND_SHELL_001.
   Presentational transport: never owns a media element or business state. */

"use client";

import type { CSSProperties } from "react";

export interface AudioTransportProps {
  playing: boolean;
  onToggle: () => void;
  positionSeconds: number;
  durationSeconds: number;
  onSeek?: (seconds: number) => void;
  volume?: number;
  onVolume?: (value: number) => void;
  disabled?: boolean;
  labels?: { play?: string; pause?: string; position?: string };
}

function formatTime(seconds: number): string {
  if (!Number.isFinite(seconds) || seconds < 0) return "0:00";
  const total = Math.floor(seconds);
  const m = Math.floor(total / 60);
  const s = total % 60;
  return `${m}:${String(s).padStart(2, "0")}`;
}

export function AudioTransport({
  playing,
  onToggle,
  positionSeconds,
  durationSeconds,
  onSeek,
  volume,
  onVolume,
  disabled = false,
  labels,
}: AudioTransportProps) {
  const progress = durationSeconds > 0 ? Math.min(100, (positionSeconds / durationSeconds) * 100) : 0;
  const root: CSSProperties = {
    display: "grid",
    gridTemplateColumns: "auto 1fr auto",
    gap: "var(--space-3)",
    alignItems: "center",
  };
  return (
    <div style={root}>
      <button
        type="button"
        aria-label={playing ? (labels?.pause ?? "Pause") : (labels?.play ?? "Play")}
        onClick={onToggle}
        disabled={disabled}
        style={{
          width: 44,
          height: 44,
          borderRadius: "50%",
          border: 0,
          background: "var(--evidence)",
          color: "var(--on-contrast)",
          fontSize: "var(--text-md)",
          cursor: disabled ? "not-allowed" : "pointer",
          opacity: disabled ? 0.45 : 1,
        }}
      >
        {playing ? "❚❚" : "▶"}
      </button>
      <div style={{ display: "grid", gap: "var(--space-2)" }}>
        <input
          type="range"
          aria-label={labels?.position ?? "Position"}
          min={0}
          max={durationSeconds || 0}
          step={1}
          value={Math.min(positionSeconds, durationSeconds || 0)}
          disabled={disabled || durationSeconds <= 0}
          onChange={(e) => onSeek?.(Number(e.target.value))}
          style={{ width: "100%", accentColor: "var(--evidence)", height: 3, cursor: "pointer" }}
        />
        <div style={{ display: "flex", justifyContent: "space-between", fontSize: "var(--text-xs)", color: "var(--text-faint)", fontVariantNumeric: "tabular-nums" }}>
          <span>{formatTime(positionSeconds)}</span>
          <span>{formatTime(durationSeconds)}</span>
        </div>
      </div>
      {typeof volume === "number" && onVolume ? (
        <input
          type="range"
          aria-label="Volume"
          min={0}
          max={1}
          step={0.01}
          value={volume}
          disabled={disabled}
          onChange={(e) => onVolume(Number(e.target.value))}
          style={{ width: 72, accentColor: "var(--evidence)", height: 3, cursor: "pointer" }}
        />
      ) : (
        <span aria-hidden style={{ width: 72 }} />
      )}
    </div>
  );
}

export { formatTime };
