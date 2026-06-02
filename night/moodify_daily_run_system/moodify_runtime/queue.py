from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Set

from .config import RuntimeConfig
from .registry import load_registry
from .utils import append_jsonl, atomic_write_jsonl, read_jsonl, utc_now_iso


def load_queue(cfg: RuntimeConfig) -> List[Dict[str, Any]]:
    return read_jsonl(cfg.queue_path)


def existing_task_keys(queue_rows: List[Dict[str, Any]]) -> Set[str]:
    return {task_key(r.get("sample_id", ""), r.get("preset", "")) for r in queue_rows}


def task_key(sample_id: str, preset: str) -> str:
    return f"{sample_id}::{preset}"


def plan_queue(
    cfg: RuntimeConfig,
    presets: Optional[List[str]] = None,
    max_new_tasks: int = 0,
    only_status: str = "active",
    priority: int = 5,
    reason: str = "daily_run",
) -> Dict[str, Any]:
    cfg = cfg.resolved()
    registry = [r for r in load_registry(cfg) if r.get("status", "active") == only_status]
    queue_rows = load_queue(cfg)
    seen = existing_task_keys(queue_rows)
    presets = presets or cfg.presets

    added = 0
    tasks: List[Dict[str, Any]] = []
    for sample in registry:
        for preset in presets:
            key = task_key(sample["sample_id"], preset)
            if key in seen:
                continue
            task = {
                "task_id": f"TASK_{sample['sample_id']}_{preset}".replace("-", "_"),
                "sample_id": sample["sample_id"],
                "input_path": sample["path"],
                "preset": preset,
                "status": "pending",
                "priority": priority,
                "reason": reason,
                "created_at": utc_now_iso(),
                "started_at": None,
                "finished_at": None,
                "run_id": None,
                "output_dir": None,
                "attempts": 0,
                "last_error": None,
            }
            append_jsonl(cfg.queue_path, task)
            tasks.append(task)
            added += 1
            if max_new_tasks and added >= max_new_tasks:
                return {"queue_path": str(cfg.queue_path), "added": added, "tasks": tasks}

    return {"queue_path": str(cfg.queue_path), "added": added, "tasks": tasks}


def rewrite_queue(cfg: RuntimeConfig, rows: List[Dict[str, Any]]) -> None:
    atomic_write_jsonl(cfg.queue_path, rows)


def update_task_status(
    cfg: RuntimeConfig,
    task_id: str,
    status: str,
    updates: Optional[Dict[str, Any]] = None,
) -> None:
    rows = load_queue(cfg)
    updates = updates or {}
    for row in rows:
        if row.get("task_id") == task_id:
            row["status"] = status
            row.update(updates)
            break
    rewrite_queue(cfg, rows)
