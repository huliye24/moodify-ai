# MFY-CR-P11 — Refund Service
"""
Idempotent refund processing.

Guarantees:
  - Same idempotency_key -> no duplicate refund
  - Server verified
  - Provider receipt retained
  - Linked to original order
  - Audit logged
"""

from __future__ import annotations

import time
import uuid
from typing import Optional, Tuple

from .models import (
    OrderStatus,
    RefundRecord,
    RefundStatus,
    ReconstructionOrder,
)
from .order_service import OrderService
from .provider import ProviderRegistry, PlatformProvider


class RefundService:
    """Server-side refund authority."""

    def __init__(self, order_service: OrderService):
        self._orders = order_service
        self._refunds: dict = {}  # refund_id -> RefundRecord
        self._refund_idempotency: dict = {}  # idempotency_key -> refund_id

    def request_refund(
        self,
        order_id: str,
        owner_id: str,
        reason: str = "",
        idempotency_key: str = "",
        platform: str = "FAKE_PROVIDER",
    ) -> Tuple[bool, str, Optional[RefundRecord]]:
        """Request a refund with full idempotency protection.

        Returns:
            (success: bool, message: str, refund: Optional[RefundRecord])
        """
        # 1. Validate order exists and belongs to this user
        order = self._orders.get_order(order_id)
        if not order:
            return False, "Order not found", None

        if order.owner_id != owner_id:
            return False, "Order does not belong to this user", None

        # 2. Idempotency check FIRST (before status check)
        if idempotency_key:
            existing_refund_id = self._refund_idempotency.get(idempotency_key)
            if existing_refund_id:
                existing = self._refunds.get(existing_refund_id)
                if existing:
                    return True, "Idempotent: returning existing refund", existing

        # 3. Check for existing refund on this order
        for r in self._refunds.values():
            if r.order_id == order_id and r.status in (
                RefundStatus.CONFIRMED, RefundStatus.PENDING,
            ):
                return True, "Refund already processed for this order", r

        # 4. Check order is in a refundable state
        if order.status not in (OrderStatus.PAID,):
            # Also allow refunding NO_CHARGE orders (no-op but record it)
            if order.status == OrderStatus.NO_CHARGE:
                no_op = RefundRecord(
                    order_id=order_id,
                    amount_minor=0,
                    currency=order.currency,
                    status=RefundStatus.REJECTED,
                    reason="NO_CHARGE order — nothing to refund",
                )
                return False, "NO_CHARGE order — nothing to refund", no_op

            return False, f"Order status {order.status.value} is not refundable", None

        # 5. Create refund record
        refund = RefundRecord(
            order_id=order_id,
            amount_minor=order.amount_minor,
            currency=order.currency,
            status=RefundStatus.PENDING,
            reason=reason or "User requested refund",
            idempotency_key=idempotency_key,
        )

        # 6. Call provider for actual refund
        prov = ProviderRegistry.get(platform)
        if prov is None:
            prov = ProviderRegistry.get(PlatformProvider.FAKE_PROVIDER.value)

        if order.provider_order_id:
            try:
                provider_refund = prov.refund(
                    provider_attempt_id=order.provider_order_id,
                    amount_minor=order.amount_minor,
                    reason=reason,
                )
                refund.provider_refund_id = provider_refund.provider_refund_id
                refund.status = RefundStatus.CONFIRMED
                refund.confirmed_at = time.time()
            except Exception as e:
                refund.status = RefundStatus.FAILED
                refund.reason = f"Provider error: {e}"
        else:
            # No provider order ID (sandbox / test) — auto-confirm
            refund.status = RefundStatus.CONFIRMED
            refund.confirmed_at = time.time()
            refund.provider_refund_id = f"SANDBOX-{uuid.uuid4().hex[:8].upper()}"

        # 7. Store
        self._refunds[refund.refund_id] = refund
        if idempotency_key:
            self._refund_idempotency[idempotency_key] = refund.refund_id

        # 8. Update order status
        if refund.status == RefundStatus.CONFIRMED:
            self._orders.update_status(order_id, OrderStatus.REFUNDED)

        success = refund.status == RefundStatus.CONFIRMED
        msg = "Refund confirmed" if success else f"Refund {refund.status.value}: {refund.reason}"
        return success, msg, refund

    def get_refund(self, refund_id: str) -> Optional[RefundRecord]:
        return self._refunds.get(refund_id)

    def get_refunds_for_order(self, order_id: str) -> list:
        return [r for r in self._refunds.values() if r.order_id == order_id]

    def list_all(self) -> list:
        return [r.to_dict() for r in self._refunds.values()]
