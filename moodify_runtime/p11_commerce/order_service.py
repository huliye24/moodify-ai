# MFY-CR-P11 — Order Service
"""
Idempotent order creation with job binding.

Key guarantees:
  - Same user + same source + same version + same intent -> no duplicate order
  - One order -> one logical ReconstructionJob (internal retries don't create new orders)
  - Duplicate taps / network retries / callback replays cannot double-charge
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass
from typing import Dict, List, Optional

from .models import (
    OrderStatus,
    ReconstructionOrder,
    ReconstructionOutcome,
    BillingDecision,
)
from .pricing import PricingPolicy


@dataclass
class OrderCreateRequest:
    """Client-submitted order creation request."""
    owner_id: str = ""
    quote_id: str = ""
    source_sha256: str = ""
    reconstruction_version: str = "v0.1.0"
    idempotency_key: str = ""  # client-provided dedup key
    platform: str = "ANDROID_PROVIDER"  # or WEB_PROVIDER, IOS_PROVIDER


class OrderService:
    """Server-side order management with idempotency.

    In production this would backed by a database.
    v0.1 uses in-memory storage for sandbox validation.
    """

    def __init__(self):
        self._orders: Dict[str, ReconstructionOrder] = {}  # order_id -> order
        self._idempotency_index: Dict[str, str] = {}  # idempotency_key -> order_id
        # Index for duplicate detection: (owner_id, source_sha256, recon_version) -> order_id
        self._source_index: Dict[str, str] = {}
        self._lock_container = _DummyLock()

    def create_order(self, req: OrderCreateRequest) -> tuple:
        """Create an order with full idempotency protection.

        Returns:
            (order: ReconstructionOrder, created: bool, message: str)

        If idempotency_key matches an existing order, returns that order
        without creating a duplicate (created=False).
        """
        # 1. Check idempotency first
        if req.idempotency_key:
            existing_order_id = self._idempotency_index.get(req.idempotency_key)
            if existing_order_id:
                existing = self._orders.get(existing_order_id)
                if existing:
                    return existing, False, "Idempotent: returning existing order"

        # 2. Check source dedup: same track + same version should not create new order
        if req.source_sha256:
            source_dedup_key = f"{req.owner_id}:{req.source_sha256}:{req.reconstruction_version}"
            existing_order_id = self._source_index.get(source_dedup_key)
            if existing_order_id:
                existing = self._orders.get(existing_order_id)
                if existing and existing.status not in (
                    OrderStatus.FAILED, OrderStatus.CANCELLED, OrderStatus.REFUNDED
                ):
                    # Existing order still active — return it
                    return existing, False, "Same track+version: returning existing order"

        # 3. Resolve pricing from server-side policy
        policy = PricingPolicy.get_instance()
        quote_amount = policy.quote_amount(quantity=1)

        # 4. Create new order
        order = ReconstructionOrder(
            owner_id=req.owner_id,
            quote_id=req.quote_id,
            source_sha256=req.source_sha256,
            reconstruction_version=req.reconstruction_version,
            currency="CNY",
            amount_minor=quote_amount,
            status=OrderStatus.CREATED,
            idempotency_key=req.idempotency_key,
        )

        # 5. Store
        self._orders[order.order_id] = order

        if req.idempotency_key:
            self._idempotency_index[req.idempotency_key] = order.order_id

        if req.source_sha256:
            source_dedup_key = f"{req.owner_id}:{req.source_sha256}:{req.reconstruction_version}"
            self._source_index[source_dedup_key] = order.order_id

        return order, True, "Order created"

    def get_order(self, order_id: str) -> Optional[ReconstructionOrder]:
        """Retrieve order by ID."""
        return self._orders.get(order_id)

    def get_orders_by_owner(self, owner_id: str) -> List[ReconstructionOrder]:
        """List all orders for a user."""
        return [o for o in self._orders.values() if o.owner_id == owner_id]

    def bind_job(self, order_id: str, job_id: str) -> bool:
        """Bind a ReconstructionJob to an order.

        One order -> one logical job. Internal retries use the same job_id.
        """
        order = self._orders.get(order_id)
        if not order:
            return False
        if order.job_id and order.job_id != job_id:
            # Job already bound — prevent rebinding to different job
            return False
        order.job_id = job_id
        order.status = OrderStatus.JOB_CREATED
        return True

    def update_status(self, order_id: str, status: OrderStatus) -> bool:
        """Update order status."""
        order = self._orders.get(order_id)
        if not order:
            return False
        now = time.time()
        order.status = status
        if status == OrderStatus.AUTHORIZED:
            order.authorized_at = now
        elif status in (OrderStatus.PAID, OrderStatus.NO_CHARGE):
            order.settled_at = now
        elif status == OrderStatus.REFUNDED:
            order.refunded_at = now
        return True

    def set_outcome(self, order_id: str, outcome: ReconstructionOutcome) -> bool:
        """Set reconstruction outcome and derive billing decision."""
        from .billing_matrix import resolve_billing
        order = self._orders.get(order_id)
        if not order:
            return False
        order.outcome = outcome
        order.billing_decision = resolve_billing(outcome)
        return True

    def check_existing_result(
        self, owner_id: str, source_sha256: str, reconstruction_version: str,
    ) -> Optional[ReconstructionOrder]:
        """Check if user already has a successful result for this track+version.

        Used for RETURN_EXISTING_RESULT optimization.
        """
        source_key = f"{owner_id}:{source_sha256}:{reconstruction_version}"
        order_id = self._source_index.get(source_key)
        if order_id:
            order = self._orders.get(order_id)
            if order and order.outcome == ReconstructionOutcome.SUCCEEDED:
                if order.status in (OrderStatus.PAID, OrderStatus.NO_CHARGE):
                    return order
        return None

    def count_unpaid_jobs(self, owner_id: str) -> int:
        """Count concurrent unpaid jobs for abuse protection."""
        count = 0
        for o in self._orders.values():
            if o.owner_id != owner_id:
                continue
            if o.status in (
                OrderStatus.CREATED,
                OrderStatus.PAYMENT_PENDING,
                OrderStatus.AUTHORIZED,
                OrderStatus.JOB_CREATED,
                OrderStatus.PROCESSING,
                OrderStatus.SETTLEMENT_PENDING,
            ):
                count += 1
        return count


class _DummyLock:
    """Placeholder lock for v0.1 in-memory store. Replace with real DB lock in production."""
    pass
