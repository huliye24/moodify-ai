"""Read-only observability collector (025 Stage B).

Collects metrics by reusing the 022/023/024 tooling — never re-implements
their logic. Deterministic data body (same input -> same values); dynamic
metadata (timestamps, run id) is separated. Collector failures are marked
PARTIAL, never silently reported as complete.
"""

from __future__ import annotations

import datetime
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GIT = r"C:\Program Files\Git\cmd\git.exe"
sys.path.insert(0, str(ROOT))


def _utc_now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _run(cmd: list[str], cwd: Path = ROOT) -> tuple[int, str]:
    proc = subprocess.run(cmd, capture_output=True, cwd=cwd, text=True)
    return proc.returncode, (proc.stdout or proc.stderr)


class Collector:
    """Deterministic metric collector with PARTIAL failure semantics."""

    def __init__(self) -> None:
        self.metrics: dict = {}
        self.partial: list[dict] = []

    def collect(self, name: str, fn, **kwargs) -> None:
        try:
            value = fn(**kwargs)
            self.metrics[name] = value
        except Exception as exc:
            self.metrics[name] = None
            self.partial.append({"metric": name, "error": str(exc)})

    # ── 023: task ledger ────────────────────────────────────────────────
    def _task_conflicts(self) -> int:
        sys.path.insert(0, str(ROOT))
        from tools.project_governance.ledger import load_ledger
        from tools.project_governance.views import build_conflict_table

        ledger = load_ledger(ROOT / "project_analytics" / "task_ledger.jsonl")
        return len(build_conflict_table(ledger))

    def _task_states(self) -> dict:
        from tools.project_governance.ledger import load_ledger

        ledger = load_ledger(ROOT / "project_analytics" / "task_ledger.jsonl")
        states: dict[str, int] = {}
        for task_id in ledger.all_task_ids():
            state, _ = ledger.state_of(task_id)
            states[state] = states.get(state, 0) + 1
        return states

    # ── 023: workspace inventory ────────────────────────────────────────
    def _workspace_unknown(self) -> int:
        data = json.loads((ROOT / "project_analytics" / "workspace_inventory.json").read_text(encoding="utf-8"))
        return sum(1 for e in data["entries"] if e["bucket"] == "UNKNOWN")

    def _workspace_counts(self) -> dict:
        data = json.loads((ROOT / "project_analytics" / "workspace_inventory.json").read_text(encoding="utf-8"))
        return {
            "tracked": data["summary"]["tracked"],
            "untracked": data["summary"]["untracked"],
            "entries": data["summary"]["total_entries"],
        }

    # ── 024: enclosure ──────────────────────────────────────────────────
    def _enclosure(self) -> dict:
        from tools.architecture.enforcer import check_enclosure

        result = check_enclosure()
        return {
            "violations": result["summary"]["violations"],
            "baseline_debt": result["summary"]["baseline_debt"],
        }

    def _budget(self) -> dict:
        from tools.architecture.budget import collect_budget

        budget = collect_budget()
        return {
            "cross_area_edges": budget["cross_area_edges"],
            "cycles": len(budget["cycles"]),
            "core_share_pct": budget["git"]["core_share_pct"],
            "oversized_top5": [m["module"] for m in budget["oversized_modules"][:5]],
        }

    # ── 022: test gates (collect layer only for daily cadence) ──────────
    def _test_collection(self) -> dict:
        import re

        code, out = _run([sys.executable, "-m", "pytest", "--collect-only", "-q"],
                         cwd=ROOT / "moodify-core-package")
        m = re.search(r"(\d+)\s+tests? collected", out)
        collected = int(m.group(1)) if m else 0
        errors = 0
        for line in out.splitlines():
            if "error" in line.lower() and "collect" in line.lower():
                errors += 1
            if re.search(r"(\d+) errors?", line):
                errors = int(re.search(r"(\d+) errors?", line).group(1))
        return {"exit_code": code, "errors": errors, "collected": collected}

    # ── git concentration ───────────────────────────────────────────────
    def _git_concentration(self) -> dict:
        proc = subprocess.run(
            [GIT, "-C", str(ROOT), "diff", "--numstat", "HEAD"],
            capture_output=True, text=True,
        )
        core_prefixes = ("moodify-core-package/src/", "moodify_runtime/", "workers/")
        total = core = 0
        for line in proc.stdout.splitlines():
            parts = line.split("\t")
            if len(parts) < 3:
                continue
            try:
                add = int(parts[0]) if parts[0] != "-" else 0
                remove = int(parts[1]) if parts[1] != "-" else 0
            except ValueError:
                continue
            total += add + remove
            if parts[2].startswith(core_prefixes):
                core += add + remove
        return {"core_share_pct": round(100 * core / total, 1) if total else 0, "total": total, "core": core}


def collect_all() -> dict:
    c = Collector()
    c.collect("task_state_conflicts", c._task_conflicts)
    c.collect("task_states", c._task_states)
    c.collect("workspace_unknown_count", c._workspace_unknown)
    c.collect("workspace_counts", c._workspace_counts)
    c.collect("enclosure", c._enclosure)
    c.collect("architecture_budget", c._budget)
    c.collect("test_collection", c._test_collection)
    c.collect("git_concentration", c._git_concentration)

    run_id = f"obs-{_utc_now().replace(':', '').replace('-', '')}"
    return {
        "schema": "moodify.analytics.observation/0.1",
        "run_id": run_id,
        "collected_at": _utc_now(),
        "status": "complete" if not c.partial else "PARTIAL",
        "partial": c.partial,
        "metrics": c.metrics,
    }


def main() -> int:
    observation = collect_all()
    target = ROOT / "project_analytics" / "observations" / f"{observation['run_id']}.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(observation, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"observation: {target}")
    print(f"  status: {observation['status']}")
    for name, value in observation["metrics"].items():
        print(f"  {name}: {value}")
    if observation["partial"]:
        for p in observation["partial"]:
            print(f"  PARTIAL: {p['metric']}: {p['error'][:80]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
