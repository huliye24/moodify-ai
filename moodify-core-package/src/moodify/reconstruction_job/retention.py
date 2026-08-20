"""Retention policy enforcement for reconstruction job workspaces (MFY-CR-P08).

Six storage classes are kept separate (SOURCE / TMP / STEMS / CANDIDATES /
RESULT / EVIDENCE) with independent TTLs. TTLs are engineering defaults and do
not by themselves constitute legal compliance.
"""

from __future__ import annotations

import shutil
from datetime import datetime, timezone
from pathlib import Path

from .contract import RetentionPolicy

_WORKSPACE_DIRS = {
    "input": "source",
    "tmp": "tmp",
    "stems": "stems",
    "candidates": "candidates",
    "result": "result",
    "case": "evidence",
}

_CLASS_TTL = {
    "source": "source_ttl_s",
    "tmp": "tmp_ttl_s",
    "stems": "stems_ttl_s",
    "candidates": "candidates_ttl_s",
    "result": "result_ttl_s",
    "evidence": "evidence_ttl_s",
}


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _expired(ttl_s: int | None, mtime: datetime) -> bool:
    if ttl_s is None:
        return False  # retain indefinitely
    return (_now() - mtime).total_seconds() >= ttl_s


def cleanup_workspace(workspace: Path, policy: RetentionPolicy) -> dict[str, int]:
    """Delete workspace dirs whose TTL elapsed; returns {storage_class: count}."""
    removed: dict[str, int] = {}
    if not workspace.is_dir():
        return removed
    for dirname, storage_class in _WORKSPACE_DIRS.items():
        target = workspace / dirname
        if not target.is_dir():
            continue
        ttl = getattr(policy, _CLASS_TTL[storage_class])
        mtime = datetime.fromtimestamp(target.stat().st_mtime, tz=timezone.utc)
        if _expired(ttl, mtime):
            shutil.rmtree(target, ignore_errors=True)
            removed[storage_class] = removed.get(storage_class, 0) + 1
    return removed


def cleanup_tmp(workspace: Path) -> bool:
    """Immediately remove the temporary scratch dir of a workspace."""
    target = workspace / "tmp"
    if target.is_dir():
        shutil.rmtree(target, ignore_errors=True)
        return True
    return False


def sweep_workspaces(
    workspace_root: Path,
    policy: RetentionPolicy,
    active_job_ids: set[str] | None = None,
) -> dict[str, dict[str, int]]:
    """Apply retention policy across every job workspace.

    Workspaces of currently leased jobs are skipped so a sweep can never
    delete scratch data of work in progress.
    """
    root = Path(workspace_root)
    active = active_job_ids or set()
    result: dict[str, dict[str, int]] = {}
    if not root.is_dir():
        return result
    for workspace in root.iterdir():
        if workspace.is_dir() and workspace.name not in active:
            result[workspace.name] = cleanup_workspace(workspace, policy)
    return result
