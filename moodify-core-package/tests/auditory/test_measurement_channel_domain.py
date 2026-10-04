"""Channel-domain correctness of the canonical measurement record (HOTFIX 000).

The F1/F2 defects slipped through because every oracle test in
``test_measurement_correctness.py`` used a **mono** fixture. For mono,
``sum(weights) == 1`` makes a mean-over-channels aggregation a no-op, and a
mono downmix is the signal itself. Stereo was never measured against a
reference.

These tests exist to make that blind spot impossible:

* loudness is compared against an independent oracle (``pyloudnorm``) on
  *stereo* signals;
* the old error is asserted to be far outside tolerance, so reintroducing it
  fails loudly;
* peak / RMS are asserted to span every channel rather than a downmix.

Every fixture is generated deterministically here — no committed audio.
"""

from __future__ import annotations

import numpy as np
import pytest

from moodify.auditory.judgment import evaluate_risk_flags
from moodify.auditory.loudness import integrated_loudness_lufs
from moodify.auditory.metrics import compute_metrics
from moodify.auditory.true_peak import true_peak_db

pyln = pytest.importorskip("pyloudnorm")

#: A mean-over-channels aggregation under-reports stereo by exactly this much.
CHANNEL_MEAN_BIAS_DB = 10 * np.log10(2)  # 3.0103 dB

#: 48 kHz uses the standard's exact K-weighting coefficients.
#: Current oracle validation on these probes: <= 0.05 LU vs both pyloudnorm
#: and ffmpeg ebur128. Tolerance is set at 0.1 LU.
LUFS_TOLERANCE_STANDARD_SR = 0.1

#: 44.1 kHz reuses the 48 kHz coefficients (a documented, pre-existing
#: approximation in loudness.py -- unrelated to the channel-aggregation
#: defect, which was 3.01 dB).
#: Observed on these deterministic probes: up to ~0.15 LU.
#: Tolerance is set at 0.2 LU, wider *at that rate only* and for that
#: documented reason.
LUFS_TOLERANCE_APPROX_SR = 0.2


class _Probe:
    sha256 = "sha256:channel-domain-fixture"


def stereo_independent(sr: int, seconds: float = 20.0) -> np.ndarray:
    """Probe A: independent tones per channel, moderate level difference."""
    t = np.arange(int(seconds * sr)) / sr
    left = 0.35 * np.sin(2 * np.pi * 440 * t) * (0.55 + 0.45 * np.sin(2 * np.pi * 0.5 * t))
    right = 0.30 * np.sin(2 * np.pi * 880 * t)
    return np.stack([left, right], axis=1)


def stereo_imbalanced(sr: int, seconds: float = 20.0) -> np.ndarray:
    """Probe B: one loud channel, one 34 dB quieter — a downmix detector."""
    t = np.arange(int(seconds * sr)) / sr
    return np.stack(
        [0.50 * np.sin(2 * np.pi * 440 * t), 0.01 * np.sin(2 * np.pi * 880 * t)], axis=1
    )


PROBES = {"independent": stereo_independent, "imbalanced": stereo_imbalanced}


def _truth(x: np.ndarray) -> tuple[float, float]:
    peak = 20 * np.log10(float(np.max(np.abs(x))) + 1e-12)
    rms = 20 * np.log10(float(np.sqrt(np.mean(x ** 2))) + 1e-12)
    return peak, rms


def _mono_downmix(x: np.ndarray) -> np.ndarray:
    return x.mean(axis=1)


# ---------------------------------------------------------------------------
# A/B. Integrated loudness against an independent oracle
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("name", sorted(PROBES))
def test_stereo_loudness_matches_pyloudnorm(name):
    """A. Moodify agrees with pyloudnorm on stereo material."""
    sr = 48000
    x = PROBES[name](sr)
    ref = pyln.Meter(sr).integrated_loudness(x)
    ours = integrated_loudness_lufs(x, sr)
    assert abs(ours - ref) <= LUFS_TOLERANCE_STANDARD_SR, f"ours={ours} pyloudnorm={ref}"


@pytest.mark.parametrize("name", sorted(PROBES))
def test_channel_mean_aggregation_cannot_pass(name):
    """B. The old /N aggregation is ~3.01 dB low and must fail this bound."""
    sr = 48000
    x = PROBES[name](sr)
    ref = pyln.Meter(sr).integrated_loudness(x)
    ours = integrated_loudness_lufs(x, sr)

    assert abs(ours - ref) <= LUFS_TOLERANCE_STANDARD_SR
    # the defect signature would land here; it must be nowhere near it
    assert abs(ours - (ref - CHANNEL_MEAN_BIAS_DB)) > 1.0


def test_stereo_loudness_at_44100_within_documented_tolerance():
    """44.1 kHz reuses 48 kHz coefficients (documented approximation)."""
    sr = 44100
    for name, make in PROBES.items():
        x = make(sr)
        ref = pyln.Meter(sr).integrated_loudness(x)
        ours = integrated_loudness_lufs(x, sr)
        assert abs(ours - ref) <= LUFS_TOLERANCE_APPROX_SR, f"{name}: ours={ours} ref={ref}"


def test_mono_loudness_still_matches_oracle():
    """Regression guard: the mono path was already correct and stays correct."""
    sr = 48000
    t = np.arange(20 * sr) / sr
    mono = 0.5 * np.sin(2 * np.pi * 440 * t)
    ref = pyln.Meter(sr).integrated_loudness(mono)
    assert abs(integrated_loudness_lufs(mono, sr) - ref) <= LUFS_TOLERANCE_STANDARD_SR


# ---------------------------------------------------------------------------
# C. sample_peak_dbfs spans every channel
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("name", sorted(PROBES))
def test_sample_peak_uses_all_channels(name):
    sr = 48000
    x = PROBES[name](sr)
    peak_truth, _ = _truth(x)
    reported = compute_metrics(x, sr, _Probe())["sample_peak_dbfs"]["value"]
    assert reported == pytest.approx(peak_truth, abs=0.05)


def test_sample_peak_matches_the_louder_channel_not_the_downmix():
    """C. The imbalanced probe makes a downmix distinctly wrong."""
    sr = 48000
    x = stereo_imbalanced(sr)
    reported = compute_metrics(x, sr, _Probe())["sample_peak_dbfs"]["value"]

    louder = 20 * np.log10(0.50)
    downmix = 20 * np.log10(float(np.max(np.abs(_mono_downmix(x)))))

    assert reported == pytest.approx(louder, abs=0.05)
    assert abs(reported - downmix) > 5.0  # the defect landed ~6 dB away


def test_sample_peak_catches_a_clipped_silent_looking_channel():
    """A loud clipped channel behind a near-silent one must not be missed."""
    sr = 48000
    n = sr
    loud = np.where(np.arange(n) % 8 < 4, 1.0, -1.0)
    quiet = np.zeros(n)
    x = np.stack([quiet, loud], axis=1)
    reported = compute_metrics(x, sr, _Probe())["sample_peak_dbfs"]["value"]
    assert reported == pytest.approx(0.0, abs=0.01)


# ---------------------------------------------------------------------------
# D. rms_dbfs does not mono-collapse
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("name", sorted(PROBES))
def test_rms_is_total_energy_over_all_samples(name):
    sr = 48000
    x = PROBES[name](sr)
    _, rms_truth = _truth(x)
    reported = compute_metrics(x, sr, _Probe())["rms_dbfs"]["value"]
    assert reported == pytest.approx(rms_truth, abs=0.05)


def test_rms_is_not_the_mono_downmix_rms():
    """D. Assert the reported value is the multichannel one, not the downmix."""
    sr = 48000
    x = stereo_imbalanced(sr)
    reported = compute_metrics(x, sr, _Probe())["rms_dbfs"]["value"]
    downmix_rms = 20 * np.log10(float(np.sqrt(np.mean(_mono_downmix(x) ** 2))))

    assert reported == pytest.approx(_truth(x)[1], abs=0.05)
    assert abs(reported - downmix_rms) > 2.5  # defect landed ~3 dB away


# ---------------------------------------------------------------------------
# E. peak metrics share one signal domain
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("name", sorted(PROBES))
def test_true_peak_and_sample_peak_are_consistent(name):
    sr = 48000
    x = PROBES[name](sr)
    m = compute_metrics(x, sr, _Probe())
    sample_peak = m["sample_peak_dbfs"]["value"]
    true_peak = m["true_peak_dbfs"]["value"]

    # True peak may exceed the sample peak, but never falls below it.
    assert true_peak >= sample_peak - 0.05
    assert true_peak == pytest.approx(sample_peak, abs=0.5)


# ---------------------------------------------------------------------------
# F. The defect-induced crest false positive is gone
# ---------------------------------------------------------------------------

def test_crest_collapse_false_positive_is_resolved():
    """F. The acceptance finding must no longer fire on the imbalanced probe."""
    sr = 48000
    x = stereo_imbalanced(sr)
    metrics = compute_metrics(x, sr, _Probe())

    corrected = metrics["crest_factor_db"]["value"]
    assert corrected > 4.0

    flag_codes = {flag.code for flag in evaluate_risk_flags({}, {}, metrics)}
    assert "CREST_FACTOR_COLLAPSE" not in flag_codes


def test_old_downmix_crest_would_have_fired():
    """F. Reproduce the defect signature analytically, to prove the test bites.

    Measuring peak and RMS on a mono downmix gives ~3 dB of crest factor that
    the signal does not have, which is what tripped the 4.0 dB floor.
    """
    sr = 48000
    x = stereo_imbalanced(sr)
    down = _mono_downmix(x)
    defect_crest = 20 * np.log10(float(np.max(np.abs(down))) + 1e-12) - 20 * np.log10(
        float(np.sqrt(np.mean(down ** 2))) + 1e-12
    )
    assert defect_crest < 4.0  # would have fired
    assert compute_metrics(x, sr, _Probe())["crest_factor_db"]["value"] > 4.0  # now does not


def test_bundled_crest_matches_its_own_inputs():
    """crest_factor_db must equal sample_peak_dbfs - rms_dbfs exactly."""
    sr = 48000
    for make in PROBES.values():
        m = compute_metrics(make(sr), sr, _Probe())
        expected = m["sample_peak_dbfs"]["value"] - m["rms_dbfs"]["value"]
        assert m["crest_factor_db"]["value"] == pytest.approx(expected, abs=0.02)


def test_true_peak_unchanged_by_channel_domain_fix():
    """true_peak_dbfs was already per-channel; the fix must not move it."""
    sr = 48000
    x = stereo_imbalanced(sr)
    assert true_peak_db(x, sr) == pytest.approx(
        compute_metrics(x, sr, _Probe())["true_peak_dbfs"]["value"], abs=0.01
    )
