# MFY-CR-P11 Reconstruction Commerce v0.1
"""
Commerce layer for Moodify Classic Reconstruction.

Submodules:
  - models:          Quote, Order, PaymentAttempt, Settlement, RefundRecord
  - pricing:         Server-side pricing policy with versioning
  - billing_matrix:  Outcome -> billing decision matrix + settlement gate
  - order_service:   Idempotent order creation with job binding
  - provider:        PaymentProvider interface + FakePaymentProvider (sandbox)
  - settlement:      Settlement gate service
  - refund:          Idempotent refund processing
  - audit:           Immutable audit log
  - reconciliation:  Orders vs payments vs settlements report
  - metrics:         Commerce metrics for unit economics

Authority:
  Price truth   = server pricing policy
  Payment truth = verified provider / server
  Job truth     = ReconstructionJob
  Audio result  = PrivateAudioObject
  Android is NEVER payment authority
"""

from .models import (
    CNY,
    OrderStatus,
    PaymentAttemptStatus,
    RefundStatus,
    BillingDecision,
    ReconstructionOutcome,
    AuditEventType,
    PlatformProvider,
    ReconstructionQuote,
    ReconstructionOrder,
    PaymentAttempt,
    Settlement,
    RefundRecord,
    ExternalCostLedger,
    AuditEntry,
)
from .pricing import PricingPolicy, PricingRule
from .billing_matrix import (
    BILLING_MATRIX,
    resolve_billing,
    is_billable,
    SettlementGate,
    can_settle,
    get_settlement_blockers,
)
from .order_service import OrderService, OrderCreateRequest
from .provider import (
    PaymentProvider,
    FakePaymentProvider,
    ProviderRegistry,
)
from .settlement import SettlementService
from .refund import RefundService
from .audit import AuditLog, get_audit_log
from .reconciliation import ReconciliationService, format_currency
from .metrics import CommerceMetrics, MetricsCollector, get_metrics

__all__ = [
    # Models
    "CNY", "OrderStatus", "PaymentAttemptStatus", "RefundStatus",
    "BillingDecision", "ReconstructionOutcome", "AuditEventType", "PlatformProvider",
    "ReconstructionQuote", "ReconstructionOrder", "PaymentAttempt",
    "Settlement", "RefundRecord", "ExternalCostLedger", "AuditEntry",
    # Pricing
    "PricingPolicy", "PricingRule",
    # Billing
    "BILLING_MATRIX", "resolve_billing", "is_billable",
    "SettlementGate", "can_settle", "get_settlement_blockers",
    # Orders
    "OrderService", "OrderCreateRequest",
    # Provider
    "PaymentProvider", "FakePaymentProvider", "ProviderRegistry",
    # Settlement & Refund
    "SettlementService", "RefundService",
    # Audit
    "AuditLog", "get_audit_log",
    # Reconciliation
    "ReconciliationService", "format_currency",
    # Metrics
    "CommerceMetrics", "MetricsCollector", "get_metrics",
]
