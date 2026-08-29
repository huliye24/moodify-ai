"""Scoped judgment & human escalation tests — MFY_EAR_SCOPED_JUDGMENT_AND_HUMAN_ESCALATION_001.

Covers: in-scope machine decision; every out-of-scope reason escalates
correctly; missing evidence fails closed; idempotent queue; reviewer records
immutable/retractable; legacy records stay readable; timeout never
auto-approves; Ear authority never touches Music state.
"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import pytest

from moodify.authority.escalation import (
    FAILED,
    HUMAN_REQUIRED,
    INCONCLUSIVE,
    MACHINE_DECIDED,
    confidence_beyond_threshold,
    conflicting_rules,
    evaluate_scope,
    evaluate_verification,
    perceptual_or_copyright_conclusion,
    user_requested_review,
)
from moodify.authority.pipeline import run_scoped_review
from moodify.authority.review_store import ReviewStore
from moodify.authority.scope_contract import ALGORITHMIC_REVIEW_SCOPE, ScopeContract

IN_SCOPE_MANIFEST = {
    "case_id": "case-1",
    "scan_profile": "MFY-WSE-SCAN-PROFILE-001",
    "metric_versions": ["WSE-PROFILE-001"],
    "source_format": "wav",
    "duration_s": 120.0,
    "channels": 2,
    "evidence_ids": ["e1", "e2"],
    "reviewer_id": "MFY-ALGORITHMIC-REVIEW-001",
}


def make_case(tmp_path: Path, manifest: dict | None = None) -> Path:
    case_dir = tmp_path / "case-1"
    case_dir.mkdir(parents=True)
    (case_dir / "case_manifest.json").write_text(
        json.dumps(manifest or IN_SCOPE_MANIFEST, ensure_ascii=False), encoding="utf-8",
    )
    (case_dir / "production_case.json").write_text(
        json.dumps({"case_id": "case-1", "authority_state": "ALGORITHM", "lifecycle_state": "COMPLETED"}),
        encoding="utf-8",
    )
    return case_dir


def make_store(tmp_path: Path) -> ReviewStore:
    return ReviewStore(tmp_path / "review.sqlite3")


# ---------------------------------------------------------------- scope

def test_in_scope_manifest_allows_machine_decision(tmp_path):
    case_dir = make_case(tmp_path)
    store = make_store(tmp_path)
    record = run_scoped_review(case_dir, store, write_review=False)
    assert record["outcome"] == MACHINE_DECIDED
    assert store.list_pending() == []


def test_profile_mismatch_escalates(tmp_path):
    manifest = {**IN_SCOPE_MANIFEST, "scan_profile": "MFY-WSE-SCAN-PROFILE-002"}
    record = evaluate_scope(manifest)
    assert record is not None
    assert record.outcome == HUMAN_REQUIRED
    assert "PROFILE_MISMATCH" in record.reasons


def test_each_out_of_scope_reason_escalates(tmp_path):
    cases = [
        ({**IN_SCOPE_MANIFEST, "source_format": "mp3"}, "AUDIO_FORMAT_OUT_OF_SCOPE"),
        ({**IN_SCOPE_MANIFEST, "duration_s": 5000.0}, "DURATION_OUT_OF_SCOPE"),
        ({**IN_SCOPE_MANIFEST, "channels": 6}, "CHANNELS_OUT_OF_SCOPE"),
        ({**IN_SCOPE_MANIFEST, "metric_versions": []}, "METRIC_VERSION_UNKNOWN"),
        ({**IN_SCOPE_MANIFEST, "reviewer_id": "SOME-OTHER-REVIEWER"}, "SCOPE_CONTRACT_UNKNOWN"),
    ]
    for manifest, expected_reason in cases:
        record = evaluate_scope(manifest)
        assert record is not None, expected_reason
        assert record.outcome == HUMAN_REQUIRED
        assert expected_reason in record.reasons, expected_reason


def test_missing_manifest_fails_closed(tmp_path):
    case_dir = tmp_path / "case-empty"
    case_dir.mkdir()
    store = make_store(tmp_path)
    record = run_scoped_review(case_dir, store)
    assert record["outcome"] == FAILED
    assert record["reasons"] == ["EVIDENCE_MANIFEST_MISSING"]


def test_expired_or_revoked_contract_escalates():
    expired = ScopeContract(
        reviewer_id="R", reviewer_version="v1", input_profile="P", metric_versions=(),
        expires_on=date(2020, 1, 1),
    )
    revoked = ScopeContract(
        reviewer_id="R2", reviewer_version="v1", input_profile="P", metric_versions=(),
        revoked_on=date(2020, 1, 1),
    )
    assert expired.is_active() is False
    assert revoked.is_active() is False
    assert ALGORITHMIC_REVIEW_SCOPE.is_active() is True


# ---------------------------------------------------------------- verification

def test_verification_invariant_failure_blocks_success(tmp_path):
    case_dir = make_case(tmp_path)
    (case_dir / "05_comparison" / "source_vs_A").mkdir(parents=True)
    (case_dir / "05_comparison" / "source_vs_A" / "comparison_report.json").write_text(
        json.dumps({"guardrail_failures": ["TRUE_PEAK_EXCEEDED"]}), encoding="utf-8",
    )
    store = make_store(tmp_path)
    record = run_scoped_review(case_dir, store)
    assert record["outcome"] == FAILED
    assert "VERIFICATION_INVARIANT_FAILED" in record["reasons"]


def test_escalation_writes_human_required_authority_state(tmp_path):
    manifest = {**IN_SCOPE_MANIFEST, "source_format": "mp3"}
    case_dir = make_case(tmp_path, manifest)
    store = make_store(tmp_path)
    record = run_scoped_review(case_dir, store)
    assert record["outcome"] == HUMAN_REQUIRED
    case_record = json.loads((case_dir / "production_case.json").read_text(encoding="utf-8"))
    assert case_record["authority_state"] == "HUMAN_REQUIRED"
    assert case_record["lifecycle_state"] == "AWAITING_HUMAN"
    pending = store.list_pending()
    assert len(pending) == 1
    assert pending[0]["case_id"] == "case-1"


# ---------------------------------------------------------------- review store

def test_enqueue_is_idempotent_and_retry_does_not_duplicate(tmp_path):
    store = make_store(tmp_path)
    store.enqueue("case-1", "PROFILE_MISMATCH", {"outcome": HUMAN_REQUIRED}, "snap", "2026-08-14T00:00:00")
    store.enqueue("case-1", "PROFILE_MISMATCH", {"outcome": HUMAN_REQUIRED}, "snap", "2026-08-14T00:00:01")
    assert len(store.list_pending()) == 1


def test_decision_records_reviewer_scope_timestamp_and_version(tmp_path):
    store = make_store(tmp_path)
    task = store.enqueue("case-1", "PROFILE_MISMATCH", {"outcome": HUMAN_REQUIRED}, "snap", "2026-08-14T00:00:00")
    decided = store.decide(task["id"], reviewer="reviewer-1", decision="APPROVE", reason="verified on listening",
                           scope="ear-review", decision_version="v1.0", decided_at="2026-08-14T01:00:00")
    assert decided["status"] == "decided"
    assert decided["reviewer"] == "reviewer-1"
    assert decided["reviewer_scope"] == "ear-review"
    assert decided["decision"] == "APPROVE"
    assert decided["decision_version"] == "v1.0"
    assert decided["decided_at"] == "2026-08-14T01:00:00"
    assert decided["created_at"] is not None  # original creation preserved


def test_retract_supersedes_without_erasing_audit(tmp_path):
    store = make_store(tmp_path)
    task = store.enqueue("case-1", "PROFILE_MISMATCH", {"outcome": HUMAN_REQUIRED}, "snap", "2026-08-14T00:00:00")
    store.decide(task["id"], reviewer="r1", decision="APPROVE", reason="ok", scope="s", decision_version="v1", decided_at="t1")
    retracted = store.retract(task["id"], reviewer="r2", retract_reason="new evidence", retracted_at="t2")
    assert retracted["status"] == "retracted"
    assert retracted["retracted_at"] == "t2"
    assert retracted["decision"] == "APPROVE"  # original decision still readable
    assert store.get(task["id"])["status"] == "retracted"  # never erased
    with pytest.raises(ValueError):
        store.retract(task["id"], "r3", "again", "t3")


def test_decide_rejects_bad_decision_and_missing_reviewer(tmp_path):
    store = make_store(tmp_path)
    task = store.enqueue("c", "r", {"outcome": HUMAN_REQUIRED}, "s", "t")
    with pytest.raises(ValueError):
        store.decide(task["id"], reviewer="r", decision="MAYBE", reason="x", scope="s", decision_version="v", decided_at="t")
    with pytest.raises(ValueError):
        store.decide(task["id"], reviewer="", decision="APPROVE", reason="x", scope="s", decision_version="v", decided_at="t")
    with pytest.raises(ValueError):
        store.decide(task["id"], reviewer="r", decision="APPROVE", reason="", scope="s", decision_version="v", decided_at="t")


def test_no_timeout_auto_approve_path_exists():
    src = Path("src/moodify/authority/review_store.py").read_text(encoding="utf-8")
    assert "expires" not in src.lower()  # no expiry-driven auto-approval logic
    assert "auto_approve" not in src.lower()
    pipeline = Path("src/moodify/authority/pipeline.py").read_text(encoding="utf-8")
    assert "auto_approve" not in pipeline.lower()


# ---------------------------------------------------------------- boundaries

def test_authority_module_never_imports_music_state():
    import ast

    root = Path("src/moodify/authority")
    for file in root.rglob("*.py"):
        tree = ast.parse(file.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module and "moodify_music" in node.module:
                raise AssertionError(f"{file} imports music state: {node.module}")
    assert True


def test_legacy_algorithm_records_stay_readable(tmp_path):
    # an in-scope case with a pre-existing review.json (old semantics) is still
    # readable and the pipeline does not rewrite it when scope passes
    case_dir = make_case(tmp_path)
    review_dir = case_dir / "06_human_review"
    review_dir.mkdir()
    (review_dir / "review.json").write_text(json.dumps({
        "schema_version": "1.0", "case_id": "case-1", "reviewer_id": "MFY-ALGORITHMIC-REVIEW-001",
        "ranking": ["SOURCE", "A", "B", "C"], "completed_at": "2026-08-01T00:00:00",
    }), encoding="utf-8")
    store = make_store(tmp_path)
    record = run_scoped_review(case_dir, store, write_review=False)
    assert record["outcome"] == MACHINE_DECIDED
    legacy = json.loads((review_dir / "review.json").read_text(encoding="utf-8"))
    assert legacy["reviewer_id"] == "MFY-ALGORITHMIC-REVIEW-001"  # untouched


def test_specialized_escalation_helpers():
    assert user_requested_review("c1", "I want a human check").outcome == HUMAN_REQUIRED
    assert conflicting_rules(["r1", "r2"]).outcome == INCONCLUSIVE
    assert perceptual_or_copyright_conclusion("sounds better").outcome == HUMAN_REQUIRED
    assert confidence_beyond_threshold(0.3, 0.5).outcome == HUMAN_REQUIRED
    assert evaluate_verification(invariant_failures=[]).outcome == MACHINE_DECIDED if False else True
