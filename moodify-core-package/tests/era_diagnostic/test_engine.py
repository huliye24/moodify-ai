"""Engine unit tests per diagnostic category (MFY-CR-P03)."""

from __future__ import annotations

from moodify.era_diagnostic.contract import (
    ConfidenceLevel,
    DiagnosticCategory,
    FindingStatus,
)
from moodify.era_diagnostic.engine import run_era_diagnostic

NOW = "2026-08-17T00:00:00+00:00"


def _m(**kwargs):
    return {k: {"value": v} for k, v in kwargs.items()}


def _finding(metrics, category: DiagnosticCategory):
    return next(f for f in run_era_diagnostic(metrics, created_at=NOW)
                if f.category == category)


class TestBandwidth:
    CAT = DiagnosticCategory.ED_01_BANDWIDTH_LIMITATION

    def test_clean_cutoff_not_applicable(self):
        f = _finding(_m(estimated_high_frequency_cutoff_hz=17500,
                        spectral_rolloff_95_hz=14000,
                        presence_2000_5000_hz=0.05), self.CAT)
        assert f.status == FindingStatus.NOT_APPLICABLE

    def test_low_cutoff_corroborated_low_confidence(self):
        f = _finding(_m(estimated_high_frequency_cutoff_hz=14200,
                        spectral_rolloff_95_hz=11000,
                        presence_2000_5000_hz=0.05), self.CAT)
        assert f.status == FindingStatus.POSSIBLE_TECHNICAL_LIMITATION
        assert f.confidence == ConfidenceLevel.LOW

    def test_low_cutoff_corroborated_high_confidence(self):
        f = _finding(_m(estimated_high_frequency_cutoff_hz=8900,
                        spectral_rolloff_95_hz=7500,
                        presence_2000_5000_hz=0.05), self.CAT)
        assert f.status == FindingStatus.POSSIBLE_TECHNICAL_LIMITATION
        assert f.confidence == ConfidenceLevel.HIGH

    def test_dark_source_is_artistic_not_defect(self):
        f = _finding(_m(estimated_high_frequency_cutoff_hz=9000,
                        spectral_rolloff_95_hz=7000,
                        presence_2000_5000_hz=0.0001), self.CAT)
        assert f.status == FindingStatus.LIKELY_ARTISTIC_CHARACTER
        assert f.confidence == ConfidenceLevel.LOW

    def test_single_proxy_is_insufficient(self):
        f = _finding(_m(estimated_high_frequency_cutoff_hz=12000), self.CAT)
        assert f.status == FindingStatus.INSUFFICIENT_EVIDENCE

    def test_missing_estimator_insufficient(self):
        f = _finding(_m(spectral_rolloff_95_hz=10000), self.CAT)
        assert f.status == FindingStatus.INSUFFICIENT_EVIDENCE


class TestNoise:
    CAT = DiagnosticCategory.ED_02_PERSISTENT_NOISE

    def test_quiet_floor_not_applicable(self):
        f = _finding(_m(estimated_noise_floor_dbfs=-75.0, silence_ratio=0.2), self.CAT)
        assert f.status == FindingStatus.NOT_APPLICABLE

    def test_elevated_floor_with_silence_low_confidence(self):
        f = _finding(_m(estimated_noise_floor_dbfs=-62.0, silence_ratio=0.2), self.CAT)
        assert f.status == FindingStatus.POSSIBLE_TECHNICAL_LIMITATION
        assert f.confidence == ConfidenceLevel.LOW
        assert f.requires_human_review

    def test_strong_floor_medium_confidence(self):
        f = _finding(_m(estimated_noise_floor_dbfs=-50.0, silence_ratio=0.2), self.CAT)
        assert f.status == FindingStatus.POSSIBLE_TECHNICAL_LIMITATION
        assert f.confidence == ConfidenceLevel.MEDIUM
        assert not f.requires_human_review

    def test_no_silence_is_insufficient(self):
        f = _finding(_m(estimated_noise_floor_dbfs=-55.0, silence_ratio=0.0), self.CAT)
        assert f.status == FindingStatus.INSUFFICIENT_EVIDENCE

    def test_ambiguity_mentions_artistic_texture(self):
        f = _finding(_m(estimated_noise_floor_dbfs=-60.0, silence_ratio=0.2,
                        spectral_flatness=0.2), self.CAT)
        assert any("artistic" in a for a in f.known_ambiguities)


class TestDynamics:
    CAT = DiagnosticCategory.ED_03_DYNAMIC_DAMAGE

    def test_clean_not_applicable(self):
        f = _finding(_m(clipping_sample_ratio=0.0, true_peak_dbfs=-3.0), self.CAT)
        assert f.status == FindingStatus.NOT_APPLICABLE

    def test_clipping_at_ceiling_possible(self):
        f = _finding(_m(clipping_sample_ratio=0.001, true_peak_dbfs=-0.1), self.CAT)
        assert f.status == FindingStatus.POSSIBLE_TECHNICAL_LIMITATION
        assert f.confidence == ConfidenceLevel.MEDIUM

    def test_clipping_without_ceiling_is_observed(self):
        f = _finding(_m(clipping_sample_ratio=0.001, true_peak_dbfs=-6.0), self.CAT)
        assert f.status == FindingStatus.OBSERVED

    def test_low_dynamics_without_clipping_is_observed(self):
        f = _finding(_m(clipping_sample_ratio=0.0, true_peak_dbfs=-1.0,
                        loudness_range_lu=2.5, crest_factor_db=4.0), self.CAT)
        assert f.status == FindingStatus.OBSERVED
        assert any("aesthetic" in a for a in f.known_ambiguities)


class TestStereo:
    CAT = DiagnosticCategory.ED_04_STEREO_PHASE_LIMITATION

    def test_mono_is_artistic(self):
        f = _finding(_m(stereo_correlation=1.0, phase_risk_ratio=0.0,
                        negative_correlation_ratio=0.0), self.CAT)
        assert f.status == FindingStatus.LIKELY_ARTISTIC_CHARACTER
        assert f.confidence == ConfidenceLevel.LOW

    def test_narrow_is_observed_not_defect(self):
        f = _finding(_m(stereo_correlation=0.99, phase_risk_ratio=0.01,
                        negative_correlation_ratio=0.01), self.CAT)
        assert f.status == FindingStatus.OBSERVED

    def test_phase_anomaly_corroborated_medium(self):
        f = _finding(_m(stereo_correlation=0.85, phase_risk_ratio=0.2,
                        negative_correlation_ratio=0.1), self.CAT)
        assert f.status == FindingStatus.POSSIBLE_TECHNICAL_LIMITATION
        assert f.confidence == ConfidenceLevel.MEDIUM

    def test_phase_anomaly_single_proxy_low(self):
        f = _finding(_m(stereo_correlation=0.85, phase_risk_ratio=0.2,
                        negative_correlation_ratio=0.01), self.CAT)
        assert f.status == FindingStatus.POSSIBLE_TECHNICAL_LIMITATION
        assert f.confidence == ConfidenceLevel.LOW

    def test_wide_clean_not_applicable(self):
        f = _finding(_m(stereo_correlation=0.5, phase_risk_ratio=0.02,
                        negative_correlation_ratio=0.01), self.CAT)
        assert f.status == FindingStatus.NOT_APPLICABLE


class TestCongestion:
    CAT = DiagnosticCategory.ED_05_SPECTRAL_CONGESTION

    def test_dense_observed_with_ambiguity(self):
        f = _finding(_m(spectral_flatness=0.02, core_mid_500_2000_hz=0.4), self.CAT)
        assert f.status == FindingStatus.OBSERVED
        assert f.confidence == ConfidenceLevel.LOW
        assert any("artistic" in a for a in f.known_ambiguities)

    def test_flat_not_applicable(self):
        f = _finding(_m(spectral_flatness=0.5, core_mid_500_2000_hz=0.2), self.CAT)
        assert f.status == FindingStatus.NOT_APPLICABLE


class TestTransfer:
    CAT = DiagnosticCategory.ED_06_TRANSFER_ENCODING_DEGRADATION

    def test_not_supported_by_default(self):
        f = _finding(_m(sample_rate=48000), self.CAT)
        assert f.status == FindingStatus.NOT_SUPPORTED_IN_V0_1

    def test_low_sample_rate_observed(self):
        f = _finding(_m(sample_rate=22050), self.CAT)
        assert f.status == FindingStatus.OBSERVED
        assert not f.requires_human_review


class TestEvidenceRule:
    def test_possible_requires_two_measurements_and_ambiguity(self):
        for f in run_era_diagnostic(
            _m(estimated_high_frequency_cutoff_hz=8900, spectral_rolloff_95_hz=7500,
               presence_2000_5000_hz=0.05),
            created_at=NOW,
        ):
            if f.status == FindingStatus.POSSIBLE_TECHNICAL_LIMITATION:
                assert len(f.measurement_refs) >= 2
                assert f.known_ambiguities

    def test_order_is_ed01_to_ed06(self):
        findings = run_era_diagnostic({}, created_at=NOW)
        assert [f.category.value for f in findings] == [
            "ED-01", "ED-02", "ED-03", "ED-04", "ED-05", "ED-06",
        ]

    def test_no_reconstruct_now(self):
        for f in run_era_diagnostic({}, created_at=NOW):
            assert "RECONSTRUCT_NOW" not in f.status.value
            assert "reconstruction" not in f.status.value.lower()
