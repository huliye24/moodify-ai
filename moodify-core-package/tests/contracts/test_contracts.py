from datetime import datetime, timezone
from pathlib import Path

import pytest
from pydantic import ValidationError

from moodify.contracts import (
    AuthorityState,
    EvidenceArtifact,
    LifecycleState,
    MeasurementRecord,
    ProductionCase,
    Provenance,
    Rule,
    RuleStatus,
)
from moodify.contracts.hashing import (
    sha256_bytes,
    sha256_file,
    sha256_json,
    validate_sha256,
)
from moodify.contracts.ids import new_id, validate_id
from moodify.contracts.serialization import (
    from_canonical_json,
    to_canonical_dict,
    to_canonical_json,
)


def now() -> datetime:
    return datetime.now(timezone.utc)


def provenance() -> Provenance:
    return Provenance(
        producer="moodify.tests",
        producer_version="1.0",
        method="fixture",
        method_version="1.0",
        parameters_hash=sha256_json({"window": "full"}),
    )


def case(**overrides: object) -> ProductionCase:
    values = {
        "case_id": new_id("case"),
        "source_id": "source_fixture",
        "objective": "measure fixture",
        "lifecycle_state": LifecycleState.CREATED,
        "authority_state": AuthorityState.SYSTEM,
        "created_at": now(),
    }
    values.update(overrides)
    return ProductionCase(**values)


def measurement(**overrides: object) -> MeasurementRecord:
    values = {
        "measurement_id": new_id("meas"),
        "case_id": new_id("case"),
        "source_id": "source_fixture",
        "created_at": now(),
        "namespace": "wse.loudness",
        "name": "integrated_lufs",
        "value": -13.7,
        "unit": "LUFS",
        "provenance": provenance(),
    }
    values.update(overrides)
    return MeasurementRecord(**values)


def evidence(**overrides: object) -> EvidenceArtifact:
    values = {
        "evidence_id": new_id("evid"),
        "case_id": new_id("case"),
        "created_at": now(),
        "artifact_type": "analysis_result",
        "media_type": "application/json",
        "content_hash": sha256_bytes(b"evidence"),
        "provenance": provenance(),
    }
    values.update(overrides)
    return EvidenceArtifact(**values)


def rule(**overrides: object) -> Rule:
    values = {
        "rule_id": new_id("rule"),
        "created_at": now(),
        "name": "Loudness observation",
        "version": "1",
        "status": RuleStatus.DRAFT,
        "scope": "wse.loudness",
        "description": "Record integrated loudness without judging quality.",
    }
    values.update(overrides)
    return Rule(**values)


@pytest.mark.parametrize("kind", ["case", "meas", "evid", "rule"])
def test_generated_ids_are_valid_and_unique(kind: str):
    values = {new_id(kind) for _ in range(100)}
    assert len(values) == 100
    assert all(validate_id(value, kind) == value for value in values)


def test_wrong_id_prefix_is_rejected():
    with pytest.raises(ValidationError):
        case(case_id=new_id("meas"))


def test_hashing_is_deterministic_and_valid(tmp_path: Path):
    payload = b"Moodify"
    path = tmp_path / "payload.bin"
    path.write_bytes(payload)
    assert sha256_bytes(payload) == sha256_file(path)
    assert sha256_json({"a": 1, "b": 2}) == sha256_json({"b": 2, "a": 1})
    assert validate_sha256(sha256_bytes(payload)) == sha256_bytes(payload)


@pytest.mark.parametrize("digest", ["", "sha256:ABC", "md5:" + "a" * 64])
def test_malformed_hash_is_rejected(digest: str):
    with pytest.raises(ValueError):
        validate_sha256(digest)


@pytest.mark.parametrize("value", [float("nan"), float("inf"), float("-inf")])
def test_non_finite_json_hash_is_rejected(value: float):
    with pytest.raises(ValueError):
        sha256_json({"value": value})


def test_contract_is_immutable_and_rejects_extra_fields():
    production_case = case()
    with pytest.raises(ValidationError):
        production_case.objective = "mutated"
    with pytest.raises(ValidationError):
        case(unknown="field")


def test_nested_json_values_are_immutable():
    record = measurement(value={"bands": [1, 2]}, metadata={"review": {"done": True}})
    with pytest.raises(TypeError):
        record.value["bands"] = []
    with pytest.raises(TypeError):
        record.metadata["review"]["done"] = False


def test_timestamp_is_normalized_to_utc_and_naive_is_rejected():
    offset = timezone.utc
    created = case(created_at=datetime(2026, 1, 2, tzinfo=offset))
    assert created.created_at.tzinfo == timezone.utc
    with pytest.raises(ValidationError):
        case(created_at=datetime(2026, 1, 2))


@pytest.mark.parametrize("value", [-13.7, "present", True, [1, {"x": 2}]])
def test_measurement_accepts_intentionally_json_safe_values(value: object):
    assert to_canonical_dict(measurement(value=value))["value"] == value


@pytest.mark.parametrize("value", [{1, 2}, b"bytes", Path("local")])
def test_measurement_rejects_non_json_safe_values(value: object):
    with pytest.raises(ValidationError):
        measurement(value=value)


@pytest.mark.parametrize("confidence", [-0.01, 1.01])
def test_measurement_confidence_is_bounded(confidence: float):
    with pytest.raises(ValidationError):
        measurement(confidence=confidence)


def test_measurement_window_and_metadata_are_json_safe():
    with pytest.raises(ValidationError):
        measurement(window={"start": Path("local")})
    with pytest.raises(ValidationError):
        measurement(metadata={"value": float("nan")})


def test_evidence_requires_hash_and_non_negative_size():
    with pytest.raises(ValidationError):
        evidence(content_hash=None)
    with pytest.raises(ValidationError):
        evidence(size_bytes=-1)


def test_evidence_does_not_require_absolute_path():
    artifact = evidence(logical_path="cases/report.json")
    assert artifact.uri is None
    assert artifact.logical_path == "cases/report.json"


def test_evidence_metadata_is_json_safe():
    with pytest.raises(ValidationError):
        evidence(metadata={"path": Path("C:/machine-only")})


def test_active_rule_requires_evidence_provenance():
    with pytest.raises(ValidationError):
        rule(status=RuleStatus.ACTIVE)
    active = rule(
        status=RuleStatus.ACTIVE,
        provenance_evidence_ids=(new_id("evid"),),
    )
    assert active.status == RuleStatus.ACTIVE


def test_rule_version_status_and_self_supersede_are_validated():
    with pytest.raises(ValidationError):
        rule(version=" ")
    with pytest.raises(ValidationError):
        rule(status="UNREVIEWED")
    rule_id = new_id("rule")
    with pytest.raises(ValidationError):
        rule(rule_id=rule_id, supersedes_rule_id=rule_id)


def test_case_references_are_typed_unique_and_not_self_parented():
    duplicate = new_id("meas")
    with pytest.raises(ValidationError):
        case(measurement_ids=(duplicate, duplicate))
    with pytest.raises(ValidationError):
        case(evidence_ids=(new_id("rule"),))
    case_id = new_id("case")
    with pytest.raises(ValidationError):
        case(case_id=case_id, parent_case_id=case_id)


@pytest.mark.parametrize("factory", [case, measurement, evidence, rule])
def test_all_contracts_round_trip(factory):
    model = factory()
    payload = to_canonical_json(model)
    assert from_canonical_json(type(model), payload) == model
    assert payload == to_canonical_json(model)


def test_schema_version_is_explicit_and_strict():
    assert case().schema_version == "1.0"
    with pytest.raises(ValidationError):
        case(schema_version="2.0")
