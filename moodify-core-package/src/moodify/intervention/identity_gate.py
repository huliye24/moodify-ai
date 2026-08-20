"""Identity gate for preserve-identity intervention (MFY_PRESERVE_IDENTITY_INTERVENTION_001).

Compares the candidate render against the input with simple, explainable
feature differences. The gate is a machine check: it never approves *listening*
quality — it only verifies that the candidate has not drifted away from the
input identity. Uncertainty (conflicting evidence, borderline differences)
escalates to HUMAN_REQUIRED / INCONCLUSIVE instead of guessing.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

# Tolerances (conservative; tuned on synthetic fixtures, not arbitrary)
RMS_DIFF_DB_MAX = 0.5
SPECTRAL_CENTROID_DIFF_MAX = 0.01  # 1% relative
BAND_DIFF_DB_MAX = 1.5  # per 4-band energy, dB
CROSS_CORR_MAX = 0.995  # below this the render is far from input


@dataclass(frozen=True)
class IdentityVerdict:
    passed: bool
    confidence: str  # FULL | PARTIAL | INCONCLUSIVE
    details: dict[str, float]
    decision: str  # PASS | FAIL | HUMAN_REQUIRED | INCONCLUSIVE


def _rms_db(x: np.ndarray) -> float:
    return float(20.0 * np.log10(np.sqrt(np.mean(x**2)) + 1e-12))


def _spectral_centroid(x: np.ndarray, sr: int) -> float:
    spec = np.abs(np.fft.rfft(x, axis=0))
    freqs = np.fft.rfftfreq(x.shape[0], 1.0 / sr)
    # DC bin excluded: a constant offset (or a DC-rich flat clip segment) would
    # otherwise dominate the centroid even though it is not musical content.
    keep = freqs > 0.0
    spec, freqs = spec[keep], freqs[keep]
    total = spec.sum()
    if total == 0:
        return 0.0
    # elementwise product; never broadcast into a matrix
    return float(np.sum(freqs * spec) / total)


def _band_energies_db(x: np.ndarray, sr: int) -> list[float]:
    spec = np.abs(np.fft.rfft(x, axis=0)) ** 2
    freqs = np.fft.rfftfreq(x.shape[0], 1.0 / sr)
    out = []
    for lo, hi in ((20, 200), (200, 2000), (2000, 8000), (8000, 20000)):
        band = (freqs >= lo) & (freqs <= hi)
        power = spec[band].mean() if band.any() else 1e-12
        out.append(float(20.0 * np.log10(power + 1e-12)))
    return out


class IdentityGate:
    """Pure, deterministic identity comparison (no hidden state)."""

    def verify(self, input_audio: np.ndarray, candidate: np.ndarray, sr: int) -> IdentityVerdict:
        if input_audio.shape != candidate.shape:
            return IdentityVerdict(False, "FULL", {"shape_match": 0.0}, "FAIL")
        if input_audio.size == 0 or not np.isfinite(candidate).all():
            return IdentityVerdict(False, "FULL", {"finite": 0.0}, "FAIL")

        rms_diff = _rms_db(candidate) - _rms_db(input_audio)
        cent_in = _spectral_centroid(input_audio, sr)
        cent_out = _spectral_centroid(candidate, sr)
        centroid_rel = abs(cent_out - cent_in) / max(cent_in, 1e-6)
        band_in = _band_energies_db(input_audio, sr)
        band_out = _band_energies_db(candidate, sr)
        band_diffs = [abs(a - b) for a, b in zip(band_out, band_in)]

        # cross-correlation at zero lag on mean-centered mono downmix:
        # DC is not musical content, so it must not dominate the correlation.
        def mono(x: np.ndarray) -> np.ndarray:
            return (x.mean(axis=1) if x.ndim == 2 else x) - np.mean(x)

        a, b = mono(input_audio), mono(candidate)
        denom = np.linalg.norm(a) * np.linalg.norm(b)
        corr = float(np.dot(a, b) / denom) if denom > 0 else 1.0

        # Spectral centroid is recorded for reference but does NOT gate:
        # it is overly sensitive to broadband leakage from local flat
        # (clipped) segments — a legitimate clip repair would trip it.
        passed = (
            abs(rms_diff) <= RMS_DIFF_DB_MAX
            and max(band_diffs) <= BAND_DIFF_DB_MAX
            and corr >= CROSS_CORR_MAX
        )

        details = {
            "rms_diff_db": round(rms_diff, 4),
            "centroid_rel_diff": round(centroid_rel, 6),
            "max_band_diff_db": round(max(band_diffs), 4),
            "cross_corr": round(corr, 6),
        }

        if passed:
            return IdentityVerdict(True, "FULL", details, "PASS")
        # Conflicting/borderline evidence -> escalate, never guess.
        return IdentityVerdict(False, "PARTIAL", details, "HUMAN_REQUIRED")
