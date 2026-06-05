"""Collect runtime execution signals from summary.json.

MHP-810: Implement Summary Collector.
Reads the runner's summary.json and extracts runtime reliability signals,
per-task scoring disagreements, and craft/preset penalty flags.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any

from moodify_runtime.utils import utc_now_iso


@dataclass
class RuntimeSignal:
    """Loop A: Runtime reliability summary."""
    success: int = 0
    failed: int = 0
    total_selected: int = 0
    dry_run: bool = False
    fatal_error: str | None = None
    elapsed_seconds: float = 0.0
    missing_artifacts: list[str] = field(default_factory=list)

    @property
    def success_rate(self) -> float:
        total = self.success + self.failed
        if total == 0:
            return 1.0
        return self.success / total

    @property
    def has_fatal(self) -> bool:
        return bool(self.fatal_error)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ScoringSignal:
    """Loop B: Scoring calibration aggregate."""
    task_count: int = 0
    disagreement_count: int = 0
    disagreeing_presets: list[str] = field(default_factory=list)
    max_abs_disagreement: float = 0.0

    @property
    def agreement_rate(self) -> float:
        if self.task_count == 0:
            return 1.0
        return 1.0 - self.disagreement_count / self.task_count

    def to_dict(self) -> dict[str, Any]:
        return {
            "task_count": self.task_count,
            "disagreement_count": self.disagreement_count,
            "agreement_rate": self.agreement_rate,
            "disagreeing_presets": sorted(self.disagreeing_presets),
            "max_abs_disagreement": self.max_abs_disagreement,
        }


@dataclass
class CraftSignal:
    """Loop C: Craft/preset penalty flags aggregate."""
    task_count: int = 0
    flagged_count: int = 0
    flag_types: list[str] = field(default_factory=list)
    flagged_presets: list[str] = field(default_factory=list)
    preset_delta_stats: dict[str, dict[str, Any]] = field(default_factory=dict)

    @property
    def flag_rate(self) -> float:
        if self.task_count == 0:
            return 0.0
        return self.flagged_count / self.task_count

    def to_dict(self) -> dict[str, Any]:
        return {
            "task_count": self.task_count,
            "flagged_count": self.flagged_count,
            "flag_rate": self.flag_rate,
            "flag_types": sorted(self.flag_types),
            "flagged_presets": sorted(self.flagged_presets),
            "preset_delta_stats": self.preset_delta_stats,
        }


@dataclass
class TaskDetail:
    """Per-task detail record — the atomic unit for DeepSeek worker micro-tasks."""
    task_id: str = ""
    sample_id: str = ""
    preset: str = ""
    status: str = "pending"
    return_code: int | None = None
    elapsed_seconds: float | None = None
    pseudo_mrs_before: float | None = None
    pseudo_mrs_after: float | None = None
    pseudo_delta_mrs: float | None = None
    mrs_open_v031_before: float | None = None
    mrs_open_v031_after: float | None = None
    delta_mrs_open_v031: float | None = None
    mrs_open_flags: str = ""
    score_direction_disagreement: bool | None = None
    recommended_loop: str = "operator_report"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class SummaryCollector:
    """Collect optimization signals from a runtime summary.json.

    Usage:
        collector = SummaryCollector(summary_path)
        record = collector.collect()
        # record contains runtime, scoring, craft signals + per-task details
    """

    def __init__(self, summary_path: Path, source_manifest: Path | None = None):
        self._path = Path(summary_path)
        self._manifest_path = source_manifest
        self._raw: dict[str, Any] = {}

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def collect(self) -> dict[str, Any]:
        """Read summary.json and return the full NightMetricRecord dict."""
        with self._path.open("r", encoding="utf-8") as f:
            self._raw = json.load(f)

        tasks = self._raw.get("tasks", [])
        task_details = [self._build_task_detail(t) for t in tasks]

        runtime = self._collect_runtime()
        scoring = self._collect_scoring(tasks)
        craft = self._collect_craft(tasks)

        return {
            "run_id": self._raw.get("run_id", ""),
            "started_at": self._raw.get("started_at", ""),
            "collected_at": utc_now_iso(),
            "source_artifacts": {
                "summary_json": str(self._path.resolve()),
                "manifest_csv": str(self._manifest_path.resolve()) if self._manifest_path else None,
            },
            "runtime": runtime.to_dict(),
            "scoring": scoring.to_dict(),
            "craft": craft.to_dict(),
            "tasks": [t.to_dict() for t in task_details],
        }

    # ------------------------------------------------------------------
    # Per-signal extractors
    # ------------------------------------------------------------------

    def _collect_runtime(self) -> RuntimeSignal:
        fatal = self._raw.get("fatal_error")
        # Determine missing artifacts from the error text if possible.
        missing: list[str] = []
        if fatal and "No such file or directory" in str(fatal):
            import re
            m = re.search(r"'([^']+)'", str(fatal))
            if m:
                missing.append(m.group(1))

        return RuntimeSignal(
            success=self._raw.get("success", 0),
            failed=self._raw.get("failed", 0),
            total_selected=self._raw.get("total_selected", 0),
            dry_run=self._raw.get("dry_run", False),
            fatal_error=fatal,
            elapsed_seconds=0.0,  # summary.json doesn't include this directly
            missing_artifacts=missing,
        )

    def _collect_scoring(self, tasks: list[dict[str, Any]]) -> ScoringSignal:
        disagreements: list[dict[str, Any]] = []
        max_abs = 0.0
        for t in tasks:
            pseudo = t.get("pseudo_delta_mrs")
            open_d = t.get("delta_mrs_open_v031")
            if pseudo is not None and open_d is not None:
                if (pseudo >= 0) != (open_d >= 0):
                    abs_d = abs(pseudo - open_d)
                    max_abs = max(max_abs, abs_d)
                    disagreements.append(t)

        return ScoringSignal(
            task_count=len(tasks),
            disagreement_count=len(disagreements),
            disagreeing_presets=list({t.get("preset", "") for t in disagreements}),
            max_abs_disagreement=max_abs,
        )

    def _collect_craft(self, tasks: list[dict[str, Any]]) -> CraftSignal:
        flagged = [t for t in tasks if t.get("mrs_open_flags")]
        flag_types_set: set[str] = set()
        flagged_presets_set: set[str] = set()
        for t in flagged:
            flags = t.get("mrs_open_flags", "")
            if flags:
                flag_types_set.add(flags)
            preset = t.get("preset", "")
            if preset:
                flagged_presets_set.add(preset)

        # Per-preset delta statistics
        preset_groups: dict[str, list[float]] = {}
        for t in tasks:
            preset = t.get("preset", "")
            delta = t.get("delta_mrs_open_v031")
            if preset and delta is not None:
                preset_groups.setdefault(preset, []).append(delta)

        preset_stats: dict[str, dict[str, Any]] = {}
        for preset, deltas in preset_groups.items():
            f_count = sum(1 for f in flagged if f.get("preset") == preset)
            preset_stats[preset] = {
                "mean_delta": round(sum(deltas) / len(deltas), 4) if deltas else 0,
                "min_delta": round(min(deltas), 4) if deltas else 0,
                "max_delta": round(max(deltas), 4) if deltas else 0,
                "count": len(deltas),
                "flagged": f_count,
            }

        return CraftSignal(
            task_count=len(tasks),
            flagged_count=len(flagged),
            flag_types=sorted(flag_types_set),
            flagged_presets=sorted(flagged_presets_set),
            preset_delta_stats=preset_stats,
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _build_task_detail(task: dict[str, Any]) -> TaskDetail:
        pseudo = task.get("pseudo_delta_mrs")
        open_d = task.get("delta_mrs_open_v031")
        disagreement = None
        if pseudo is not None and open_d is not None:
            disagreement = (pseudo >= 0) != (open_d >= 0)

        # Determine recommended loop for this task
        flags = task.get("mrs_open_flags", "")
        if disagreement:
            loop = "scoring_calibration"
        elif flags:
            loop = "craft_preset_selection"
        else:
            loop = "operator_report"

        return TaskDetail(
            task_id=task.get("task_id", ""),
            sample_id=task.get("sample_id", ""),
            preset=task.get("preset", ""),
            status=task.get("status", "pending"),
            return_code=task.get("return_code"),
            elapsed_seconds=float(task["elapsed_seconds"]) if task.get("elapsed_seconds") else None,
            pseudo_mrs_before=task.get("pseudo_mrs_before"),
            pseudo_mrs_after=task.get("pseudo_mrs_after"),
            pseudo_delta_mrs=pseudo,
            mrs_open_v031_before=task.get("mrs_open_v031_before"),
            mrs_open_v031_after=task.get("mrs_open_v031_after"),
            delta_mrs_open_v031=open_d,
            mrs_open_flags=flags,
            score_direction_disagreement=disagreement,
            recommended_loop=loop,
        )
