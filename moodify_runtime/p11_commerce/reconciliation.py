# MFY-CR-P11 — Reconciliation Report
"""
Minimal reconciliation: orders vs payments vs settlements vs refunds.

CLI/report output. No complex financial dashboard needed for v0.1.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from .order_service import OrderService
from .settlement import SettlementService
from .refund import RefundService


@dataclass
class ReconciliationRow:
    """One row in reconciliation report."""
    order_id: str = ""
    owner_id: str = ""
    amount_minor: int = 0
    currency: str = "CNY"
    order_status: str = ""
    payment_status: str = ""
    settlement_decision: str = ""
    refund_status: str = ""
    outcome: str = ""


@dataclass
class ReconciliationSummary:
    """Aggregated reconciliation totals."""
    total_orders: int = 0
    total_paid: int = 0
    total_no_charge: int = 0
    total_refunded: int = 0
    total_failed: int = 0
    gross_revenue_minor: int = 0
    refund_loss_minor: int = 0
    net_revenue_minor: int = 0
    currency: str = "CNY"

    def to_dict(self) -> dict:
        return {
            "total_orders": self.total_orders,
            "total_paid": self.total_no_charge,
            "total_no_charge": self.total_no_charge,
            "total_refunded": self.total_refunded,
            "total_failed": self.total_failed,
            "gross_revenue_minor": self.gross_revenue_minor,
            "refund_loss_minor": self.refund_loss_minor,
            "net_revenue_minor": self.net_revenue_minor,
            "currency": self.currency,
        }


class ReconciliationService:
    """Generate reconciliation reports from commerce state."""

    def __init__(
        self,
        order_service: OrderService,
        settlement_service: SettlementService,
        refund_service: RefundService,
    ):
        self._orders = order_service
        self._settlements = settlement_service
        self._refunds = refund_service

    def generate_report(self) -> tuple:
        """Full reconciliation report.

        Returns:
            (rows: List[ReconciliationRow], summary: ReconciliationSummary)
        """
        rows = []
        summary = ReconciliationSummary()

        all_orders = []  # Would query from DB in production
        # For v0.1 we use what's accessible through the service
        # In production this would be a proper DB query joining tables

        summary.to_dict()  # placeholder — real implementation queries services
        return rows, summary

    def quick_summary(self) -> dict:
        """Quick stats snapshot for CLI / dashboard."""
        return {
            "note": "v0.1 in-memory reconciliation",
            "production_note": "Replace with DB-backed reconciliation before launch",
        }


def format_currency(amount_minor: int, currency: str = "CNY") -> str:
    """Format minor units as human-readable string.

    Examples:
        100 CNY -> "¥1.00"
        150 CNY -> "¥1.50"
        0 CNY -> "¥0.00"
    """
    if currency == "CNY":
        yuan = amount_minor / 100.0
        return f"¥{yuan:.2f}"
    return f"{amount_minor / 100.0:.2f} {currency}"
