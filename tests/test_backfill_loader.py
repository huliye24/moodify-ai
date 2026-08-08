"""Tests for backfill_loader — historical data seeding."""
import json
import tempfile
from pathlib import Path

import pytest

from moodify_runtime.backfill_loader import discover_summaries, backfill, load_summary
from moodify_runtime.learning_store import read_store, store_index, append_night, NightRecord


class TestDiscoverSummaries:
    def test_finds_summaries(self):
        d = tempfile.mkdtemp()
        run_dir = Path(d) / "DLRUN_test"
        run_dir.mkdir()
        (run_dir / "summary.json").write_text(
            '{"run_id":"R1","started_at":"2026-06-08T12:00:00+08:00","records":[]}',
            encoding="utf-8",
        )
        found = discover_summaries([Path(d)])
        assert len(found) == 1

    def test_empty_dir(self):
        d = tempfile.mkdtemp()
        found = discover_summaries([Path(d)])
        assert found == []

    def test_nonexistent_dir(self):
        found = discover_summaries([Path("/nonexistent/path")])
        assert found == []


class TestBackfill:
    def test_seeds_store(self):
        d = tempfile.mkdtemp()
        store_path = Path(d) / "store.jsonl"

        # Create a fake summary
        run_dir = Path(d) / "DLRUN_test"
        run_dir.mkdir()
        (run_dir / "summary.json").write_text(
            json.dumps({
                "run_id": "R1",
                "started_at": "2026-06-08T12:00:00+08:00",
                "selected_count": 5,
                "success": 5,
                "failed": 0,
                "emotion": "calm",
                "records": [
                    {"idx": 1, "success": True, "eds": -15.0, "elapsed_s": 100.0},
                    {"idx": 2, "success": True, "eds": -17.0, "elapsed_s": 120.0},
                ],
            }),
            encoding="utf-8",
        )

        result = backfill(store_path, [Path(d)])
        assert result["stored"] == 1
        assert result["errors"] == 0

        rows = read_store(store_path)
        assert len(rows) == 1
        assert rows[0]["run_id"] == "R1"
        assert rows[0]["avg_eds"] == -16.0

    def test_idempotent(self):
        d = tempfile.mkdtemp()
        store_path = Path(d) / "store.jsonl"
        run_dir = Path(d) / "DLRUN_test"
        run_dir.mkdir()
        (run_dir / "summary.json").write_text(
            json.dumps({"run_id": "R1", "started_at": "2026-01-01T12:00:00", "records": []}),
            encoding="utf-8",
        )

        r1 = backfill(store_path, [Path(d)])
        r2 = backfill(store_path, [Path(d)])
        assert r1["stored"] == 1
        assert r2["stored"] == 0
        assert r2["skipped"] == 1

    def test_handles_missing_run_id(self):
        d = tempfile.mkdtemp()
        store_path = Path(d) / "store.jsonl"
        run_dir = Path(d) / "DLRUN_bad"
        run_dir.mkdir()
        (run_dir / "summary.json").write_text('{"records":[]}', encoding="utf-8")
        result = backfill(store_path, [Path(d)])
        assert result["errors"] == 1
