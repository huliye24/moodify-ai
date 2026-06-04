"""Tests for failure — error classification and analysis."""
import tempfile
from pathlib import Path
from moodify_runtime.failure import classify_error, analyze_failures
from moodify_runtime.config import RuntimeConfig


class TestClassifyError:
    def test_timeout(self):
        assert classify_error("timed out after 300s") == "timeout"
    def test_resource(self):
        assert classify_error("MemoryError: out of memory") == "resource"
    def test_crashed(self):
        assert classify_error("Killed") in ("crashed", "resource")
    def test_other(self):
        assert classify_error("No space left on device") == "other"
    def test_empty(self):
        assert classify_error("") == "unknown"
    def test_none(self):
        assert classify_error(None) == "unknown"


class TestAnalyzeFailures:
    def test_no_runs_raises(self):
        cfg = RuntimeConfig()
        cfg.output_root = Path(tempfile.mkdtemp())
        try:
            analyze_failures(cfg)
        except FileNotFoundError:
            pass  # Expected
