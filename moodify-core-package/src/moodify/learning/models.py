"""Learning-domain models (DSK-MFY-AUDITORY-INTELLIGENCE-RECLASSIFICATION-001).

AuditoryObservation / InterventionRecord / HumanListeningEvaluation /
LearningRecord / RightsMetadata / TrainingEligibility / PairwisePreference /
CandidateOutcome. Versioned schemas; eligibility defaults safely.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

SCHEMA_VERSION = "1.0"


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


# ---------------------------------------------------------------------------
# AuditoryObservation (representation)
# ---------------------------------------------------------------------------


@dataclass
class TimeRegion:
    start_s: float
    end_s: float


@dataclass
class FrequencyRegion:
    low_hz: float
    high_hz: float


@dataclass
class AuditoryObservation:
    observation_id: str
    case_id: str
    observation_type: str  # e.g. LOW_END_CONGESTION, HF_DARK, CLIPPING_RISK, TRANSIENT_SMEAR
    source_stage: str  # BEFORE | AFTER | CANDIDATE
    severity: str = "INFO"  # INFO | WARNING | BLOCKING
    confidence: str = "LOW"  # LOW | MEDIUM | HIGH
    status: str = "OPEN"  # OPEN | CONFIRMED | REJECTED
    rationale: str = ""
    time_regions: list[TimeRegion] = field(default_factory=list)
    frequency_regions: list[FrequencyRegion] = field(default_factory=list)
    channel_scope: str = "STEREO"
    candidate_id: str | None = None
    evidence_refs: list[str] = field(default_factory=list)
    method_id: str = ""
    warnings: list[str] = field(default_factory=list)
    created_by: str = ""
    created_at: str = field(default_factory=utcnow)
    schema_version: str = SCHEMA_VERSION

    def to_dict(self) -> dict:
        return {
            "observation_id": self.observation_id,
            "schema_version": self.schema_version,
            "case_id": self.case_id,
            "candidate_id": self.candidate_id,
            "observation_type": self.observation_type,
            "source_stage": self.source_stage,
            "time_regions": [{"start_s": t.start_s, "end_s": t.end_s} for t in self.time_regions],
            "frequency_regions": [{"low_hz": f.low_hz, "high_hz": f.high_hz} for f in self.frequency_regions],
            "channel_scope": self.channel_scope,
            "severity": self.severity,
            "confidence": self.confidence,
            "status": self.status,
            "rationale": self.rationale,
            "evidence_refs": self.evidence_refs,
            "created_by": self.created_by,
            "created_at": self.created_at,
            "method_id": self.method_id,
            "warnings": self.warnings,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "AuditoryObservation":
        return cls(
            observation_id=data["observation_id"],
            case_id=data["case_id"],
            observation_type=data["observation_type"],
            source_stage=data.get("source_stage", "BEFORE"),
            severity=data.get("severity", "INFO"),
            confidence=data.get("confidence", "LOW"),
            status=data.get("status", "OPEN"),
            rationale=data.get("rationale", ""),
            time_regions=[TimeRegion(t["start_s"], t["end_s"]) for t in data.get("time_regions", [])],
            frequency_regions=[FrequencyRegion(f["low_hz"], f["high_hz"])
                               for f in data.get("frequency_regions", [])],
            channel_scope=data.get("channel_scope", "STEREO"),
            candidate_id=data.get("candidate_id"),
            evidence_refs=data.get("evidence_refs", []),
            method_id=data.get("method_id", ""),
            warnings=data.get("warnings", []),
            created_by=data.get("created_by", ""),
            created_at=data.get("created_at", utcnow()),
            schema_version=data.get("schema_version", SCHEMA_VERSION),
        )


# ---------------------------------------------------------------------------
# InterventionRecord
# ---------------------------------------------------------------------------

EXECUTION_MODES = (
    "EXTERNAL_GUI_PROCESSING",
    "MOODIFY_DSP",
    "SCRIPTED_TOOL",
    "MANUAL_ENGINEER",
    "UNKNOWN_LEGACY",
)


@dataclass
class InterventionRecord:
    intervention_id: str
    case_id: str
    candidate_id: str
    parent_audio_sha256: str
    producing_application: str
    processing_operator: str
    execution_mode: str = "EXTERNAL_GUI_PROCESSING"
    producing_application_version: str | None = None
    hypothesis: str = ""
    intended_goals: list[str] = field(default_factory=list)
    operations: list[dict] = field(default_factory=list)
    guardrails: list[dict] = field(default_factory=list)
    started_at: str = field(default_factory=utcnow)
    completed_at: str = ""
    output_audio_sha256: str = ""
    evidence_refs: list[str] = field(default_factory=list)
    status: str = "COMPLETED"  # PLANNED | RUNNING | COMPLETED | FAILED | REJECTED
    warnings: list[str] = field(default_factory=list)
    schema_version: str = SCHEMA_VERSION

    def to_dict(self) -> dict:
        return {
            "intervention_id": self.intervention_id,
            "schema_version": self.schema_version,
            "case_id": self.case_id,
            "candidate_id": self.candidate_id,
            "parent_audio_sha256": self.parent_audio_sha256,
            "producing_application": self.producing_application,
            "producing_application_version": self.producing_application_version,
            "execution_mode": self.execution_mode,
            "operator": self.processing_operator,
            "hypothesis": self.hypothesis,
            "intended_goals": self.intended_goals,
            "operations": self.operations,
            "guardrails": self.guardrails,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "output_audio_sha256": self.output_audio_sha256,
            "evidence_refs": self.evidence_refs,
            "status": self.status,
            "warnings": self.warnings,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "InterventionRecord":
        return cls(
            intervention_id=data["intervention_id"],
            case_id=data["case_id"],
            candidate_id=data["candidate_id"],
            parent_audio_sha256=data["parent_audio_sha256"],
            producing_application=data["producing_application"],
            processing_operator=data.get("operator", ""),
            execution_mode=data.get("execution_mode", "EXTERNAL_GUI_PROCESSING"),
            producing_application_version=data.get("producing_application_version"),
            hypothesis=data.get("hypothesis", ""),
            intended_goals=data.get("intended_goals", []),
            operations=data.get("operations", []),
            guardrails=data.get("guardrails", []),
            started_at=data.get("started_at", utcnow()),
            completed_at=data.get("completed_at", ""),
            output_audio_sha256=data.get("output_audio_sha256", ""),
            evidence_refs=data.get("evidence_refs", []),
            status=data.get("status", "COMPLETED"),
            warnings=data.get("warnings", []),
            schema_version=data.get("schema_version", SCHEMA_VERSION),
        )


# ---------------------------------------------------------------------------
# HumanListeningEvaluation
# ---------------------------------------------------------------------------

APPROVAL_STATUS = ("PENDING", "APPROVED", "REJECTED")


@dataclass
class HumanListeningEvaluation:
    evaluation_id: str
    case_id: str
    candidate_ids: list[str]
    evaluator_id: str  # real id or pseudonymous reference
    listening_context: str = ""
    comparison_mode: str = "A_B_BLIND"  # A_B_BLIND | A_B_OPEN | SINGLE
    preferred_candidate_id: str | None = None
    audible_difference: str = "NONE"  # NONE | SUBTLE | CLEAR | LARGE
    goal_achieved: str = "UNKNOWN"  # YES | NO | UNKNOWN | PARTIAL
    artistic_damage_detected: bool = False
    reasons: list[str] = field(default_factory=list)
    confidence: str = "MEDIUM"
    approval_status: str = "PENDING"
    created_at: str = field(default_factory=utcnow)
    schema_version: str = SCHEMA_VERSION

    def to_dict(self) -> dict:
        return {
            "evaluation_id": self.evaluation_id,
            "schema_version": self.schema_version,
            "case_id": self.case_id,
            "evaluator_id": self.evaluator_id,
            "candidate_ids": self.candidate_ids,
            "listening_context": self.listening_context,
            "comparison_mode": self.comparison_mode,
            "preferred_candidate_id": self.preferred_candidate_id,
            "audible_difference": self.audible_difference,
            "goal_achieved": self.goal_achieved,
            "artistic_damage_detected": self.artistic_damage_detected,
            "reasons": self.reasons,
            "confidence": self.confidence,
            "approval_status": self.approval_status,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "HumanListeningEvaluation":
        return cls(
            evaluation_id=data["evaluation_id"],
            case_id=data["case_id"],
            candidate_ids=data["candidate_ids"],
            evaluator_id=data["evaluator_id"],
            listening_context=data.get("listening_context", ""),
            comparison_mode=data.get("comparison_mode", "A_B_BLIND"),
            preferred_candidate_id=data.get("preferred_candidate_id"),
            audible_difference=data.get("audible_difference", "NONE"),
            goal_achieved=data.get("goal_achieved", "UNKNOWN"),
            artistic_damage_detected=data.get("artistic_damage_detected", False),
            reasons=data.get("reasons", []),
            confidence=data.get("confidence", "MEDIUM"),
            approval_status=data.get("approval_status", "PENDING"),
            created_at=data.get("created_at", utcnow()),
            schema_version=data.get("schema_version", SCHEMA_VERSION),
        )


# ---------------------------------------------------------------------------
# Rights metadata + training eligibility
# ---------------------------------------------------------------------------


@dataclass
class RightsMetadata:
    audio_origin: str = "UNKNOWN"
    rights_holder: str = "UNKNOWN"
    processing_authorization: str = "UNKNOWN"
    research_use_authorized: str = "UNKNOWN"
    model_training_authorized: str = "UNKNOWN"
    derivative_data_authorized: str = "UNKNOWN"
    commercial_training_authorized: str = "UNKNOWN"
    retention_policy: str = "UNKNOWN"
    consent_reference: str = ""
    jurisdiction_notes: str = ""
    reviewed_by: str = ""
    reviewed_at: str = ""

    def to_dict(self) -> dict:
        return {
            "audio_origin": self.audio_origin,
            "rights_holder": self.rights_holder,
            "processing_authorization": self.processing_authorization,
            "research_use_authorized": self.research_use_authorized,
            "model_training_authorized": self.model_training_authorized,
            "derivative_data_authorized": self.derivative_data_authorized,
            "commercial_training_authorized": self.commercial_training_authorized,
            "retention_policy": self.retention_policy,
            "consent_reference": self.consent_reference,
            "jurisdiction_notes": self.jurisdiction_notes,
            "reviewed_by": self.reviewed_by,
            "reviewed_at": self.reviewed_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "RightsMetadata":
        return cls(**{k: data.get(k, v) for k, v in cls().to_dict().items()})


ELIGIBILITY_STATES = (
    "ELIGIBLE",
    "INELIGIBLE",
    "PENDING_REVIEW",
    "RESTRICTED_INTERNAL_RESEARCH",
    "UNKNOWN",
)


def default_eligibility() -> str:
    """Never default to ELIGIBLE."""
    return "UNKNOWN"


# ---------------------------------------------------------------------------
# Pairwise preference / candidate outcome
# ---------------------------------------------------------------------------


@dataclass
class PairwisePreference:
    case_id: str
    preferred_candidate_id: str
    other_candidate_id: str
    basis: str = "HUMAN_LISTENING"
    evaluator_id: str = ""
    created_at: str = field(default_factory=utcnow)
    schema_version: str = SCHEMA_VERSION

    def to_dict(self) -> dict:
        return {
            "case_id": self.case_id,
            "preferred_candidate_id": self.preferred_candidate_id,
            "other_candidate_id": self.other_candidate_id,
            "basis": self.basis,
            "evaluator_id": self.evaluator_id,
            "created_at": self.created_at,
            "schema_version": self.schema_version,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "PairwisePreference":
        return cls(
            case_id=data["case_id"],
            preferred_candidate_id=data["preferred_candidate_id"],
            other_candidate_id=data["other_candidate_id"],
            basis=data.get("basis", "HUMAN_LISTENING"),
            evaluator_id=data.get("evaluator_id", ""),
            created_at=data.get("created_at", utcnow()),
            schema_version=data.get("schema_version", SCHEMA_VERSION),
        )


@dataclass
class CandidateOutcome:
    case_id: str
    candidate_id: str
    outcome: str  # ACCEPTED | REJECTED | NEUTRAL | FAILED | OVERPROCESSED | UNCERTAIN
    technical_assessment: str | None = None
    workflow_decision: str | None = None
    artistic_decision: str | None = None
    reasons: list[str] = field(default_factory=list)
    created_at: str = field(default_factory=utcnow)
    schema_version: str = SCHEMA_VERSION

    def to_dict(self) -> dict:
        return {
            "case_id": self.case_id,
            "candidate_id": self.candidate_id,
            "outcome": self.outcome,
            "technical_assessment": self.technical_assessment,
            "workflow_decision": self.workflow_decision,
            "artistic_decision": self.artistic_decision,
            "reasons": self.reasons,
            "created_at": self.created_at,
            "schema_version": self.schema_version,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "CandidateOutcome":
        return cls(
            case_id=data["case_id"],
            candidate_id=data["candidate_id"],
            outcome=data["outcome"],
            technical_assessment=data.get("technical_assessment"),
            workflow_decision=data.get("workflow_decision"),
            artistic_decision=data.get("artistic_decision"),
            reasons=data.get("reasons", []),
            created_at=data.get("created_at", utcnow()),
            schema_version=data.get("schema_version", SCHEMA_VERSION),
        )


# ---------------------------------------------------------------------------
# LearningRecord
# ---------------------------------------------------------------------------

LEARNING_STATUS = (
    "NOT_STARTED", "CAPTURE_PENDING", "CAPTURED", "REVIEW_PENDING",
    "COMMITTED", "EXCLUDED", "INVALID",
)


@dataclass
class LearningRecord:
    learning_record_id: str
    case_id: str
    source_sha256: str
    candidate_ids: list[str]
    before_scan_ref: str = ""
    after_scan_refs: list[str] = field(default_factory=list)
    observations: list[str] = field(default_factory=list)
    intervention_refs: list[str] = field(default_factory=list)
    comparison_refs: list[str] = field(default_factory=list)
    human_evaluation_refs: list[str] = field(default_factory=list)
    pairwise_preferences: list[PairwisePreference] = field(default_factory=list)
    candidate_outcomes: list[CandidateOutcome] = field(default_factory=list)
    failure_labels: list[str] = field(default_factory=list)
    annotation_quality: str = "UNKNOWN"  # LOW | MEDIUM | HIGH | UNKNOWN
    rights: RightsMetadata = field(default_factory=RightsMetadata)
    training_eligibility: str = field(default_factory=default_eligibility)
    exclusion_reasons: list[str] = field(default_factory=list)
    review_status: str = "UNREVIEWED"  # UNREVIEWED | REVIEWED | APPROVED | REJECTED
    learning_status: str = "NOT_STARTED"
    committed_at: str = ""
    committed_by: str = ""
    evidence_manifest_ref: str = ""
    created_at: str = field(default_factory=utcnow)
    schema_version: str = SCHEMA_VERSION

    def to_dict(self) -> dict:
        return {
            "learning_record_id": self.learning_record_id,
            "schema_version": self.schema_version,
            "case_id": self.case_id,
            "source_sha256": self.source_sha256,
            "candidate_ids": self.candidate_ids,
            "before_scan_ref": self.before_scan_ref,
            "after_scan_refs": self.after_scan_refs,
            "observations": self.observations,
            "intervention_refs": self.intervention_refs,
            "comparison_refs": self.comparison_refs,
            "human_evaluation_refs": self.human_evaluation_refs,
            "pairwise_preferences": [p.to_dict() for p in self.pairwise_preferences],
            "candidate_outcomes": [c.to_dict() for c in self.candidate_outcomes],
            "failure_labels": self.failure_labels,
            "annotation_quality": self.annotation_quality,
            "rights": self.rights.to_dict(),
            "training_eligibility": self.training_eligibility,
            "exclusion_reasons": self.exclusion_reasons,
            "review_status": self.review_status,
            "learning_status": self.learning_status,
            "committed_at": self.committed_at,
            "committed_by": self.committed_by,
            "evidence_manifest_ref": self.evidence_manifest_ref,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "LearningRecord":
        return cls(
            learning_record_id=data["learning_record_id"],
            case_id=data["case_id"],
            source_sha256=data["source_sha256"],
            candidate_ids=data["candidate_ids"],
            before_scan_ref=data.get("before_scan_ref", ""),
            after_scan_refs=data.get("after_scan_refs", []),
            observations=data.get("observations", []),
            intervention_refs=data.get("intervention_refs", []),
            comparison_refs=data.get("comparison_refs", []),
            human_evaluation_refs=data.get("human_evaluation_refs", []),
            pairwise_preferences=[PairwisePreference.from_dict(p) for p in data.get("pairwise_preferences", [])],
            candidate_outcomes=[CandidateOutcome.from_dict(c) for c in data.get("candidate_outcomes", [])],
            failure_labels=data.get("failure_labels", []),
            annotation_quality=data.get("annotation_quality", "UNKNOWN"),
            rights=RightsMetadata.from_dict(data.get("rights", {})),
            training_eligibility=data.get("training_eligibility", default_eligibility()),
            exclusion_reasons=data.get("exclusion_reasons", []),
            review_status=data.get("review_status", "UNREVIEWED"),
            learning_status=data.get("learning_status", "NOT_STARTED"),
            committed_at=data.get("committed_at", ""),
            committed_by=data.get("committed_by", ""),
            evidence_manifest_ref=data.get("evidence_manifest_ref", ""),
            created_at=data.get("created_at", utcnow()),
            schema_version=data.get("schema_version", SCHEMA_VERSION),
        )
