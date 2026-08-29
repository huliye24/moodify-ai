"""Product-layer reconstruction job contracts (MFY-CR-P08).

ReconstructionJob is a product orchestration object only. ProductionCase /
EvidenceArtifact / Rule remain the canonical production authority; job status
is a projection, never a second source of truth.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from moodify.compat import StrEnum

RECONSTRUCTION_VERSION = "reconstruction-job-v0.1"
PRIVACY_POLICY_VERSION = "privacy-policy-v0.1"
RETENTION_POLICY_VERSION = "retention-policy-v0.1"
BILLING_STATE_NOT_IMPLEMENTED = "NOT_IMPLEMENTED"

FAILURE_CODES = (
    "INVALID_INPUT",
    "UNSUPPORTED_FORMAT",
    "DECODE_FAILED",
    "RESOURCE_LIMIT",
    "PIPELINE_FAILED",
    "IDENTITY_REJECTED",
    "HUMAN_REQUIRED",
    "EXTERNAL_SERVICE_FAILED",
    "EXTERNAL_BILLING_AMBIGUOUS",
    "STORAGE_FAILED",
    "AUTH_FAILED",
    "CANCELLED",
)

RETRY_POLICIES = ("TRANSIENT", "PERMANENT", "HUMAN_REQUIRED", "EXTERNAL_BILLABLE")


class JobStatus(StrEnum):
    QUEUED = "QUEUED"
    VALIDATING = "VALIDATING"
    ANALYZING = "ANALYZING"
    PLANNING = "PLANNING"
    RECONSTRUCTING = "RECONSTRUCTING"
    VERIFYING = "VERIFYING"
    HUMAN_REQUIRED = "HUMAN_REQUIRED"
    SUCCEEDED = "SUCCEEDED"
    SOURCE_WINS = "SOURCE_WINS"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


TERMINAL_STATUSES = frozenset(
    {JobStatus.HUMAN_REQUIRED, JobStatus.SUCCEEDED, JobStatus.SOURCE_WINS,
     JobStatus.FAILED, JobStatus.CANCELLED}
)

# Product-facing progress projection (P08 §17): internal stages stay internal.
PROGRESS_LABELS = {
    JobStatus.QUEUED: "Preparing",
    JobStatus.VALIDATING: "Preparing",
    JobStatus.ANALYZING: "Listening",
    JobStatus.PLANNING: "Reconstructing",
    JobStatus.RECONSTRUCTING: "Reconstructing",
    JobStatus.VERIFYING: "Verifying",
    JobStatus.HUMAN_REQUIRED: "Verifying",
    JobStatus.SUCCEEDED: "Ready",
    JobStatus.SOURCE_WINS: "Ready",
    JobStatus.FAILED: "Failed",
    JobStatus.CANCELLED: "Cancelled",
}


def progress_label(status: str) -> str:
    return PROGRESS_LABELS.get(JobStatus(status), "Preparing")


@dataclass(frozen=True)
class FailureInfo:
    failure_code: str
    stage: str
    retry_policy: str
    user_action: str
    internal_detail: str
    public_message_key: str

    @property
    def retryable(self) -> bool:
        return self.retry_policy == "TRANSIENT"


@dataclass(frozen=True)
class RetentionPolicy:
    source_ttl_s: Optional[int] = 30 * 86400
    tmp_ttl_s: Optional[int] = 0
    stems_ttl_s: Optional[int] = 0
    candidates_ttl_s: Optional[int] = 7 * 86400
    result_ttl_s: Optional[int] = 90 * 86400
    evidence_ttl_s: Optional[int] = None

    @classmethod
    def from_dict(cls, payload: dict) -> "RetentionPolicy":
        allowed = {f.name for f in cls.__dataclass_fields__.values()}
        return cls(**{k: v for k, v in payload.items() if k in allowed})

    def to_dict(self) -> dict:
        return {f.name: getattr(self, f.name) for f in self.__dataclass_fields__.values()}


@dataclass(frozen=True)
class ResourceUsage:
    cpu_time_s: float = 0.0
    wall_time_s: float = 0.0
    peak_memory_mb: float = 0.0
    disk_temp_usage_mb: float = 0.0
    external_api_usage: int = 0
    candidate_count: int = 0
    stem_count: int = 0

    def to_dict(self) -> dict:
        return {
            "cpu_time_s": round(self.cpu_time_s, 3),
            "wall_time_s": round(self.wall_time_s, 3),
            "peak_memory_mb": round(self.peak_memory_mb, 1),
            "disk_temp_usage_mb": round(self.disk_temp_usage_mb, 1),
            "external_api_usage": self.external_api_usage,
            "candidate_count": self.candidate_count,
            "stem_count": self.stem_count,
        }


@dataclass(frozen=True)
class ReconstructionJob:
    job_id: str
    owner_id: str
    source_asset_id: str
    source_sha256: str
    status: str
    progress_stage: str
    requested_at: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    failed_at: Optional[str] = None
    production_case_id: Optional[str] = None
    reconstruction_version: str = RECONSTRUCTION_VERSION
    result_object_id: Optional[str] = None
    result_status: Optional[str] = None
    failure_code: Optional[str] = None
    failure_stage: Optional[str] = None
    retry_policy: Optional[str] = None
    attempts: int = 0
    billing_state_placeholder: str = BILLING_STATE_NOT_IMPLEMENTED
    privacy_policy_version: str = PRIVACY_POLICY_VERSION
    training_permission: bool = False
    public_demo_permission: bool = False
    retention_policy: str = RETENTION_POLICY_VERSION
    idempotency_key: Optional[str] = None
    workspace_path: Optional[str] = None
    cancel_requested: bool = False
    lease_until: Optional[str] = None
    last_error: Optional[str] = None
    updated_at: str = ""

    def product_view(self) -> dict:
        """Owner-safe product projection; no internal paths or details."""
        return {
            "job_id": self.job_id,
            "status": self.status,
            "progress": progress_label(self.status),
            "source_sha256": self.source_sha256,
            "created_at": self.requested_at,
            "updated_at": self.updated_at,
            "result_available": self.result_object_id is not None,
            "user_action_required": self.status == JobStatus.HUMAN_REQUIRED,
        }


@dataclass(frozen=True)
class ReconstructionResult:
    result_id: str
    job_id: str
    production_case_id: str
    source_sha256: str
    selected_candidate: str
    audio_object_ref: str
    reconstruction_version: str
    plan_hash: Optional[str]
    engine_version: str
    identity_status: str
    technical_status: str
    created_at: str

    def to_dict(self) -> dict:
        return {
            "result_id": self.result_id,
            "job_id": self.job_id,
            "production_case_id": self.production_case_id,
            "source_sha256": self.source_sha256,
            "selected_candidate": self.selected_candidate,
            "audio_object_ref": self.audio_object_ref,
            "reconstruction_version": self.reconstruction_version,
            "plan_hash": self.plan_hash,
            "engine_version": self.engine_version,
            "identity_status": self.identity_status,
            "technical_status": self.technical_status,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, payload: dict) -> "ReconstructionResult":
        allowed = {f.name for f in cls.__dataclass_fields__.values()}
        return cls(**{k: v for k, v in payload.items() if k in allowed})


@dataclass(frozen=True)
class JobRecord:
    job: ReconstructionJob
    result: Optional[ReconstructionResult] = None
