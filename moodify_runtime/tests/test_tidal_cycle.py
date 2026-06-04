"""Tests for tidal_cycle — engine, phases, heartbeat."""
import tempfile, json
from pathlib import Path
from moodify_runtime.tidal_cycle import (
    TideRecord, TidalEngine, _disk_free_gb, _mem_free_gb, _utc_now,
    phase_register, phase_plan, phase_report, phase_craft,
)


class TestTideRecord:
    def test_default(self):
        r = TideRecord(cycle_id="C1", cycle_number=1)
        assert r.cycle_id == "C1"
        assert r.phase == "init"

    def test_to_dict(self):
        r = TideRecord(cycle_id="C2", cycle_number=2, phase="run",
                       started_at="2026-01-01T00:00:00Z",
                       finished_at="2026-01-01T01:00:00Z",
                       tasks_processed=5, tasks_succeeded=4, tasks_failed=1,
                       elapsed_s=3600.0, free_disk_gb=50.0, free_mem_gb=8.0)
        d = r.to_dict()
        assert d["cycle_id"] == "C2"
        assert d["tasks_succeeded"] == 4
        assert d["tasks_failed"] == 1


class TestHealthUtils:
    def test_disk_free_positive(self):
        assert _disk_free_gb(Path(".")) > 0

    def test_mem_free(self):
        assert _mem_free_gb() != 0

    def test_utc_now_iso(self):
        ts = _utc_now()
        assert "T" in ts and "Z" in ts


class TestTidalEngine:
    def test_init(self):
        tmp = Path(tempfile.mkdtemp())
        e = TidalEngine(interval=60, max_cycles=10, task_limit=5, output_dir=tmp)
        assert e.interval == 60
        assert e.max_cycles == 10
        assert (tmp / "tidal.pid").exists()

    def test_heartbeat(self):
        tmp = Path(tempfile.mkdtemp())
        e = TidalEngine(interval=1, max_cycles=1, output_dir=tmp)
        e._heartbeat()
        hb = json.loads((tmp / "tidal_heartbeat.json").read_text())
        for k in ["timestamp", "pid", "cycle", "free_disk_gb"]:
            assert k in hb

    def test_emit_event(self):
        tmp = Path(tempfile.mkdtemp())
        e = TidalEngine(interval=1, max_cycles=1, output_dir=tmp)
        e._emit("TEST", "msg", extra=42)
        events = (tmp / "tidal_events.jsonl").read_text()
        assert "TEST" in events

    def test_health_check_passes(self):
        tmp = Path(tempfile.mkdtemp())
        e = TidalEngine(interval=1, max_cycles=1, output_dir=tmp)
        assert e._health_check()

    def test_signal_shutdown(self):
        tmp = Path(tempfile.mkdtemp())
        e = TidalEngine(interval=1, max_cycles=100, output_dir=tmp)
        assert e._running
        e._handle_shutdown(15, None)
        assert not e._running

    def test_mini_cycle(self):
        tmp = Path(tempfile.mkdtemp())
        e = TidalEngine(interval=1, max_cycles=1, task_limit=1, output_dir=tmp)
        result = e.run()
        assert result["cycles_completed"] >= 1
        assert (tmp / "tidal_heartbeat.json").exists()

    def test_pid_cleanup(self):
        tmp = Path(tempfile.mkdtemp())
        e = TidalEngine(interval=1, max_cycles=1, output_dir=tmp)
        e.run()
        assert not (tmp / "tidal.pid").exists()


class TestPhaseRunners:
    def test_register(self):
        r = phase_register()
        assert isinstance(r, dict)
        assert "ok" in r

    def test_plan(self):
        r = phase_plan(presets="warm_vocal")
        assert isinstance(r, dict)
        assert "ok" in r
