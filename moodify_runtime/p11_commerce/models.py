# MFY-CR-P11 Reconstruction Commerce v0.1
"""
Commerce layer for Moodify Classic Reconstruction.

Authority boundaries:
  - Price truth   = server pricing policy
  - Payment truth = verified provider / server
  - Job truth     = ReconstructionJob
  - Audio result  = PrivateAudioObject
  - Android is NEVER payment authority

Flow: Quote -> Order -> Payment -> Job -> PrivateResult -> Settlement -> Receipt
"""

from __future__ import annotations

import enum
import time
import uuid
from dataclasses import dataclass, field
from typing import Optional


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

CNY = "CNY"
DEFAULT_PRICING_VERSION = "v0.1.0"
DEFAULT_RECONSTRUCTION_VERSION = "v0.1.0"
QUOTE_TTL_SECONDS = 600  # 10 minutes


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class OrderStatus(enum.Enum):
    """Product-level order status — independent of provider status."""
    CREATED = "CREATED"
    PAYMENT_PENDING = "PAYMENT_PENDING"
    AUTHORIZED = "AUTHORIZED"
    JOB_CREATED = "JOB_CREATED"
    PROCESSING = "PROCESSING"
    SETTLEMENT_PENDING = "SETTLEMENT_PENDING"
    PAID = "PAID"
    NO_CHARGE = "NO_CHARGE"
    REFUND_PENDING = "REFUND_PENDING"
    REFUNDED = "REFUNDED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class PaymentAttemptStatus(enum.Enum):
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    TIMEOUT = "TIMEOUT"
    REFUNDED = "REFUNDED"


class RefundStatus(enum.Enum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    REJECTED = "REJECTED"
    FAILED = "FAILED"


class BillingDecision(enum.Enum):
    CHARGE = "CHARGE"
    NO_CHARGE = "NO_CHARGE"
    NO_CHARGE_YET = "NO_CHARGE_YET"  # e.g. HUMAN_REQUIRED waiting approval
    PENDING_VERIFICATION = "PENDING_VERIFICATION"


class ReconstructionOutcome(enum.Enum):
    SUCCEEDED = "SUCCEEDED"           # Moodify reconstruction succeeded
    SOURCE_WINS = "SOURCE_WINS"       # Original was better
    HUMAN_REQUIRED = "HUMAN_REQUIRED" # Needs human judgment
    TECHNICAL_FAILED = "TECHNICAL_FAILED"
    UNSUPPORTED = "UNSUPPORTED"
    ENCRYPTION_FAILED = "ENCRYPTION_FAILED"
    PLAYBACK_VERIFY_FAILED = "PLAYBACK_VERIFY_FAILED"


class AuditEventType(enum.Enum):
    QUOTE_CREATED = "quote_created"
    ORDER_CREATED = "order_created"
    PAYMENT_STARTED = "payment_started"
    PAYMENT_VERIFIED = "payment_verified"
    JOB_CREATED = "job_created"
    JOB_COMPLETED = "job_completed"
    PRIVATE_OBJECT_FINALIZED = "private_object_finalized"
    SETTLEMENT_REQUESTED = "settlement_requested"
    SETTLEMENT_CONFIRMED = "settlement_confirmed"
    REFUND_REQUESTED = "refund_requested"
    REFUND_CONFIRMED = "refund_confirmed"
    PRICING_CHANGED = "pricing_changed"


class PlatformProvider(enum.Enum):
    ANDROID_PROVIDER = "ANDROID_PROVIDER"
    WEB_PROVIDER = "WEB_PROVIDER"
    IOS_PROVIDER = "IOS_PROVIDER"
    FAKE_PROVIDER = "FAKE_PROVIDER"  # sandbox only


# ---------------------------------------------------------------------------
# Commerce Objects
# ---------------------------------------------------------------------------

@dataclass
class ReconstructionQuote:
    """Server-generated price quote for a reconstruction.

    Android may DISPLAY this but must never fabricate or modify it.
    """
    quote_id: str = field(default_factory=lambda: f"QT-{uuid.uuid4().hex[:12].upper()}")
    owner_id: str = ""
    currency: str = CNY
    unit_amount_minor: int = 100  # 1 CNY in minor units (fen/分)
    quantity: int = 1
    total_amount_minor: int = field(init=False)
    pricing_version: str = DEFAULT_PRICING_VERSION
    reconstruction_version: str = DEFAULT_RECONSTRUCTION_VERSION
    expires_at: float = field(init=False)
    created_at: float = field(default_factory=time.time)

    def __post_init__(self):
        self.total_amount_minor = self.unit_amount_minor * self.quantity
        self.expires_at = self.created_at + QUOTE_TTL_SECONDS

    def is_expired(self) -> bool:
        return time.time() > self.expires_at

    def to_dict(self) -> dict:
        return {
            "quote_id": self.quote_id,
            "owner_id": self.owner_id,
            "currency": self.currency,
            "unit_amount_minor": self.unit_amount_minor,
            "quantity": self.quantity,
            "total_amount_minor": self.total_amount_minor,
            "pricing_version": self.pricing_version,
            "reconstruction_version": self.reconstruction_version,
            "expires_at": self.expires_at,
            "created_at": self.created_at,
        }


@dataclass
class ReconstructionOrder:
    """One order -> one logical job -> multiple internal retries.

    Client cannot self-declare paid. Server is sole authority.
    """
    order_id: str = field(default_factory=lambda: f"ORD-{uuid.uuid4().hex[:12].upper()}")
    owner_id: str = ""
    quote_id: str = ""
    job_id: str = ""  # bound after job creation
    source_sha256: str = ""
    reconstruction_version: str = DEFAULT_RECONSTRUCTION_VERSION
    currency: str = CNY
    amount_minor: int = 0
    status: OrderStatus = OrderStatus.CREATED
    payment_provider: str = ""
    provider_order_id: str = ""
    idempotency_key: str = ""  # client-provided dedup key
    created_at: float = field(default_factory=time.time)
    authorized_at: float = 0.0
    settled_at: float = 0.0
    refunded_at: float = 0.0
    failure_reason: str = ""
    billing_decision: Optional[BillingDecision] = None
    outcome: Optional[ReconstructionOutcome] = None

    def to_dict(self) -> dict:
        return {
            "order_id": self.order_id,
            "owner_id": self.owner_id,
            "quote_id": self.quote_id,
            "job_id": self.job_id,
            "source_sha256": self.source_sha256,
            "reconstruction_version": self.reconstruction_version,
            "currency": self.currency,
            "amount_minor": self.amount_minor,
            "status": self.status.value,
            "payment_provider": self.payment_provider,
            "provider_order_id": self.provider_order_id,
            "idempotency_key": self.idempotency_key,
            "created_at": self.created_at,
            "authorized_at": self.authorized_at,
            "settled_at": self.settled_at,
            "refunded_at": self.refunded_at,
            "failure_reason": self.failure_reason,
            "billing_decision": self.billing_decision.value if self.billing_decision else None,
            "outcome": self.outcome.value if self.outcome else None,
        }


@dataclass
class PaymentAttempt:
    """One order can have multiple attempts, but only one final result."""
    payment_attempt_id: str = field(default_factory=lambda: f"PA-{uuid.uuid4().hex[:12].upper()}")
    order_id: str = ""
    provider: str = ""
    provider_attempt_id: str = ""
    amount_minor: int = 0
    currency: str = CNY
    status: PaymentAttemptStatus = PaymentAttemptStatus.PENDING
    created_at: float = field(default_factory=time.time)
    completed_at: float = 0.0
    error_code: str = ""
    provider_event_id: str = ""  # for replay detection

    def to_dict(self) -> dict:
        return {
            "payment_attempt_id": self.payment_attempt_id,
            "order_id": self.order_id,
            "provider": self.provider,
            "provider_attempt_id": self.provider_attempt_id,
            "amount_minor": self.amount_minor,
            "currency": self.currency,
            "status": self.status.value,
            "created_at": self.created_at,
            "completed_at": self.completed_at,
            "error_code": self.error_code,
            "provider_event_id": self.provider_event_id,
        }


@dataclass
class Settlement:
    """Final financial resolution of an order."""
    settlement_id: str = field(default_factory=lambda: f"STL-{uuid.uuid4().hex[:12].upper()}")
    order_id: str = ""
    amount_minor: int = 0
    currency: str = CNY
    billing_decision: BillingDecision = BillingDecision.NO_CHARGE
    outcome: Optional[ReconstructionOutcome] = None
    private_object_finalized: bool = False
    playback_verified: bool = False
    settled_at: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        return {
            "settlement_id": self.settlement_id,
            "order_id": self.order_id,
            "amount_minor": self.amount_minor,
            "currency": self.currency,
            "billing_decision": self.billing_decision.value,
            "outcome": self.outcome.value if self.outcome else None,
            "private_object_finalized": self.private_object_finalized,
            "playback_verified": self.playback_verified,
            "settled_at": self.settled_at,
        }


@dataclass
class RefundRecord:
    """Idempotent refund record linked to an order."""
    refund_id: str = field(default_factory=lambda: f"RFN-{uuid.uuid4().hex[:12].upper()}")
    order_id: str = ""
    amount_minor: int = 0
    currency: str = CNY
    status: RefundStatus = RefundStatus.PENDING
    reason: str = ""
    provider_refund_id: str = ""
    idempotency_key: str = ""  # dedup key for refund
    created_at: float = field(default_factory=time.time)
    confirmed_at: float = 0.0

    def to_dict(self) -> dict:
        return {
            "refund_id": self.refund_id,
            "order_id": self.order_id,
            "amount_minor": self.amount_minor,
            "currency": self.currency,
            "status": self.status.value,
            "reason": self.reason,
            "provider_refund_id": self.provider_refund_id,
            "idempotency_key": self.idempotency_key,
            "created_at": self.created_at,
            "confirmed_at": self.confirmed_at,
        }


@dataclass
class ExternalCostLedger:
    """Track external service costs (LALAL/Audiolla/future providers).

    Internal cost != user price.
    """
    entry_id: str = field(default_factory=lambda: f"ECL-{uuid.uuid4().hex[:12].upper()}")
    job_id: str = ""
    provider: str = ""
    operation: str = ""
    units: int = 0
    estimated_cost_minor: int = 0
    actual_cost_minor: int = 0
    currency: str = CNY
    created_at: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        return {
            "entry_id": self.entry_id,
            "job_id": self.job_id,
            "provider": self.provider,
            "operation": self.operation,
            "units": self.units,
            "estimated_cost_minor": self.estimated_cost_minor,
            "actual_cost_minor": self.actual_cost_minor,
            "currency": self.currency,
            "created_at": self.created_at,
        }


@dataclass
class AuditEntry:
    """Immutable audit log entry."""
    event_id: str = field(default_factory=lambda: uuid.uuid4().hex)
    event_type: AuditEventType = AuditEventType.QUOTE_CREATED
    owner_id: str = ""
    order_id: str = ""
    job_id: str = ""
    details: dict = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        return {
            "event_id": self.event_id,
            "event_type": self.event_type.value,
            "owner_id": self.owner_id,
            "order_id": self.order_id,
            "job_id": self.job_id,
            "details": self.details,
            "timestamp": self.timestamp,
        }
