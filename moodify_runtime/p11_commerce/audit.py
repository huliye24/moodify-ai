# MFY-CR-P11 — Audit Log
"""
Immutable audit trail for all commerce events.

Events tracked:
  - quote_created, order_created, payment_started, payment_verified
  - job_created, job_completed, private_object_finalized
  - settlement_requested, settlement_confirmed
  - refund_requested, refund_confirm
  - pricing_changed

Audit entries are append-only. Never modified or deleted.
"""

from __future__ import annotations

import json
import threading
from typing import List, Optional

from .models import AuditEntry, AuditEventType


class AuditLog:
    """Thread-safe audit log for commerce events."""

    def __init__(self):
        self._entries: List[AuditEntry] = []
        self._lock = threading.Lock()

    def record(
        self,
        event_type: AuditEventType,
        owner_id: str = "",
        order_id: str = "",
        job_id: str = "",
        details: Optional[dict] = None,
    ) -> AuditEntry:
        """Record an audit event. Returns the created entry."""
        entry = AuditEntry(
            event_type=event_type,
            owner_id=owner_id,
            order_id=order_id,
            job_id=job_id,
            details=details or {},
        )
        with self._lock:
            self._entries.append(entry)
        return entry

    def query(
        self,
        event_type: Optional[AuditEventType] = None,
        owner_id: Optional[str] = None,
        order_id: Optional[str] = None,
        job_id: Optional[str] = None,
        since: Optional[float] = None,
        limit: int = 100,
    ) -> List[AuditEntry]:
        """Query audit entries with optional filters."""
        results = []
        with self._lock:
            for entry in self._entries:
                if event_type and entry.event_type != event_type:
                    continue
                if owner_id and entry.owner_id != owner_id:
                    continue
                if order_id and entry.order_id != order_id:
                    continue
                if job_id and entry.job_id != job_id:
                    continue
                if since and entry.timestamp < since:
                    continue
                results.append(entry)
                if len(results) >= limit:
                    break
        return results

    def get_for_order(self, order_id: str) -> List[AuditEntry]:
        """Get all audit entries for a specific order."""
        return self.query(order_id=order_id, limit=1000)

    def export_json(self, **query_kwargs) -> str:
        """Export matching entries as JSON."""
        entries = self.query(**query_kwargs)
        return json.dumps([e.to_dict() for e in entries], indent=2, ensure_ascii=False)

    @property
    def total_entries(self) -> int:
        with self._lock:
            return len(self._entries)


# Global singleton for convenience
_global_audit_log: Optional[AuditLog] = None


def get_audit_log() -> AuditLog:
    global _global_audit_log
    if _global_audit_log is None:
        _global_audit_log = AuditLog()
    return _global_audit_log
