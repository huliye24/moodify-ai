"""Open access policy: metering costs, tiers, quotas, referral rewards
(DSK-MFY-ACCESS-CWC-PATCH-001).

All numeric policy (operation costs, starter balance, tier limits,
referral rewards, queue depth) lives in one versioned YAML.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

DEFAULT_POLICY_PATH = Path(__file__).resolve().parents[3] / "configs" / "access_policy_v1.yaml"


@dataclass(frozen=True)
class AccessPolicy:
    version: str = "access_policy_v1"
    open_registration: bool = True
    invite_required: bool = False
    starter_cwc: float = 100.0
    max_users: int = 10000
    operation_costs: dict[str, float] = field(default_factory=dict)
    tier_concurrency: dict[str, int] = field(default_factory=lambda: {"free": 1, "creator": 3, "enterprise": 10})
    tier_daily_limits: dict[str, dict[str, int]] = field(default_factory=dict)
    tier_rate_limits: dict[str, int] = field(default_factory=lambda: {"free": 3, "creator": 10, "enterprise": 60})
    referral_enabled: bool = True
    inviter_reward_cwc: float = 10.0
    invitee_reward_cwc: float = 5.0
    reward_after_compute_task: bool = False
    one_time_per_inviter: bool = True
    max_referrals_per_inviter: int = 20
    max_queue_depth: int = 100
    backpressure_message: str = "当前任务较多，你的任务已加入队列。"

    @classmethod
    def from_yaml(cls, path: str | Path = DEFAULT_POLICY_PATH) -> "AccessPolicy":
        data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
        registration = data.get("registration", {})
        tiers = data.get("tiers", {})
        referral = data.get("referral", {})
        queue = data.get("queue", {})
        return cls(
            version=data.get("policy_version", "access_policy_v1"),
            open_registration=bool(registration.get("open_registration", True)),
            invite_required=bool(registration.get("invite_required", False)),
            starter_cwc=float(registration.get("starter_cwc", 100.0)),
            max_users=int(registration.get("max_users", 10000)),
            operation_costs={k: float(v["base_cwc"]) for k, v in data.get("operations", {}).items()},
            tier_concurrency={k: int(v.get("concurrency_limit", 1)) for k, v in tiers.items()},
            tier_daily_limits={k: dict(v.get("daily_limits", {})) for k, v in tiers.items()},
            tier_rate_limits={k: int(v.get("rate_limit_submissions_per_minute", 3)) for k, v in tiers.items()},
            referral_enabled=bool(referral.get("enabled", True)),
            inviter_reward_cwc=float(referral.get("inviter_reward_cwc", 10.0)),
            invitee_reward_cwc=float(referral.get("invitee_reward_cwc", 5.0)),
            reward_after_compute_task=bool(referral.get("reward_after_compute_task", False)),
            one_time_per_inviter=bool(referral.get("one_time_per_inviter", True)),
            max_referrals_per_inviter=int(referral.get("max_referrals_per_inviter", 20)),
            max_queue_depth=int(queue.get("max_queue_depth", 100)),
            backpressure_message=str(queue.get("backpressure_message", "当前任务较多，你的任务已加入队列。")),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "policy_version": self.version,
            "registration": {
                "open_registration": self.open_registration,
                "invite_required": self.invite_required,
                "starter_cwc": self.starter_cwc,
                "max_users": self.max_users,
            },
            "operations": {k: {"base_cwc": v} for k, v in self.operation_costs.items()},
            "tiers": {
                tier: {
                    "concurrency_limit": self.tier_concurrency.get(tier, 1),
                    "daily_limits": self.tier_daily_limits.get(tier, {}),
                    "rate_limit_submissions_per_minute": self.tier_rate_limits.get(tier, 3),
                }
                for tier in self.tier_concurrency
            },
            "referral": {
                "enabled": self.referral_enabled,
                "inviter_reward_cwc": self.inviter_reward_cwc,
                "invitee_reward_cwc": self.invitee_reward_cwc,
                "reward_after_compute_task": self.reward_after_compute_task,
                "one_time_per_inviter": self.one_time_per_inviter,
                "max_referrals_per_inviter": self.max_referrals_per_inviter,
            },
            "queue": {
                "max_queue_depth": self.max_queue_depth,
                "backpressure_message": self.backpressure_message,
            },
        }

    def cost_for(self, operation_type: str) -> float:
        return self.operation_costs.get(operation_type, 0.0)

    def has_operation(self, operation_type: str) -> bool:
        return operation_type in self.operation_costs
