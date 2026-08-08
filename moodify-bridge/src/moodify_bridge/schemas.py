"""Versioned, strict domain schemas (v1)."""
from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from typing import Annotated, Any, Literal
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

SCHEMA_VERSION: Literal["1.0.0"] = "1.0.0"


def utc_now() -> datetime:
    return datetime.now(UTC)


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    schema_version: Literal["1.0.0"] = SCHEMA_VERSION


Sha256 = Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")]


class AssetKind(StrEnum):
    AUDIO = "audio"
    PROJECT = "project"
    STEM = "stem"
    MIDI = "midi"
    SCORE = "score"
    LYRICS = "lyrics"
    OTHER = "other"


class AssetManifest(StrictModel):
    asset_id: UUID = Field(default_factory=uuid4)
    kind: AssetKind
    local_path: str
    sha256: Sha256
    size_bytes: int = Field(ge=0)
    media_type: str | None = None
    role: str


class SourceAsset(AssetManifest):
    """A source asset whose bytes are never mutated by Moodify."""

    source_type: Literal["ai_stereo_mix", "vocal", "instrumental", "stem", "reference", "symbolic", "other"]
    rights_status: Literal["authorized", "restricted", "unknown"] = "unknown"


class ProcessingStage(StrictModel):
    stage_id: UUID = Field(default_factory=uuid4)
    name: str
    ordinal: int = Field(ge=0)
    software: str
    software_version: str
    rule_ids: tuple[str, ...] = ()
    parameters: dict[str, Any] = Field(default_factory=dict)
    input_asset_ids: tuple[UUID, ...] = ()
    output_asset_ids: tuple[UUID, ...] = ()


class MeasurementRecord(StrictModel):
    measurement_id: UUID = Field(default_factory=uuid4)
    case_id: UUID
    asset_id: UUID | None = None
    adapter: str
    adapter_version: str = "1.0.0"
    measured_at: datetime = Field(default_factory=utc_now)
    values: dict[str, float | None]
    units: dict[str, str] = Field(default_factory=dict)
    parquet_path: str | None = None
    warnings: tuple[str, ...] = ()


class SymbolicAnchor(StrictModel):
    anchor_id: UUID = Field(default_factory=uuid4)
    label: str
    asset_id: UUID | None = None
    start_seconds: float | None = Field(default=None, ge=0)
    end_seconds: float | None = Field(default=None, ge=0)
    bar: int | None = Field(default=None, ge=1)
    beat: float | None = Field(default=None, ge=1)
    description: str | None = None


class HumanObservation(StrictModel):
    observation_id: UUID = Field(default_factory=uuid4)
    observer: str
    observed_at: datetime = Field(default_factory=utc_now)
    text: str
    anchor_ids: tuple[UUID, ...] = ()
    tags: tuple[str, ...] = ()
    rating: float | None = None


class CaseEvent(StrictModel):
    event_id: UUID = Field(default_factory=uuid4)
    event_type: Literal["failure", "rollback", "limitation", "revision"]
    occurred_at: datetime = Field(default_factory=utc_now)
    description: str
    supersedes_event_id: UUID | None = None
    details: dict[str, Any] = Field(default_factory=dict)


class ProductionCase(StrictModel):
    case_id: UUID = Field(default_factory=uuid4)
    title: str
    created_at: datetime = Field(default_factory=utc_now)
    moodify_version: str
    rule_versions: dict[str, str] = Field(default_factory=dict)
    source_asset_ids: tuple[UUID, ...]
    output_asset_ids: tuple[UUID, ...]
    assets: tuple[AssetManifest, ...]
    processing_stages: tuple[ProcessingStage, ...] = ()
    symbolic_anchors: tuple[SymbolicAnchor, ...] = ()
    human_observations: tuple[HumanObservation, ...] = ()
    events: tuple[CaseEvent, ...] = ()
    limitations: tuple[str, ...] = ()
    golden: bool = False
    external_case_id: str | None = Field(default=None, pattern=r"^CASE-\d{8}-[A-Z0-9]{4}$")
    pipeline_version: str | None = None
    selected_candidate_id: str | None = None
    selection_reason: str | None = None
    runtime_seconds: float | None = Field(default=None, ge=0)
    failure_status: Literal["none", "partial", "failed", "rolled_back"] = "none"

    @model_validator(mode="after")
    def identities_exist(self) -> ProductionCase:
        known = {a.asset_id for a in self.assets}
        missing = (set(self.source_asset_ids) | set(self.output_asset_ids)) - known
        if missing:
            raise ValueError(f"source/output asset identities missing from manifest: {sorted(map(str, missing))}")
        return self


class EvidencePacket(StrictModel):
    packet_id: UUID = Field(default_factory=uuid4)
    case_id: UUID
    compiled_at: datetime = Field(default_factory=utc_now)
    case_digest: Sha256
    measurement_ids: tuple[UUID, ...] = ()
    observation_ids: tuple[UUID, ...] = ()
    hypothesis_ids: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()


class HypothesisStatus(StrEnum):
    DRAFT = "draft"
    TESTING = "testing"
    SUPPORTED = "supported"
    REJECTED = "rejected"


class ResearchHypothesis(StrictModel):
    hypothesis_id: str
    version: str
    title: str
    statement: str
    status: HypothesisStatus = HypothesisStatus.DRAFT
    expected_evidence: tuple[str, ...]
    limitations: tuple[str, ...] = ()
    created_by: str
    created_at: datetime = Field(default_factory=utc_now)


class RuleState(StrEnum):
    PROPOSED = "proposed"
    EXPERIMENTAL = "experimental"
    VALIDATED = "validated"
    PRODUCTION = "production"
    DEPRECATED = "deprecated"


class MoodifyRule(StrictModel):
    rule_id: str
    version: str
    title: str
    state: RuleState = RuleState.PROPOSED
    rationale: str
    parameters: dict[str, Any]
    hypothesis_ids: tuple[str, ...] = ()
    evidence_packet_ids: tuple[UUID, ...] = ()
    limitations: tuple[str, ...] = ()


class HumanApproval(StrictModel):
    approval_id: UUID = Field(default_factory=uuid4)
    rule_id: str
    rule_version: str
    approver: str
    approved_at: datetime = Field(default_factory=utc_now)
    decision: Literal["approve"] = "approve"
    rationale: str


class ValidationResult(StrictModel):
    validation_id: UUID = Field(default_factory=uuid4)
    subject_type: Literal["case", "rule", "regression"]
    subject_id: str
    valid: bool
    checked_at: datetime = Field(default_factory=utc_now)
    checks: dict[str, bool]
    warnings: tuple[str, ...] = ()
    errors: tuple[str, ...] = ()
    approval_id: UUID | None = None


class Confidence(StrictModel):
    value: float | None = Field(default=None, ge=0, le=1)
    method: str
    backend: str | None = None
    warnings: tuple[str, ...] = ()


class StructuralRecord(StrictModel):
    structural_record_id: str = Field(pattern=r"^STRUCT-[A-Z0-9-]+-v\d+$")
    case_id: UUID
    asset_id: UUID
    analyzer_version: str
    bpm: float | None = Field(default=None, gt=0)
    beat_times_seconds: tuple[float, ...] = ()
    key: str | None = None
    sections: tuple[SymbolicAnchor, ...] = ()
    phrases: tuple[SymbolicAnchor, ...] = ()
    melody_asset_id: UUID | None = None
    chord_timeline_asset_id: UUID | None = None
    lyrics_timeline_asset_id: UUID | None = None
    midi_asset_ids: tuple[UUID, ...] = ()
    score_asset_ids: tuple[UUID, ...] = ()
    instrument_roles: dict[str, str] = Field(default_factory=dict)
    confidence: dict[str, Confidence] = Field(default_factory=dict)
    human_corrections: tuple[HumanObservation, ...] = ()
    warnings: tuple[str, ...] = ()


class ExperimentRecord(StrictModel):
    experiment_id: str = Field(pattern=r"^EXP-\d{8}-[A-Z0-9]{4}$")
    case_id: UUID
    hypothesis_ids: tuple[str, ...]
    pipeline_version: str
    variables: dict[str, Any]
    controls: dict[str, Any] = Field(default_factory=dict)
    stopping_conditions: tuple[str, ...] = ()
    status: Literal["planned", "running", "completed", "failed"] = "planned"
    started_at: datetime | None = None
    completed_at: datetime | None = None
    failure_reason: str | None = None


class CandidateRecord(StrictModel):
    candidate_id: str = Field(pattern=r"^CAND-[A-Z0-9-]+-\d{2}$")
    case_id: UUID
    experiment_id: str
    parent_asset_ids: tuple[UUID, ...]
    output_asset_id: UUID
    pipeline_version: str
    rule_versions: dict[str, str]
    processing_stages: tuple[ProcessingStage, ...]
    measurement_ids: tuple[UUID, ...] = ()
    structural_record_ids: tuple[str, ...] = ()
    runtime_seconds: float | None = Field(default=None, ge=0)
    status: Literal["generated", "invalid", "evaluated", "selected", "rejected"] = "generated"


class EvaluationRecord(StrictModel):
    evaluation_id: str = Field(pattern=r"^EVAL-[A-Z0-9-]+-v\d+$")
    case_id: UUID
    candidate_ids: tuple[str, ...]
    evaluation_type: Literal["technical", "structural", "perceptual", "production"]
    evaluator_type: Literal["adapter", "rule", "human"]
    evaluator_id: str
    protocol_version: str
    scores: dict[str, float | None]
    measurement_ids: tuple[UUID, ...] = ()
    observations: tuple[HumanObservation, ...] = ()
    warnings: tuple[str, ...] = ()


class DecisionRecord(StrictModel):
    decision_id: str = Field(pattern=r"^DEC-[A-Z0-9-]+-v\d+$")
    case_id: UUID
    candidate_ids: tuple[str, ...]
    selected_candidate_id: str | None
    decision: Literal["select", "reject_all", "hold", "rework"]
    reason: str
    evaluation_ids: tuple[str, ...]
    decision_maker_type: Literal["human", "rule"]
    decision_maker_id: str
    rule_version: str | None = None
    decided_at: datetime = Field(default_factory=utc_now)

    @model_validator(mode="after")
    def selected_candidate_is_known(self) -> DecisionRecord:
        if self.decision == "select" and self.selected_candidate_id not in self.candidate_ids:
            raise ValueError("selected candidate must be present in candidate_ids")
        if self.decision != "select" and self.selected_candidate_id is not None:
            raise ValueError("only a select decision may name a selected candidate")
        return self


class RuleRecord(MoodifyRule):
    domain: Literal["WSE", "MSE", "PPE", "treatment", "evaluation"]
    validation_ids: tuple[UUID, ...] = ()
    human_approval_id: UUID | None = None

    @model_validator(mode="after")
    def production_requires_approval(self) -> RuleRecord:
        if self.state is RuleState.PRODUCTION and self.human_approval_id is None:
            raise ValueError("production rule requires an explicit human approval id")
        return self


class DeliverableManifest(StrictModel):
    deliverable_id: str = Field(pattern=r"^REPORT-[A-Z0-9-]+-v\d+$")
    case_id: UUID
    selected_candidate_id: str
    asset_ids: tuple[UUID, ...]
    report_paths: tuple[str, ...] = ()
    structural_record_ids: tuple[str, ...] = ()
    validation_ids: tuple[UUID, ...] = ()
    packaged_at: datetime = Field(default_factory=utc_now)
    pipeline_version: str
    rule_versions: dict[str, str]
    limitations: tuple[str, ...] = ()


# ── PPE Gate & Runner models (DSK-MFY-PPE-HARDENING-005) ────────────────


class GateStatus(StrEnum):
    PASS = "PASS"
    WARN = "WARN"
    FAIL = "FAIL"


class GateResult(StrictModel):
    schema_version: Literal["1.0.0"] = SCHEMA_VERSION
    gate_id: str = Field(
        pattern=r"^(input_complete|identity_consistent|measurement_available|"
        r"candidates_comparable|human_approved|report_complete)$"
    )
    status: GateStatus
    blocking: bool
    reason_code: str
    message: str
    evidence_paths: tuple[str, ...] = ()
    checked_at: datetime = Field(default_factory=utc_now)
    checker_version: str = "1.0.0"


class PPEFinalStatus(StrEnum):
    PASS = "PASS"
    PASS_WITH_WARNINGS = "PASS_WITH_WARNINGS"
    FAIL = "FAIL"


class EnvironmentInfo(StrictModel):
    python_version: str
    python_executable: str
    platform: str
    packages: dict[str, str] = Field(default_factory=dict)


class CommandResult(StrictModel):
    action: str
    started_at: datetime
    ended_at: datetime = Field(default_factory=utc_now)
    exit_code: int
    status: GateStatus
    error_code: str | None = None
    error_message: str | None = None
    artifact_paths: tuple[str, ...] = ()


class RunManifest(StrictModel):
    manifest_id: UUID = Field(default_factory=uuid4)
    task_id: str
    case_path: str
    run_dir: str
    started_at: datetime
    ended_at: datetime = Field(default_factory=utc_now)
    final_status: PPEFinalStatus
    environment: EnvironmentInfo
    commands: tuple[CommandResult, ...] = ()
    gates: tuple[GateResult, ...] = ()
    case_id: UUID | None = None
    evidence_path: str | None = None
    report_md_path: str | None = None
    report_html_path: str | None = None
    case_digest: str | None = None
    artifact_hashes: dict[str, Sha256] = Field(default_factory=dict)


# ── One-Point models (DSK-MFY-ONE-POINT-006) ────────────────────────────


class OnePointStatus(StrEnum):
    READY_FOR_REVIEW = "READY_FOR_REVIEW"
    BLOCKED = "BLOCKED"
    NEEDS_EVIDENCE = "NEEDS_EVIDENCE"
    FAILED = "FAILED"


class AssetRef(StrictModel):
    path: str
    sha256: Sha256 | None = None
    role: str = "reference"


# ── Lyrics Intent Evidence (DSK-MFY-LYRICS-INTENT-007) ──────────────────


class LyricsRights(StrEnum):
    OWNER_PROVIDED = "owner-provided"
    PUBLIC_DOMAIN = "public-domain"
    LICENSED = "licensed"
    UNKNOWN = "unknown"


class LyricsVersion(StrEnum):
    AUTHORIZED_DRAFT = "authorized-draft"
    AUTHORIZED_FINAL = "authorized-final"
    OWNER_PROVIDED_VERSION = "owner-provided"


class LyricsRef(StrictModel):
    path: str = Field(min_length=1, max_length=1024)
    language: str = Field(
        min_length=2,
        max_length=35,
        pattern=r"^(?:[A-Za-z]{2,3}|mixed)(?:-[A-Za-z0-9]{2,8})*$",
    )
    version: LyricsVersion
    rights_basis: LyricsRights
    declared_intent: str | None = Field(default=None, max_length=500)
    encoding: Literal["utf-8"] = "utf-8"

    @field_validator("path", "language")
    @classmethod
    def not_blank(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("value must not be blank")
        return stripped

    @field_validator("declared_intent")
    @classmethod
    def declared_intent_not_blank(cls, value: str | None) -> str | None:
        if value is None:
            return None
        stripped = value.strip()
        if not stripped:
            raise ValueError("declared_intent must not be blank")
        return stripped


class LyricsSourceFacts(StrictModel):
    path: str
    sha256: Sha256
    byte_size: int = Field(ge=0)
    language: str
    version: str
    rights_basis: str
    line_count: int = Field(ge=0)
    paragraph_count: int = Field(ge=0)
    has_explicit_section_labels: bool = False
    section_labels_found: tuple[str, ...] = ()


class LyricsSection(StrictModel):
    label: str
    start_line: int = Field(ge=1)
    end_line: int = Field(ge=1)
    line_count: int = Field(ge=0)


class RepeatedLine(StrictModel):
    text_hash: Sha256
    occurrences: int = Field(ge=1)
    locations: tuple[int, ...] = ()


class LyricsStructuralObservations(StrictModel):
    sections: tuple[LyricsSection, ...] = ()
    repeated_lines: tuple[RepeatedLine, ...] = ()
    normalized_repetition_count: int = Field(ge=0, default=0)


class LyricsEvidence(StrictModel):
    schema_version: Literal["1.0.0"] = SCHEMA_VERSION
    source_facts: LyricsSourceFacts
    declared_intent: str | None = None
    structural_observations: LyricsStructuralObservations = Field(
        default_factory=LyricsStructuralObservations
    )
    uncertainties: tuple[str, ...] = ()
    conflicts: tuple[str, ...] = ()


class OnePointSpec(StrictModel):
    schema_version: Literal["1.0.0"] = SCHEMA_VERSION
    spec_id: UUID = Field(default_factory=uuid4)
    source: str
    case_id: UUID | None = None
    essence: str = Field(min_length=1, max_length=500)
    must_preserve: tuple[str, ...]
    desired_change: str = Field(min_length=1, max_length=500)
    must_avoid: tuple[str, ...]
    human_owner: str = Field(min_length=1)
    limitations: tuple[str, ...] = ()
    reference_assets: tuple[AssetRef, ...] = ()
    delivery_conditions: tuple[str, ...] = ()
    lyrics: LyricsRef | None = None

    @field_validator("source", "essence", "desired_change", "human_owner")
    @classmethod
    def text_must_not_be_blank(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("value must not be blank")
        return stripped

    @field_validator("must_preserve", "must_avoid")
    @classmethod
    def list_items_must_not_be_blank(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        stripped = tuple(item.strip() for item in value)
        if any(not item for item in stripped):
            raise ValueError("items must not be blank")
        return stripped

    @model_validator(mode="after")
    def preserve_not_empty(self) -> OnePointSpec:
        if not self.must_preserve:
            raise ValueError("must_preserve must contain at least one item")
        if not self.must_avoid:
            raise ValueError("must_avoid must contain at least one item")
        return self


class OnePointResult(StrictModel):
    schema_version: Literal["1.0.0"] = SCHEMA_VERSION
    result_id: UUID = Field(default_factory=uuid4)
    spec_identity: Sha256
    status: OnePointStatus
    essence: str
    protect: str
    allow: str
    avoid: str
    action: str
    entrust: str
    owner: str
    evidence_path: str
    created_at: datetime = Field(default_factory=utc_now)
    case_id: UUID | None = None
    warnings: tuple[str, ...] = ()
    gate_summary: dict[str, str] = Field(default_factory=dict)
