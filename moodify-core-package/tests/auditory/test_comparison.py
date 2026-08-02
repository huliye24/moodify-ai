"""Comparison + judgment tests (DSK-MFY-AUDITORY-SCAN-001)."""

from __future__ import annotations

import json

import pytest

from moodify.auditory.comparison import DURATION_TOLERANCE_S, compute_deltas, validate_pair
from moodify.auditory.errors import (
    ComparisonDurationMismatch,
    ScanProfileMismatch,
)
from moodify.auditory.judgment import evaluate_risk_flags, judge
from moodify.auditory.profiles import MFY_WSE_SCAN_PROFILE_001
from moodify.auditory.service import compare_scans, load_scan_evidence, scan_audio


def _evidence(path, case, stage, tmp_path):
    scan_dir = tmp_path / f"{stage}"
    scan_audio(case, stage, path, scan_dir)
    return load_scan_evidence(scan_dir, MFY_WSE_SCAN_PROFILE_001)


def _plan(case_id, goals=None, guardrails=None):
    return {
        "case_id": case_id, "plan_version": "1.0", "plan_id": "PLAN-T",
        "observations": [], "technical_goals": goals or [],
        "guardrails": guardrails or [], "artistic_intent_notes": [],
        "approved_by": "t", "approved_at": None,
    }


def test_loudness_gain_raw_large_normalized_small(fx_stereo_sine, fx_loudness_gain, tmp_path):
    before = _evidence(fx_stereo_sine, "C", "b", tmp_path)
    after = _evidence(fx_loudness_gain, "C", "a", tmp_path)
    deltas = compute_deltas(before, after)
    assert deltas.normalization_valid
    raw = deltas.metric_delta["integrated_lufs"]["absolute_delta"]
    assert raw > 2.0  # raw loudness delta is large
    # normalized band deltas must be near zero for a pure gain change
    for key, val in deltas.normalized_band_deltas.items():
        if val is not None:
            assert abs(val) < 0.05, f"{key} normalized delta too large: {val}"


def test_low_frequency_modification_detected(fx_stereo_sine, fx_low_freq_heavy, tmp_path):
    before = _evidence(fx_stereo_sine, "C", "b", tmp_path)
    after = _evidence(fx_low_freq_heavy, "C", "a", tmp_path)
    deltas = compute_deltas(before, after)
    assert deltas.raw_band_deltas["sub_20_60_hz"] > 0
    assert deltas.raw_band_deltas["bass_60_120_hz"] > 0


def test_duration_mismatch_fails_closed(fx_stereo_sine, fx_duration_mismatch, tmp_path):
    before = _evidence(fx_stereo_sine, "C", "b", tmp_path)
    after = _evidence(fx_duration_mismatch, "C", "a", tmp_path)
    assert abs(before.duration_s - after.duration_s) > DURATION_TOLERANCE_S
    with pytest.raises(ComparisonDurationMismatch):
        validate_pair(before, after)


def test_profile_mismatch_fails_closed(fx_stereo_sine, tmp_path):
    before = _evidence(fx_stereo_sine, "C", "b", tmp_path)
    after = _evidence(fx_stereo_sine, "C", "a", tmp_path)
    # tamper the after profile hash as if a different profile had been used
    after.profile_hash = "0" * 64
    with pytest.raises(ScanProfileMismatch):
        validate_pair(before, after)


def test_missing_evidence_prevents_compare(fx_stereo_sine, tmp_path):
    from moodify.auditory.errors import ComparisonEvidenceIncomplete
    _evidence(fx_stereo_sine, "C", "b", tmp_path)
    empty_dir = tmp_path / "missing"
    empty_dir.mkdir()
    with pytest.raises(ComparisonEvidenceIncomplete):
        load_scan_evidence(empty_dir, MFY_WSE_SCAN_PROFILE_001)


def test_guardrail_failure_reject_technical(fx_stereo_sine, fx_clipped, tmp_path):
    before = _evidence(fx_stereo_sine, "C", "b", tmp_path)
    after = _evidence(fx_clipped, "C", "a", tmp_path)
    deltas = compute_deltas(before, after)
    flags = evaluate_risk_flags(deltas.metric_delta, before.metrics, after.metrics)
    plan = _plan("C", goals=[], guardrails=[
        {"guardrail_id": "NO_NEW_CLIPPING", "metric": "clipping_sample_count",
         "comparator": "EQUAL", "threshold": 0, "severity": "BLOCKING"},
    ])
    j = judge(deltas.metric_delta, before.metrics, after.metrics, plan, flags)
    assert j.workflow_decision == "REJECT_TECHNICAL"
    assert j.technical_assessment == "DEGRADED"
    assert "NEW_CLIPPING" in [f.code for f in flags]


def test_successful_goals_pass_to_listening(fx_stereo_sine, fx_loudness_gain, tmp_path):
    before = _evidence(fx_stereo_sine, "C", "b", tmp_path)
    after = _evidence(fx_loudness_gain, "C", "a", tmp_path)
    deltas = compute_deltas(before, after)
    flags = evaluate_risk_flags(deltas.metric_delta, before.metrics, after.metrics)
    plan = _plan("C", goals=[
        {"goal_id": "G1", "metric": "integrated_lufs", "desired_direction": "INCREASE",
         "minimum_meaningful_change": 1.0},
    ])
    j = judge(deltas.metric_delta, before.metrics, after.metrics, plan, flags)
    assert j.workflow_decision == "PASS_TO_LISTENING"
    assert j.technical_assessment == "IMPROVED"
    assert "G1" in j.goals_met


def test_no_plan_remains_conservative(fx_stereo_sine, fx_loudness_gain, tmp_path):
    before = _evidence(fx_stereo_sine, "C", "b", tmp_path)
    after = _evidence(fx_loudness_gain, "C", "a", tmp_path)
    deltas = compute_deltas(before, after)
    flags = evaluate_risk_flags(deltas.metric_delta, before.metrics, after.metrics)
    j = judge(deltas.metric_delta, before.metrics, after.metrics, None, flags)
    assert j.technical_assessment == "UNCERTAIN"
    assert j.workflow_decision == "INCONCLUSIVE"
    assert "IMPROVED" not in j.technical_assessment


def test_artistic_approval_never_automatic(fx_stereo_sine, fx_loudness_gain, tmp_path):
    before = _evidence(fx_stereo_sine, "C", "b", tmp_path)
    after = _evidence(fx_loudness_gain, "C", "a", tmp_path)
    plan = _plan("C", goals=[
        {"goal_id": "G1", "metric": "integrated_lufs", "desired_direction": "INCREASE",
         "minimum_meaningful_change": 1.0},
    ])
    result = compare_scans(before, after, plan, tmp_path / "cmp", case_id="C",
                           candidate_id="K", source_sha256="s" * 64, candidate_sha256="c" * 64)
    report = json.loads(result["report_path"].read_text(encoding="utf-8"))
    assert report["human_listening_required"] is True
    assert report["artistic_approval_granted"] is False
    assert report["judgment"]["workflow_decision"] == "PASS_TO_LISTENING"
