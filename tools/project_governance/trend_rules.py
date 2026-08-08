"""Trend and decision rules (025 Stage D).

Red lines (automatic, must be visible):
- test collection errors > 0
- task state conflicts > 0
- new enclosure violations > 0

Observation items (no hard target):
- change concentration, task cycle, model ROI

Decisions: "resume development" / "continue stabilizing" / "trigger special
assessment". Metrics never auto-publish, never auto-close tasks, never
auto-block work. Medians and intervals, not small-sample means.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _load_latest_observation() -> dict | None:
    obs_dir = ROOT / "project_analytics" / "observations"
    if not obs_dir.exists():
        return None
    files = sorted(obs_dir.glob("obs-*.json"))
    if not files:
        return None
    return json.loads(files[-1].read_text(encoding="utf-8"))


def evaluate() -> dict:
    obs = _load_latest_observation()
    if obs is None:
        return {
            "schema": "moodify.analytics.trend-rules/0.1",
            "status": "NOT_MEASURED",
            "reason": "no observation snapshot",
        }
    m = obs.get("metrics", {})
    test_errors = m.get("test_collection", {}).get("errors", 1)
    conflicts = m.get("task_state_conflicts", 1)
    violations = m.get("enclosure", {}).get("violations", 1)

    red_lines = {
        "test_collection_errors": test_errors > 0,
        "task_state_conflicts": conflicts > 0,
        "enclosure_violations": violations > 0,
    }

    # observation items: trend indicators, no calibrated thresholds
    observations = {
        "core_change_concentration_pct": m.get("git_concentration", {}).get("core_share_pct"),
        "cross_area_edges": m.get("architecture_budget", {}).get("cross_area_edges"),
        "cycles": m.get("architecture_budget", {}).get("cycles"),
        "accepted_share_pct": None,
    }

    # decision
    if any(red_lines.values()):
        decision = "TRIGGER_SPECIAL_ASSESSMENT"
        reason = "red line(s) crossed: " + ", ".join(k for k, v in red_lines.items() if v)
    elif (obs.get("status") or "") == "PARTIAL":
        decision = "CONTINUE_STABILIZING"
        reason = "observation partially collected; evidence incomplete"
    else:
        decision = "RESUME_DEVELOPMENT"
        reason = "all red lines clear, observation complete"

    return {
        "schema": "moodify.analytics.trend-rules/0.1",
        "status": obs.get("status", "PARTIAL"),
        "red_lines": red_lines,
        "observations": observations,
        "decision": decision,
        "reason": reason,
        "note": "metrics never auto-publish, auto-close tasks, or auto-block work",
    }


def main() -> int:
    result = evaluate()
    target = ROOT / "project_analytics" / "trend_decision.json"
    target.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"trend decision: {target}")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
