"""Tests for learning_store — multi-night append-only store."""
import json
import tempfile
from pathlib import Path

import pytest

from moodify_runtime.learning_store import (
    NightRecord,
    read_store,
    store_index,
    append_night,
    load_store,
    store_summary,
    _derive_night_label,
)


class TestNightRecord:
    def test_from_summary_basic(self):
        summary = {
            "run_id": "DLRUN_test",
            "started_at": "2026-06-08T12:00:00+08:00",
            "input_dir": "data/audio",
            "selected_count": 10,
            "success": 9,
            "failed": 1,
            "emotion": "calm",
            "records": [
                {"idx": 1, "success": True, "eds": -15.0, "elapsed_s": 100.0},
                {"idx": 2, "success": True, "eds": -17.0, "elapsed_s": 120.0},
                {"idx": 3, "success": False},
            ],
        }
        r = NightRecord.from_summary(summary, "path/to/summary.json")
        assert r.run_id == "DLRUN_test"
        assert r.night_label == "2026-06-08"
        assert r.selected_count == 10
        assert r.success_count == 9
        assert r.failed_count == 1
        assert r.avg_eds == -16.0
        assert r.avg_elapsed_s == 110.0
        assert r.provenance_path == "path/to/summary.json"

    def test_from_summary_empty_records(self):
        summary = {"run_id": "R1", "started_at": "2026-06-08T12:00:00", "records": []}
        r = NightRecord.from_summary(summary)
        assert r.avg_eds is None
        assert r.avg_elapsed_s is None

    def test_to_dict_round_trip(self):
        r = NightRecord(
            run_id="R1", started_at="2026-06-08T12:00:00+08:00",
            night_label="2026-06-08", avg_eds=-15.0, selected_count=5, success_count=5,
        )
        d = r.to_dict()
        r2 = NightRecord.from_dict(d)
        assert r2.run_id == r.run_id
        assert r2.avg_eds == r.avg_eds

    def test_night_label_formats(self):
        assert _derive_night_label("2026-06-08T12:00:00+08:00") == "2026-06-08"
        assert _derive_night_label("2026-01-15T12:00:00") == "2026-01-15"
        assert _derive_night_label("2026-03-20T12:00:00+0800") == "2026-03-20"


class TestAppendNight:
    def test_stores_and_dedup(self):
        d = tempfile.mkdtemp()
        p = Path(d) / "store.jsonl"
        r = NightRecord(run_id="R1", started_at="2026-06-08T12:00:00")
        result = append_night(p, r)
        assert result["status"] == "stored"
        result2 = append_night(p, r)
        assert result2["status"] == "skipped"

    def test_multiple_runs(self):
        d = tempfile.mkdtemp()
        p = Path(d) / "store.jsonl"
        append_night(p, NightRecord(run_id="R1", started_at="2026-01-01T12:00:00"))
        append_night(p, NightRecord(run_id="R2", started_at="2026-01-02T12:00:00"))
        assert len(read_store(p)) == 2


class TestStoreIndex:
    def test_indexes(self):
        d = tempfile.mkdtemp()
        p = Path(d) / "store.jsonl"
        append_night(p, NightRecord(run_id="A", started_at="2026-01-01T12:00:00"))
        append_night(p, NightRecord(run_id="B", started_at="2026-01-02T12:00:00"))
        idx = store_index(p)
        assert "A" in idx
        assert "B" in idx

    def test_empty_store(self):
        d = tempfile.mkdtemp()
        p = Path(d) / "nonexistent.jsonl"
        assert store_index(p) == set()


class TestLoadStore:
    def test_loads_sorted(self):
        d = tempfile.mkdtemp()
        p = Path(d) / "store.jsonl"
        append_night(p, NightRecord(run_id="R2", started_at="2026-01-02T12:00:00", night_label="2026-01-02"))
        append_night(p, NightRecord(run_id="R1", started_at="2026-01-01T12:00:00", night_label="2026-01-01"))
        records = load_store(p)
        assert len(records) == 2
        assert records[0].run_id in ("R1", "R2")


class TestStoreSummary:
    def test_empty(self):
        d = tempfile.mkdtemp()
        p = Path(d) / "store.jsonl"
        s = store_summary(p)
        assert s["total_nights"] == 0

    def test_populated(self):
        d = tempfile.mkdtemp()
        p = Path(d) / "store.jsonl"
        append_night(p, NightRecord(run_id="R1", started_at="2026-01-01T12:00:00", night_label="2026-01-01"))
        s = store_summary(p)
        assert s["total_nights"] == 1
        assert s["earliest"] == "2026-01-01"
