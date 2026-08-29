"""MFY-ALGORITHMIC-REVIEW-001 deterministic review tests.

The review formula is frozen; these tests lock the scoring semantics so a
formula change is a deliberate, versioned act.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from moodify.data_factory.algorithmic_review import (
    GOAL_MET_POINTS,
    BLOCKING_GUARDRAIL_PENALTY,
    WARNING_RISK_PENALTY,
    _candidate_score,
    generate_algorithmic_review,
    write_algorithmic_review,
)


def _report(goals_met=None, guardrail_failures=None, warnings=None, assessment=None):
    risk_flags = [
        {"code": f"W{i}", "severity": "WARNING", "message": "w"} for i in range(warnings or 0)
    ]
    return {
        "judgment": {
            "technical_assessment": assessment or (
                "DEGRADED" if guardrail_failures else ("IMPROVED" if goals_met else "NEUTRAL")
            ),
            "workflow_decision": "PASS_TO_LISTENING",
            "goals_met": goals_met or [],
            "guardrail_failures": guardrail_failures or [],
            "risk_flags": risk_flags,
        }
    }


def test_score_rewards_goals_and_punishes_warnings():
    score, detail = _candidate_score(_report(goals_met=["G1", "G2"], warnings=1))
    assert score == pytest.approx(2 * GOAL_MET_POINTS - WARNING_RISK_PENALTY)
    assert detail["goals_met"] == ["G1", "G2"]
    assert detail["warning_count"] == 1


def test_blocking_guardrail_dominates_any_goal_progress():
    score, _ = _candidate_score(
        _report(goals_met=["G1", "G2", "G3"], guardrail_failures=["TRUE_PEAK_SAFE"])
    )
    assert score == pytest.approx(3 * GOAL_MET_POINTS - BLOCKING_GUARDRAIL_PENALTY)
    assert score < 0


def test_baseline_source_scores_zero():
    review = generate_algorithmic_review(_case_dir_with([]))
    scores = json.loads(review["notes"])
    assert scores["SOURCE"]["score"] == 0.0


def test_rejected_candidates_listed_when_blocking():
    case = _case_dir_with(
        [
            ("A", _report(goals_met=["G1"])),
            ("B", _report(guardrail_failures=["TRUE_PEAK_SAFE"])),
            ("C", _report(goals_met=["G1", "G2"])),
        ]
    )
    review = generate_algorithmic_review(case)
    assert review["rejected"] == ["B"]
    assert review["ranking"][0] == "C"  # highest score first
    assert review["ranking"][-1] == "B"


def test_ranking_deterministic_across_calls():
    case = _case_dir_with([("A", _report(goals_met=["G1"])), ("B", _report(goals_met=["G1"]))])
    first = generate_algorithmic_review(case)
    second = generate_algorithmic_review(case)
    assert first["ranking"] == second["ranking"]


def test_write_persists_review_and_scores(tmp_path):
    case = _case_dir_with([("A", _report(goals_met=["G1"]))], root=tmp_path / "case")
    review_path = write_algorithmic_review(case)
    review = json.loads(review_path.read_text(encoding="utf-8"))
    assert review["reviewer_id"].startswith("algorithm:")
    assert len(review["ranking"]) == 4
    assert (case / "06_human_review" / "algorithmic_scores.json").is_file()


def test_missing_comparison_report_raises(tmp_path):
    case = tmp_path / "case"
    (case / "05_comparison").mkdir(parents=True)
    (case / "case_manifest.json").write_text(
        json.dumps({"case_id": "case_x"}), encoding="utf-8"
    )
    with pytest.raises(FileNotFoundError):
        generate_algorithmic_review(case)


def _case_dir_with(candidates, root=None) -> Path:
    import tempfile

    root = root or Path(tempfile.mkdtemp())
    case = root
    (case / "05_comparison").mkdir(parents=True, exist_ok=True)
    (case / "06_human_review").mkdir(parents=True, exist_ok=True)
    (case / "case_manifest.json").write_text(
        json.dumps({"case_id": "case_test"}), encoding="utf-8"
    )
    supplied = dict(candidates)
    for label in ("A", "B", "C"):
        report = supplied.get(label) or _report()
        d = case / "05_comparison" / f"source_vs_{label}"
        d.mkdir(parents=True, exist_ok=True)
        (d / "comparison_report.json").write_text(
            json.dumps(report, ensure_ascii=False), encoding="utf-8"
        )
    return case
