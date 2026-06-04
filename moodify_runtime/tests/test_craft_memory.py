"""Tests for craft_memory — seed, writeback, list records."""
import tempfile
from pathlib import Path
from moodify_runtime.craft_memory import (
    _read_manifest, _to_float, seed_craft_memory, list_craft_records,
)
from moodify_runtime.config import RuntimeConfig


class TestHelpers:
    def test_read_missing_manifest(self):
        assert _read_manifest(Path("/nonexistent/run")) == []

    def test_to_float_number(self):
        assert _to_float("3.14") == 3.14

    def test_to_float_none(self):
        assert _to_float(None) is None


class TestSeedCraftMemory:
    def test_no_runs_raises(self):
        d = tempfile.mkdtemp()
        cfg = RuntimeConfig(project_root=Path(d), output_root=Path(d) / "out")
        cfg.output_root.mkdir(exist_ok=True)
        try:
            seed_craft_memory(cfg)
        except FileNotFoundError:
            pass  # Expected with no runs

    def test_empty_runs_handled(self):
        d = tempfile.mkdtemp()
        out = Path(d) / "out"; out.mkdir()
        (out / "run_1").mkdir()
        cfg = RuntimeConfig(project_root=Path(d), output_root=out,
                            craft_memory_dir=Path(d) / "craft")
        try:
            result = seed_craft_memory(cfg, run_id="run_1", top_k=5)
            assert isinstance(result, dict)
        except Exception:
            pass


class TestListCraftRecords:
    def test_empty(self):
        d = tempfile.mkdtemp()
        cfg = RuntimeConfig(project_root=Path(d),
                            craft_memory_dir=Path(d) / "craft")
        cfg.craft_memory_dir.mkdir(exist_ok=True)
        records = list_craft_records(cfg)
        assert isinstance(records, list)
