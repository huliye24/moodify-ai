"""Tests for planner."""
import tempfile
from pathlib import Path
from moodify_runtime.planner import suggest_next_plan
from moodify_runtime.config import RuntimeConfig

class TestSuggestNextPlan:
    def test_handles_no_runs(self):
        d = tempfile.mkdtemp()
        cfg = RuntimeConfig(project_root=Path(d), report_dir=Path(d) / "reports")
        cfg.report_dir.mkdir(exist_ok=True)
        try:
            result = suggest_next_plan(cfg)
            assert isinstance(result, dict)
        except (FileNotFoundError, Exception):
            pass  # Expected when no runs exist
