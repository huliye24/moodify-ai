"""Open registration + referral rewards orchestration
(DSK-MFY-ACCESS-CWC-PATCH-001).

Registration never requires an invite code. A referral code is an
optional reward trigger: both inviter and invitee receive bonus CWC
under the configured policy, with one-time and per-inviter caps.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any
from uuid import uuid4

from moodify.access.admission import AdmissionController
from moodify.access.ledger import AccessLedger
from moodify.access.models import ReferralRewardRecord
from moodify.access.policy import AccessPolicy

DEFAULT_ACCESS_ROOT = Path(os.environ.get("MOODIFY_ACCESS_ROOT", "outputs/access"))


def _atomic_write(path: Path, payload: Any) -> None:
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(tmp, path)


class AccessService:
    """Open signup, referral rewards, and compute admission facade."""

    def __init__(self, root: Path = DEFAULT_ACCESS_ROOT, policy: AccessPolicy | None = None) -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self.policy = policy or AccessPolicy.from_yaml()
        self.ledger = AccessLedger(self.root)
        self.admission = AdmissionController(self.root, policy=self.policy)
        self._referrals_path = self.root / "referrals.jsonl"

    # -- registration --------------------------------------------------------

    def register(self, user_id: str, referral_code: str | None = None) -> dict[str, Any]:
        """Open registration. Referral code is optional and never required."""
        if not self.policy.open_registration:
            raise ValueError("registration is closed by policy")
        if self.policy.invite_required and not referral_code:
            raise ValueError("invite code required by policy")

        profile = self.ledger.register_user(
            user_id,
            registration_mode="REFERRAL" if referral_code else "OPEN",
            referral_code_used=referral_code,
            policy=self.policy,
        )
        result: dict[str, Any] = {
            "user_id": user_id,
            "registration_mode": profile.registration_mode,
            "access_tier": profile.access_tier,
            "balance": self.ledger.balance(user_id).to_dict(),
            "referral_code_used": profile.referral_code_used,
        }
        if referral_code:
            result["referral"] = self.grant_referral_reward(inviter_id=referral_code,
                                                            invitee_id=user_id)
        return result

    def grant_referral_reward(self, inviter_id: str, invitee_id: str) -> dict[str, Any]:
        """Grant both parties their referral bonus under policy caps."""
        if not self.policy.referral_enabled:
            return {"state": "DISABLED", "reward_amount": 0.0}
        inviter = self.ledger.get_user(inviter_id)
        if inviter is None:
            return {"state": "INVALID_INVITER", "reward_amount": 0.0}
        if inviter_id == invitee_id:
            return {"state": "SELF_REFERRAL_REJECTED", "reward_amount": 0.0}

        existing = self._load_referrals()
        if any(r.invitee_id == invitee_id for r in existing):
            return {"state": "INVITEE_ALREADY_REWARDED", "reward_amount": 0.0}
        if self.policy.one_time_per_inviter and any(
            r.inviter_id == inviter_id and r.state == "GRANTED" for r in existing
        ):
            return {"state": "INVITER_ALREADY_REWARDED", "reward_amount": 0.0}
        inviter_count = len([r for r in existing if r.inviter_id == inviter_id])
        if inviter_count >= self.policy.max_referrals_per_inviter:
            return {"state": "INVITER_CAP_REACHED", "reward_amount": 0.0}

        self.ledger.referral_reward(inviter_id, self.policy.inviter_reward_cwc,
                                    metadata={"kind": "referral_inviter", "invitee": invitee_id})
        self.ledger.referral_reward(invitee_id, self.policy.invitee_reward_cwc,
                                    metadata={"kind": "referral_invitee", "inviter": inviter_id})
        record = ReferralRewardRecord(
            record_id=f"rr-{uuid4().hex[:12]}",
            inviter_id=inviter_id,
            invitee_id=invitee_id,
            reward_amount=self.policy.inviter_reward_cwc + self.policy.invitee_reward_cwc,
            state="GRANTED",
            metadata={"inviter_reward": self.policy.inviter_reward_cwc,
                      "invitee_reward": self.policy.invitee_reward_cwc},
        )
        self._append_referral(record)
        return {
            "state": "GRANTED",
            "inviter_reward": self.policy.inviter_reward_cwc,
            "invitee_reward": self.policy.invitee_reward_cwc,
            "record_id": record.record_id,
        }

    def referral_status(self, user_id: str) -> dict[str, Any]:
        records = [r for r in self._load_referrals()
                   if r.inviter_id == user_id or r.invitee_id == user_id]
        total = 0.0
        for record in records:
            if record.state != "GRANTED":
                continue
            metadata = record.metadata if hasattr(record, "metadata") else {}
            if record.inviter_id == user_id:
                total += float(metadata.get("inviter_reward", self.policy.inviter_reward_cwc))
            if record.invitee_id == user_id:
                total += float(metadata.get("invitee_reward", self.policy.invitee_reward_cwc))
        return {
            "user_id": user_id,
            "referral_records": [r.to_dict() for r in records],
            "total_rewarded_cwc": round(total, 6),
        }

    # -- pass-through admission ----------------------------------------------

    def estimate(self, operation_type: str) -> dict[str, Any]:
        return self.admission.estimate(operation_type)

    def admit(self, owner_id: str, operation_type: str, priority_tier: str = "free") -> dict[str, Any]:
        return self.admission.admit(owner_id, operation_type, priority_tier)

    def settle(self, admission_id: str, actual_cwc: float) -> dict[str, Any]:
        return self.admission.settle(admission_id, actual_cwc)

    def fail(self, admission_id: str, failure_reason: str = "") -> dict[str, Any]:
        return self.admission.fail(admission_id, failure_reason)

    def quota(self, owner_id: str) -> dict[str, Any]:
        return self.admission.quota(owner_id)

    def balance(self, owner_id: str) -> dict[str, Any]:
        return self.ledger.balance(owner_id).to_dict()

    def history(self, owner_id: str) -> list[dict[str, Any]]:
        return [t.to_dict() for t in self.ledger.transactions() if t.owner_id == owner_id]

    # -- persistence ---------------------------------------------------------

    def _load_referrals(self) -> list[ReferralRewardRecord]:
        if not self._referrals_path.is_file():
            return []
        return [ReferralRewardRecord.from_dict(json.loads(line))
                for line in self._referrals_path.read_text(encoding="utf-8").splitlines()
                if line.strip()]

    def _append_referral(self, record: ReferralRewardRecord) -> None:
        with self._referrals_path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record.to_dict(), ensure_ascii=False) + "\n")
