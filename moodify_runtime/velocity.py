"""MHP-377/379/383-386: Engineering Velocity Infrastructure — worktree isolation,
executable MHP queue, auto report/gate, failure replay library.

Provides the core acceleration modules for X-AEVF on a single server.
"""

from __future__ import annotations

import json
import subprocess
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from .utils import utc_now_iso, append_jsonl, read_jsonl, atomic_write_jsonl

PROJECT_ROOT = Path(__file__).resolve().parent.parent


# ═══════════════════════════════════════════════════════════════════════
# MHP-377: Worktree Isolation Manager
# ═══════════════════════════════════════════════════════════════════════


@dataclass
class IsolatedWorktree:
    """A git worktree isolated environment for parallel agent work."""
    wt_id: str
    branch_name: str
    base_ref: str = "HEAD"
    path: str = ""
    task_label: str = ""
    created_at: str = field(default_factory=utc_now_iso)
    status: str = "active"   # active, merged, abandoned

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def create_worktree(
    task_label: str,
    base_ref: str = "HEAD",
    worktree_root: Optional[Path] = None,
) -> IsolatedWorktree:
    """Create an isolated git worktree for a parallel agent task.

    Returns IsolatedWorktree with the branch name and path.
    """
    root = worktree_root or (PROJECT_ROOT / ".claude" / "worktrees")
    root.mkdir(parents=True, exist_ok=True)

    wt_id = f"WT_{uuid.uuid4().hex[:8].upper()}"
    branch = f"auto/wt-{wt_id}-{task_label[:20].replace(' ', '-').lower()}"
    wt_path = root / wt_id

    try:
        subprocess.run(
            ["git", "worktree", "add", str(wt_path), base_ref],
            capture_output=True, text=True, timeout=30,
            cwd=str(PROJECT_ROOT),
        )
        subprocess.run(
            ["git", "checkout", "-b", branch],
            capture_output=True, text=True, timeout=10,
            cwd=str(wt_path),
        )
    except (subprocess.TimeoutExpired, subprocess.CalledProcessError) as e:
        raise RuntimeError(f"Worktree creation failed: {e}")

    return IsolatedWorktree(
        wt_id=wt_id,
        branch_name=branch,
        base_ref=base_ref,
        path=str(wt_path),
        task_label=task_label,
    )


def list_worktrees(project_root: Optional[Path] = None) -> List[Dict[str, Any]]:
    """List existing git worktrees."""
    try:
        r = subprocess.run(
            ["git", "worktree", "list", "--porcelain"],
            capture_output=True, text=True, timeout=10,
            cwd=str(project_root or PROJECT_ROOT),
        )
        worktrees = []
        current = {}
        for line in r.stdout.splitlines():
            if line.startswith("worktree "):
                if current:
                    worktrees.append(current)
                current = {"path": line.split("worktree ", 1)[1]}
            elif line.startswith("HEAD ") or line.startswith("branch "):
                key, val = line.split(" ", 1)
                current[key] = val.strip("refs/heads/")
        if current:
            worktrees.append(current)
        return worktrees
    except Exception:
        return []


def remove_worktree(wt_path: str, force: bool = False) -> bool:
    """Remove a git worktree."""
    try:
        cmd = ["git", "worktree", "remove"]
        if force:
            cmd.append("--force")
        cmd.append(wt_path)
        subprocess.run(cmd, capture_output=True, text=True, timeout=30, cwd=str(PROJECT_ROOT))
        return True
    except Exception:
        return False


# ═══════════════════════════════════════════════════════════════════════
# MHP-379: Executable MHP Queue
# ═══════════════════════════════════════════════════════════════════════


@dataclass
class ExecutableMHP:
    """An MHP task converted into an executable queue item."""
    mhp_id: str
    plan_path: str
    status: str = "queued"     # queued, running, done, failed, skipped
    assigned_worktree: str = ""
    started_at: str = ""
    finished_at: str = ""
    exit_code: int = -1
    output_summary: str = ""
    error: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _exec_queue_path() -> Path:
    return PROJECT_ROOT / "outputs" / "velocity" / "exec_queue.jsonl"


def enqueue_mhp(mhp_id: str, plan_path: str) -> Dict[str, Any]:
    """Add an MHP to the executable queue."""
    item = ExecutableMHP(mhp_id=mhp_id, plan_path=plan_path)
    append_jsonl(_exec_queue_path(), item.to_dict())
    return item.to_dict()


def dequeue_next() -> Optional[ExecutableMHP]:
    """Get the next queued MHP. Returns None if queue is empty."""
    rows = read_jsonl(_exec_queue_path())
    for r in rows:
        if r.get("status") == "queued":
            return ExecutableMHP(**{k: v for k, v in r.items() if k in ExecutableMHP.__dataclass_fields__})
    return None


def mark_mhp_done(mhp_id: str, exit_code: int = 0, summary: str = "", error: str = "") -> None:
    """Mark an MHP as completed in the queue."""
    rows = read_jsonl(_exec_queue_path())
    for r in rows:
        if r.get("mhp_id") == mhp_id:
            r["status"] = "done" if exit_code == 0 else "failed"
            r["exit_code"] = exit_code
            r["output_summary"] = summary[:500]
            r["error"] = error[:500]
            r["finished_at"] = utc_now_iso()
    _exec_queue_path().write_text(
        "\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + "\n"
    )


def list_exec_queue() -> List[Dict[str, Any]]:
    return read_jsonl(_exec_queue_path())


# ═══════════════════════════════════════════════════════════════════════
# MHP-383/384/385: Auto Reporter — summary, gate, next-action
# ═══════════════════════════════════════════════════════════════════════


def auto_summary(output_dir: Path) -> Dict[str, Any]:
    """Generate automatic execution summary from tidal records and events."""
    events_path = output_dir / "tidal_events.jsonl"
    records_path = output_dir / "tidal_records.jsonl"

    cycles = 0
    tasks_done = 0
    tasks_failed = 0
    errors = []

    if records_path.exists():
        for r in read_jsonl(records_path):
            cycles += 1
            tasks_done += r.get("tasks_succeeded", 0)
            tasks_failed += r.get("tasks_failed", 0)
            if r.get("errors"):
                errors.extend(r["errors"])

    return {
        "generated_at": utc_now_iso(),
        "total_cycles": cycles,
        "tasks_succeeded": tasks_done,
        "tasks_failed": tasks_failed,
        "error_count": len(errors),
        "last_errors": errors[-5:],
        "health": "healthy" if tasks_failed == 0 else "degraded",
    }


def auto_gate_decision(summary: Dict[str, Any]) -> Dict[str, Any]:
    """Automatic gate decision based on execution summary."""
    total = summary["tasks_succeeded"] + summary["tasks_failed"]
    success_rate = summary["tasks_succeeded"] / max(total, 1)

    if success_rate >= 0.95 and summary["error_count"] == 0:
        decision = "ADOPT"
    elif success_rate >= 0.80:
        decision = "HOLD"
    else:
        decision = "REBUILD"

    return {
        "decision": decision,
        "success_rate": round(success_rate, 4),
        "total_tasks": total,
        "rationale": f"Success rate {success_rate:.1%}, {summary['error_count']} errors → {decision}",
        "generated_at": utc_now_iso(),
    }


def auto_next_action(gate: Dict[str, Any]) -> str:
    """Generate next action recommendation from gate decision."""
    actions = {
        "ADOPT": "进入下一 NEM。检查 PROJECT_ROADMAP.md 获取下一个入口。",
        "HOLD": "审查失败案例。运行 bash scripts/tidal_status.sh 查看详情。",
        "REBUILD": "回退到 Build NEM。检查 failure_log.jsonl 修复 P0 问题。",
    }
    return actions.get(gate["decision"], "Manual review required.")


# ═══════════════════════════════════════════════════════════════════════
# MHP-386: Failure Replay Library
# ═══════════════════════════════════════════════════════════════════════


@dataclass
class FailureReplayCase:
    """A cataloged failure case for faster diagnosis."""
    case_id: str
    error_signature: str     # hash or key pattern of the error
    error_type: str          # classified failure type
    root_cause: str = ""
    reproduction_steps: str = ""
    fix_applied: str = ""
    occurred_at: str = field(default_factory=utc_now_iso)
    occurred_count: int = 1

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _replay_lib_path() -> Path:
    return PROJECT_ROOT / "data" / "failure_replay_library.jsonl"


def catalog_failure(
    error_signature: str,
    error_type: str,
    root_cause: str = "",
    reproduction: str = "",
    fix: str = "",
) -> Dict[str, Any]:
    """Add a failure to the replay library. Deduplicates by signature."""
    path = _replay_lib_path()
    existing = read_jsonl(path)

    # Check if already cataloged
    for r in existing:
        if r.get("error_signature") == error_signature:
            r["occurred_count"] = r.get("occurred_count", 0) + 1
            atomic_write_jsonl(path, existing)
            return r

    case = FailureReplayCase(
        case_id=f"FR_{uuid.uuid4().hex[:8].upper()}",
        error_signature=error_signature,
        error_type=error_type,
        root_cause=root_cause,
        reproduction_steps=reproduction,
        fix_applied=fix,
    )
    append_jsonl(path, case.to_dict())
    return case.to_dict()


def lookup_failure(error_signature: str) -> Optional[Dict[str, Any]]:
    """Look up a failure by signature. Returns None if not found."""
    for r in read_jsonl(_replay_lib_path()):
        if r.get("error_signature") == error_signature:
            return r
    return None


# ═══════════════════════════════════════════════════════════════════════
# MHP-391: Velocity Dashboard Data Writer
# ═══════════════════════════════════════════════════════════════════════


def write_velocity_metrics(
    output_dir: Path,
    cycles_completed: int = 0,
    tasks_per_hour: float = 0.0,
    success_rate: float = 0.0,
    avg_cycle_time_s: float = 0.0,
    friction_events: int = 0,
) -> Dict[str, Any]:
    """Write velocity metrics for the operator dashboard."""
    metrics = {
        "timestamp": utc_now_iso(),
        "cycles_completed": cycles_completed,
        "tasks_per_hour": round(tasks_per_hour, 2),
        "success_rate": round(success_rate, 4),
        "avg_cycle_time_s": round(avg_cycle_time_s, 1),
        "friction_events": friction_events,
        "free_disk_gb": round(
            __import__("shutil").disk_usage(output_dir).free / (1024**3), 1
        ),
    }
    path = output_dir / "velocity_metrics.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    append_jsonl(path, metrics)
    return metrics
