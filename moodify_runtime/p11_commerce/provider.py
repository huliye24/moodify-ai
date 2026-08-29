# MFY-CR-P11 — Payment Provider Interface
"""
Unified payment provider abstraction.

Business logic must NOT be scattered across provider-specific if/else.
All providers implement the same interface.
"""

from __future__ import annotations

import time
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from .models import (
    PaymentAttempt,
    PaymentAttemptStatus,
    PlatformProvider,
    RefundRecord,
    RefundStatus,
)


# ---------------------------------------------------------------------------
# Provider interface
# ---------------------------------------------------------------------------

class PaymentProvider(ABC):
    """Abstract payment provider contract.

    All real providers (WeChat Pay, Alipay, Stripe, Google Pay, Apple IAP)
    must implement this interface.
    """

    @abstractmethod
    def capabilities(self) -> dict:
        """Return provider capabilities.

        Example:
            {
                "preauth": bool,
                "capture": bool,
                "webhook": bool,
                "refund": bool,
                "async_notification": bool,
            }
        """
        ...

    @abstractmethod
    def create_payment(
        self, order_id: str, amount_minor: int, currency: str,
        description: str = "", **kwargs,
    ) -> PaymentAttempt:
        """Initiate a payment.

        Returns a PaymentAttempt with provider-specific IDs.
        """
        ...

    @abstractmethod
    def query_payment(self, provider_attempt_id: str) -> PaymentAttempt:
        """Query payment status from provider."""
        ...

    @abstractmethod
    def verify_callback(
        self, raw_payload: dict, signature: str, **kwargs,
    ) -> tuple:
        """Verify webhook/callback authenticity.

        Returns:
            (is_valid: bool, event_id: str, payload: dict)
        """
        ...

    @abstractmethod
    def refund(
        self, provider_attempt_id: str, amount_minor: Optional[int] = None,
        reason: str = "", **kwargs,
    ) -> RefundRecord:
        """Process a refund.

        If amount_minor is None, refund full amount.
        """
        ...


# ---------------------------------------------------------------------------
# FakePaymentProvider — sandbox / testing only
# ---------------------------------------------------------------------------

@dataclass
class _FakePaymentState:
    """In-memory state for fake provider."""
    payments: Dict[str, PaymentAttempt] = field(default_factory=dict)
    refunds: Dict[str, RefundRecord] = field(default_factory=dict)
    callback_events: Dict[str, dict] = field(default_factory=dict)  # event_id -> payload
    # Simulate failure modes
    _fail_next: bool = False
    _timeout_next: bool = False


class FakePaymentProvider(PaymentProvider):
    """Sandbox payment provider for P11 development and testing.

    NEVER use in production. Always returns success unless configured otherwise.

    Secrets: none (sandbox). In production, secrets live in secret manager.
    """

    def __init__(self):
        self._state = _FakePaymentState()

    def capabilities(self) -> dict:
        return {
            "preauth": True,
            "capture": True,
            "webhook": True,
            "refund": True,
            "async_notification": True,
        }

    def simulate_failure(self, fail: bool = True) -> None:
        """Configure next payment to fail (for testing)."""
        self._state._fail_next = fail

    def simulate_timeout(self, timeout: bool = True) -> None:
        """Configure next payment to timeout (for testing)."""
        self._state._timeout_next = timeout

    def create_payment(
        self, order_id: str, amount_minor: int, currency: str,
        description: str = "", **kwargs,
    ) -> PaymentAttempt:
        attempt = PaymentAttempt(
            order_id=order_id,
            provider="FAKE_PROVIDER",
            provider_attempt_id=f"FAKE-{uuid.uuid4().hex[:12].upper()}",
            amount_minor=amount_minor,
            currency=currency,
            status=PaymentAttemptStatus.PENDING,
            provider_event_id=f"EVT-{uuid.uuid4().hex[:8]}",
        )

        if self._state._fail_next:
            attempt.status = PaymentAttemptStatus.FAILED
            attempt.error_code = "SIMULATED_FAILURE"
            attempt.completed_at = time.time()
            self._state._fail_next = False
        elif self._state._timeout_next:
            # Leave as PENDING to simulate timeout
            attempt.error_code = "SIMULATED_TIMEOUT"
            self._state._timeout_next = False
        else:
            # Auto-succeed for sandbox
            attempt.status = PaymentAttemptStatus.SUCCESS
            attempt.completed_at = time.time()

        self._state.payments[attempt.payment_attempt_id] = attempt
        return attempt

    def query_payment(self, provider_attempt_id: str) -> PaymentAttempt:
        for attempt in self._state.payments.values():
            if attempt.provider_attempt_id == provider_attempt_id:
                return attempt
        raise ValueError(f"No payment found for {provider_attempt_id}")

    def verify_callback(
        self, raw_payload: dict, signature: str, **kwargs,
    ) -> tuple:
        """Verify fake callback. Accepts any non-empty signature."""
        event_id = raw_payload.get("event_id", f"EVT-{uuid.uuid4().hex[:8]}")

        # Replay detection
        if event_id in self._state.callback_events:
            return True, event_id, self._state.callback_events[event_id]

        self._state.callback_events[event_id] = raw_payload
        return True, event_id, raw_payload

    def refund(
        self, provider_attempt_id: str, amount_minor: Optional[int] = None,
        reason: str = "", **kwargs,
    ) -> RefundRecord:
        original = None
        for attempt in self._state.payments.values():
            if attempt.provider_attempt_id == provider_attempt_id:
                original = attempt
                break

        if not original:
            raise ValueError(f"No payment found for refund: {provider_attempt_id}")

        refund_amount = amount_minor if amount_minor is not None else original.amount_minor

        refund = RefundRecord(
            order_id=original.order_id,
            amount_minor=refund_amount,
            currency=original.currency,
            status=RefundStatus.CONFIRMED,  # auto-confirm in fake
            reason=reason or "Sandbox refund",
            provider_refund_id=f"RFN-FAKE-{uuid.uuid4().hex[:8].upper()}",
        )

        self._state.refunds[refund.refund_id] = refund
        return refund


# ---------------------------------------------------------------------------
# Provider Registry
# ---------------------------------------------------------------------------

class ProviderRegistry:
    """Registry mapping platform -> provider instance."""

    _providers: Dict[str, PaymentProvider] = {}

    @classmethod
    def register(cls, platform: str, provider: PaymentProvider) -> None:
        cls._providers[platform] = provider

    @classmethod
    def get(cls, platform: str) -> Optional[PaymentProvider]:
        return cls._providers.get(platform)

    @classmethod
    def list_platforms(cls) -> list:
        return list(cls._providers.keys())


# Bootstrap: register fake provider for sandbox
ProviderRegistry.register(PlatformProvider.FAKE_PROVIDER.value, FakePaymentProvider())
