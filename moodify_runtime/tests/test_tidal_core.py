"""Tidal Core unit tests — NEM-MOODIFY-TIDAL-CORE-BUILD-025 (MHP-490, MHP-496)."""
import json
import tempfile
from pathlib import Path

import pytest

from moodify_runtime.tidal_cycle import (
    TidalEngine, TideRecord, _disk_free_gb, _mem_free_gb, _utc_now,
    phase_register, phase_plan,
)


class TestTideRecord:
    """MHP-485: State machine integrity."""

    def test_record_has_all_required_fields(self):
        r = TideRecord(cycle_id="T1", cycle_number=1)
        d = r.to_dict()
        required = ["cycle_id", "cycle_number", "phase", "started_at", "finished_at",
                     "tasks_processed", "tasks_succeeded", "tasks_failed",
                     "gate_approve", "gate_reprocess", "gate_reject",
                     "craft_records_written", "elapsed_s", "free_disk_gb", "free_mem_gb", "errors"]
        for field in required:
            assert field in d, f"Missing: {field}"

    def test_record_phase_transitions(self):
        r = TideRecord(cycle_id="T2", cycle_number=1)
        assert r.phase == "init"
        r.phase = "register"
        assert r.phase == "register"
        r.phase = "sleep"
        assert r.phase == "sleep"

    def test_record_serialization_roundtrip(self):
        r = TideRecord(cycle_id="T3", cycle_number=2, phase="run",
                        started_at="2026-06-04T00:00:00Z",
                        finished_at="2026-06-04T01:00:00Z",
                        tasks_processed=5, tasks_succeeded=4, tasks_failed=1,
                        elapsed_s=3600.0, free_disk_gb=50.0, free_mem_gb=8.0)
        d = r.to_dict()
        assert d["cycle_id"] == "T3"
        assert d["tasks_succeeded"] == 4
        assert d["tasks_failed"] == 1


class TestHealthChecks:
    """MHP-489: Safety cutoff engine."""

    def test_disk_free_positive(self):
        gb = _disk_free_gb(Path("."))
        assert gb > 0

    def test_mem_free_returns_value(self):
        gb = _mem_free_gb()
        assert gb != 0

    def test_utc_now_iso_format(self):
        ts = _utc_now()
        assert "T" in ts and "Z" in ts


class TestTidalEngine:
    """MHP-488 + MHP-496: Heartbeat + integration smoke."""

    def test_engine_init(self):
        tmp = Path(tempfile.mkdtemp())
        e = TidalEngine(interval=60, max_cycles=10, task_limit=5, output_dir=tmp)
        assert e.interval == 60
        assert e.max_cycles == 10
        assert e.task_limit == 5
        assert (tmp / "tidal.pid").exists()

    def test_heartbeat_valid_json(self):
        tmp = Path(tempfile.mkdtemp())
        e = TidalEngine(interval=1, max_cycles=1, output_dir=tmp)
        e._heartbeat()
        hb = json.loads((tmp / "tidal_heartbeat.json").read_text())
        for k in ["timestamp", "pid", "cycle", "free_disk_gb", "free_mem_gb"]:
            assert k in hb

    def test_event_emission(self):
        tmp = Path(tempfile.mkdtemp())
        e = TidalEngine(interval=1, max_cycles=1, output_dir=tmp)
        e._emit("TEST", "msg", extra=42)
        events = (tmp / "tidal_events.jsonl").read_text()
        assert "TEST" in events
        assert "extra" in events

    def test_health_check_passes(self):
        tmp = Path(tempfile.mkdtemp())
        e = TidalEngine(interval=1, max_cycles=1, output_dir=tmp)
        assert e._health_check() is True

    def test_signal_shutdown(self):
        tmp = Path(tempfile.mkdtemp())
        e = TidalEngine(interval=1, max_cycles=100, output_dir=tmp)
        assert e._running is True
        e._handle_shutdown(15, None)
        assert e._running is False

    def test_pid_cleaned_after_run(self):
        tmp = Path(tempfile.mkdtemp())
        e = TidalEngine(interval=1, max_cycles=1, output_dir=tmp)
        e.run()
        assert not (tmp / "tidal.pid").exists()

    def test_mini_cycle_completes(self):
        """MHP-496: Full integration smoke."""
        tmp = Path(tempfile.mkdtemp())
        e = TidalEngine(interval=1, max_cycles=1, task_limit=1, output_dir=tmp)
        result = e.run()
        assert result["cycles_completed"] >= 1
        assert (tmp / "tidal_heartbeat.json").exists()
        assert (tmp / "tidal_events.jsonl").exists()


class TestPhaseRunners:
    """MHP-491: CLI integration."""

    def test_phase_register(self):
        r = phase_register()
        assert isinstance(r, dict)
        assert "ok" in r

    def test_phase_plan(self):
        r = phase_plan(presets="warm_vocal")
        assert isinstance(r, dict)
        assert "ok" in r
