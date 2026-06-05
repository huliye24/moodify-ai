"""MHP-813: Collector Unit Tests — summary, tidal, queue collectors + pipeline.

Tests cover:
  - SummaryCollector: runtime signals, scoring disagreements, craft flags, per-task details
  - TidalEventCollector: cycle counting, event tallying, gate aggregation
  - QueueCollector: status distribution, abandonment detection, oldest pending
  - CollectorPipeline: end-to-end merge, missing optional inputs
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest

from moodify_runtime.collectors.summary_collector import (
    SummaryCollector,
    RuntimeSignal,
    ScoringSignal,
    CraftSignal,
    TaskDetail,
)
from moodify_runtime.collectors.tidal_collector import (
    TidalEventCollector,
    TidalSignal,
)
from moodify_runtime.collectors.queue_collector import (
    QueueCollector,
    QueueSignal,
)
from moodify_runtime.collectors.pipeline import (
    CollectorPipeline,
    collect_night_metrics,
)


# ═══════════════════════════════════════════════════════════════════════
# Fixtures
# ═══════════════════════════════════════════════════════════════════════


def _write_json(path: Path, data: dict) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def _write_jsonl(path: Path, records: list[dict]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    return path


@pytest.fixture
def summary_dict():
    """Mimics outputs/20260605_000141/summary.json shape."""
    return {
        "run_id": "20260605_test",
        "started_at": "2026-06-05T00:01:41+00:00",
        "success": 3,
        "failed": 1,
        "total_selected": 4,
        "dry_run": False,
        "fatal_error": None,
        "tasks": [
            {
                "task_id": "TASK_A_warm_vocal", "sample_id": "SMP_A",
                "preset": "warm_vocal", "status": "done", "return_code": 0,
                "elapsed_seconds": "0.5",
                "pseudo_mrs_before": 80.0, "pseudo_mrs_after": 60.0,
                "pseudo_delta_mrs": -20.0,
                "mrs_open_v031_before": 1036.0, "mrs_open_v031_after": 1120.0,
                "delta_mrs_open_v031": 84.0,
                "mrs_open_flags": "",
            },
            {
                "task_id": "TASK_B_clean_master", "sample_id": "SMP_B",
                "preset": "clean_master", "status": "done", "return_code": 0,
                "elapsed_seconds": "0.7",
                "pseudo_mrs_before": 82.0, "pseudo_mrs_after": 84.0,
                "pseudo_delta_mrs": 2.0,
                "mrs_open_v031_before": 1036.0, "mrs_open_v031_after": 1035.0,
                "delta_mrs_open_v031": -1.0,
                "mrs_open_flags": "over_dark",
            },
            {
                "task_id": "TASK_C_wide_space", "sample_id": "SMP_C",
                "preset": "wide_space", "status": "done", "return_code": 0,
                "elapsed_seconds": "0.8",
                "pseudo_mrs_before": 82.0, "pseudo_mrs_after": 64.0,
                "pseudo_delta_mrs": -18.0,
                "mrs_open_v031_before": 1036.0, "mrs_open_v031_after": 1118.0,
                "delta_mrs_open_v031": 82.0,
                "mrs_open_flags": "",
            },
            {
                "task_id": "TASK_D_failed", "sample_id": "SMP_D",
                "preset": "warm_vocal", "status": "failed", "return_code": 1,
                "elapsed_seconds": "1.2",
                "pseudo_mrs_before": None, "pseudo_mrs_after": None,
                "pseudo_delta_mrs": None,
                "mrs_open_v031_before": None, "mrs_open_v031_after": None,
                "delta_mrs_open_v031": None,
                "mrs_open_flags": "",
            },
        ],
    }


@pytest.fixture
def summary_file(tmp_path, summary_dict):
    return _write_json(tmp_path / "summary.json", summary_dict)


@pytest.fixture
def tidal_events():
    return [
        {"cycle_id": "tide_001", "cycle_number": 1, "phase": "register",
         "tasks_processed": 4, "tasks_succeeded": 4, "tasks_failed": 0,
         "gate_approve": 4, "gate_reprocess": 0, "gate_reject": 0},
        {"cycle_id": "tide_002", "cycle_number": 2, "phase": "run",
         "tasks_processed": 6, "tasks_succeeded": 5, "tasks_failed": 1,
         "gate_approve": 4, "gate_reprocess": 1, "gate_reject": 0},
        {"cycle_id": "tide_003", "cycle_number": 3, "phase": "gate",
         "tasks_processed": 4, "tasks_succeeded": 3, "tasks_failed": 1,
         "gate_approve": 2, "gate_reprocess": 0, "gate_reject": 1},
    ]


@pytest.fixture
def tidal_file(tmp_path, tidal_events):
    return _write_jsonl(tmp_path / "tidal_events.jsonl", tidal_events)


@pytest.fixture
def queue_tasks():
    return [
        {"task_id": "TASK_1", "status": "done", "created_at": "2026-06-04T10:00:00Z"},
        {"task_id": "TASK_2", "status": "done", "created_at": "2026-06-04T10:00:00Z"},
        {"task_id": "TASK_3", "status": "done", "created_at": "2026-06-04T10:00:00Z"},
        {"task_id": "TASK_4", "status": "pending", "created_at": "2026-06-04T10:00:00Z"},
        {"task_id": "TASK_5", "status": "pending", "created_at": "2026-06-04T10:00:00Z"},
        {"task_id": "TASK_6", "status": "failed", "created_at": "2026-06-04T10:00:00Z"},
        {"task_id": "TASK_7", "status": "claimed", "started_at": "2026-06-04T09:00:00Z"},
    ]


@pytest.fixture
def queue_file(tmp_path, queue_tasks):
    return _write_jsonl(tmp_path / "queue.jsonl", queue_tasks)


# ═══════════════════════════════════════════════════════════════════════
# MHP-810: SummaryCollector
# ═══════════════════════════════════════════════════════════════════════


class TestSummaryCollector:

    def test_collect_basic_structure(self, summary_file):
        collector = SummaryCollector(summary_file)
        record = collector.collect()

        assert record["run_id"] == "20260605_test"
        assert "started_at" in record
        assert "collected_at" in record
        assert "runtime" in record
        assert "scoring" in record
        assert "craft" in record
        assert "tasks" in record

    def test_runtime_signal(self, summary_file):
        record = SummaryCollector(summary_file).collect()
        rt = record["runtime"]

        assert rt["success"] == 3
        assert rt["failed"] == 1
        assert rt["total_selected"] == 4
        assert rt["dry_run"] is False

    def test_runtime_signal_success_rate(self, summary_file):
        collector = SummaryCollector(summary_file)
        collector.collect()
        # Expose internals for assertion via direct construction
        rt = collector._collect_runtime()
        assert rt.success_rate == 0.75  # 3 success / 4 total

    def test_runtime_fatal_error_detection(self, tmp_path):
        data = {
            "run_id": "test", "started_at": "", "success": 0, "failed": 0,
            "total_selected": 0, "dry_run": False,
            "fatal_error": "FileNotFoundError: [Errno 2] No such file or directory: '/tmp/missing.log'",
            "tasks": [],
        }
        path = _write_json(tmp_path / "fatal_summary.json", data)
        collector = SummaryCollector(path)
        record = collector.collect()
        rt = record["runtime"]
        assert rt["fatal_error"] == data["fatal_error"]
        assert len(rt["missing_artifacts"]) == 1
        assert "/tmp/missing.log" in rt["missing_artifacts"][0]

    def test_scoring_signal_disagreement_count(self, summary_file):
        record = SummaryCollector(summary_file).collect()
        sc = record["scoring"]

        # TASK_A: -20 pseudo vs +84 open → disagreement
        # TASK_B: +2 pseudo vs -1 open → disagreement
        # TASK_C: -18 pseudo vs +82 open → disagreement
        # TASK_D: no scores → no disagreement
        assert sc["task_count"] == 4
        assert sc["disagreement_count"] == 3
        assert sc["agreement_rate"] == 0.25

    def test_scoring_disagreeing_presets(self, summary_file):
        record = SummaryCollector(summary_file).collect()
        assert set(record["scoring"]["disagreeing_presets"]) == {
            "warm_vocal", "clean_master", "wide_space",
        }

    def test_craft_signal_flagged_count(self, summary_file):
        record = SummaryCollector(summary_file).collect()
        cr = record["craft"]

        # Only TASK_B has mrs_open_flags="over_dark"
        assert cr["task_count"] == 4
        assert cr["flagged_count"] == 1
        assert cr["flag_rate"] == 0.25
        assert "over_dark" in cr["flag_types"]

    def test_craft_preset_delta_stats(self, summary_file):
        record = SummaryCollector(summary_file).collect()
        stats = record["craft"]["preset_delta_stats"]

        assert "warm_vocal" in stats
        assert stats["warm_vocal"]["mean_delta"] == 84.0
        assert stats["clean_master"]["flagged"] == 1

    def test_task_detail_disagreement_detection(self, summary_file):
        record = SummaryCollector(summary_file).collect()
        tasks = record["tasks"]

        # TASK_A: pseudo -20 (negative), open +84 (positive) → disagree
        t_a = next(t for t in tasks if t["task_id"] == "TASK_A_warm_vocal")
        assert t_a["score_direction_disagreement"] is True
        assert t_a["recommended_loop"] == "scoring_calibration"

    def test_task_detail_without_scores(self, summary_file):
        record = SummaryCollector(summary_file).collect()
        tasks = record["tasks"]
        t_d = next(t for t in tasks if t["task_id"] == "TASK_D_failed")
        assert t_d["score_direction_disagreement"] is None
        assert t_d["pseudo_delta_mrs"] is None

    def test_task_detail_recommended_loop(self, summary_file):
        record = SummaryCollector(summary_file).collect()
        tasks = {t["task_id"]: t for t in record["tasks"]}

        # TASK_B: disagreement + flags → scoring takes priority
        assert tasks["TASK_B_clean_master"]["recommended_loop"] == "scoring_calibration"
        # TASK_D: no scores, no flags → operator_report
        assert tasks["TASK_D_failed"]["recommended_loop"] == "operator_report"

    def test_empty_summary(self, tmp_path):
        data = {
            "run_id": "empty", "started_at": "", "success": 0, "failed": 0,
            "total_selected": 0, "dry_run": True, "tasks": [],
        }
        path = _write_json(tmp_path / "empty.json", data)
        record = SummaryCollector(path).collect()

        assert record["runtime"]["success"] == 0
        assert record["scoring"]["task_count"] == 0
        assert record["scoring"]["disagreement_count"] == 0
        assert record["craft"]["flagged_count"] == 0


# ═══════════════════════════════════════════════════════════════════════
# MHP-811: TidalEventCollector
# ═══════════════════════════════════════════════════════════════════════


class TestTidalEventCollector:

    def test_collect_cycle_count(self, tidal_file):
        collector = TidalEventCollector(events_path=tidal_file)
        signal = collector.collect()

        assert signal["cycle_count"] == 3
        assert signal["events_since_last"] == 3

    def test_aggregate_task_counts(self, tidal_file):
        collector = TidalEventCollector(events_path=tidal_file)
        signal = collector.collect()

        # 4+6+4 = 14 processed, 4+5+3 = 12 succeeded, 0+1+1 = 2 failed
        assert signal["total_tasks_processed"] == 14
        assert signal["total_tasks_succeeded"] == 12
        assert signal["total_tasks_failed"] == 2

    def test_aggregate_gate_counts(self, tidal_file):
        collector = TidalEventCollector(events_path=tidal_file)
        signal = collector.collect()

        assert signal["total_gate_approve"] == 10   # 4+4+2
        assert signal["total_gate_reprocess"] == 1  # 0+1+0
        assert signal["total_gate_reject"] == 1     # 0+0+1

    def test_last_cycle_phases(self, tidal_file):
        collector = TidalEventCollector(events_path=tidal_file)
        signal = collector.collect()

        assert "register" in signal["last_cycle_phases"]
        assert "run" in signal["last_cycle_phases"]
        assert "gate" in signal["last_cycle_phases"]

    def test_no_events_file(self, tmp_path):
        collector = TidalEventCollector(events_path=tmp_path / "nonexistent.jsonl")
        signal = collector.collect()

        assert signal["cycle_count"] == 0
        assert signal["events_since_last"] == 0

    def test_with_heartbeat(self, tmp_path):
        hb = _write_json(tmp_path / "heartbeat.json", {"last_heartbeat_at": "2026-06-04T10:00:00Z"})
        events = _write_jsonl(tmp_path / "events.jsonl", [{
            "cycle_id": "t1", "cycle_number": 1, "phase": "run",
            "tasks_processed": 1, "tasks_succeeded": 1, "tasks_failed": 0,
            "gate_approve": 1, "gate_reprocess": 0, "gate_reject": 0,
        }])
        collector = TidalEventCollector(events_path=events, heartbeat_path=hb)
        signal = collector.collect()

        assert signal["last_heartbeat_at"] == "2026-06-04T10:00:00Z"
        assert signal["cycle_count"] == 1


# ═══════════════════════════════════════════════════════════════════════
# MHP-812: QueueCollector
# ═══════════════════════════════════════════════════════════════════════


class TestQueueCollector:

    def test_status_distribution(self, queue_file):
        collector = QueueCollector(queue_file)
        signal = collector.collect()

        assert signal["total_tasks"] == 7
        assert signal["done"] == 3
        assert signal["pending"] == 2
        assert signal["failed"] == 1
        assert signal["claimed"] == 1

    def test_abandonment_risk_detection(self, tmp_path):
        # Task claimed > 1 hour ago
        tasks = [
            {"task_id": "OLD", "status": "claimed",
             "started_at": "2026-06-03T00:00:00Z"},
            {"task_id": "NEW", "status": "claimed",
             "started_at": "2026-06-05T00:00:00Z"},
        ]
        path = _write_jsonl(tmp_path / "queue.jsonl", tasks)
        collector = QueueCollector(path)
        signal = collector.collect()

        assert signal["abandonment_risk_count"] >= 1

    def test_oldest_pending(self, tmp_path):
        tasks = [
            {"task_id": "P1", "status": "pending",
             "created_at": "2026-06-01T00:00:00Z"},  # very old
            {"task_id": "P2", "status": "pending",
             "created_at": "2026-06-05T10:00:00Z"},  # recent
        ]
        path = _write_jsonl(tmp_path / "queue.jsonl", tasks)
        collector = QueueCollector(path)
        signal = collector.collect()

        assert signal["oldest_pending_minutes"] is not None
        assert signal["oldest_pending_minutes"] > 60  # definitely > 1 hour old

    def test_empty_queue(self, tmp_path):
        path = _write_jsonl(tmp_path / "empty.jsonl", [])
        collector = QueueCollector(path)
        signal = collector.collect()

        assert signal["total_tasks"] == 0
        assert signal["abandonment_risk_count"] == 0

    def test_no_queue_file(self, tmp_path):
        collector = QueueCollector(queue_path=tmp_path / "nonexistent.jsonl")
        signal = collector.collect()

        assert signal["total_tasks"] == 0


# ═══════════════════════════════════════════════════════════════════════
# MHP-813: CollectorPipeline
# ═══════════════════════════════════════════════════════════════════════


class TestCollectorPipeline:

    def test_run_with_summary_only(self, summary_file):
        pipeline = CollectorPipeline(summary_path=summary_file)
        record = pipeline.run()

        assert record["run_id"] == "20260605_test"
        assert record["queue"]["total_tasks"] == 0    # no queue file
        assert record["tidal"]["cycle_count"] == 0     # no tidal file

    def test_run_with_all_sources(self, summary_file, queue_file, tidal_file):
        pipeline = CollectorPipeline(
            summary_path=summary_file,
            queue_path=queue_file,
            tidal_events_path=tidal_file,
        )
        record = pipeline.run()

        assert record["queue"]["total_tasks"] == 7
        assert record["tidal"]["cycle_count"] == 3

    def test_write_output(self, summary_file, tmp_path):
        pipeline = CollectorPipeline(summary_path=summary_file)
        record = pipeline.run()
        out = tmp_path / "night_metrics.json"
        result = pipeline.write(record, out)

        assert result.exists()
        reloaded = json.loads(result.read_text(encoding="utf-8"))
        assert reloaded["run_id"] == "20260605_test"

    def test_convenience_function(self, summary_file):
        record = collect_night_metrics(summary_path=summary_file)
        assert record["run_id"] == "20260605_test"
        assert "collected_at" in record

    def test_pipeline_collected_at_timestamp(self, summary_file):
        record = collect_night_metrics(summary_path=summary_file)
        # collected_at should be an ISO-ish string
        assert "T" in record["collected_at"] or "2026" in record["collected_at"]

    def test_signal_types_are_serializable(self, summary_file):
        """All signal dataclasses should be JSON-serializable via asdict."""
        record = collect_night_metrics(summary_path=summary_file)
        # Must not raise
        json.dumps(record, ensure_ascii=False)
