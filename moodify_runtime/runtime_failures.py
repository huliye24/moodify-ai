"""MHP-111: Failure Classifier and Retry Policy — production failure handling.

Integrates with supervisor.py for crash classification and retry decisions.
Extends failure.py with structured severity levels and retry policies.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

from .utils import utc_now_iso


class Severity(Enum):
    CRITICAL = "critical"   # Blocks production — supervisor intervention needed
    HIGH = "high"           # Degrades quality — task should be retried or marked failed
    MEDIUM = "medium"       # Operational friction — log and continue
    LOW = "low"             # Edge case — document and defer


@dataclass
class FailureRecord:
    failure_id: str
    task_id: str = ""
    sample_id: str = ""
    preset: str = ""
    exit_code: int = -1
    error_message: str = ""
    severity: Severity = Severity.MEDIUM
    retryable: bool = True
    attempt: int = 0
    max_retries: int = 2
    classified_at: str = field(default_factory=utc_now_iso)
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "failure_id": self.failure_id,
            "task_id": self.task_id,
            "sample_id": self.sample_id,
            "preset": self.preset,
            "exit_code": self.exit_code,
            "error_message": self.error_message[:500],
            "severity": self.severity.value,
            "retryable": self.retryable,
            "attempt": self.attempt,
            "max_retries": self.max_retries,
            "classified_at": self.classified_at,
            "notes": self.notes,
        }


def classify_failure(exit_code: int, error: str, attempt: int = 0) -> FailureRecord:
    """Classify a subprocess failure and determine retry policy.

    Returns a FailureRecord with severity and retryable flag.
    """
    msg = (error or "").lower()
    record = FailureRecord(
        failure_id="",
        exit_code=exit_code,
        error_message=error,
        attempt=attempt,
    )

    # ── CRITICAL: cannot recover, must alert ──
    if "disk full" in msg or "no space" in msg:
        record.severity = Severity.CRITICAL
        record.retryable = False
        record.notes = "disk_exhausted"
    elif "memory" in msg or "killed" in msg or "oom" in msg:
        record.severity = Severity.CRITICAL
        record.retryable = False
        record.notes = "resource_exhausted"

    # ── MEDIUM: operational issues (check BEFORE generic exit_code) ──
    elif "not found" in msg or "no such file" in msg:
        record.severity = Severity.MEDIUM
        record.retryable = False
        record.notes = "file_not_found"
    elif "argument" in msg or "usage:" in msg:
        record.severity = Severity.MEDIUM
        record.retryable = False
        record.notes = "cli_argument_error"

    # ── HIGH: can retry, but indicates a real problem ──
    elif "timeout" in msg or "timed out" in msg:
        record.severity = Severity.HIGH
        record.retryable = True
        record.notes = "task_timeout"
    elif exit_code != 0 and exit_code != -1:
        record.severity = Severity.HIGH
        record.retryable = True
        record.notes = f"non_zero_exit_{exit_code}"

    # ── LOW: transient or unknown ──
    elif "connection" in msg or "network" in msg:
        record.severity = Severity.LOW
        record.retryable = True
        record.notes = "transient_network"

    else:
        record.severity = Severity.MEDIUM
        record.retryable = attempt < 2  # default: retry up to 2 times
        record.notes = "unclassified"

    return record


def should_retry(record: FailureRecord) -> bool:
    """Determine if a failure should be retried."""
    return record.retryable and record.attempt < record.max_retries


def backoff_delay(attempt: int, base: float = 1.0, max_delay: float = 60.0) -> float:
    """Exponential backoff: base * 2^attempt, capped at max_delay."""
    return min(base * (2 ** attempt), max_delay)
