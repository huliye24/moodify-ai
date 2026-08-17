"""Objective model tests (MFY-CR-P04)."""

from __future__ import annotations

import pytest

from moodify.era_diagnostic.contract import (
    ConfidenceLevel,
    DiagnosticCategory,
    EraDiagnosticFinding,
    FindingStatus,
)
from moodify.reconstruction_objective.budget import InterventionBudget
from moodify.reconstruction_objective.generator import build_objectives
from moodify.reconstruction_objective.objective import (
    HONEST_BANDWIDTH_NAME,
    ObjectiveKind,
    forbidden_changes,
)

pytestmark = pytest.mark.v01

SRC = "sha256_abc"
CASE = "case_01"


def _finding(category, status=FindingStatus.POSSIBLE_TECHNICAL_LIMITATION, conf=ConfidenceLevel.HIGH, fid="f1"):
    return EraDiagnosticFinding(
        category=category, status=status, finding_id=fid,
        reasoning_summary="test", confidence=conf, measurement_refs=("metric_x",),
    )


def test_valid_high_confidence_generates_objective():
    findings = [_finding(DiagnosticCategory.ED_01_BANDWIDTH_LIMITATION)]
    objs = build_objectives(findings, source_hash=SRC, production_case_id=CASE)
    assert len(objs) == 1
    o = objs[0]
    assert o.objective_id.startswith("obj_")
    assert o.kind == ObjectiveKind.BANDWIDTH_BALANCE
    assert o.diagnostic_finding_refs == ("f1",)
    assert o.confidence == "HIGH"
    assert o.requires_human_review is False


def test_bandwidth_objective_honest_name():
    o = build_objectives(
        [_finding(DiagnosticCategory.ED_01_BANDWIDTH_LIMITATION)],
        source_hash=SRC, production_case_id=CASE,
    )[0]
    # v0.1 engine cannot restore missing content; the name is BALANCE, never RECOVERY
    assert HONEST_BANDWIDTH_NAME == "BANDWIDTH_BALANCE"
    assert o.kind.value == "RO-01"
    assert "RECOVERY" not in o.kind.value


def test_noise_objective_unsupported_not_faked():
    o = build_objectives(
        [_finding(DiagnosticCategory.ED_02_PERSISTENT_NOISE)],
        source_hash=SRC, production_case_id=CASE,
    )[0]
    assert o.kind == ObjectiveKind.NOISE_REDUCTION
    assert o.unsupported_reason == "INTERVENTION_NOT_SUPPORTED_V0_1"


def test_artistic_character_grants_no_objective():
    findings = [_finding(DiagnosticCategory.ED_01_BANDWIDTH_LIMITATION, status=FindingStatus.LIKELY_ARTISTIC_CHARACTER)]
    assert build_objectives(findings, source_hash=SRC, production_case_id=CASE) == []


def test_insufficient_evidence_grants_nothing():
    findings = [_finding(DiagnosticCategory.ED_03_DYNAMIC_DAMAGE, status=FindingStatus.INSUFFICIENT_EVIDENCE)]
    assert build_objectives(findings, source_hash=SRC, production_case_id=CASE) == []


def test_low_confidence_bypasses():
    findings = [_finding(DiagnosticCategory.ED_03_DYNAMIC_DAMAGE, conf=ConfidenceLevel.LOW)]
    assert build_objectives(findings, source_hash=SRC, production_case_id=CASE) == []


def test_medium_confidence_requires_human_and_bounded_scope():
    findings = [_finding(DiagnosticCategory.ED_04_STEREO_PHASE_LIMITATION, conf=ConfidenceLevel.MEDIUM)]
    objs = build_objectives(findings, source_hash=SRC, production_case_id=CASE)
    assert len(objs) == 1
    o = objs[0]
    assert o.requires_human_review is True
    assert o.target_conditions["max_plan_intensity"] == 0.2


def test_deterministic_across_runs():
    findings = [_finding(DiagnosticCategory.ED_05_SPECTRAL_CONGESTION)]
    a = build_objectives(findings, source_hash=SRC, production_case_id=CASE)
    b = build_objectives(findings, source_hash=SRC, production_case_id=CASE)
    assert [x.to_dict() for x in a] == [x.to_dict() for x in b]


def test_different_source_different_objective_id():
    f = [_finding(DiagnosticCategory.ED_06_TRANSFER_ENCODING_DEGRADATION)]
    a = build_objectives(f, source_hash="sha_A", production_case_id=CASE)[0]
    b = build_objectives(f, source_hash="sha_B", production_case_id=CASE)[0]
    assert a.objective_id != b.objective_id


def test_forbidden_changes_complete():
    fc = forbidden_changes()
    assert "no_duration_change" in fc
    assert "no_new_clipping" in fc
    assert "no_channel_count_change" in fc
    assert "no_vocal_replacement" in fc
    assert "no_automatic_stem_remix" in fc


def test_budget_bounded():
    b = InterventionBudget()
    assert b.eq_gain_db_max <= 3.0
    assert b.loudness_delta_db_max <= 0.5
