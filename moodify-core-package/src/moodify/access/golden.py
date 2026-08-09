"""Golden scenarios for open access + CWC compute credit
(DSK-MFY-ACCESS-CWC-PATCH-001).

Seven deterministic scenarios through the real ledger and admission
services. Run: python -m moodify.access.golden
Output: outputs/access_golden/golden_summary.json
"""

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

from moodify.access.policy import AccessPolicy
from moodify.access.service import AccessService

OUT_DIR = Path(__file__).resolve().parents[3] / "outputs" / "access_golden"


def _fresh_service() -> AccessService:
    tmp = OUT_DIR / "store"
    if tmp.exists():
        shutil.rmtree(tmp)
    return AccessService(tmp, policy=AccessPolicy.from_yaml())


def scenario_open_signup_no_code() -> dict:
    service = _fresh_service()
    result = service.register("u-open-1")
    ok = result["registration_mode"] == "OPEN" and result["balance"]["available_cwc"] == 100.0
    return {"name": "OPEN_SIGNUP_NO_CODE", "ok": ok,
            "mode": result["registration_mode"], "balance": result["balance"]["available_cwc"]}


def scenario_open_signup_with_referral() -> dict:
    service = _fresh_service()
    service.register("u-inviter")
    result = service.register("u-invitee", referral_code="u-inviter")
    ok = result["registration_mode"] == "REFERRAL" and result["referral"]["state"] == "GRANTED"
    return {"name": "OPEN_SIGNUP_WITH_REFERRAL", "ok": ok,
            "mode": result["registration_mode"], "referral_state": result["referral"]["state"]}


def scenario_ab_judge_estimated_cost() -> dict:
    service = _fresh_service()
    estimate = service.estimate("pairwise_ab_judge")
    ok = estimate["estimated_cwc"] == 5.0
    return {"name": "AB_JUDGE_ESTIMATED_COST", "ok": ok, "estimate": estimate}


def scenario_insufficient_cwc() -> dict:
    from dataclasses import replace

    policy = replace(AccessPolicy.from_yaml(), tier_rate_limits={"free": 1000, "creator": 1000, "enterprise": 1000})
    tmp = OUT_DIR / "store_insufficient"
    if tmp.exists():
        shutil.rmtree(tmp)
    service = AccessService(tmp, policy=policy)
    service.register("u-poor")
    # Drain the starter balance with settled full analyses (3 CWC each).
    for _ in range(40):
        result = service.admit("u-poor", "full_analysis")
        if result["queue_state"] == "ADMITTED":
            service.settle(result["admission_id"], 3.0)
    result = service.admit("u-poor", "pairwise_ab_judge")
    ok = result["queue_state"] == "REJECTED_INSUFFICIENT"
    return {"name": "INSUFFICIENT_CWC", "ok": ok,
            "queue_state": result["queue_state"],
            "balance": service.balance("u-poor")["available_cwc"]}


def scenario_queue_under_load() -> dict:
    service = _fresh_service()
    service.register("u-queue")
    first = service.admit("u-queue", "pairwise_ab_judge")  # ADMITTED (concurrency 1)
    second = service.admit("u-queue", "pairwise_ab_judge")  # QUEUED (concurrency full)
    ok = first["queue_state"] == "ADMITTED" and second["queue_state"] == "QUEUED"
    return {"name": "QUEUE_UNDER_LOAD", "ok": ok,
            "first": first["queue_state"], "second": second["queue_state"],
            "message": second.get("message", "")}


def scenario_referral_reward_granted() -> dict:
    service = _fresh_service()
    service.register("u-ref-inviter")
    service.register("u-ref-invitee", referral_code="u-ref-inviter")
    inviter_balance = service.balance("u-ref-inviter")["available_cwc"]
    invitee_balance = service.balance("u-ref-invitee")["available_cwc"]
    ok = inviter_balance == 110.0 and invitee_balance == 105.0
    return {"name": "REFERRAL_REWARD_GRANTED", "ok": ok,
            "inviter_balance": inviter_balance, "invitee_balance": invitee_balance}


def scenario_legacy_cwc_copy_removed() -> dict:
    root = Path(__file__).resolve().parents[4]
    forbidden = ("平台币", "钱包资产", "交易中心", "购买藏品")
    hits: list[str] = []
    for path in (root / "src" / "moodify" / "access").rglob("*.py"):
        text = path.read_text(encoding="utf-8", errors="ignore")
        for term in forbidden:
            if term in text:
                hits.append(f"{path.name}:{term}")
    ok = not hits
    return {"name": "LEGACY_CWC_COPY_REMOVED", "ok": ok, "forbidden_hits": hits}


def run_all() -> list[dict]:
    scenarios = [
        scenario_open_signup_no_code(),
        scenario_open_signup_with_referral(),
        scenario_ab_judge_estimated_cost(),
        scenario_insufficient_cwc(),
        scenario_queue_under_load(),
        scenario_referral_reward_granted(),
        scenario_legacy_cwc_copy_removed(),
    ]
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    summary = {"task": "DSK-MFY-ACCESS-CWC-PATCH-001", "cases": scenarios}
    (OUT_DIR / "golden_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return scenarios


def main() -> int:
    cases = run_all()
    ok = all(c["ok"] for c in cases)
    for case in cases:
        print(f"{case['name']}: ok={case['ok']}")
    print(f"GOLDEN: {'ALL PASS' if ok else 'FAILURES PRESENT'} -> outputs/access_golden/golden_summary.json")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
