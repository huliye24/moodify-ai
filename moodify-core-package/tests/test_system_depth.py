import json

import pytest

from moodify.system_depth import (
    DepthRecord,
    KnowledgeKind,
    KnowledgeStatus,
    active_depth,
    append_depth_record,
    assess_depth,
    read_depth_ledger,
)


def record(**overrides):
    values = {
        "kind": KnowledgeKind.FAILURE_BOUNDARY,
        "scope": "score.export",
        "lesson": "Never report an unavailable renderer as successful.",
        "rationale": "A missing backend previously produced deceptive success.",
        "evidence_refs": ("failure-ledger#missing-renderer",),
        "guard_refs": ("tests/test_backend.py::test_missing_backend",),
        "observed_at": "2026-08-02T00:00:00+00:00",
        "recorded_at": "2026-08-02T01:00:00+00:00",
    }
    values.update(overrides)
    return DepthRecord(**values)


def test_record_id_is_stable_across_recording_time():
    first = record(recorded_at="2026-08-02T01:00:00+00:00")
    later = record(recorded_at="2026-08-03T01:00:00+00:00")
    assert first.record_id == later.record_id


def test_append_is_idempotent_and_history_is_strict(tmp_path):
    path = tmp_path / "depth.jsonl"
    item = record()
    assert append_depth_record(path, item) == "stored"
    assert append_depth_record(path, item) == "skipped"
    conflicting = record(record_id=item.record_id, lesson="Different lesson")
    with pytest.raises(ValueError, match="record_id conflict"):
        append_depth_record(path, conflicting)
    assert read_depth_ledger(path) == [item]


def test_unknown_fields_fail_closed(tmp_path):
    path = tmp_path / "depth.jsonl"
    value = record().to_dict()
    value["surprise"] = True
    path.write_text(json.dumps(value) + "\n", encoding="utf-8")
    with pytest.raises(ValueError, match="unknown system-depth fields"):
        read_depth_ledger(path)


def test_supersession_is_explicit_and_queryable(tmp_path):
    path = tmp_path / "depth.jsonl"
    old = record()
    append_depth_record(path, old)
    replacement = record(
        record_id="depth-replacement",
        lesson="Renderer absence must be exposed as UNAVAILABLE.",
        supersedes=(old.record_id,),
    )
    append_depth_record(path, replacement)
    assert active_depth(read_depth_ledger(path)) == [replacement]


def test_unknown_supersession_is_rejected(tmp_path):
    with pytest.raises(ValueError, match="supersedes unknown records"):
        append_depth_record(
            tmp_path / "depth.jsonl",
            record(record_id="new", supersedes=("missing",)),
        )


def test_depth_audit_exposes_unresolved_knowledge():
    uncertainty = record(
        kind=KnowledgeKind.INTERFACE_UNCERTAINTY,
        record_id="depth-uncertain",
        evidence_refs=(),
        guard_refs=(),
        limitations=(),
    )
    result = assess_depth([uncertainty])
    assert result["ready"] is False
    assert result["truthful_interface"] is False
    assert {gap["gap"] for gap in result["gaps"]} == {
        "missing_guard",
        "missing_evidence",
        "uncertainty_not_exposed",
    }


def test_depth_audit_accepts_operational_inheritable_knowledge():
    result = assess_depth([record()])
    assert result == {
        "schema": "moodify.system-depth/0.1",
        "active_records": 1,
        "operationalized_records": 1,
        "inheritable_records": 1,
        "truthful_interface": True,
        "ready": True,
        "gaps": [],
    }


def test_retired_knowledge_is_preserved_but_not_active():
    retired = record(status=KnowledgeStatus.RETIRED)
    assert active_depth([retired]) == []
