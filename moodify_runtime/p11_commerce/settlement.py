# MFY-CR-P11 — Settlement Service
"""
Settlement: final financial resolution of an order.

Only settles when ALL gates pass:
  1. Billable outcome (SUCCEEDED)
  2. PrivateAudioObject FINALIZED
  3. Playback verification PASS
  4. Payment authorized

Cannot double-settle. Cannot settle before private result finalization.
"""

from __future__ import annotations

import time
from typing import Optional, Tuple

from .models import (
    OrderStatus,
    Settlement,
    ReconstructionOutcome,
    BillingDecision,
    ReconstructionOrder,
)
from .billing_matrix import (
    resolve_billing,
    SettlementGate,
    can_settle,
)
from .order_service import OrderService


class SettlementService:
    """Server-side settlement authority."""

    def __init__(self, order_service: OrderService):
        self._orders = order_service
        self._settlements: dict = {}  # order_id -> Settlement

    def evaluate_settlement(
        self,
        order_id: str,
        outcome: Optional[ReconstructionOutcome],
        private_object_finalized: bool = False,
        playback_verified: bool = False,
        payment_authorized: bool = False,
    ) -> Tuple[bool, str, Optional[Settlement]]:
        """Evaluate and optionally execute settlement.

        Returns:
            (settled: bool, message: str, settlement: Optional[Settlement])
        """
        order = self._orders.get_order(order_id)
        if not order:
            return False, "Order not found", None

        # Prevent double-settlement
        if order_id in self._settlements:
            existing = self._settlements[order_id]
            return False, f"Already settled at {existing.settled_at}", existing

        # Run settlement gate
        allowed, reason = SettlementGate.check(
            outcome, private_object_finalized, playback_verified, payment_authorized,
        )

        if not allowed:
            return False, f"Settlement blocked: {reason}", None

        # Gate passed — determine billing
        billing = resolve_billing(outcome)

        if billing != BillingDecision.CHARGE:
            # No-charge settlement (SOURCE_WINS, TECHNICAL_FAILED, etc.)
            settlement = self._create_no_charge_settlement(order, outcome, billing)
            self._settlements[order_id] = settlement
            self._orders.update_status(order_id, OrderStatus.NO_CHARGE)
            return True, f"No-charge settlement: {reason}", settlement

        # Full CHARGE settlement — strict: only SUCCEEDED with all gates
        settlement = Settlement(
            order_id=order_id,
            amount_minor=order.amount_minor,
            currency=order.currency,
            billing_decision=billing,
            outcome=outcome,
            private_object_finalized=private_object_finalized,
            playback_verified=playback_verified,
            settled_at=time.time(),
        )

        self._settlements[order_id] = settlement
        self._orders.update_status(order_id, OrderStatus.PAID)

        return True, "Settlement completed — CHARGE", settlement

    def _create_no_charge_settlement(
        self, order: ReconstructionOrder,
        outcome: ReconstructionOutcome, billing: BillingDecision,
    ) -> Settlement:
        return Settlement(
            order_id=order.order_id,
            amount_minor=0,
            currency=order.currency,
            billing_decision=billing,
            outcome=outcome,
            private_object_finalized=False,
            playback_verified=False,
            settled_at=time.time(),
        )

    def get_settlement(self, order_id: str) -> Optional[Settlement]:
        return self._settlements.get(order_id)

    def list_settlements(self) -> list:
        return [s.to_dict() for s in self._settlements.values()]
