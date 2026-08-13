"""Machine Finding contract tests — allowed vs forbidden conclusions, provenance."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest
from pydantic import ValidationError

from datetime import datetime, timezone

from moodify.contracts import (
    FORBIDDEN_CONCLUSIONS,
    FindingType,
    MachineFinding,
    Provenance,
)

SCHEMAS = Path(__file__).resolve().parents[3] / "schemas" / "canonical"


def _finding(**overrides) -> MachineFinding:
    base = dict(
        finding_id="finding_" + "a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6",
        case_id="case_" + "a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6",
        finding_type=FindingType.CLIPPING_EVENT,
        measurement_ids=["meas_" + "a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6"],
        evidence_ids=["evid_" + "a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6"],
        domain="wse/loudness",
        confidence=0.9,
        uncertainty_note="peak analysis over 100ms window",
        created_at=datetime(2026, 8, 13, tzinfo=timezone.utc),
    )
    base.update(overrides)
    return MachineFinding(**base)


def test_allowed_finding_types():
    for t in FindingType:
        f = _finding(finding_type=t)
        assert f.finding_type == t


def test_forbidden_conclusions_are_not_finding_types():
    for name in FORBIDDEN_CONCLUSIONS:
        assert name not in FindingType.__members__, f"{name} must not be a FindingType"
    assert "SOUNDS_BETTER" in FORBIDDEN_CONCLUSIONS
    assert "PRODUCTION_APPROVED" in FORBIDDEN_CONCLUSIONS
    assert "OVERALL_QUALITY_SCORE" in FORBIDDEN_CONCLUSIONS


def test_finding_id_validation():
    with pytest.raises(ValidationError):
        _finding(finding_id="not-a-finding-id")


def test_confidence_bounds():
    with pytest.raises(ValidationError):
        _finding(confidence=1.5)


def test_provenance_backward_compatible_extension():
    old = Provenance(
        producer="moodify", producer_version="1.0", method="scan",
        method_version="1", parameters_hash="sha256:" + "a" * 64,
    )
    assert old.algorithm_version == ""
    assert old.input_sha256 is None
    new = Provenance(
        producer="moodify", producer_version="1.0", method="scan",
        method_version="1", parameters_hash="sha256:" + "a" * 64,
        algorithm_version="librosa 0.11.0", input_sha256="sha256:" + "b" * 64,
    )
    assert new.algorithm_version == "librosa 0.11.0"
    assert new.input_sha256 == "sha256:" + "b" * 64


def test_machine_finding_schema_exists_and_matches():
    schema_path = SCHEMAS / "machine_finding.v1.schema.json"
    assert schema_path.exists()
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    assert "properties" in schema
    props = schema["properties"]
    assert "finding_type" in props
    assert "domain" in props
    # forbidden conclusions must not appear in the enum
    finding_schema = props["finding_type"]
    enum_values = set()
    if "enum" in finding_schema:
        enum_values = set(finding_schema["enum"])
    elif "$ref" in finding_schema:
        ref_name = finding_schema["$ref"].split("/")[-1]
        enum_values = set(schema["$defs"][ref_name]["enum"])
    assert not (enum_values & FORBIDDEN_CONCLUSIONS)


def test_production_case_schema_authority_state_regenerated():
    schema_path = SCHEMAS / "production_case.v1.schema.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    authority = schema["properties"]["authority_state"]
    if "enum" not in authority:
        ref_name = authority["$ref"].split("/")[-1]
        authority = schema["$defs"][ref_name]
    assert "ALGORITHM" in authority["enum"]  # drift fixed by regeneration
