"""Data Loop Runner — wire collectors + recommenders into a single pipeline.

MHP-821: Add Data Loop CLI
MHP-822: Add Data Loop Report Writer

Orchestrates the full nightly optimization loop:
  1. Collect → NightMetricRecord from runtime artifacts
  2. Recommend → RecommendationBundle across all four loops
  3. Report → formatted Markdown + JSON outputs
  4. Writeback → craft memory hooks + MRS calibration proposals (MHP-823/824)

Usage (CLI):
  python3 -m moodify_runtime.cli data-loop run --summary outputs/20260605_000141/summary.json

Usage (API):
  from moodify_runtime.data_loop_runner import DataLoopRunner
  runner = DataLoopRunner(summary_path="outputs/.../summary.json")
  result = runner.run()
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from moodify_runtime.collectors import CollectorPipeline, collect_night_metrics
from moodify_runtime.recommenders import RecommendationEngine
from moodify_runtime.recommenders.base import Recommendation, RecommendationBundle
from moodify_runtime.utils import utc_now_iso


@dataclass
class DataLoopResult:
    """Complete output from a data-loop run."""
    run_id: str
    started_at: str = ""
    finished_at: str = ""
    # Inputs
    source_summary: str = ""
    source_queue: str = ""
    # Outputs
    night_metric_record: dict[str, Any] = field(default_factory=dict)
    recommendation_bundle: dict[str, Any] = field(default_factory=dict)
    # Writeback results
    craft_writeback_count: int = 0
    calibration_writeback_count: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "source_summary": self.source_summary,
            "source_queue": self.source_queue,
            "night_metric_record": self.night_metric_record,
            "recommendation_bundle": self.recommendation_bundle,
            "craft_writeback_count": self.craft_writeback_count,
            "calibration_writeback_count": self.calibration_writeback_count,
        }


class DataLoopRunner:
    """Orchestrate the full data optimization loop pipeline.

    Usage:
        runner = DataLoopRunner(
            summary_path="outputs/20260605_000141/summary.json",
            queue_path="data/tidal_queue.jsonl",
            output_dir="reports/data_loop/",
        )
        result = runner.run()
    """

    def __init__(
        self,
        summary_path: Path | str,
        manifest_path: Path | str | None = None,
        queue_path: Path | str | None = None,
        tidal_events_path: Path | str | None = None,
        tidal_heartbeat_path: Path | str | None = None,
        output_dir: Path | str = "reports/data_loop",
        craft_memory_dir: Path | str | None = None,
    ):
        self._summary_path = Path(summary_path)
        self._manifest_path = Path(manifest_path) if manifest_path else None
        self._queue_path = Path(queue_path) if queue_path else None
        self._tidal_events_path = Path(tidal_events_path) if tidal_events_path else None
        self._tidal_heartbeat_path = Path(tidal_heartbeat_path) if tidal_heartbeat_path else None
        self._output_dir = Path(output_dir)
        self._craft_memory_dir = Path(craft_memory_dir) if craft_memory_dir else None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def run(self, writeback: bool = False) -> DataLoopResult:
        """Execute the full data loop pipeline."""
        run_id = self._infer_run_id()
        started_at = utc_now_iso()

        # Step 1: Collect
        pipeline = CollectorPipeline(
            summary_path=self._summary_path,
            manifest_path=self._manifest_path,
            queue_path=self._queue_path,
            tidal_events_path=self._tidal_events_path,
            tidal_heartbeat_path=self._tidal_heartbeat_path,
        )
        record = pipeline.run()

        # Step 2: Recommend
        engine = RecommendationEngine()
        bundle = engine.run(record)

        # Step 3: Writeback (optional)
        craft_count = 0
        cal_count = 0
        if writeback:
            craft_count = self._writeback_craft(bundle)
            cal_count = self._writeback_calibration(bundle)

        # Step 4: Write outputs
        self._write_outputs(record, bundle)

        result = DataLoopResult(
            run_id=run_id,
            started_at=started_at,
            finished_at=utc_now_iso(),
            source_summary=str(self._summary_path.resolve()),
            source_queue=str(self._queue_path.resolve()) if self._queue_path else "",
            night_metric_record=record,
            recommendation_bundle=bundle.to_dict(),
            craft_writeback_count=craft_count,
            calibration_writeback_count=cal_count,
        )

        return result

    # ------------------------------------------------------------------
    # Output
    # ------------------------------------------------------------------

    def _write_outputs(
        self,
        record: dict[str, Any],
        bundle: RecommendationBundle,
    ) -> None:
        out = self._output_dir
        out.mkdir(parents=True, exist_ok=True)

        # NightMetricRecord
        (out / "night_metric_record.json").write_text(
            json.dumps(record, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

        # Recommendation bundle
        (out / "recommendation_bundle.json").write_text(
            json.dumps(bundle.to_dict(), ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

        # Human-readable report
        report = DataLoopRunner._format_report(record, bundle)
        (out / "data_loop_report.md").write_text(report, encoding="utf-8")

    # ------------------------------------------------------------------
    # Writeback hooks (MHP-823, MHP-824)
    # ------------------------------------------------------------------

    def _writeback_craft(self, bundle: RecommendationBundle) -> int:
        """Write craft/preset recommendations back to craft memory."""
        if not self._craft_memory_dir:
            return 0
        craft_recs = bundle.by_loop("craft_preset_selection")
        if not craft_recs:
            return 0

        craft_dir = self._craft_memory_dir
        craft_dir.mkdir(parents=True, exist_ok=True)
        ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

        entries: list[dict[str, Any]] = []
        for r in craft_recs:
            entries.append({
                "timestamp": ts,
                "source": "data_loop",
                "task_id": r.task_id,
                "severity": r.severity,
                "action": r.next_action,
                "preset": r.task_id.split(":")[0] if ":" in r.task_id else r.task_id,
            })

        path = craft_dir / f"data_loop_craft_writeback_{ts}.json"
        path.write_text(json.dumps(entries, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return len(entries)

    def _writeback_calibration(self, bundle: RecommendationBundle) -> int:
        """Write scoring calibration recommendations as proposals."""
        score_recs = bundle.by_loop("scoring_calibration")
        if not score_recs:
            return 0

        proposals_dir = self._output_dir / "calibration_proposals"
        proposals_dir.mkdir(parents=True, exist_ok=True)
        ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

        proposals: list[dict[str, Any]] = []
        for r in score_recs:
            proposals.append({
                "timestamp": ts,
                "source": "data_loop",
                "task_id": r.task_id,
                "severity": r.severity,
                "reason": r.reason,
                "proposed_action": r.next_action,
                "needs_human_review": r.needs_human_review,
            })

        path = proposals_dir / f"calibration_proposal_{ts}.json"
        path.write_text(json.dumps(proposals, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return len(proposals)

    # ------------------------------------------------------------------
    # Report formatting (MHP-822)
    # ------------------------------------------------------------------

    @staticmethod
    def _format_report(
        record: dict[str, Any],
        bundle: RecommendationBundle,
    ) -> str:
        rt = record.get("runtime", {})
        sc = record.get("scoring", {})
        cr = record.get("craft", {})
        q = record.get("queue", {})
        td = record.get("tidal", {})

        lines: list[str] = [
            f"# Data Loop Report — {bundle.run_id}",
            "",
            f"**Generated**: {utc_now_iso()}",
            f"**Operator Decision**: **{bundle.summary.get('decision', '?')}** "
            f"→ {bundle.summary.get('next_mhp', '?')}",
            "",
            "## Summary",
            "",
            f"| Metric | Value |",
            f"|--------|-------|",
            f"| Tasks | {rt.get('success', 0)} success / {rt.get('failed', 0)} failed / {rt.get('total_selected', 0)} selected |",
            f"| Fatal error | {rt.get('fatal_error') or 'none'} |",
            f"| Scoring disagreements | {sc.get('disagreement_count', 0)} / {sc.get('task_count', 0)} (rate: {sc.get('agreement_rate', 1):.1%}) |",
            f"| Craft flags | {cr.get('flagged_count', 0)} / {cr.get('task_count', 0)} ({', '.join(cr.get('flag_types', [])) or 'none'}) |",
            f"| Queue depth | {q.get('total_tasks', 0)} total, {q.get('pending', 0)} pending, {q.get('failed', 0)} failed |",
            f"| Tidal cycles | {td.get('cycle_count', 0)} (events: {td.get('events_since_last', 0)}) |",
            "",
            "## Recommendations",
            "",
            f"**{len(bundle.high_severity)} high**, "
            f"**{len(bundle.recommendations) - len(bundle.high_severity)} other**, "
            f"**{len(bundle.needs_review)} need review**",
            "",
            "| Severity | Loop | Task ID | Action | Review |",
            "|----------|------|---------|--------|--------|",
        ]

        for r in bundle.recommendations:
            review = "⚠️ yes" if r.needs_human_review else "no"
            lines.append(
                f"| **{r.severity}** | {r.loop} | {r.task_id} | "
                f"{r.next_action[:80]}{'...' if len(r.next_action) > 80 else ''} | {review} |"
            )

        lines += [
            "",
            "## Decision Rationale",
            "",
            bundle.summary.get("decision_reason", "No decision reason provided."),
            "",
            "## Next Steps",
            "",
            f"1. Review {len(bundle.needs_review)} recommendation(s) flagged for human review.",
            f"2. Execute the highest-severity recommendations first.",
            f"3. Run tonight's cycle and compare the new NightMetricRecord.",
            f"4. Next MHP direction: **{bundle.summary.get('next_mhp', 'TBD')}**",
            "",
            "---",
            f"*Generated by Data Loop Runner — ECHAIN-MOODIFY-DATA-LOOP-014 / Build NEM-043*",
        ]

        return "\n".join(lines) + "\n"

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _infer_run_id(self) -> str:
        """Infer run_id from summary content, falling back to directory name."""
        try:
            with self._summary_path.open("r", encoding="utf-8") as f:
                data = json.loads(f.read())
            rid = data.get("run_id", "")
            if rid:
                return rid
        except Exception:
            pass
        try:
            return self._summary_path.parent.name
        except Exception:
            return "unknown"
