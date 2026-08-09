"""Compute admission control (DSK-MFY-ACCESS-CWC-PATCH-001).

Entry to the product is open; entry to expensive compute is controlled.
estimate -> balance check -> optional reservation -> queue -> concurrency
cap -> settle/refund. Queueing and backpressure replace uncontrolled
parallel execution; insufficient balance is a controlled state, never a
crash.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from moodify.access.ledger import AccessLedger, InsufficientCWCError
from moodify.access.models import ComputeJobAdmission, QuotaState
from moodify.access.policy import AccessPolicy

QUEUE_QUEUED = "QUEUED"
QUEUE_ADMITTED = "ADMITTED"
QUEUE_COMPLETED = "COMPLETED"
QUEUE_FAILED = "FAILED"
QUEUE_REJECTED_INSUFFICIENT = "REJECTED_INSUFFICIENT"


def _atomic_write(path: Path, payload: Any) -> None:
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(tmp, path)


class AdmissionController:
    """Reservation-based admission: estimate, reserve, queue, settle."""

    def __init__(self, root: Path, policy: AccessPolicy | None = None) -> None:
        self.ledger = AccessLedger(root)
        self.policy = policy or AccessPolicy()
        self._admissions_path = root / "admissions.json"
        self._quotas_path = root / "quotas.json"

    # -- persistence ---------------------------------------------------------

    def _load_admissions(self) -> list[ComputeJobAdmission]:
        if not self._admissions_path.is_file():
            return []
        return [ComputeJobAdmission.from_dict(a)
                for a in json.loads(self._admissions_path.read_text(encoding="utf-8"))]

    def _save_admissions(self, admissions: list[ComputeJobAdmission]) -> None:
        _atomic_write(self._admissions_path, [a.to_dict() for a in admissions])

    def _load_quotas(self) -> dict[str, QuotaState]:
        if not self._quotas_path.is_file():
            return {}
        return {uid: QuotaState.from_dict(q)
                for uid, q in json.loads(self._quotas_path.read_text(encoding="utf-8")).items()}

    def _save_quotas(self, quotas: dict[str, QuotaState]) -> None:
        _atomic_write(self._quotas_path, {uid: q.to_dict() for uid, q in quotas.items()})

    # -- queries -------------------------------------------------------------

    def estimate(self, operation_type: str) -> dict[str, Any]:
        if not self.policy.has_operation(operation_type):
            raise ValueError(f"unknown operation: {operation_type}")
        return {
            "operation_type": operation_type,
            "estimated_cwc": self.policy.cost_for(operation_type),
            "policy_version": self.policy.version,
        }

    def quota(self, owner_id: str) -> dict[str, Any]:
        state = self._load_quotas().get(owner_id, QuotaState(owner_id=owner_id, tier="free"))
        balance = self.ledger.balance(owner_id)
        tier = state.tier
        return {
            "owner_id": owner_id,
            "tier": tier,
            "available_cwc": balance.available_cwc,
            "reserved_cwc": balance.reserved_cwc,
            "concurrency_active": state.concurrency_active,
            "concurrency_limit": self.policy.tier_concurrency.get(tier, 1),
            "daily_usage": {k: v for k, v in state.daily_usage.items() if k != "_date"},
            "daily_limits": self.policy.tier_daily_limits.get(tier, {}),
        }

    def admission(self, admission_id: str) -> ComputeJobAdmission | None:
        for admission in self._load_admissions():
            if admission.admission_id == admission_id:
                return admission
        return None

    # -- admission flow ------------------------------------------------------

    def admit(self, owner_id: str, operation_type: str,
              priority_tier: str = "free") -> dict[str, Any]:
        """Estimate, check balance, respect concurrency/rate/daily limits,
        and either admit (with reservation) or queue the job."""
        if not self.policy.has_operation(operation_type):
            raise ValueError(f"unknown operation: {operation_type}")
        cost = self.policy.cost_for(operation_type)
        balance = self.ledger.balance(owner_id)
        if balance.available_cwc < cost:
            return self._reject(owner_id, operation_type, cost,
                                reason="INSUFFICIENT_CWC",
                                state=QUEUE_REJECTED_INSUFFICIENT)

        quotas = self._load_quotas()
        state = quotas.get(owner_id, QuotaState(owner_id=owner_id, tier=priority_tier))
        refreshed = self._refresh_windows(state)

        tier = priority_tier if priority_tier in self.policy.tier_concurrency else refreshed.tier

        # rate limit: submissions per rolling minute
        if refreshed.submissions_last_minute >= self.policy.tier_rate_limits.get(tier, 3):
            return self._reject(owner_id, operation_type, cost, reason="RATE_LIMITED",
                                state=QUEUE_QUEUED)

        # daily quota per operation
        daily_limit = self.policy.tier_daily_limits.get(tier, {}).get(operation_type)
        if daily_limit is not None and refreshed.daily_usage.get(operation_type, 0) >= daily_limit:
            return self._reject(owner_id, operation_type, cost,
                                reason="DAILY_QUOTA_EXCEEDED", state=QUEUE_QUEUED)

        admissions = self._load_admissions()
        active = [a for a in admissions
                  if a.owner_id == owner_id and a.queue_state in (QUEUE_ADMITTED, QUEUE_QUEUED)]

        submissions = refreshed.submissions_last_minute + 1
        last_submission = datetime.now(timezone.utc).isoformat(timespec="seconds")

        if len(active) >= self.policy.tier_concurrency.get(tier, 1):
            queue_size = len([a for a in admissions if a.queue_state == QUEUE_QUEUED])
            if queue_size >= self.policy.max_queue_depth:
                return self._reject(owner_id, operation_type, cost,
                                    reason="QUEUE_FULL", state=QUEUE_QUEUED)
            admission = self._create(owner_id, operation_type, cost, tier, QUEUE_QUEUED)
            concurrency_active = refreshed.concurrency_active
        else:
            try:
                self.ledger.reserve(owner_id, cost, job_id="", operation=operation_type)
            except InsufficientCWCError:
                return self._reject(owner_id, operation_type, cost,
                                    reason="INSUFFICIENT_CWC",
                                    state=QUEUE_REJECTED_INSUFFICIENT)
            admission = self._create(owner_id, operation_type, cost, tier, QUEUE_ADMITTED)
            concurrency_active = refreshed.concurrency_active + 1

        state = QuotaState(
            owner_id=owner_id,
            tier=tier,
            concurrency_active=concurrency_active,
            daily_usage=dict(refreshed.daily_usage, **{operation_type: refreshed.daily_usage.get(operation_type, 0) + 1}),
            last_submission_at=last_submission,
            submissions_last_minute=submissions,
        )

        admissions.append(admission)
        self._save_admissions(admissions)
        quotas[owner_id] = state
        self._save_quotas(quotas)
        return self._admission_response(admission, cost, tier)

    def settle(self, admission_id: str, actual_cwc: float) -> dict[str, Any]:
        """Consume the actual cost and release/refund the difference."""
        admissions = self._load_admissions()
        for idx, admission in enumerate(admissions):
            if admission.admission_id != admission_id:
                continue
            if admission.queue_state not in (QUEUE_ADMITTED,):
                raise ValueError(f"cannot settle admission in state {admission.queue_state}")
            estimated = admission.estimated_cwc
            self.ledger.consume(admission.owner_id, actual_cwc, admission_id,
                                admission.operation_type)
            difference = estimated - actual_cwc
            if difference > 0:
                self.ledger.release(admission.owner_id, difference, admission_id)
            elif difference < 0:
                self.ledger.consume(admission.owner_id, abs(difference), admission_id,
                                    admission.operation_type)
            completed = ComputeJobAdmission(
                admission_id=admission.admission_id,
                owner_id=admission.owner_id,
                operation_type=admission.operation_type,
                estimated_cwc=admission.estimated_cwc,
                actual_cwc=round(actual_cwc, 6),
                queue_state=QUEUE_COMPLETED,
                priority_tier=admission.priority_tier,
                completed_at=datetime.now(timezone.utc).isoformat(timespec="seconds"),
            )
            admissions[idx] = completed
            self._save_admissions(admissions)
            self._decrement_concurrency(admission.owner_id)
            return self._admission_response(completed, actual_cwc, admission.priority_tier)
        raise ValueError(f"unknown admission: {admission_id}")

    def fail(self, admission_id: str, failure_reason: str = "") -> dict[str, Any]:
        """Release the reservation when a job fails."""
        admissions = self._load_admissions()
        for idx, admission in enumerate(admissions):
            if admission.admission_id != admission_id:
                continue
            if admission.queue_state not in (QUEUE_ADMITTED, QUEUE_QUEUED):
                raise ValueError(f"cannot fail admission in state {admission.queue_state}")
            if admission.queue_state == QUEUE_ADMITTED:
                self.ledger.release(admission.owner_id, admission.estimated_cwc, admission_id)
            failed = ComputeJobAdmission(
                admission_id=admission.admission_id,
                owner_id=admission.owner_id,
                operation_type=admission.operation_type,
                estimated_cwc=admission.estimated_cwc,
                queue_state=QUEUE_FAILED,
                priority_tier=admission.priority_tier,
                failure_reason=failure_reason or "unknown failure",
            )
            admissions[idx] = failed
            self._save_admissions(admissions)
            if admission.queue_state == QUEUE_ADMITTED:
                self._decrement_concurrency(admission.owner_id)
            return self._admission_response(failed, admission.estimated_cwc,
                                            admission.priority_tier)
        raise ValueError(f"unknown admission: {admission_id}")

    # -- internals -----------------------------------------------------------

    def _refresh_windows(self, state: QuotaState) -> QuotaState:
        now = datetime.now(timezone.utc)
        today = now.date().isoformat()
        daily = dict(state.daily_usage)
        if daily.get("_date", "") != today:
            daily = {"_date": today}
        submissions = state.submissions_last_minute
        if state.last_submission_at:
            try:
                last = datetime.fromisoformat(state.last_submission_at)
                if (now - last).total_seconds() > 60:
                    submissions = 0
            except ValueError:
                pass
        return QuotaState(
            owner_id=state.owner_id,
            tier=state.tier,
            concurrency_active=state.concurrency_active,
            daily_usage=daily,
            last_submission_at=state.last_submission_at,
            submissions_last_minute=submissions,
        )

    def _reject(self, owner_id: str, operation: str, cost: float,
                reason: str, state: str) -> dict[str, Any]:
        admission = ComputeJobAdmission(
            admission_id=f"adm-{uuid4().hex[:12]}",
            owner_id=owner_id,
            operation_type=operation,
            estimated_cwc=cost,
            queue_state=state,
            priority_tier="free",
            failure_reason=reason,
        )
        return self._admission_response(admission, cost, "free")

    def _create(self, owner_id: str, operation: str, cost: float,
                tier: str, state: str) -> ComputeJobAdmission:
        return ComputeJobAdmission(
            admission_id=f"adm-{uuid4().hex[:12]}",
            owner_id=owner_id,
            operation_type=operation,
            estimated_cwc=cost,
            queue_state=state,
            priority_tier=tier,
        )

    def _admission_response(self, admission: ComputeJobAdmission,
                            cost: float, tier: str) -> dict[str, Any]:
        response = {
            "admission_id": admission.admission_id,
            "operation_type": admission.operation_type,
            "estimated_cwc": admission.estimated_cwc,
            "queue_state": admission.queue_state,
            "priority_tier": admission.priority_tier,
            "failure_reason": admission.failure_reason,
        }
        if admission.queue_state == QUEUE_QUEUED:
            response["message"] = self.policy.backpressure_message
        return response

    def _decrement_concurrency(self, owner_id: str) -> None:
        quotas = self._load_quotas()
        state = quotas.get(owner_id)
        if state is None:
            return
        state = QuotaState(
            owner_id=state.owner_id,
            tier=state.tier,
            concurrency_active=max(0, state.concurrency_active - 1),
            daily_usage=state.daily_usage,
            last_submission_at=state.last_submission_at,
            submissions_last_minute=state.submissions_last_minute,
        )
        quotas[owner_id] = state
        self._save_quotas(quotas)
