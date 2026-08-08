"""Independent regression tests for rights and MRS authority gates."""

import json
from pathlib import Path

from moodify_runtime.hardening_gates import (
    MRS_AUTHORITY_STATEMENT,
    authorize_audio_source,
    check_rights_cleared,
    is_rights_pending_audio,
    mrs_can_release,
)


def _write_manifest(path: Path, statuses: list[tuple[str, str]]) -> Path:
    path.write_text(json.dumps({
        "schema_version": "1.0.0",
        "gate_id": "TEST-RIGHTS",
        "assets": [
            {"asset_id": asset_id, "source_path": f"C:/audio/{asset_id}.wav", "status": status}
            for asset_id, status in statuses
        ],
    }), encoding="utf-8")
    return path


def test_missing_manifest_fails_closed(tmp_path):
    result = check_rights_cleared(tmp_path / "missing.json")
    assert result["rights_cleared"] is False
    assert result["errors"]


def test_malformed_manifest_fails_closed(tmp_path):
    path = tmp_path / "rights.json"
    path.write_text("{bad", encoding="utf-8")
    result = check_rights_cleared(path)
    assert result["rights_cleared"] is False
    assert "invalid rights manifest" in result["errors"][0]


def test_all_assets_must_be_explicitly_ready(tmp_path):
    path = _write_manifest(tmp_path / "rights.json", [("VS-001", "ready"), ("VS-002", "pending")])
    result = check_rights_cleared(path)
    assert result["total_assets"] == 2
    assert result["ready_count"] == 1
    assert result["pending_count"] == 1
    assert result["rights_cleared"] is False


def test_all_ready_passes(tmp_path):
    path = _write_manifest(tmp_path / "rights.json", [("VS-001", "ready"), ("VS-002", "ready")])
    result = check_rights_cleared(path)
    assert result["rights_cleared"] is True
    assert result["ready_assets"] == ["VS-001", "VS-002"]


def test_unknown_status_and_duplicate_id_fail_closed(tmp_path):
    path = _write_manifest(tmp_path / "rights.json", [("VS-001", "ready"), ("VS-001", "granted")])
    result = check_rights_cleared(path)
    assert result["rights_cleared"] is False
    assert any("duplicate asset_id" in error for error in result["errors"])


def test_asset_lookup_is_fail_closed(tmp_path):
    path = _write_manifest(tmp_path / "rights.json", [("VS-001", "ready"), ("VS-002", "blocked")])
    assert is_rights_pending_audio(path, "VS-001") is False
    assert is_rights_pending_audio(path, "VS-002") is True
    assert is_rights_pending_audio(path, "UNKNOWN") is True


def test_authorization_binds_ready_asset_to_exact_source_path(tmp_path):
    source = tmp_path / "source.wav"
    path = _write_manifest(tmp_path / "rights.json", [("VS-001", "ready")])
    data = json.loads(path.read_text(encoding="utf-8"))
    data["assets"][0]["source_path"] = str(source)
    path.write_text(json.dumps(data), encoding="utf-8")
    assert authorize_audio_source(path, "VS-001", source) == (True, "ok")
    allowed, reason = authorize_audio_source(path, "VS-001", tmp_path / "other.wav")
    assert allowed is False
    assert "source path" in reason


def test_feedback_fields_cannot_be_used_as_rights_manifest(tmp_path):
    path = tmp_path / "treatment.json"
    path.write_text(json.dumps({
        "record_type": "moodify_treatment_record",
        "human_feedback": {"status": "completed"},
    }), encoding="utf-8")
    result = check_rights_cleared(path)
    assert result["rights_cleared"] is False
    assert result["errors"]


def test_mrs_alone_is_rejected():
    allowed, reason = mrs_can_release(mrs_score=100.0, human_approved=False)
    assert allowed is False
    assert "human listening approval required" in reason


def test_human_approval_is_required_even_without_score():
    allowed, reason = mrs_can_release(mrs_score=None, human_approved=True)
    assert allowed is True
    assert reason == "ok"


def test_authority_statement_preserves_historic_risk_metrics():
    assert "9.1%" in MRS_AUTHORITY_STATEMENT
    assert "0.19" in MRS_AUTHORITY_STATEMENT
    assert "60.6%" in MRS_AUTHORITY_STATEMENT
