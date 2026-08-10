"""MFY-DATA-FACTORY-001 ABC plan generator tests."""

from __future__ import annotations

import json

from moodify.data_factory.models import PLAN_GENERATOR_VERSION
from moodify.data_factory.plan_generator import generate_abc_plans

CASE_ID = "case_" + "a" * 32


def _metrics() -> dict:
    return {
        "presence_2000_5000_hz": {"value": 0.05},
        "low_mid_120_250_hz": {"value": 0.13},
        "mid_250_500_hz": {"value": 0.14},
        "air_10000_16000_hz": {"value": 0.01},
        "crest_factor_db": {"value": 15.0},
    }


def _plans() -> list:
    return generate_abc_plans(
        case_id=CASE_ID,
        source_metrics=_metrics(),
        source_sha256="b" * 64,
        scan_profile_id="MFY-WSE-SCAN-PROFILE-001",
        scan_profile_hash="c" * 64,
    )


def test_generate_exact_ordered_abc_plans():
    plans = _plans()
    assert [p.candidate_label for p in plans] == ["A", "B", "C"]
    assert plans[0].intensity < plans[1].intensity < plans[2].intensity
    assert plans[0].params["P02_vocal_presence_gain"] < plans[1].params["P02_vocal_presence_gain"]
    assert plans[1].params["P02_vocal_presence_gain"] < plans[2].params["P02_vocal_presence_gain"]


def test_plan_and_candidate_ids_deterministic_within_case():
    plans = _plans()
    for label, plan in zip(("A", "B", "C"), plans):
        assert plan.plan_id == f"{CASE_ID}__PLAN_{label}"
        assert plan.candidate_id == f"{CASE_ID}__CAND_{label}"


def test_plans_are_json_serializable_and_round_trip():
    plans = _plans()
    for plan in plans:
        payload = json.dumps(plan.to_dict())
        loaded = json.loads(payload)
        assert loaded["plan_id"] == plan.plan_id
        assert loaded["plan_generator_version"] == PLAN_GENERATOR_VERSION
        assert loaded["candidate_label"] == plan.candidate_label
        assert loaded["intensity"] == plan.intensity


def test_shared_technical_objective_across_abc():
    plans = _plans()
    objective = [g["goal_id"] for g in plans[0].technical_goals]
    for plan in plans[1:]:
        assert [g["goal_id"] for g in plan.technical_goals] == objective


def test_guardrails_follow_live_judgment_contract():
    plans = _plans()
    for plan in plans:
        assert len(plan.guardrails) == 3
        for guardrail in plan.guardrails:
            assert set(("guardrail_id", "metric", "comparator", "threshold", "severity")).issubset(
                guardrail
            )
    ids = [g["guardrail_id"] for g in plans[0].guardrails]
    assert ids == ["NO_NEW_CLIPPING", "TRUE_PEAK_SAFE", "FINITE_SAMPLES_ONLY"]
    assert all(g["severity"] == "BLOCKING" for g in plans[0].guardrails)
