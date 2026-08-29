"""Batch factory tests (MFY-CR-P07)."""

from __future__ import annotations

import pytest

from moodify.reconstruction_factory.factory import (
    ProposedRuleUpdate,
    run_reconstruction_batch,
)
from moodify.reconstruction_factory.learning_record import build_learning_record
from moodify.reconstruction_factory.rights import default_rights

pytestmark = pytest.mark.v01

VERSIONS = {"diagnostic": "v1", "engine": "v1"}


def _ok_case(case_id: str, source_hash: str = "hash_x") -> dict[str, object]:
    return {"case_id": case_id, "source_hash": source_hash, "rights": default_rights()}


def _proc(case: dict[str, object]):
    return build_learning_record(
        str(case["case_id"]), str(case["source_hash"]), default_rights(), {}, VERSIONS,
        golden_status="SOURCE_WINS",
    )


def test_serial_batch_processes_all():
    cases = [_ok_case("T01"), _ok_case("T02"), _ok_case("T03")]
    result = run_reconstruction_batch(cases, _proc)
    assert len(result.records) == 3
    assert result.metrics["tracks_total"] == 3
    assert result.metrics["source_wins"] == 3


def test_duplicate_source_preserved_not_silent():
    cases = [_ok_case("T01"), _ok_case("T01")]  # same case_id + hash
    result = run_reconstruction_batch(cases, _proc)
    assert len(result.records) == 1
    assert len(result.failures) == 1
    assert result.failures[0].failure_code == "DUPLICATE_SOURCE"


def test_failure_preserved_with_code_and_stage():
    def boom(case):
        raise RuntimeError("decoder exploded")

    cases = [_ok_case("T01")]
    result = run_reconstruction_batch(cases, boom)
    assert len(result.records) == 0
    assert len(result.failures) == 1
    f = result.failures[0]
    assert f.failure_code == "ENGINE_FAILURE"
    assert f.stage == "process_case"
    assert f.human_action == "REQUIRED"
    assert "decoder exploded" in f.detail


def test_rights_blocked_preserved():
    cases = [{"case_id": "T09", "source_hash": "h", "rights": {"rights_status": "SCRAPED", "processing_permission": True}}]
    result = run_reconstruction_batch(cases, _proc)
    assert len(result.records) == 0
    assert result.failures[0].failure_code == "RIGHTS_BLOCKED"
    assert result.failures[0].human_action == "REQUIRED"


def test_idempotent_across_batches_with_seen():
    seen: set[str] = set()
    r1 = run_reconstruction_batch([_ok_case("T01")], _proc, seen_ids=seen)
    r2 = run_reconstruction_batch([_ok_case("T01")], _proc, seen_ids=seen)
    assert len(r1.records) == 1
    assert len(r2.records) == 0
    assert r2.failures[0].failure_code == "DUPLICATE_SOURCE"


def test_threshold_updates_only_proposed_never_applied():
    proposal = ProposedRuleUpdate(
        proposal_id="pr1", target="clip_threshold", current_value="0.999", proposed_value="0.995",
        evidence_refs=("rlr_x",),
    )
    result = run_reconstruction_batch([_ok_case("T01")], lambda c: proposal)
    assert len(result.proposals) == 1
    assert result.proposals[0].status == "PENDING_REVIEW"
    # no production threshold was touched (factory has no threshold write path)
    assert len(result.records) == 0


def test_batch_result_json_serializable(tmp_path):
    result = run_reconstruction_batch([_ok_case("T01")], _proc)
    out = tmp_path / "batch.json"
    result.to_json(str(out))
    import json

    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload["version"] == "reconstruction-batch-v1"
    assert payload["metrics"]["tracks_total"] == 1
