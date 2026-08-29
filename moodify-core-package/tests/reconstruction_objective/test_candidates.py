"""Candidate plan tests (MFY-CR-P04)."""

from __future__ import annotations

import pytest

from moodify.era_diagnostic.contract import (
    ConfidenceLevel,
    DiagnosticCategory,
    EraDiagnosticFinding,
    FindingStatus,
)
from moodify.reconstruction_objective.candidates import generate_reconstruction_candidates
from moodify.reconstruction_objective.generator import build_objectives

pytestmark = pytest.mark.v01

SRC = "sha256_abc"
CASE = "case_01"


def _obj(category, conf=ConfidenceLevel.HIGH):
    f = EraDiagnosticFinding(
        category=category, status=FindingStatus.POSSIBLE_TECHNICAL_LIMITATION,
        finding_id="f1", reasoning_summary="t", confidence=conf, measurement_refs=("metric_x",),
    )
    return build_objectives([f], source_hash=SRC, production_case_id=CASE)[0]


def test_high_confidence_generates_abc():
    o = _obj(DiagnosticCategory.ED_01_BANDWIDTH_LIMITATION)
    plans = generate_reconstruction_candidates(o, {"sample_rate": 44100})
    assert [p.candidate_label for p in plans] == ["A", "B", "C"]
    assert plans[0].intensity < plans[1].intensity < plans[2].intensity
    # C is the pressure test, never the default product output
    assert plans[2].intensity == 0.7


def test_medium_confidence_minimal_only():
    o = _obj(DiagnosticCategory.ED_04_STEREO_PHASE_LIMITATION, conf=ConfidenceLevel.MEDIUM)
    plans = generate_reconstruction_candidates(o, {})
    assert [p.candidate_label for p in plans] == ["A", "B"]
    assert max(p.intensity for p in plans) <= 0.2


def test_unsupported_noise_gives_no_plans():
    o = _obj(DiagnosticCategory.ED_02_PERSISTENT_NOISE)
    assert generate_reconstruction_candidates(o, {}) == []


def test_low_confidence_no_aggressive_plans():
    f = EraDiagnosticFinding(
        category=DiagnosticCategory.ED_03_DYNAMIC_DAMAGE,
        status=FindingStatus.POSSIBLE_TECHNICAL_LIMITATION,
        finding_id="f1", reasoning_summary="t", confidence=ConfidenceLevel.LOW, measurement_refs=("metric_x",),
    )
    objs = build_objectives([f], source_hash=SRC, production_case_id=CASE)
    assert objs == []  # BYPASS default


def test_params_within_budget():
    o = _obj(DiagnosticCategory.ED_01_BANDWIDTH_LIMITATION)
    plans = generate_reconstruction_candidates(o, {})
    for p in plans:
        assert abs(p.params.get("eq_gain_db", 0.0)) <= 2.5
    o2 = _obj(DiagnosticCategory.ED_03_DYNAMIC_DAMAGE)
    for p in generate_reconstruction_candidates(o2, {}):
        assert abs(p.params.get("loudness_delta_db", 0.0)) <= 0.4


def test_reproducible_plan_hashes():
    o = _obj(DiagnosticCategory.ED_05_SPECTRAL_CONGESTION)
    a = generate_reconstruction_candidates(o, {"x": 1.0})
    b = generate_reconstruction_candidates(o, {"x": 1.0})
    assert [p.plan_id for p in a] == [p.plan_id for p in b]
    assert [p.params for p in a] == [p.params for p in b]


def test_different_sources_different_plans():
    f = EraDiagnosticFinding(
        category=DiagnosticCategory.ED_01_BANDWIDTH_LIMITATION,
        status=FindingStatus.POSSIBLE_TECHNICAL_LIMITATION,
        finding_id="f1", reasoning_summary="t", confidence=ConfidenceLevel.HIGH,
        measurement_refs=("metric_x",),
    )
    oa = build_objectives([f], source_hash="sha_A", production_case_id=CASE)[0]
    ob = build_objectives([f], source_hash="sha_B", production_case_id=CASE)[0]
    pa = generate_reconstruction_candidates(oa, {})
    pb = generate_reconstruction_candidates(ob, {})
    # objective id differs -> plan ids differ even with same metrics
    assert pa[0].objective_id != pb[0].objective_id
