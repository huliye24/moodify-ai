"""Three report rhythms (025 Stage C).

- weekly   : trust, state conflicts, workspace, boundary violations, WIP
- stage    : investment, rework, change propagation, first acceptance,
             horizontalization trend
- special  : architecture migration, major features, quality incidents,
             metric anomalies

Each report: JSON data + Markdown summary + run manifest. Deterministic
data body; timestamps in manifest only.
"""

from __future__ import annotations

import datetime
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))


def _utc_now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_observation() -> dict | None:
    obs_dir = ROOT / "project_analytics" / "observations"
    if not obs_dir.exists():
        return None
    files = sorted(obs_dir.glob("obs-*.json"))
    if not files:
        return None
    return json.loads(files[-1].read_text(encoding="utf-8"))


def _load_contracts() -> dict:
    return json.loads((ROOT / "project_analytics" / "metric_contracts.json").read_text(encoding="utf-8"))


def weekly_report() -> dict:
    obs = _load_observation()
    if obs is None:
        return {"schema": "moodify.analytics.weekly/0.1", "status": "NOT_MEASURED",
                "reason": "no observation snapshot"}
    m = obs.get("metrics", {})
    return {
        "schema": "moodify.analytics.weekly/0.1",
        "status": obs.get("status", "PARTIAL"),
        "test_collection_errors": m.get("test_collection", {}).get("errors", "NOT_MEASURED"),
        "test_collected": m.get("test_collection", {}).get("collected", "NOT_MEASURED"),
        "task_state_conflicts": m.get("task_state_conflicts", "NOT_MEASURED"),
        "task_states": m.get("task_states", {}),
        "workspace_unknown": m.get("workspace_unknown_count", "NOT_MEASURED"),
        "workspace_counts": m.get("workspace_counts", {}),
        "enclosure_violations": m.get("enclosure", {}).get("violations", "NOT_MEASURED"),
        "enclosure_debt": m.get("enclosure", {}).get("baseline_debt", "NOT_MEASURED"),
        "in_progress": sum(1 for s, n in m.get("task_states", {}).items() if s in ("IN_PROGRESS", "REWORK")),
        "red_lines": {
            "test_collection_errors": m.get("test_collection", {}).get("errors", 1) > 0,
            "task_state_conflicts": m.get("task_state_conflicts", 1) > 0,
            "enclosure_violations": m.get("enclosure", {}).get("violations", 1) > 0,
        },
    }


def stage_report() -> dict:
    obs = _load_observation()
    if obs is None:
        return {"schema": "moodify.analytics.stage/0.1", "status": "NOT_MEASURED",
                "reason": "no observation snapshot"}
    m = obs.get("metrics", {})
    states = m.get("task_states", {})
    accepted = states.get("ACCEPTED", 0)
    started = sum(v for k, v in states.items() if k != "PLANNED")
    budget = m.get("architecture_budget", {})
    return {
        "schema": "moodify.analytics.stage/0.1",
        "status": obs.get("status", "PARTIAL"),
        "accepted_tasks": accepted,
        "started_tasks": started,
        "accepted_share_pct": round(100 * accepted / started, 1) if started else None,
        "first_acceptance_rate_pct": "NOT_MEASURED",  # needs ledger rework-tracking (023)
        "rework_drag_pct": "NOT_MEASURED",  # needs task investment records
        "core_change_concentration_pct": m.get("git_concentration", {}).get("core_share_pct"),
        "change_propagation_scope": "NOT_MEASURED",  # needs task->commit mapping
        "cross_area_edges": budget.get("cross_area_edges"),
        "cycles": budget.get("cycles"),
        "horizontalization_judgment": "EVIDENCE_INSUFFICIENT",  # needs 3+ stage windows
    }


def special_report(trigger: str) -> dict:
    obs = _load_observation()
    m = obs.get("metrics", {}) if obs else {}
    return {
        "schema": "moodify.analytics.special/0.1",
        "trigger": trigger,
        "generated_at": _utc_now(),
        "snapshot": {
            "test_collection": m.get("test_collection"),
            "enclosure": m.get("enclosure"),
            "task_states": m.get("task_states"),
        },
        "recommended_action": "investigate and record root cause in FAILURE_LEDGER",
    }


def _markdown(report: dict, kind: str) -> str:
    lines = [f"# Moodify {kind} report", "", f"generated: {_utc_now()}", ""]
    for key, value in report.items():
        if key in ("schema",):
            continue
        lines.append(f"- **{key}**: {value}")
    return "\n".join(lines)


def main() -> int:
    kind = sys.argv[1] if len(sys.argv) > 1 else "weekly"
    if kind == "weekly":
        report = weekly_report()
    elif kind == "stage":
        report = stage_report()
    elif kind == "special":
        trigger = sys.argv[2] if len(sys.argv) > 2 else "manual"
        report = special_report(trigger)
    else:
        print(f"ERROR: unknown report {kind!r}; valid: weekly | stage | special")
        return 2

    stamp = _utc_now().replace(":", "").replace("-", "")
    out_dir = ROOT / "project_analytics" / "reports" / kind
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / f"{kind}_{stamp}.json"
    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    md_path = out_dir / f"{kind}_{stamp}.md"
    md_path.write_text(_markdown(report, kind), encoding="utf-8")
    manifest = {
        "schema": "moodify.analytics.report-manifest/0.1",
        "kind": kind,
        "stamp": stamp,
        "json": str(json_path),
        "markdown": str(md_path),
    }
    manifest_path = out_dir / f"{kind}_{stamp}.manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"report: {json_path}")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
