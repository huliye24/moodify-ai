"""Tests for config — RuntimeConfig, load_config."""
import json, tempfile
from pathlib import Path
import pytest
from moodify_runtime.config import RuntimeConfig, load_config


class TestRuntimeConfig:
    def test_defaults(self):
        c = RuntimeConfig()
        assert c.project_root is not None
        assert len(c.presets) >= 3
        assert c.max_files == 30
        assert c.max_retries_per_task == 2

    def test_custom_values(self):
        c = RuntimeConfig(max_files=10, timeout_seconds_per_task=300, max_retries_per_task=5)
        assert c.max_files == 10
        assert c.timeout_seconds_per_task == 300

    def test_to_dict_roundtrip(self):
        c = RuntimeConfig(project_root=Path("/tmp"))
        d = c.to_dict()
        assert d["project_root"] == "/tmp"
        assert isinstance(d["presets"], list)

    def test_from_dict(self):
        raw = {"max_files": 5, "presets": ["warm_vocal"], "timeout_seconds_per_task": 60}
        c = RuntimeConfig.from_dict(raw)
        assert c.max_files == 5
        assert c.timeout_seconds_per_task == 60

    def test_from_json(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({"max_files": 7, "sleep_seconds_between_tasks": 0.5}, f)
            f.flush()
            c = RuntimeConfig.from_json(f.name)
        assert c.max_files == 7

    def test_resolved_makes_absolute(self):
        c = RuntimeConfig(project_root=Path("."))
        r = c.resolved()
        assert r.project_root.is_absolute()

    def test_config_paths_are_paths(self):
        c = RuntimeConfig()
        assert isinstance(c.output_root, Path)
        assert isinstance(c.registry_path, Path)
        assert isinstance(c.report_dir, Path)


class TestLoadConfig:
    def test_returns_runtime_config(self):
        c = load_config()
        assert isinstance(c, RuntimeConfig)
        assert c.project_root.is_absolute()
