"""Measurement → MRS feature adapter + quality scoring.

The engine normalizes raw acoustic measurements into the
``MRSFeatures`` contract (five factors in [0, 1]) and delegates scoring
to the legacy ``RuleBasedMRSScorer`` (``moodify.mrs.scoring``) — the
transparent research baseline. No second scoring implementation.

Normalization curves are explicit and auditable:
    loudness  — distance of integrated LUFS from the -14 LUFS streaming target
    dynamic   — short-window dynamic spread + crest factor
    spectral  — band balance deviation from a smooth spectral envelope
    spatial   — L/R correlation mapped to a width optimum (~0.5)
    artifact  — clipping / near-clipping risk from sample peak
"""

from __future__ import annotations

from typing import Any

from engine._compat import ensure_core_package

ensure_core_package()

from moodify.mrs.metrics import MRSFeatures                      # noqa: E402
from moodify.mrs.scoring import RuleBasedMRSScorer, MRSScore     # noqa: E402

from engine.acoustic_analysis.analyzer import AcousticProfile

_SCORER = RuleBasedMRSScorer()

_STREAMING_TARGET_LUFS = -14.0
_LOUDNESS_OK_LU = 1.0          # within 1 LU of target  -> 1.0
_LOUDNESS_MAX_LU = 12.0       # 12 LU or more off      -> 0.0


def build_features(profile: AcousticProfile) -> MRSFeatures:
    """Map an AcousticProfile to the normalized MRS feature contract."""
    return MRSFeatures(
        loudness=_loudness_factor(profile),
        dynamic=_dynamic_factor(profile),
        spectral=_spectral_factor(profile),
        spatial=_spatial_factor(profile),
        artifact=_artifact_factor(profile),
    )


def score_quality(profile: AcousticProfile) -> dict[str, Any]:
    """Score one profile with the rule-based MRS baseline."""
    features = build_features(profile)
    result: MRSScore = _SCORER.calculate(features)
    return result.to_dict()


# ── normalization factors ────────────────────────────────────


def _clamp01(x: float) -> float:
    return max(0.0, min(1.0, x))


def _loudness_factor(profile: AcousticProfile) -> float:
    if profile.integrated_lufs is None:
        return 0.5  # insufficient duration → neutral, not fabricated
    deviation = abs(profile.integrated_lufs - _STREAMING_TARGET_LUFS)
    if deviation <= _LOUDNESS_OK_LU:
        return 1.0
    return _clamp01(1.0 - (deviation - _LOUDNESS_OK_LU)
                    / (_LOUDNESS_MAX_LU - _LOUDNESS_OK_LU))


def _dynamic_factor(profile: AcousticProfile) -> float:
    # Healthy short-window spread: >= 12 dB → 1.0; <= 2 dB → 0.0
    spread = _clamp01((profile.dynamic_range_db - 2.0) / 10.0)
    # Healthy crest: >= 10 dB → 1.0; <= 3 dB → 0.0
    crest = _clamp01((profile.crest_factor - 3.0) / 7.0)
    return 0.6 * spread + 0.4 * crest


def _spectral_factor(profile: AcousticProfile) -> float:
    """Penalize band-energy imbalance (each band far from its neighbors)."""
    order = ["sub", "bass", "low_mid", "mid", "presence", "air"]
    values = [profile.spectrum.get(b, -60.0) for b in order]
    roughness = sum(abs(values[i + 1] - values[i]) for i in range(len(values) - 1))
    # Typical well-balanced masters show ~25–35 dB of monotonic rolloff.
    if roughness <= 30.0:
        return 1.0
    return _clamp01(1.0 - (roughness - 30.0) / 40.0)


def _spatial_factor(profile: AcousticProfile) -> float:
    if profile.correlation_lr is None:
        return 0.5
    # Optimum around 0.5 correlation; penalize both near-mono and near-out-of-phase.
    return _clamp01(1.0 - abs(profile.correlation_lr - 0.5) / 0.6)


def _artifact_factor(profile: AcousticProfile) -> float:
    # -6 dBFS or below headroom → 1.0; >= -0.1 dBFS (clipped) → 0.0
    return _clamp01((profile.peak_db + 0.1) / 5.9)
