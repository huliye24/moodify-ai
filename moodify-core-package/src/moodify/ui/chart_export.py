"""Headless chart-export bridge for non-Tk shells (Electron desktop app).

The Electron shell renders the report itself; the measurement-faithful
charts still come from the same figure builders the Tk window uses —
exported here as PNGs over an Agg backend, no Tk, no display, no new
chart semantics. stdout is JSON: ``{"charts": {name: path}}``.

Usage::

    python -m moodify.ui.chart_export <report.json> [--out DIR]
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from moodify.ui.report_window import (
    build_band_figure,
    build_level_figure,
    build_stereo_figure,
    select_chart_measurements,
)


def export_chart_pngs(report: dict[str, Any], out_dir: Path) -> dict[str, str]:
    """Render the three unit-honest bar charts from a 0.2 report to PNGs."""
    out_dir.mkdir(parents=True, exist_ok=True)
    series = select_chart_measurements(report.get("measurements") or [])
    builders = (("bands", build_band_figure), ("levels_db", build_level_figure),
                ("stereo_ratios", build_stereo_figure))
    charts: dict[str, str] = {}
    for name, builder in builders:
        rows = series.get(name) or []
        if not rows:
            continue
        path = out_dir / f"chart_{name}.png"
        builder(rows).savefig(path, dpi=110)
        charts[name] = str(path)
    return charts


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if not args:
        print("usage: python -m moodify.ui.chart_export <report.json> [--out DIR]",
              file=sys.stderr)
        return 2
    report_path = Path(args[0])
    out_dir = Path(args[args.index("--out") + 1]) if "--out" in args \
        else report_path.parent / "charts"
    try:
        report = json.loads(report_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "error", "error": str(exc)}, ensure_ascii=False),
              file=sys.stderr)
        return 2
    charts = export_chart_pngs(report, out_dir)
    print(json.dumps({"status": "ok", "charts": charts}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
