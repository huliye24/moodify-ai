"""Unit tests for the EraDiagnosticFinding contract and policy (MFY-CR-P03)."""

from __future__ import annotations

import json

import pytest

from moodify.era_diagnostic.contract import (
    ConfidenceLevel,
    DiagnosticCategory,
    EraDiagnosticFinding,
    FindingStatus,
)
from moodify.era_diagnostic.engine import DETECTOR_INPUTS, run_era_diagnostic
from moodify.era_diagnostic.thresholds import ERA_DIAGNOSTIC_POLICY_V1

NOW = "2026-08-17T00:00:00+00:00"


def _finding(**overrides) -> EraDiagnosticFinding:
    base = dict(
        category=DiagnosticCategory.ED_01_BANDWIDTH_LIMITATION,
        status=FindingStatus.POSSIBLE_TECHNICAL_LIMITATION,
        finding_id="ED-01-1",
        reasoning_summary="test",
        measurement_refs=("estimated_high_frequency_cutoff_hz", "spectral_rolloff_95_hz"),
        confidence=ConfidenceLevel.MEDIUM,
        known_ambiguities=("maybe artistic",),
        created_at=NOW,
    )
    base.update(overrides)
    return EraDiagnosticFinding(**base)


class TestStatusConfidenceValidation:
    def test_possible_requires_confidence(self):
        with pytest.raises(ValueError):
            _finding(status=FindingStatus.POSSIBLE_TECHNICAL_LIMITATION, confidence=None)

    def test_artistic_requires_confidence(self):
        with pytest.raises(ValueError):
            _finding(status=FindingStatus.LIKELY_ARTISTIC_CHARACTER, confidence=None)

    def test_insufficient_requires_confidence(self):
        with pytest.raises(ValueError):
            _finding(status=FindingStatus.INSUFFICIENT_EVIDENCE, confidence=None)

    def test_not_applicable_forbids_confidence(self):
        with pytest.raises(ValueError):
            _finding(status=FindingStatus.NOT_APPLICABLE, confidence=ConfidenceLevel.LOW)

    def test_not_supported_forbids_confidence(self):
        with pytest.raises(ValueError):
            _finding(status=FindingStatus.NOT_SUPPORTED_IN_V0_1, confidence=ConfidenceLevel.LOW)

    def test_observed_allows_confidence(self):
        f = _finding(status=FindingStatus.OBSERVED, confidence=ConfidenceLevel.LOW)
        assert f.status == FindingStatus.OBSERVED

    def test_invalid_uncertainty_reason_rejected(self):
        with pytest.raises(ValueError):
            _finding(uncertainty_reason="NOT_A_REAL_REASON")

    def test_valid_uncertainty_reason_accepted(self):
        f = _finding(uncertainty_reason="MEASUREMENT_UNCERTAINTY")
        assert f.uncertainty_reason == "MEASUREMENT_UNCERTAINTY"

    def test_empty_measurement_refs_rejected(self):
        with pytest.raises(ValueError):
            _finding(measurement_refs=())


class TestSerialization:
    def test_round_trip(self):
        f = _finding(uncertainty_reason="EVIDENCE_INCOMPLETE",
                     requires_human_review=True,
                     evidence_refs=("ev-1",))
        restored = EraDiagnosticFinding.from_dict(f.to_dict())
        assert restored == f

    def test_json_deterministic(self):
        f1 = _finding()
        f2 = _finding()
        assert json.dumps(f1.to_dict(), sort_keys=True) == json.dumps(f2.to_dict(), sort_keys=True)

    def test_finding_id_unique_per_category(self):
        findings = run_era_diagnostic({}, created_at=NOW)
        ids = [f.finding_id for f in findings]
        assert len(ids) == len(set(ids))


class TestUnknownHandling:
    def test_empty_metrics_produces_no_crash(self):
        findings = run_era_diagnostic({}, created_at=NOW)
        assert len(findings) == 6
        assert all(f.status in {FindingStatus.INSUFFICIENT_EVIDENCE,
                                FindingStatus.NOT_SUPPORTED_IN_V0_1} for f in findings)

    def test_missing_metrics_never_possible(self):
        findings = run_era_diagnostic({"stereo_correlation": {"value": 0.5}}, created_at=NOW)
        assert all(f.status != FindingStatus.POSSIBLE_TECHNICAL_LIMITATION
                   for f in findings)


class TestPolicyEnforcement:
    def test_detector_inputs_are_diagnostic_eligible(self):
        eligible = {name for name, cls in
                    ERA_DIAGNOSTIC_POLICY_V1["metric_eligibility"].items()
                    if cls == "ELIGIBLE_FOR_DIAGNOSTIC"}
        for detector, inputs in DETECTOR_INPUTS.items():
            assert inputs, f"detector {detector} declares no inputs"
            assert set(inputs) <= eligible, (
                f"{detector} uses non-eligible metrics: {set(inputs) - eligible}"
            )

    def test_judgment_eligibility_untouched(self):
        """P03 must NOT promote estimators in the global registry."""
        import yaml
        from pathlib import Path

        registry = yaml.safe_load(
            (Path(__file__).parents[2] / "configs" / "measurement_registry_v1.yaml").read_text()
        )
        assert registry["estimated_high_frequency_cutoff_hz"]["judgment_eligible"] is False
        assert registry["estimated_noise_floor_dbfs"]["judgment_eligible"] is False
