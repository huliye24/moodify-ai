"""Tests for registry — input registration and lookup."""
import tempfile
from pathlib import Path
from moodify_runtime.registry import (
    load_registry, registry_index, register_inputs, find_sample,
)
from moodify_runtime.config import RuntimeConfig


class TestRegistryIndex:
    def test_empty(self):
        assert registry_index([]) == {}
    def test_indexes(self):
        rows = [{"sample_id": "s1", "preset": "warm_vocal", "path": "/a.wav"}]
        assert "s1" in registry_index(rows)


class TestRegisterInputs:
    def test_no_input_dirs(self):
        d = tempfile.mkdtemp()
        cfg = RuntimeConfig(project_root=Path(d), input_dirs=[],
                            registry_path=Path(d) / "reg.jsonl")
        result = register_inputs(cfg, source="test")
        assert isinstance(result, dict)
        assert "added" in result  # actual key

    def test_empty_dir(self):
        d = tempfile.mkdtemp()
        indir = Path(d) / "inputs"; indir.mkdir()
        cfg = RuntimeConfig(project_root=Path(d), input_dirs=[indir],
                            registry_path=Path(d) / "reg.jsonl")
        result = register_inputs(cfg, source="test")
        assert isinstance(result, dict)


class TestFindSample:
    def test_not_found(self):
        d = tempfile.mkdtemp()
        cfg = RuntimeConfig(project_root=Path(d), registry_path=Path(d) / "reg.jsonl")
        assert find_sample(cfg, "nonexistent") is None
