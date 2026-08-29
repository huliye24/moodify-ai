# MFY-CR-P11 — Commerce Metrics
"""
Minimal metrics tracking for commerce health monitoring.

Counters:
  - quotes_created, orders_created, payments_started, payments_succeeded
  - jobs_succeeded, source_wins, paid_jobs, no_charge_jobs
  - refunds, payment_failures
  - gross_revenue, external_cost

Used for unit economics and cash flow quality assessment.
"""

from __future__ import annotations

import threading
from dataclasses import dataclass, field
from typing import Dict, Optional


@dataclass
class CommerceMetrics:
    """Snapshot of commerce metrics."""
    quotes_created: int = 0
    orders_created: int = 0
    payments_started: int = 0
    payments_succeeded: int = 0
    jobs_succeeded: int = 0
    source_wins: int = 0
    paid_jobs: int = 0
    no_charge_jobs: int = 0
    refunds: int = 0
    payment_failures: int = 0
    gross_revenue_minor: int = 0
    external_cost_minor: int = 0
    compute_cost_minor: int = 0
    storage_cost_minor: int = 0
    payment_fee_minor: int = 0
    refund_loss_minor: int = 0

    @property
    def net_revenue_minor(self) -> int:
        return (
            self.gross_revenue_minor
            - self.external_cost_minor
            - self.compute_cost_minor
            - self.storage_cost_minor
            - self.payment_fee_minor
            - self.refund_loss_minor
        )

    @property
    def contribution_margin_pct(self) -> float:
        if self.gross_revenue_minor == 0:
            return 0.0
        return (self.net_revenue_minor / self.gross_revenue_minor) * 100

    def to_dict(self) -> dict:
        return {
            "quotes_created": self.quotes_created,
            "orders_created": self.orders_created,
            "payments_started": self.payments_started,
            "payments_succeeded": self.payments_succeeded,
            "jobs_succeeded": self.jobs_succeeded,
            "source_wins": self.source_wins,
            "paid_jobs": self.paid_jobs,
            "no_charge_jobs": self.no_charge_jobs,
            "refunds": self.refunds,
            "payment_failures": self.payment_failures,
            "gross_revenue_minor": self.gross_revenue_minor,
            "external_cost_minor": self.external_cost_minor,
            "compute_cost_minor": self.compute_cost_minor,
            "storage_cost_minor": self.storage_cost_minor,
            "payment_fee_minor": self.payment_fee_minor,
            "refund_loss_minor": self.refund_loss_minor,
            "net_revenue_minor": self.net_revenue_minor,
            "contribution_margin_pct": round(self.contribution_margin_pct, 2),
        }


class MetricsCollector:
    """Thread-safe metrics collector."""

    def __init__(self):
        self._metrics = CommerceMetrics()
        self._lock = threading.Lock()

    def increment(self, field_name: str, value: int = 1) -> None:
        """Increment a counter field."""
        with self._lock:
            current = getattr(self._metrics, field_name, 0)
            setattr(self._metrics, field_name, current + value)

    def add_revenue(self, amount_minor: int) -> None:
        with self._lock:
            self._metrics.gross_revenue_minor += amount_minor

    def add_cost(
        self,
        external: int = 0,
        compute: int = 0,
        storage: int = 0,
        payment_fee: int = 0,
        refund_loss: int = 0,
    ) -> None:
        with self._lock:
            self._metrics.external_cost_minor += external
            self._metrics.compute_cost_minor += compute
            self._metrics.storage_cost_minor += storage
            self._metrics.payment_fee_minor += payment_fee
            self._metrics.refund_loss_minor += refund_loss

    def snapshot(self) -> CommerceMetrics:
        with self._lock:
            # Return a copy to prevent external mutation
            return CommerceMetrics(**self._metrics.__dict__)

    def reset(self) -> None:
        with self._lock:
            self._metrics = CommerceMetrics()


# Global singleton
_global_metrics: Optional[MetricsCollector] = None


def get_metrics() -> MetricsCollector:
    global _global_metrics
    if _global_metrics is None:
        _global_metrics = MetricsCollector()
    return _global_metrics
