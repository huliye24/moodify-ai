"""Tests for report — daily report generation."""
import tempfile
from pathlib import Path
import pytest
from moodify_runtime.report import (
    _read_manifest, _to_float, _fmt_float, generate_daily_report,
)
from moodify_runtime.config import RuntimeConfig


class TestHelpers:
    def test_read_missing(self):
        assert _read_manifest(Path("/nonexistent/x.csv")) == []

    def test_to_float_number(self):
        assert _to_float(3.14) == 3.14

    def test_to_float_null(self):
        assert _to_float(None) is None
        assert _to_float("") is None

    def test_fmt_float(self):
        assert _fmt_float(3.14159, 2) == "3.14"

    def test_fmt_float_null(self):
        assert _fmt_float(None) == "-"


class TestGenerateDailyReport:
    def test_no_runs_raises(self):
        d = tempfile.mkdtemp()
        out = Path(d) / "out"; out.mkdir()
        cfg = RuntimeConfig(project_root=Path(d), output_root=out,
                            report_dir=Path(d) / "reports")
        with pytest.raises(FileNotFoundError):
            generate_daily_report(cfg)

    def test_valid_run_dir(self):
        d = tempfile.mkdtemp()
        out = Path(d) / "out"; out.mkdir()
        run = out / "run_001"; run.mkdir()
        (run / "manifest.csv").write_text(
            "run_id,task_id,sample_id,preset,status,return_code,elapsed_seconds\n"
            "R1,T1,S1,warm_vocal,done,0,5.0\n")
        cfg = RuntimeConfig(project_root=Path(d), output_root=out,
                            report_dir=Path(d) / "reports")
        cfg.report_dir.mkdir(exist_ok=True)
        result = generate_daily_report(cfg)
        assert isinstance(result, dict)
