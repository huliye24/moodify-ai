"""Runtime Reliability Recommender (Loop A).

MHP-817: Implement Runtime Reliability Recommender.

Analyzes fatal errors, task failures, and missing artifacts to produce
runtime fix recommendations.
"""

from __future__ import annotations

from typing import Any

from moodify_runtime.recommenders.base import Recommendation


# Known fatal error patterns and their recommended fixes
FATAL_PATTERNS: list[tuple[str, str, str]] = [
    ("FileNotFoundError", "daily_run.log",
     "Add daily_run.log existence check at phase start; emit log or skip with warning",
     ),
    ("FileNotFoundError", "",
     "Add artifact existence pre-check; ensure all required files are created before report phase",
     ),
    ("PermissionError", "",
     "Check file permissions on output directory; ensure runtime user has write access",
     ),
    ("MemoryError", "",
     "Reduce task batch size or increase memory limits; check for memory leaks",
     ),
    ("TimeoutError", "",
     "Increase timeout or add intermediate checkpoints for long-running tasks",
     ),
]


class RuntimeReliabilityRecommender:
    """Produce runtime fix recommendations from fatal errors and task failures.

    Usage:
        rec = RuntimeReliabilityRecommender()
        recommendations = rec.analyze(runtime_signal, tasks)
    """

    def analyze(
        self,
        runtime_signal: dict[str, Any],
        tasks: list[dict[str, Any]] | None = None,
    ) -> list[Recommendation]:
        """Analyze runtime signals and return fix recommendations."""
        recommendations: list[Recommendation] = []
        run_id = runtime_signal.get("run_id", runtime_signal.get("source_run", ""))

        # Fatal error → always high severity
        fatal = runtime_signal.get("fatal_error")
        if fatal:
            rec = self._analyze_fatal_error(fatal, run_id)
            recommendations.append(rec)

        # Task failures → medium severity
        failed = runtime_signal.get("failed", 0)
        if failed > 0 and tasks:
            rec = self._analyze_failures(failed, tasks, run_id)
            if rec:
                recommendations.append(rec)

        return recommendations

    def _analyze_fatal_error(self, fatal: str, run_id: str) -> Recommendation:
        # Match known patterns
        matched_action = None
        matched_reason = ""
        for pattern, keyword, action in FATAL_PATTERNS:
            if pattern in fatal and keyword in fatal:
                matched_action = action
                matched_reason = f"Matched pattern: {pattern} with '{keyword}'"
                break

        if not matched_action:
            # Fallback: classify by error type
            if "FileNotFoundError" in fatal:
                matched_action = "Add missing file check; ensure artifact generation has no gaps"
            elif "PermissionError" in fatal:
                matched_action = "Fix file permissions on the affected path"
            else:
                matched_action = "Investigate fatal error root cause; add guard before next run"

        reason = f"Fatal error detected: {fatal[:120]}"
        if matched_reason:
            reason = f"{matched_reason}. {fatal[:100]}"

        return Recommendation(
            task_id=f"{run_id}:runtime",
            loop="runtime_reliability",
            severity="high",
            reason=reason[:180],
            next_action=matched_action[:220],
            needs_human_review=False,
            source_signal="fatal_error",
            owner_subsystem="runtime_runner",
            estimated_effort="S",
        )

    def _analyze_failures(
        self,
        failed_count: int,
        tasks: list[dict[str, Any]],
        run_id: str,
    ) -> Recommendation | None:
        failed_tasks = [t for t in tasks if t.get("status") == "failed"]
        if not failed_tasks:
            return None

        # Group failures by preset
        fail_presets: dict[str, int] = {}
        for t in failed_tasks:
            preset = t.get("preset", "unknown")
            fail_presets[preset] = fail_presets.get(preset, 0) + 1

        worst = max(fail_presets, key=fail_presets.get)
        reason = (
            f"{failed_count} task(s) failed. "
            f"Most affected preset: {worst} ({fail_presets[worst]} failures)."
        )
        action = (
            f"Review failure logs for preset '{worst}'. "
            f"Check command template, input file integrity, and resource limits."
        )

        return Recommendation(
            task_id=f"{run_id}:runtime:failures",
            loop="runtime_reliability",
            severity="medium",
            reason=reason[:180],
            next_action=action[:220],
            needs_human_review=False,
            source_signal="task_failures",
            owner_subsystem="runtime_runner",
            estimated_effort="M",
        )
