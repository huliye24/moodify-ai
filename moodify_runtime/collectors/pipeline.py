"""Orchestrate all collectors into a single NightMetricRecord.

MHP-813: Collector Unit Tests
MHP-814: Collector Build Report

Usage:
    from moodify_runtime.collectors import collect_night_metrics

    record = collect_night_metrics(
        summary_path=Path("outputs/20260605_000141/summary.json"),
        queue_path=Path("data/tidal_queue.jsonl"),
    )
    # record is a dict conforming to schemas/night_metric_record.schema.json
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from moodify_runtime.collectors.summary_collector import SummaryCollector
from moodify_runtime.collectors.tidal_collector import TidalEventCollector
from moodify_runtime.collectors.queue_collector import QueueCollector
from moodify_runtime.utils import utc_now_iso


class CollectorPipeline:
    """Orchestrate all data collectors and produce a unified NightMetricRecord.

    Usage:
        pipeline = CollectorPipeline(
            summary_path="outputs/20260605_000141/summary.json",
            queue_path="data/tidal_queue.jsonl",
        )
        record = pipeline.run()
        pipeline.write(record, Path("reports/night_metrics_20260605.json"))
    """

    def __init__(
        self,
        summary_path: Path | str,
        manifest_path: Path | str | None = None,
        queue_path: Path | str | None = None,
        tidal_events_path: Path | str | None = None,
        tidal_heartbeat_path: Path | str | None = None,
    ):
        self._summary_path = Path(summary_path)
        self._manifest_path = Path(manifest_path) if manifest_path else None
        self._queue_path = Path(queue_path) if queue_path else None
        self._tidal_events_path = Path(tidal_events_path) if tidal_events_path else None
        self._tidal_heartbeat_path = Path(tidal_heartbeat_path) if tidal_heartbeat_path else None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def run(self) -> dict[str, Any]:
        """Run all collectors and return the merged NightMetricRecord."""
        # Core collector — always required
        summary_collector = SummaryCollector(
            self._summary_path,
            source_manifest=self._manifest_path,
        )
        record = summary_collector.collect()

        # Queue collector
        if self._queue_path and self._queue_path.exists():
            queue_collector = QueueCollector(self._queue_path)
            record["queue"] = queue_collector.collect()
        else:
            record["queue"] = {
                "total_tasks": 0, "pending": 0, "claimed": 0,
                "running": 0, "done": 0, "failed": 0, "abandoned": 0,
            }

        # Tidal collector
        if self._tidal_events_path and self._tidal_events_path.exists():
            tidal_collector = TidalEventCollector(
                self._tidal_events_path,
                self._tidal_heartbeat_path,
            )
            record["tidal"] = tidal_collector.collect()
        else:
            record["tidal"] = {
                "cycle_count": 0, "events_since_last": 0,
                "last_cycle_phases": [], "last_heartbeat_at": None,
            }

        record["collected_at"] = utc_now_iso()
        return record

    def write(self, record: dict[str, Any], output_path: Path) -> Path:
        """Write the NightMetricRecord to a JSON file."""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with output_path.open("w", encoding="utf-8") as f:
            json.dump(record, f, ensure_ascii=False, indent=2)
            f.write("\n")
        return output_path


# ------------------------------------------------------------------
# Convenience function
# ------------------------------------------------------------------


def collect_night_metrics(
    summary_path: Path | str,
    manifest_path: Path | str | None = None,
    queue_path: Path | str | None = None,
    tidal_events_path: Path | str | None = None,
    tidal_heartbeat_path: Path | str | None = None,
) -> dict[str, Any]:
    """One-call convenience: run all collectors and return a NightMetricRecord dict."""
    pipeline = CollectorPipeline(
        summary_path=summary_path,
        manifest_path=manifest_path,
        queue_path=queue_path,
        tidal_events_path=tidal_events_path,
        tidal_heartbeat_path=tidal_heartbeat_path,
    )
    return pipeline.run()
