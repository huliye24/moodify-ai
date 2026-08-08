"""case pairwise-judge / pairwise-decision CLI registration tests."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from unittest.mock import patch

from moodify.cli_v2.main import CLIError, cmd_case_pairwise_decision, cmd_case_pairwise_judge

FAKE_RESULT = {
    "judgment_id": "jud-123",
    "outcome": "A_WINS",
    "confidence_level": "HIGH",
    "winner_margin": 0.65,
    "evidence_coverage": 0.85,
    "top_reasons": ["WINNER_MARGIN=0.650"],
    "analysis_failed": [],
    "judgment_dir": "x",
}


def _project(tmp_path: Path) -> Path:
    project = tmp_path / "project"
    project.mkdir()
    valid = {"schema_version": "1.0.0", "title": "t", "project_id": "p-1",
             "assets": {}, "plans": {}, "runs": {}}
    (project / "project.json").write_text(json.dumps(valid), encoding="utf-8")
    (project / "cases" / "PW-1").mkdir(parents=True)
    return project


def test_pairwise_judge_registered(tmp_path: Path) -> None:
    project = _project(tmp_path)
    a = tmp_path / "a.wav"
    b = tmp_path / "b.wav"
    a.write_bytes(b"RIFF-a")
    b.write_bytes(b"RIFF-b")
    args = argparse.Namespace(project_dir=str(project), case_id="PW-1",
                              candidate_a=str(a), candidate_b=str(b), config=None)
    with patch("moodify.evaluation.pairwise.service.run_pairwise_judge", return_value=FAKE_RESULT) as mocked:
        result = cmd_case_pairwise_judge(args)
    assert result["status"] == "ok"
    assert result["result_status"] == "PAIRWISE_JUDGMENT_COMPLETED"
    assert result["outcome"] == "A_WINS"
    assert mocked.call_count == 1


def test_pairwise_decision_requires_prior_judgment(tmp_path: Path) -> None:
    project = _project(tmp_path)
    args = argparse.Namespace(project_dir=str(project), case_id="PW-1",
                              decision="CHOOSE_B", reason="prefer B")
    with patch("moodify.evaluation.pairwise.service.record_human_decision") as mocked:
        try:
            cmd_case_pairwise_decision(args)
            raise AssertionError("expected CLIError")
        except CLIError as exc:
            assert exc.code == "PAIRWISE_JUDGMENT_NOT_FOUND"
    mocked.assert_not_called()


def test_pairwise_decision_records_from_stored_judgment(tmp_path: Path) -> None:
    project = _project(tmp_path)
    pairwise_dir = project / "cases" / "PW-1" / "06_pairwise"
    pairwise_dir.mkdir()
    (pairwise_dir / "judgment.json").write_text(
        json.dumps({"outcome": "B_WINS", "confidence_level": "MEDIUM"}), encoding="utf-8"
    )
    args = argparse.Namespace(project_dir=str(project), case_id="PW-1",
                              decision="CONFIRM_MODEL", reason="")
    with patch("moodify.evaluation.pairwise.service.record_human_decision",
               return_value={"human_decision": {"decision": "CONFIRM_MODEL"},
                             "preference_record": {"label_source": "HUMAN_CONFIRMED"}}) as mocked:
        result = cmd_case_pairwise_decision(args)
    assert result["status"] == "ok"
    assert result["result_status"] == "PAIRWISE_HUMAN_DECISION_RECORDED"
    mocked.assert_called_once()
    assert mocked.call_args.kwargs["machine_outcome"] == "B_WINS"
