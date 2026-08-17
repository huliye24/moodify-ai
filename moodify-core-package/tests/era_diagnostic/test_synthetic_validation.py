"""Synthetic validation matrix V01-V12 + negative controls N01-N05 (MFY-CR-P03).

Uses the real measurement chain (compute_metrics + compute_stereo_metrics) so
the diagnostics are validated end-to-end on generated audio with known truth.
"""

from __future__ import annotations

import numpy as np

from moodify.era_diagnostic.contract import (
    ConfidenceLevel,
    DiagnosticCategory,
    FindingStatus,
)
from moodify.era_diagnostic.engine import run_era_diagnostic

from conftest import (
    add_noise,
    clean_stereo,
    clipped,
    dark_but_clean,
    lowpass,
    metricize,
    phase_flipped,
    to_mono,
    width_scaled,
)

NOW = "2026-08-17T00:00:00+00:00"

_SEVERITY = {
    FindingStatus.NOT_APPLICABLE: 0,
    FindingStatus.NOT_SUPPORTED_IN_V0_1: 0,
    FindingStatus.OBSERVED: 1,
    FindingStatus.INSUFFICIENT_EVIDENCE: 1,
    FindingStatus.LIKELY_ARTISTIC_CHARACTER: 1,
    FindingStatus.POSSIBLE_TECHNICAL_LIMITATION: 2,
}
_CONF = {None: 0, ConfidenceLevel.LOW: 1, ConfidenceLevel.MEDIUM: 2, ConfidenceLevel.HIGH: 3}


def _score(metrics, category: DiagnosticCategory) -> int:
    f = next(x for x in run_era_diagnostic(metrics, created_at=NOW) if x.category == category)
    return _SEVERITY[f.status] * 10 + _CONF[f.confidence]


def _finding(metrics, category: DiagnosticCategory):
    return next(x for x in run_era_diagnostic(metrics, created_at=NOW) if x.category == category)


class TestSyntheticMatrix:
    """V01-V12 from 03_VALIDATION_MATRIX.md."""

    def test_v01_clean_full_band_no_bandwidth_limitation(self, clean_metrics):
        f = _finding(clean_metrics, DiagnosticCategory.ED_01_BANDWIDTH_LIMITATION)
        assert f.status == FindingStatus.NOT_APPLICABLE

    def test_v02_v03_v04_lowpass_ladder_is_monotonic(self):
        base = clean_stereo()
        scores = {}
        for cutoff in (18000, 15000, 12000, 9000):
            x = lowpass(base, cutoff)
            scores[cutoff] = _score(metricize(x), DiagnosticCategory.ED_01_BANDWIDTH_LIMITATION)
        assert scores[9000] > scores[12000] >= scores[15000] >= scores[18000], scores
        assert scores[9000] >= 21  # POSSIBLE + at least MEDIUM

    def test_v02_18k_is_weak(self):
        x = lowpass(clean_stereo(), 18000)
        f = _finding(metricize(x), DiagnosticCategory.ED_01_BANDWIDTH_LIMITATION)
        assert f.status in {FindingStatus.NOT_APPLICABLE,
                            FindingStatus.INSUFFICIENT_EVIDENCE,
                            FindingStatus.POSSIBLE_TECHNICAL_LIMITATION}
        if f.status == FindingStatus.POSSIBLE_TECHNICAL_LIMITATION:
            assert f.confidence == ConfidenceLevel.LOW

    def test_v04_9k_is_strong(self):
        x = lowpass(clean_stereo(), 9000)
        f = _finding(metricize(x), DiagnosticCategory.ED_01_BANDWIDTH_LIMITATION)
        assert f.status == FindingStatus.POSSIBLE_TECHNICAL_LIMITATION
        assert f.confidence in {ConfidenceLevel.HIGH, ConfidenceLevel.MEDIUM}

    def test_v05_v06_v07_hiss_ladder(self):
        """Floor estimator responds monotonically; -70 stays quiet, -60 is
        measurable, -50 is loud but fills the quiet windows so the honest
        outcome is POSSIBLE or INSUFFICIENT — never HIGH."""
        rng = np.random.default_rng(11)
        base = clean_stereo()
        floors: dict[int, float] = {}
        statuses: dict[int, str] = {}
        for dbfs in (-70, -60, -50):
            mm = metricize(add_noise(base, dbfs, rng, everywhere=True))
            floors[dbfs] = mm["estimated_noise_floor_dbfs"]["value"]
            f = _finding(mm, DiagnosticCategory.ED_02_PERSISTENT_NOISE)
            statuses[dbfs] = f.status.value
            assert f.confidence != ConfidenceLevel.HIGH
            if f.status == FindingStatus.POSSIBLE_TECHNICAL_LIMITATION:
                assert f.known_ambiguities
        assert floors[-50] > floors[-60] > floors[-70], floors
        assert statuses[-70] == FindingStatus.NOT_APPLICABLE.value
        assert statuses[-60] == FindingStatus.POSSIBLE_TECHNICAL_LIMITATION.value
        assert statuses[-50] in {FindingStatus.POSSIBLE_TECHNICAL_LIMITATION.value,
                                 FindingStatus.INSUFFICIENT_EVIDENCE.value}

    def test_v05_quiet_hiss_not_flagged(self):
        rng = np.random.default_rng(13)
        x = add_noise(clean_stereo(), -70, rng, everywhere=True)
        f = _finding(metricize(x), DiagnosticCategory.ED_02_PERSISTENT_NOISE)
        assert f.status in {FindingStatus.NOT_APPLICABLE,
                            FindingStatus.INSUFFICIENT_EVIDENCE,
                            FindingStatus.POSSIBLE_TECHNICAL_LIMITATION}
        if f.status == FindingStatus.POSSIBLE_TECHNICAL_LIMITATION:
            assert f.confidence == ConfidenceLevel.LOW

    def test_v08_clipping_found(self):
        x = clipped(clean_stereo())
        f = _finding(metricize(x), DiagnosticCategory.ED_03_DYNAMIC_DAMAGE)
        assert f.status == FindingStatus.POSSIBLE_TECHNICAL_LIMITATION

    def test_v09_mono_folddown_not_auto_defect(self):
        x = to_mono(clean_stereo())
        f = _finding(metricize(x), DiagnosticCategory.ED_04_STEREO_PHASE_LIMITATION)
        assert f.status == FindingStatus.LIKELY_ARTISTIC_CHARACTER

    def test_v10_width_50_observed_not_defect(self):
        x = width_scaled(clean_stereo(), 0.5)
        f = _finding(metricize(x), DiagnosticCategory.ED_04_STEREO_PHASE_LIMITATION)
        assert f.status in {FindingStatus.OBSERVED,
                            FindingStatus.NOT_APPLICABLE,
                            FindingStatus.LIKELY_ARTISTIC_CHARACTER}
        assert f.status != FindingStatus.POSSIBLE_TECHNICAL_LIMITATION

    def test_v11_phase_perturbation_raises_risk(self):
        x = phase_flipped(clean_stereo(), 2.0, 4.0)
        f = _finding(metricize(x), DiagnosticCategory.ED_04_STEREO_PHASE_LIMITATION)
        assert f.status == FindingStatus.POSSIBLE_TECHNICAL_LIMITATION

    def test_v12_transcode_not_supported(self):
        f = _finding(metricize(clean_stereo()), DiagnosticCategory.ED_06_TRANSFER_ENCODING_DEGRADATION)
        assert f.status == FindingStatus.NOT_SUPPORTED_IN_V0_1


class TestNegativeControls:
    """N01-N05 — style must not be called a defect."""

    def test_n01_intentional_mono_not_defect(self):
        x = to_mono(clean_stereo())
        f = _finding(metricize(x), DiagnosticCategory.ED_04_STEREO_PHASE_LIMITATION)
        assert f.status == FindingStatus.LIKELY_ARTISTIC_CHARACTER
        assert f.confidence == ConfidenceLevel.LOW

    def test_n02_dark_mix_avoids_false_bandwidth(self):
        x = dark_but_clean()
        f = _finding(metricize(x), DiagnosticCategory.ED_01_BANDWIDTH_LIMITATION)
        assert f.status == FindingStatus.LIKELY_ARTISTIC_CHARACTER
        assert f.confidence == ConfidenceLevel.LOW

    def test_n03_lofi_texture_never_high_noise(self):
        rng = np.random.default_rng(17)
        x = add_noise(lowpass(clean_stereo(), 12000), -45, rng, everywhere=True)
        f = _finding(metricize(x), DiagnosticCategory.ED_02_PERSISTENT_NOISE)
        assert f.status != FindingStatus.NOT_APPLICABLE
        assert f.confidence != ConfidenceLevel.HIGH
        assert f.known_ambiguities

    def test_n04_compressed_aesthetic_not_damage(self):
        rng = np.random.default_rng(19)
        x = clean_stereo()
        # soft compression via tanh — no hard clipping
        y = 0.8 * np.tanh(3.0 * x)
        y += 0.001 * rng.standard_normal(y.shape)
        f = _finding(metricize(y), DiagnosticCategory.ED_03_DYNAMIC_DAMAGE)
        assert f.status in {FindingStatus.NOT_APPLICABLE, FindingStatus.OBSERVED}

    def test_n05_narrow_vintage_preserves_uncertainty(self):
        x = width_scaled(clean_stereo(), 0.3)
        f = _finding(metricize(x), DiagnosticCategory.ED_04_STEREO_PHASE_LIMITATION)
        assert f.status != FindingStatus.POSSIBLE_TECHNICAL_LIMITATION
        assert f.known_ambiguities


class TestRepeatability:
    def test_identical_inputs_identical_output(self):
        metrics = metricize(clean_stereo())
        a = [f.to_dict() for f in run_era_diagnostic(metrics, created_at=NOW)]
        b = [f.to_dict() for f in run_era_diagnostic(metrics, created_at=NOW)]
        assert a == b

    def test_report_json_deterministic(self, clean_metrics, tmp_path):
        from moodify.era_diagnostic.report import dump_json

        findings = run_era_diagnostic(clean_metrics, created_at=NOW)
        p1, p2 = tmp_path / "a.json", tmp_path / "b.json"
        dump_json(findings, p1, source_identifier="s")
        dump_json(findings, p2, source_identifier="s")
        assert p1.read_bytes() == p2.read_bytes()
