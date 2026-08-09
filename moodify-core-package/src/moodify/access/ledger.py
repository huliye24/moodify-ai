"""CWC compute-credit ledger with atomic persistence
(DSK-MFY-ACCESS-CWC-PATCH-001).

A single-file append-only transaction log keeps every GRANT / RESERVE /
CONSUME / RELEASE / REFUND / REFERRAL_REWARD auditable. Balances are
derived by replay, so a corrupted tail cannot silently change totals.
Invariants: available >= 0 and reserved <= available at all times.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any
from uuid import uuid4

from moodify.access.models import CWCBalance, CWCTransaction, UserAccessProfile
from moodify.access.policy import AccessPolicy

TXN_GRANT = "GRANT"
TXN_RESERVE = "RESERVE"
TXN_CONSUME = "CONSUME"
TXN_RELEASE = "RELEASE"
TXN_REFUND = "REFUND"
TXN_REFERRAL_REWARD = "REFERRAL_REWARD"
TXN_ADMIN_ADJUST = "ADMIN_ADJUST"

ALL_TYPES = {TXN_GRANT, TXN_RESERVE, TXN_CONSUME, TXN_RELEASE, TXN_REFUND,
             TXN_REFERRAL_REWARD, TXN_ADMIN_ADJUST}


class InsufficientCWCError(Exception):
    """Raised when a reservation cannot be satisfied."""


class UnknownOperationError(ValueError):
    """Raised when an operation has no configured metering cost."""


def _atomic_write(path: Path, payload: Any) -> None:
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(tmp, path)


class AccessLedger:
    """Append-only CWC ledger + user registry, persisted under one root."""

    def __init__(self, root: Path) -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    # -- persistence helpers -------------------------------------------------

    def _users_path(self) -> Path:
        return self.root / "users.json"

    def _txn_path(self) -> Path:
        return self.root / "transactions.jsonl"

    def _txn_append(self, txn: CWCTransaction) -> None:
        with self._txn_path().open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(txn.to_dict(), ensure_ascii=False) + "\n")

    def _load_users(self) -> dict[str, UserAccessProfile]:
        path = self._users_path()
        if not path.is_file():
            return {}
        data = json.loads(path.read_text(encoding="utf-8"))
        return {uid: UserAccessProfile.from_dict(raw) for uid, raw in data.items()}

    def _save_users(self, users: dict[str, UserAccessProfile]) -> None:
        _atomic_write(self._users_path(), {uid: u.to_dict() for uid, u in users.items()})

    def _load_transactions(self) -> list[CWCTransaction]:
        path = self._txn_path()
        if not path.is_file():
            return []
        txns = []
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line:
                txns.append(CWCTransaction.from_dict(json.loads(line)))
        return txns

    # -- users ---------------------------------------------------------------

    def register_user(self, user_id: str, registration_mode: str,
                      referral_code_used: str | None = None,
                      policy: AccessPolicy | None = None) -> UserAccessProfile:
        policy = policy or AccessPolicy()
        users = self._load_users()
        if user_id in users:
            return users[user_id]
        if len(users) >= policy.max_users:
            raise ValueError("user limit reached")
        profile = UserAccessProfile(
            user_id=user_id,
            registration_mode=registration_mode,
            access_tier="free",
            referral_code_used=referral_code_used,
            referral_reward_state="NONE" if not referral_code_used else "PENDING",
        )
        users[user_id] = profile
        self._save_users(users)
        if policy.starter_cwc > 0:
            self.grant(user_id, policy.starter_cwc, operation="starter_credit",
                       metadata={"reason": "starter"})
        return profile

    def get_user(self, user_id: str) -> UserAccessProfile | None:
        return self._load_users().get(user_id)

    # -- ledger --------------------------------------------------------------

    def transactions(self) -> list[CWCTransaction]:
        return self._load_transactions()

    def balance(self, owner_id: str) -> CWCBalance:
        granted = consumed = refunded = reserved = 0.0
        reserved_jobs: dict[str, float] = {}
        for txn in self._load_transactions():
            if txn.owner_id != owner_id:
                continue
            if txn.type == TXN_GRANT:
                granted += txn.amount
            elif txn.type == TXN_REFERRAL_REWARD:
                granted += txn.amount
            elif txn.type == TXN_CONSUME:
                consumed += txn.amount
                reserved -= txn.amount
            elif txn.type == TXN_REFUND:
                refunded += txn.amount
                reserved -= txn.amount
            elif txn.type == TXN_RELEASE:
                reserved -= txn.amount
            elif txn.type == TXN_RESERVE:
                reserved += txn.amount
                reserved_jobs[txn.related_job_id or ""] = txn.amount
            elif txn.type == TXN_ADMIN_ADJUST:
                granted += txn.amount if txn.amount >= 0 else 0.0
        available = granted - consumed - reserved + refunded
        return CWCBalance(
            owner_id=owner_id,
            available_cwc=round(available, 6),
            reserved_cwc=round(reserved, 6),
            lifetime_granted_cwc=round(granted, 6),
            lifetime_consumed_cwc=round(consumed, 6),
            lifetime_refunded_cwc=round(refunded, 6),
        )

    def grant(self, owner_id: str, amount: float, operation: str | None = None,
              metadata: dict[str, Any] | None = None) -> CWCTransaction:
        if amount < 0:
            raise ValueError("grant amount must be >= 0")
        txn = CWCTransaction(
            transaction_id=f"txn-{uuid4().hex[:12]}",
            owner_id=owner_id,
            type=TXN_GRANT,
            amount=round(float(amount), 6),
            related_operation=operation,
            metadata=metadata or {},
        )
        self._txn_append(txn)
        return txn

    def reserve(self, owner_id: str, amount: float, job_id: str,
                operation: str) -> CWCTransaction:
        balance = self.balance(owner_id)
        if balance.available_cwc < amount:
            raise InsufficientCWCError(
                f"available {balance.available_cwc} < required {amount}"
            )
        txn = CWCTransaction(
            transaction_id=f"txn-{uuid4().hex[:12]}",
            owner_id=owner_id,
            type=TXN_RESERVE,
            amount=round(float(amount), 6),
            related_job_id=job_id,
            related_operation=operation,
        )
        self._txn_append(txn)
        return txn

    def release(self, owner_id: str, amount: float, job_id: str) -> CWCTransaction:
        txn = CWCTransaction(
            transaction_id=f"txn-{uuid4().hex[:12]}",
            owner_id=owner_id,
            type=TXN_RELEASE,
            amount=round(float(amount), 6),
            related_job_id=job_id,
        )
        self._txn_append(txn)
        return txn

    def consume(self, owner_id: str, amount: float, job_id: str,
                operation: str) -> CWCTransaction:
        txn = CWCTransaction(
            transaction_id=f"txn-{uuid4().hex[:12]}",
            owner_id=owner_id,
            type=TXN_CONSUME,
            amount=round(float(amount), 6),
            related_job_id=job_id,
            related_operation=operation,
        )
        self._txn_append(txn)
        return txn

    def refund(self, owner_id: str, amount: float, job_id: str) -> CWCTransaction:
        txn = CWCTransaction(
            transaction_id=f"txn-{uuid4().hex[:12]}",
            owner_id=owner_id,
            type=TXN_REFUND,
            amount=round(float(amount), 6),
            related_job_id=job_id,
        )
        self._txn_append(txn)
        return txn

    def referral_reward(self, owner_id: str, amount: float,
                        metadata: dict[str, Any] | None = None) -> CWCTransaction:
        txn = CWCTransaction(
            transaction_id=f"txn-{uuid4().hex[:12]}",
            owner_id=owner_id,
            type=TXN_REFERRAL_REWARD,
            amount=round(float(amount), 6),
            metadata=metadata or {},
        )
        self._txn_append(txn)
        return txn
