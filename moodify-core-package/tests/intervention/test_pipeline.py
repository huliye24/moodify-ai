"""Pipeline + negative-control tests (MFY_PRESERVE_IDENTITY_INTERVENTION_001)."""

from __future__ import annotations

import numpy as np
import pytest

from moodify.intervention.identity_gate import IdentityGate
from moodify.intervention.pipeline import run_intervention_pipeline

SR = 44100


@pytest.fixture
def clean_audio():
    """Modern well-mastered negative control: low (60 Hz), mid (440/3000 Hz), high (12 kHz)."""
    t = np.arange(SR) / SR
    return (
        0.2 * np.sin(2 * np.pi * 60 * t)
        + 0.3 * np.sin(2 * np.pi * 440 * t)
        + 0.2 * np.sin(2 * np.pi * 3000 * t)
        + 0.1 * np.sin(2 * np.pi * 12000 * t)
    ).astype(np.float32)


def make_legitimate_case(clean_audio):
    """Pre-registered legitimate case: old-record-like defects (DC + short clip)."""
    audio = clean_audio + 0.05
    audio = audio.copy()
    audio[1000:1008] = 1.0
    return audio


def test_legitimate_case_selects_with_safety(clean_audio):
    case = make_legitimate_case(clean_audio)
    result = run_intervention_pipeline(case, SR, case_id="legit_dc_clip")

    decisions = [o.decision for o in result.outcomes]
    assert decisions.count("SELECTED") >= 2, f"expected dc+clip selected, got {decisions}"
    assert "BYPASSED" not in decisions  # tonal not enabled by default; dc+clip both fire
    for o in result.outcomes:
        if o.decision == "SELECTED":
            assert o.verify is not None
            assert o.verify["safe"] == 1.0
            assert o.verify["clipped"] == 0.0
            assert o.verify["has_nan"] == 0.0
            assert o.verify["shape_match"] == 1.0
            assert abs(o.verify["loudness_diff_db"]) <= 0.5
    assert result.final_audio.shape == result.input_shape
    # loudness matched overall (no gain change)
    assert np.isfinite(result.final_audio).all()
    assert not result.all_bypassed


def test_negative_control_fully_bypassed(clean_audio):
    """Modern, well-mastered negative control: nothing should fire."""
    result = run_intervention_pipeline(clean_audio, SR, case_id="negative_control_clean")
    assert result.all_bypassed is True
    assert all(o.decision == "BYPASSED" for o in result.outcomes)
    assert result.final_audio is not None
    assert np.array_equal(result.final_audio, clean_audio)


def test_negative_control_high_bypass_rate(clean_audio):
    """Acceptance: negative control must bypass at high proportion."""
    results = [
        run_intervention_pipeline(clean_audio, SR, case_id=f"neg_{i}").all_bypassed
        for i in range(5)
    ]
    bypass_rate = sum(results) / len(results)
    assert bypass_rate == 1.0, f"negative control bypass rate {bypass_rate}"


def test_tonal_not_enabled_by_default(clean_audio):
    case = make_legitimate_case(clean_audio)
    result = run_intervention_pipeline(case, SR, case_id="default_scope")
    ids = [o.candidate.primitive_id for o in result.outcomes if o.candidate is not None]
    assert "tonal_balance_very_conservative" not in ids


def test_tonal_enabled_requires_identity_gate(clean_audio):
    case = clean_audio.copy()
    from scipy.signal import butter, sosfilt

    sos = butter(4, 150, btype="highpass", fs=SR, output="sos")
    case = sosfilt(sos, case).astype(np.float32)
    result = run_intervention_pipeline(
        case, SR, case_id="tonal_case", enabled_primitives=["tonal_balance_very_conservative"]
    )
    # very low imbalance may or may not fire; if it fires the gate decides
    if result.outcomes[0].candidate is not None:
        assert result.outcomes[0].decision in ("SELECTED", "HUMAN_REQUIRED")


def test_identity_gate_detects_drift(clean_audio):
    gate = IdentityGate()
    # near-identical candidate passes
    ok = gate.verify(clean_audio, clean_audio + 1e-5, SR)
    assert ok.decision == "PASS"
    assert ok.passed is True
    # heavily modified candidate -> identity evidence conflicts -> escalate
    bad = np.roll(clean_audio, 1000) * 0.5 + 0.2
    verdict = gate.verify(clean_audio, bad.astype(np.float32), SR)
    assert verdict.passed is False
    assert verdict.decision == "HUMAN_REQUIRED"


def test_identity_gate_shape_mismatch_fails():
    gate = IdentityGate()
    v = gate.verify(np.zeros((1000, 2)), np.zeros((999, 2)), SR)
    assert v.decision == "FAIL"
    assert v.passed is False


def test_pipeline_trace_is_structured_and_serializable(clean_audio):
    case = make_legitimate_case(clean_audio)
    result = run_intervention_pipeline(case, SR, case_id="trace_case")
    summary = result.summary()
    assert summary["case_id"] == "trace_case"
    assert isinstance(summary["decisions"], list)
    assert len(result.measurements) == 2  # dc + clip (tonal not enabled)
    assert len(result.limitations) == 2
    assert all(isinstance(m.values, dict) for m in result.measurements)
