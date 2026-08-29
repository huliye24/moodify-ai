"""run_golden_pipeline parameterization regression (MFY-CR-P08).

Default-argument behavior must remain identical to P06; explicit overrides
(case_id / record_id / skip_blind_kit / candidates_dir) must take effect.
"""

from __future__ import annotations

import json

import pytest

from moodify.reconstruction.pipeline import run_golden_pipeline

pytestmark = pytest.mark.v01


def test_defaults_preserve_p06_behavior(mock_wav, tmp_path):
    result = run_golden_pipeline(mock_wav, tmp_path)
    assert result.record.record_id == "GOLDEN-001-source"
    assert result.record.technical_result["technical_top"] in ("SOURCE", "A", "B", "C")
    assert (tmp_path / "candidates").is_dir()
    assert (tmp_path / "golden_record.json").is_file()
    # default keeps the blind kit materialised
    assert result.blind_kit  # non-empty when blind kit is generated


def test_case_id_propagates_to_diagnostics_and_interventions(mock_wav, tmp_path):
    result = run_golden_pipeline(mock_wav, tmp_path, case_id="case_custom")
    assert all(f.production_case_id == "case_custom" for f in result.diagnostics)
    record = json.loads((tmp_path / "golden_record.json").read_text(encoding="utf-8"))
    assert record["record_id"] == "GOLDEN-001-source"


def test_record_id_override(mock_wav, tmp_path):
    result = run_golden_pipeline(mock_wav, tmp_path, record_id="job_custom")
    assert result.record.record_id == "job_custom"


def test_skip_blind_kit_leaves_empty_kit_and_no_kit_files(mock_wav, tmp_path):
    result = run_golden_pipeline(mock_wav, tmp_path, skip_blind_kit=True)
    assert result.blind_kit == {}
    assert not (tmp_path / "blind_kit").exists()


def test_candidates_dir_override(mock_wav, tmp_path):
    target = tmp_path / "ws" / "candidates"
    result = run_golden_pipeline(mock_wav, tmp_path, candidates_dir=target)
    assert target.is_dir()
    non_source = [c for c in result.candidates if c != "SOURCE"]
    for cid in non_source:
        assert (target / f"{cid}.wav").is_file()
