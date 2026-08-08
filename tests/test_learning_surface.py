"""Tests for learning_surface — operator-facing pack generator."""
import json
import tempfile
from pathlib import Path

from moodify_runtime.learning_store import NightRecord, append_night
from moodify_runtime.learning_surface import generate_learning_report


class TestGenerateLearningReport:
    def _seed_store(self, store_path: Path, n_nights: int = 6) -> None:
        for i in range(n_nights):
            append_night(store_path, NightRecord(
                run_id=f"R{i}",
                started_at=f"2026-01-0{i+1}T12:00:00+08:00",
                night_label=f"2026-01-0{i+1}",
                selected_count=10, success_count=10, failed_count=0,
                avg_eds=-15.0 + i * 0.5,
                avg_elapsed_s=110.0 - i * 2.0,
            ))

    def test_generates_pack(self):
        d = tempfile.mkdtemp()
        store_path = Path(d) / "store.jsonl"
        self._seed_store(store_path, 6)

        out_dir = Path(d) / "learning_surface"
        manifest = generate_learning_report(store_path, out_dir)

        assert manifest["pack_id"].startswith("learning_surface_")
        assert "trend_report.md" in manifest["files"]
        assert "learning_summary.md" in manifest["files"]
        assert "significance_report.md" in manifest["files"]
        assert manifest["store_summary"]["total_nights"] == 6

        # Check all output files exist
        for f in manifest["files"]:
            assert (out_dir / f).exists()

        # Check LATEST.json
        latest_path = out_dir.parent / "LATEST.json"
        assert latest_path.exists()
        latest = json.loads(latest_path.read_text())
        assert latest["latest_pack_id"] == manifest["pack_id"]

    def test_minimal_store(self):
        d = tempfile.mkdtemp()
        store_path = Path(d) / "store.jsonl"
        append_night(store_path, NightRecord(
            run_id="R1", started_at="2026-01-01T12:00:00+08:00",
            night_label="2026-01-01", selected_count=5, success_count=5,
            avg_eds=-15.0, avg_elapsed_s=110.0,
        ))
        out_dir = Path(d) / "learning_surface"
        manifest = generate_learning_report(store_path, out_dir)
        assert manifest["store_summary"]["total_nights"] == 1
        # With only 1 night, significance is skipped
        assert "significance_report.md" not in manifest["files"]
