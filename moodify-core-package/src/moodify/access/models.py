"""Open access + CWC compute credit domain models (DSK-MFY-ACCESS-CWC-PATCH-001).

CWC is a non-transferable compute quota (计算额度), never a token or
financial instrument. Admission controls expensive operations through
estimated cost, balance checks, reservation, queueing, concurrency
limits, and settlement with refunds — while registration itself is open.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any


def _iso_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


@dataclass(frozen=True)
class UserAccessProfile:
    user_id: str
    registration_mode: str  # OPEN | REFERRAL
    access_tier: str  # free | creator | enterprise
    referral_code_used: str | None = None
    referral_reward_state: str = "NONE"  # NONE | PENDING | GRANTED
    created_at: str = field(default_factory=_iso_now)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "UserAccessProfile":
        return cls(**data)


@dataclass(frozen=True)
class CWCBalance:
    owner_id: str
    available_cwc: float = 0.0
    reserved_cwc: float = 0.0
    lifetime_granted_cwc: float = 0.0
    lifetime_consumed_cwc: float = 0.0
    lifetime_refunded_cwc: float = 0.0
    updated_at: str = field(default_factory=_iso_now)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "CWCBalance":
        return cls(**data)


@dataclass(frozen=True)
class CWCTransaction:
    transaction_id: str
    owner_id: str
    type: str  # GRANT | RESERVE | CONSUME | RELEASE | REFUND | REFERRAL_REWARD | ADMIN_ADJUST
    amount: float
    related_job_id: str | None = None
    related_operation: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=_iso_now)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "CWCTransaction":
        return cls(**data)


@dataclass(frozen=True)
class ComputeJobAdmission:
    admission_id: str
    owner_id: str
    operation_type: str
    estimated_cwc: float
    queue_state: str  # QUEUED | ADMITTED | COMPLETED | FAILED | REJECTED_INSUFFICIENT
    priority_tier: str = "free"
    actual_cwc: float | None = None
    admitted_at: str | None = None
    completed_at: str | None = None
    failure_reason: str | None = None
    created_at: str = field(default_factory=_iso_now)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ComputeJobAdmission":
        return cls(**data)


@dataclass(frozen=True)
class QuotaState:
    owner_id: str
    tier: str
    concurrency_active: int = 0
    daily_usage: dict[str, int] = field(default_factory=dict)
    last_submission_at: str = ""
    submissions_last_minute: int = 0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "QuotaState":
        return cls(**data)


@dataclass(frozen=True)
class ReferralRewardRecord:
    record_id: str
    inviter_id: str
    invitee_id: str
    reward_amount: float
    state: str  # PENDING | GRANTED | REVOKED
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=_iso_now)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ReferralRewardRecord":
        return cls(**data)
