"""Learning workflow + export tests (DSK-MFY-AUDITORY-INTELLIGENCE-RECLASSIFICATION-001)."""

from __future__ import annotations

import json

import pytest

from moodify.learning.errors import (
    LearningRecordIncomplete,
    LearningRecordNotReviewed,
)
from moodify.learning.exports import export_learning_records, validate_export_bundle
from moodify.learning.models import (
    CandidateOutcome,
    HumanListeningEvaluation,
    LearningRecord,
    PairwisePreference,
    RightsMetadata,
)
from moodify.learning.service import (
    build_learning_record,
    commit_learning_record,
    review_learning_record,
)
from moodify.learning.store import CaseLearningStore

S64 = "a" * 64


def _fake_case(tmp_path, with_evidence=True, with_evaluation=True):
    """Build a case directory shaped like a scanned case."""
    case_root = tmp_path / "cases" / "MFY-CASE-L"
    (case_root / "01_before_scan").mkdir(parents=True)
    (case_root / "05_comparison").mkdir(parents=True)
    if with_evidence:
        (case_root / "01_before_scan" / "scan_manifest.json").write_text(
            json.dumps({"input_sha256": S64}), encoding="utf-8"
        )
        (case_root / "05_comparison" / "comparison_report.json").write_text(
            json.dumps({"case_id": "MFY-CASE-L"}), encoding="utf-8"
        )
    store = CaseLearningStore(case_root)
    if with_evaluation:
        store.save_evaluation(HumanListeningEvaluation(
            evaluation_id="EV-1", case_id="MFY-CASE-L", candidate_ids=["K1"],
            evaluator_id="e", approval_status="APPROVED",
        ))
    return store


def test_build_incomplete_evidence_fails_closed(tmp_path):
    store = _fake_case(tmp_path, with_evidence=False)
    with pytest.raises(LearningRecordIncomplete):
        build_learning_record(store, "MFY-CASE-L")


def test_build_and_commit_cycle(tmp_path):
    store = _fake_case(tmp_path)
    record = build_learning_record(store, "MFY-CASE-L")
    assert record.learning_status in ("CAPTURED", "CAPTURE_PENDING")
    assert record.training_eligibility != "ELIGIBLE"
    assert record.candidate_ids == []

    rights = RightsMetadata(
        rights_holder="owner", model_training_authorized="YES",
        derivative_data_authorized="YES", research_use_authorized="YES",
        processing_authorization="YES", commercial_training_authorized="YES",
        reviewed_by="reviewer",
    )
    reviewed = review_learning_record(store, "MFY-CASE-L", rights)
    assert reviewed.training_eligibility == "ELIGIBLE"
    assert reviewed.review_status == "REVIEWED"

    committed = commit_learning_record(store, "MFY-CASE-L", "reviewer")
    assert committed.learning_status == "COMMITTED"


def test_commit_without_review_rejected(tmp_path):
    store = _fake_case(tmp_path)
    build_learning_record(store, "MFY-CASE-L")
    with pytest.raises(LearningRecordNotReviewed):
        commit_learning_record(store, "MFY-CASE-L", "reviewer")


def test_explicit_exclusion_when_ineligible(tmp_path):
    store = _fake_case(tmp_path)
    build_learning_record(store, "MFY-CASE-L")
    rights = RightsMetadata(rights_holder="owner", model_training_authorized="NO")
    reviewed = review_learning_record(store, "MFY-CASE-L", rights)
    assert reviewed.training_eligibility == "INELIGIBLE"
    committed = commit_learning_record(store, "MFY-CASE-L", "reviewer")
    assert committed.learning_status == "EXCLUDED"


def test_learning_commit_idempotent(tmp_path):
    store = _fake_case(tmp_path)
    build_learning_record(store, "MFY-CASE-L")
    rights = RightsMetadata(
        rights_holder="o", model_training_authorized="YES",
        derivative_data_authorized="YES", research_use_authorized="YES",
        processing_authorization="YES", commercial_training_authorized="YES",
        reviewed_by="r",
    )
    review_learning_record(store, "MFY-CASE-L", rights)
    first = commit_learning_record(store, "MFY-CASE-L", "r")
    second = commit_learning_record(store, "MFY-CASE-L", "r")
    assert first.learning_status == second.learning_status == "COMMITTED"
    assert first.learning_record_id == second.learning_record_id


def _eligible_record(case_id="C1"):
    return LearningRecord(
        learning_record_id=f"LR-{case_id}", case_id=case_id, source_sha256=S64,
        candidate_ids=["K1"],
        rights=RightsMetadata(rights_holder="o", model_training_authorized="YES"),
        training_eligibility="ELIGIBLE",
        review_status="REVIEWED", learning_status="COMMITTED",
    )


def test_export_only_eligible(tmp_path):
    eligible = _eligible_record()
    ineligible = _eligible_record("C2")
    ineligible.training_eligibility = "UNKNOWN"
    ineligible.exclusion_reasons = ["unknown rights"]
    manifest = export_learning_records([eligible, ineligible], tmp_path / "out", "DS-1")
    assert manifest["included_count"] == 1
    assert manifest["excluded_count"] == 1
    included = json.loads((tmp_path / "out" / "DS-1_records.json").read_text(encoding="utf-8"))
    assert [r["case_id"] for r in included] == ["C1"]
    excluded = json.loads((tmp_path / "out" / "DS-1_excluded.json").read_text(encoding="utf-8"))
    assert excluded[0]["training_eligibility"] == "UNKNOWN"


def test_export_fails_closed_on_ambiguous(tmp_path):
    records = [_eligible_record("C1")]
    records[0].training_eligibility = "PENDING_REVIEW"
    manifest = export_learning_records(records, tmp_path / "out", "DS-2")
    assert manifest["included_count"] == 0
    assert manifest["excluded_count"] == 1


def test_export_manifest_hashes_verify(tmp_path):
    records = [_eligible_record("C1"), _eligible_record("C2")]
    export_learning_records(records, tmp_path / "out", "DS-3")
    problems = validate_export_bundle(tmp_path / "out", "DS-3")
    assert problems == []


def test_export_deterministic(tmp_path):
    records = [_eligible_record("C1")]
    export_learning_records(records, tmp_path / "out1", "DS-4")
    export_learning_records(records, tmp_path / "out2", "DS-4")
    a = (tmp_path / "out1" / "DS-4_records.json").read_text(encoding="utf-8")
    b = (tmp_path / "out2" / "DS-4_records.json").read_text(encoding="utf-8")
    assert a == b


def test_preferences_and_outcomes_retained(tmp_path):
    store = _fake_case(tmp_path)
    store.append_preference(PairwisePreference(case_id="C", preferred_candidate_id="K1",
                                               other_candidate_id="K2"))
    store.append_outcome(CandidateOutcome(case_id="C", candidate_id="K1", outcome="ACCEPTED"))
    store.append_outcome(CandidateOutcome(case_id="C", candidate_id="K2", outcome="REJECTED"))
    record = build_learning_record(store, "MFY-CASE-L")
    assert len(record.pairwise_preferences) == 1
    assert {o.candidate_id for o in record.candidate_outcomes} == {"K1", "K2"}
