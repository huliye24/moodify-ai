"""Golden scenarios for the recommendation layer
(DSK-MFY-TASTE-FEED-PATCH-001).

Deterministic synthetic track vectors exercise cold start, profile
linkage, feedback-driven taste updates, skip penalties, exploration
budget, quality gates, and request traceability.
Run: python -m moodify.recommendation.golden
Output: outputs/feed_golden/golden_summary.json
"""

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

from moodify.recommendation.service import FeedService

OUT_DIR = Path(__file__).resolve().parents[3] / "outputs" / "feed_golden"


def _fresh_service() -> FeedService:
    tmp = OUT_DIR / "store"
    if tmp.exists():
        shutil.rmtree(tmp)
    return FeedService(tmp)


def _register(svc: FeedService, count: int = 8) -> None:
    for i in range(count):
        svc.register_track(
            f"t{i}", f"src-{i}",
            [0.1 * i, 0.2 * i, 0.3 * i, 0.4 * i, 0.1 + 0.01 * i, 0.1, 0.1],
            quality_confidence=0.6 + 0.05 * i,
        )


def scenario_new_user_cold_start() -> dict:
    svc = _fresh_service()
    _register(svc)
    feed = svc.get_for_you("new-user", size=5)
    ok = len(feed["feed"]) == 5 and feed["request_id"].startswith("req-")
    return {"name": "NEW_USER_COLD_START", "ok": ok,
            "feed_size": len(feed["feed"]), "request_id": feed["request_id"]}


def scenario_track_profile_linkage() -> dict:
    svc = _fresh_service()
    _register(svc, 1)
    profile = svc.auditory_profile("t0")
    ok = profile is not None and len(profile.feature_vector) == 7
    return {"name": "TRACK_PROFILE_LINKAGE", "ok": ok,
            "profile_id": profile.auditory_profile_id if profile else None}


def scenario_feedback_updates_taste() -> dict:
    svc = _fresh_service()
    _register(svc, 2)
    before = svc.taste_profile("u1").long_term_vector
    svc.record_feedback("u1", "t1", "COMPLETION", duration_ms=100_000, elapsed_ms=100_000)
    after = svc.taste_profile("u1").long_term_vector
    ok = before != after and any(v != 0.0 for v in after)
    return {"name": "FEEDBACK_UPDATES_TASTE", "ok": ok,
            "long_term_changed": before != after}


def scenario_skip_penalty_ranking() -> dict:
    svc = _fresh_service()
    _register(svc, 4)
    # Repeatedly hard-skip the top similarity track.
    for _ in range(3):
        svc.record_feedback("u1", "t3", "SKIP", elapsed_ms=1_500)
    first_before = svc.get_for_you("u1", size=4)["feed"][0]["track_id"]
    ok = first_before != "t3"
    return {"name": "SKIP_PENALTY_RANKING", "ok": ok, "first_after_skips": first_before}


def scenario_exploration_budget() -> dict:
    svc = _fresh_service()
    _register(svc, 12)
    feed = svc.get_for_you("u1", size=10)
    sources = {c["candidate_source"] for c in feed["feed"]}
    ok = len(feed["feed"]) <= 10 and bool(sources & {"similarity", "exploration"})
    return {"name": "EXPLORATION_BUDGET", "ok": ok,
            "sources": sorted(sources), "size": len(feed["feed"])}


def scenario_quality_gate_filter() -> dict:
    svc = _fresh_service()
    _register(svc, 4)
    svc.register_track("bad", "src-bad", [0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5],
                       quality_state="SEVERE_ISSUES")
    feed = svc.get_for_you("u1", size=5)
    ok = all(c["track_id"] != "bad" for c in feed["feed"])
    return {"name": "QUALITY_GATE_FILTER", "ok": ok,
            "bad_in_feed": any(c["track_id"] == "bad" for c in feed["feed"])}


def scenario_request_traceability() -> dict:
    svc = _fresh_service()
    _register(svc, 4)
    feed = svc.get_for_you("u1", size=3)
    request_id = feed["request_id"]
    first = feed["feed"][0]
    svc.record_feedback("u1", first["track_id"], "COMPLETION",
                        request_id=request_id, rank_position=first["final_rank"],
                        duration_ms=100_000, elapsed_ms=100_000)
    events = svc.feedback.events_for_request(request_id)
    ok = len(events) >= 4  # 3 impressions + 1 completion
    return {"name": "REQUEST_TRACEABILITY", "ok": ok,
            "events_for_request": len(events), "ranking_version": feed["ranking_version"]}


def run_all() -> list[dict]:
    scenarios = [
        scenario_new_user_cold_start(),
        scenario_track_profile_linkage(),
        scenario_feedback_updates_taste(),
        scenario_skip_penalty_ranking(),
        scenario_exploration_budget(),
        scenario_quality_gate_filter(),
        scenario_request_traceability(),
    ]
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    summary = {"task": "DSK-MFY-TASTE-FEED-PATCH-001", "cases": scenarios}
    (OUT_DIR / "golden_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return scenarios


def main() -> int:
    cases = run_all()
    ok = all(c["ok"] for c in cases)
    for case in cases:
        print(f"{case['name']}: ok={case['ok']}")
    print(f"GOLDEN: {'ALL PASS' if ok else 'FAILURES PRESENT'} -> outputs/feed_golden/golden_summary.json")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
