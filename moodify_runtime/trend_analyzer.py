"""Cross-night trend analyzer for the multi-night learning store.

Computes rolling trend metrics, direction flags, and change markers.
Deterministic, no live feedback coupling.
Part of ECHAIN-MOODIFY-MULTI-NIGHT-STORE-016 / MHP-906.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .learning_store import load_store, NightRecord

DEFAULT_WINDOW = 3


@dataclass
class TrendPoint:
    night_label: str
    avg_eds: float | None
    avg_elapsed_s: float | None
    success_rate: float | None
    eds_direction: str = "stable"
    elapsed_direction: str = "stable"
    success_direction: str = "stable"


@dataclass
class TrendReport:
    window_size: int
    points: list[TrendPoint] = field(default_factory=list)
    summary: dict[str, Any] = field(default_factory=dict)
    generated_at: str = ""


def _direction(prev: float | None, curr: float | None, threshold: float = 0.02) -> str:
    if prev is None or curr is None:
        return "stable"
    if prev == 0:
        return "improving" if curr > 0 else "stable"
    pct = (curr - prev) / abs(prev)
    if pct > threshold:
        return "improving"
    if pct < -threshold:
        return "declining"
    return "stable"


def analyze_trends(store_path: Path, window_size: int = DEFAULT_WINDOW) -> TrendReport:
    records = load_store(store_path)
    records.sort(key=lambda r: r.night_label)

    points: list[TrendPoint] = []
    eds_prev: float | None = None
    elapsed_prev: float | None = None
    success_prev: float | None = None

    for r in records:
        sr = r.success_count / r.selected_count if r.selected_count > 0 else None
        tp = TrendPoint(
            night_label=r.night_label,
            avg_eds=r.avg_eds,
            avg_elapsed_s=r.avg_elapsed_s,
            success_rate=round(sr, 4) if sr is not None else None,
        )
        tp.eds_direction = _direction(eds_prev, r.avg_eds)
        tp.elapsed_direction = _direction(elapsed_prev, r.avg_elapsed_s)
        tp.success_direction = _direction(success_prev, sr)
        points.append(tp)
        eds_prev = r.avg_eds
        elapsed_prev = r.avg_elapsed_s
        success_prev = sr

    eds_vals = [p.avg_eds for p in points if p.avg_eds is not None]
    elapsed_vals = [p.avg_elapsed_s for p in points if p.avg_elapsed_s is not None]

    summary = {
        "total_nights": len(records),
        "window_size": window_size,
        "eds_overall_direction": _direction(
            eds_vals[0] if len(eds_vals) > 1 else None,
            eds_vals[-1] if eds_vals else None,
        ),
        "elapsed_overall_direction": _direction(
            elapsed_vals[0] if len(elapsed_vals) > 1 else None,
            elapsed_vals[-1] if elapsed_vals else None,
        ),
    }
    improving = sum(1 for p in points if p.eds_direction == "improving")
    declining = sum(1 for p in points if p.eds_direction == "declining")
    summary["eds_improving_nights"] = improving
    summary["eds_declining_nights"] = declining

    return TrendReport(
        window_size=window_size,
        points=points,
        summary=summary,
        generated_at=_utc_now_iso(),
    )


def _utc_now_iso() -> str:
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).isoformat()


def format_trend_json(report: TrendReport) -> str:
    points_data = []
    for p in report.points:
        points_data.append({
            "night_label": p.night_label,
            "avg_eds": p.avg_eds,
            "avg_elapsed_s": p.avg_elapsed_s,
            "success_rate": p.success_rate,
            "eds_direction": p.eds_direction,
            "elapsed_direction": p.elapsed_direction,
            "success_direction": p.success_direction,
        })
    return json.dumps({
        "window_size": report.window_size,
        "generated_at": report.generated_at,
        "summary": report.summary,
        "points": points_data,
    }, ensure_ascii=False, indent=2)


def format_trend_markdown(report: TrendReport) -> str:
    lines = [
        "# Multi-Night Trend Report",
        "",
        f"**Window size**: {report.window_size} nights",
        f"**Generated**: {report.generated_at}",
        f"**Total nights**: {report.summary['total_nights']}",
        "",
        f"**EDS overall**: {report.summary.get('eds_overall_direction', 'n/a')}",
        f"**Elapsed overall**: {report.summary.get('elapsed_overall_direction', 'n/a')}",
        "",
        "| Night | EDS | Elapsed(s) | Success Rate | EDS Dir | Time Dir |",
        "|---|---|---|---|---|---|",
    ]
    for p in report.points:
        eds_str = f"{p.avg_eds:.1f}" if p.avg_eds is not None else "-"
        el_str = f"{p.avg_elapsed_s:.0f}" if p.avg_elapsed_s is not None else "-"
        sr_str = f"{p.success_rate:.1%}" if p.success_rate is not None else "-"
        lines.append(
            f"| {p.night_label} | {eds_str} | {el_str} | {sr_str} | "
            f"{p.eds_direction} | {p.elapsed_direction} |"
        )
    return "\n".join(lines)
