"""Fixed-width pitch sketch from a pitch observation.

All values are ESTIMATOR: dominant F0 is not perceived pitch, harmonic
support is not harmony understanding, and candidates are not notes.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .config import PitchConfig
from .pitch import PitchObservation

TRACK_FEATURE_NAMES: tuple[str, ...] = (
    "voicing_fraction",
    "harmonic_consistency_mean",
    "dominant_frequency_hz",
    "mean_confidence_voiced",
    "n_stable_pitch_runs",
    "ambiguity_index",
)

FRAME_FEATURE_NAMES: tuple[str, ...] = (
    "frame_voiced",
    "frame_dominant_f0",
    "frame_confidence",
)

FEATURE_NAMES: tuple[str, ...] = TRACK_FEATURE_NAMES + FRAME_FEATURE_NAMES

FEATURE_AUTHORITY: dict[str, str] = {
    "voicing_fraction": "ESTIMATOR — voicing evidence, not a binary pitch claim",
    "harmonic_consistency_mean": "ESTIMATOR — harmonic support, not harmony",
    "dominant_frequency_hz": "ESTIMATOR — not perceived pitch",
    "mean_confidence_voiced": "ESTIMATOR",
    "n_stable_pitch_runs": "DESCRIPTOR",
    "ambiguity_index": "ESTIMATOR — polyphonic ambiguity, not uncertainty of the track",
    "frame_voiced": "ESTIMATOR",
    "frame_dominant_f0": "ESTIMATOR — not perceived pitch",
    "frame_confidence": "ESTIMATOR",
}


@dataclass
class PitchSketch:
    feature_names: tuple[str, ...]
    times_s: np.ndarray
    values: np.ndarray  # frames x features; NaN = unavailable
    status: str
    geometry_id: str
    config_hash: str
    track_features: dict[str, float]

    def to_dict(self) -> dict:
        return {
            "feature_schema": "mamse-016-pitch-features-v1",
            "status": self.status,
            "geometry_id": self.geometry_id,
            "config_hash": self.config_hash,
            "n_frames": int(self.times_s.size),
            "track_features": self.track_features,
        }


def build_pitch_sketch(obs: PitchObservation, config: PitchConfig) -> PitchSketch:
    """Decimate a pitch observation into a fixed-width sketch."""
    voiced_conf = obs.confidence[obs.voiced]
    dom_voiced = obs.dominant_f0[obs.voiced]
    dominant_hz = float(np.nanmedian(dom_voiced)) if dom_voiced.size else float("nan")
    ambiguity = 0.0
    if np.any(obs.voiced):
        gaps = []
        for cands in obs.candidates:
            if len(cands) >= 2:
                top = sorted(cands, key=lambda c: -c.confidence)[:2]
                gaps.append(abs(_cents(top[0].frequency_hz, top[1].frequency_hz)))
        ambiguity = float(np.mean(gaps)) if gaps else 0.0

    track = {
        "voicing_fraction": obs.voicing_fraction,
        "harmonic_consistency_mean": obs.harmonic_consistency_mean,
        "dominant_frequency_hz": dominant_hz,
        "mean_confidence_voiced": float(np.mean(voiced_conf)) if voiced_conf.size else 0.0,
        "n_stable_pitch_runs": float(len(obs.events)),
        "ambiguity_index": ambiguity,
    }

    values = np.column_stack([
        obs.voiced.astype(np.float64),
        obs.dominant_f0,
        obs.confidence,
    ])
    values[~np.isfinite(values)] = np.nan

    return PitchSketch(
        feature_names=FEATURE_NAMES,
        times_s=obs.times_s,
        values=values,
        status=obs.status,
        geometry_id=config.geometry_id,
        config_hash=config.sha256(),
        track_features=track,
    )


def _cents(a: float, b: float) -> float:
    return 1200.0 * np.log2(a / b)
