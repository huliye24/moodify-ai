"""Contracts for Moodify's internal commercial-music production loop.

These models describe accountable facts.  They deliberately do not implement a
second workflow state machine: readiness is derived from the supplied records.
"""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from moodify.compat import StrEnum

from .hashing import validate_sha256


class CommercialModel(BaseModel):
    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        validate_by_name=True,
        serialize_by_alias=True,
    )


class CueKind(StrEnum):
    OPENING = "OPENING"
    ENDING = "ENDING"
    INSERT = "INSERT"
    SCORE = "SCORE"
    STINGER = "STINGER"
    OTHER = "OTHER"


class RightsConclusion(StrEnum):
    INCOMPLETE = "INCOMPLETE"
    HUMAN_VERIFIED = "HUMAN_VERIFIED"
    REJECTED = "REJECTED"


class JudgeConclusion(StrEnum):
    ACCEPT = "ACCEPT"
    RETRY = "RETRY"
    KEEP_ORIGINAL = "KEEP_ORIGINAL"
    HUMAN_REQUIRED = "HUMAN_REQUIRED"
    INCONCLUSIVE = "INCONCLUSIVE"


class HumanDecision(StrEnum):
    APPROVED = "APPROVED"
    REVISION_NEEDED = "REVISION_NEEDED"
    REJECTED = "REJECTED"


class ProjectBrief(CommercialModel):
    schema_name: Literal["moodify.commercial.project/0.1"] = Field(
        "moodify.commercial.project/0.1", alias="schema"
    )
    project_id: str
    title: str
    client_name: str
    production_type: str = "WEB_SERIES"
    delivery_spec_ref: str
    created_at: datetime

    @field_validator("project_id", "title", "client_name", "production_type", "delivery_spec_ref")
    @classmethod
    def require_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("field must be non-empty")
        return value


class CueBrief(CommercialModel):
    schema_name: Literal["moodify.commercial.cue/0.1"] = Field(
        "moodify.commercial.cue/0.1", alias="schema"
    )
    cue_id: str
    project_id: str
    title: str
    kind: CueKind
    scene: str
    creative_intent: str
    target_duration_s: float = Field(gt=0)
    dialogue_present: bool
    vocal_preference: Literal["INSTRUMENTAL", "VOCAL", "EITHER"] = "EITHER"
    reference_ids: tuple[str, ...] = ()
    deadline: datetime | None = None

    @field_validator("cue_id", "project_id", "title", "scene", "creative_intent")
    @classmethod
    def require_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("field must be non-empty")
        return value


class CandidateTrack(CommercialModel):
    schema_name: Literal["moodify.commercial.candidate/0.1"] = Field(
        "moodify.commercial.candidate/0.1", alias="schema"
    )
    candidate_id: str
    cue_id: str
    source_provider: str
    source_asset_id: str | None = None
    source_sha256: str
    generated_at: datetime | None = None
    ingested_at: datetime

    @field_validator("candidate_id", "cue_id", "source_provider")
    @classmethod
    def require_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("field must be non-empty")
        return value

    @field_validator("source_sha256")
    @classmethod
    def require_sha256(cls, value: str) -> str:
        return validate_sha256(value)


class RightsRecord(CommercialModel):
    """Human-owned provenance record; never a machine-created legal opinion."""

    schema_name: Literal["moodify.commercial.rights/0.1"] = Field(
        "moodify.commercial.rights/0.1", alias="schema"
    )
    candidate_id: str
    conclusion: RightsConclusion
    account_tier: str | None = None
    provider_terms_ref: str | None = None
    lyrics_source: str
    third_party_material: tuple[str, ...] = ()
    evidence_refs: tuple[str, ...] = ()
    reviewed_by: str | None = None
    reviewed_at: datetime | None = None
    notes: str = ""

    @model_validator(mode="after")
    def require_attributed_human_verification(self) -> "RightsRecord":
        if self.conclusion == RightsConclusion.HUMAN_VERIFIED:
            missing = []
            if not self.provider_terms_ref:
                missing.append("provider_terms_ref")
            if not self.evidence_refs:
                missing.append("evidence_refs")
            if not self.reviewed_by:
                missing.append("reviewed_by")
            if not self.reviewed_at:
                missing.append("reviewed_at")
            if missing:
                raise ValueError("HUMAN_VERIFIED rights require " + ", ".join(missing))
        return self


class JudgeRecord(CommercialModel):
    schema_name: Literal["moodify.commercial.judge/0.1"] = Field(
        "moodify.commercial.judge/0.1", alias="schema"
    )
    candidate_id: str
    phase: Literal["BEFORE", "AFTER"]
    conclusion: JudgeConclusion
    judge_version: str
    evidence_refs: tuple[str, ...]
    preserve: tuple[str, ...] = ()
    uncertainty: str | None = None

    @field_validator("evidence_refs")
    @classmethod
    def require_evidence(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        if not value:
            raise ValueError("Judge record requires evidence")
        return value


class ApprovalRecord(CommercialModel):
    schema_name: Literal["moodify.commercial.approval/0.1"] = Field(
        "moodify.commercial.approval/0.1", alias="schema"
    )
    candidate_id: str
    decision: HumanDecision
    reviewer: str
    reviewed_at: datetime
    evidence_refs: tuple[str, ...]
    notes: str = ""

    @field_validator("reviewer")
    @classmethod
    def require_reviewer(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("reviewer must be non-empty")
        return value


class DeliveryReadiness(CommercialModel):
    schema_name: Literal["moodify.commercial.delivery-readiness/0.1"] = Field(
        "moodify.commercial.delivery-readiness/0.1", alias="schema"
    )
    candidate_id: str
    ready: bool
    blockers: tuple[str, ...]


def derive_delivery_readiness(
    candidate: CandidateTrack,
    rights: RightsRecord | None,
    judge_before: JudgeRecord | None,
    judge_after: JudgeRecord | None,
    approval: ApprovalRecord | None,
) -> DeliveryReadiness:
    """Derive delivery eligibility without persisting another workflow authority."""

    blockers: list[str] = []
    records = [record for record in (rights, judge_before, judge_after, approval) if record]
    if any(record.candidate_id != candidate.candidate_id for record in records):
        blockers.append("CANDIDATE_ID_MISMATCH")
    if rights is None or rights.conclusion != RightsConclusion.HUMAN_VERIFIED:
        blockers.append("RIGHTS_NOT_HUMAN_VERIFIED")
    if judge_before is None or judge_before.phase != "BEFORE":
        blockers.append("JUDGE_BEFORE_MISSING")
    if judge_after is None or judge_after.phase != "AFTER":
        blockers.append("JUDGE_AFTER_MISSING")
    elif judge_after.conclusion != JudgeConclusion.ACCEPT:
        blockers.append(f"JUDGE_AFTER_{judge_after.conclusion.value}")
    if approval is None or approval.decision != HumanDecision.APPROVED:
        blockers.append("HUMAN_APPROVAL_MISSING")
    return DeliveryReadiness(
        candidate_id=candidate.candidate_id,
        ready=not blockers,
        blockers=tuple(dict.fromkeys(blockers)),
    )
