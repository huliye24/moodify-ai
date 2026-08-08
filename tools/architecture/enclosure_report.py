"""Enclosure weekly/stage report entry (024 Stage E).

Weekly: new violations, public API deltas, concentration trend.
Stage: whether the wall reduced change propagation scope.
Special: triggered by architecture migration or exception spikes.

Read-only; outputs JSON + markdown summary.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from tools.architecture.budget import collect_budget  # noqa: E402
from tools.architecture.enforcer import check_enclosure  # noqa: E402


def build_enclosure_report(previous_budget: dict | None = None) -> dict:
    budget = collect_budget(previous=previous_budget)
    enclosure = check_enclosure()
    return {
        "schema": "moodify.architecture.enclosure-report/0.1",
        "violations": enclosure["summary"]["violations"],
        "baseline_debt": enclosure["summary"]["baseline_debt"],
        "cross_area_edges": budget["cross_area_edges"],
        "cycles": len(budget["cycles"]),
        "core_share_pct": budget["git"]["core_share_pct"],
        "symbol_deltas": budget["symbol_deltas"],
        "oversized_modules": [m["module"] for m in budget["oversized_modules"][:5]],
        "documented_exceptions": budget["documented_exceptions"],
        "pass": enclosure["summary"]["violations"] == 0,
    }


def main() -> int:
    report = build_enclosure_report()
    target = ROOT / "project_analytics" / "enclosure_report.json"
    target.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"enclosure report: {target}")
    print(f"  violations: {report['violations']}  baseline debt: {report['baseline_debt']}")
    print(f"  cross-area edges: {report['cross_area_edges']}  cycles: {report['cycles']}")
    print(f"  core share: {report['core_share_pct']}%")
    print(f"  status: {'PASS' if report['pass'] else 'FAIL'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
