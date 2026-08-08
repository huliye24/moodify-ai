#!/usr/bin/env python3
"""Generate an X-CLP gate report for Moodify modules.

Part of ECHAIN-MOODIFY-DEEPSEEK-API-015 / MHP-900.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Ensure moodify_runtime is importable from the scripts dir.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from moodify_runtime.xclp_gate import (  # type: ignore[import-not-found]
    GateReport,
    gate_module,
    format_gate_report_markdown,
)

DEFAULT_MODULES = {
    "deepseek_worker_client": {"R": 70, "S": 60, "M": 60, "E": 55, "target": 60},
    "xclp_gate": {"R": 75, "S": 80, "M": 80, "E": 80, "target": 80},
    "mainline_registry": {"R": 70, "S": 70, "M": 70, "E": 65, "target": 70},
    "handoff_pack": {"R": 80, "S": 80, "M": 80, "E": 80, "target": 80},
}


def load_module_scores(path: Path) -> dict[str, dict]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    return raw


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="X-CLP Moodify gate report generator")
    parser.add_argument("--modules-json", type=Path, default=None,
                        help="JSON file with module scores (default: built-in targets)")
    parser.add_argument("--output", type=Path, default=None,
                        help="Output markdown file (default: stdout)")
    parser.add_argument("--title", default="Moodify X-CLP Gate Report",
                        help="Report title")
    args = parser.parse_args(argv)

    if args.modules_json:
        modules = load_module_scores(args.modules_json)
    else:
        modules = DEFAULT_MODULES

    reports: list[GateReport] = []
    for name, cfg in modules.items():
        r = gate_module(
            name,
            r_speed=cfg["R"],
            s_structure=cfg["S"],
            m_maintainability=cfg["M"],
            e_evolvability=cfg["E"],
            xclp_target=cfg.get("target", 60),
        )
        reports.append(r)

    md = format_gate_report_markdown(reports, title=args.title)

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(md, encoding="utf-8")
        print(f"Report written to {args.output}")
    else:
        print(md)

    failures = sum(1 for r in reports if not r.passed)
    if failures:
        print(f"\n{failures} module(s) below X-CLP target.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
