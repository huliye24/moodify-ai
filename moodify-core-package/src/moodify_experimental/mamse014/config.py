"""MAMSE-014 masking-inference geometry (Chapter II §9).

Two sounds can both be physically present while one becomes perceptually
difficult to hear. Masking inference is probabilistic: this module models
spectral competition with a simple ERB-spaced spreading rule. It never
claims that masked equals absent — it only estimates how much energy is
likely unavailable under competition, and reports INSUFFICIENT when
evidence is weak.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass

import numpy as np

OPERATOR_ID = "MAMSE-014"
OPERATOR_VERSION = "mamse-014-v0.1"
GEOMETRY_ID = "erb-spread-masking-v0.1"
FEATURE_SCHEMA_VERSION = "mamse-014-masking-features-v1"
EVIDENCE_SCHEMA_VERSION = "mamse-014-evidence-v1"
MANIFEST_SCHEMA_VERSION = "mamse-014-manifest-v1"

# Glasberg & Moore (1990) ERB bandwidth — same formula as MAMSE-013,
# re-declared here so this module stays self-contained.
def erb_bandwidth_hz(f_hz: np.ndarray | float) -> np.ndarray | float:
    arr = np.asarray(f_hz, dtype=np.float64)
    return 24.7 * (4.37 * arr / 1000.0 + 1.0)


def hz_to_erb(f_hz: np.ndarray | float) -> np.ndarray | float:
    arr = np.asarray(f_hz, dtype=np.float64)
    return 21.4 * np.log10(1.0 + 4.37 * arr / 1000.0)


def erb_to_hz(erb: np.ndarray | float) -> np.ndarray | float:
    arr = np.asarray(erb, dtype=np.float64)
    return (10.0 ** (arr / 21.4) - 1.0) * 1000.0 / 4.37


@dataclass(frozen=True)
class MaskConfig:
    operator_id: str = OPERATOR_ID
    operator_version: str = OPERATOR_VERSION
    geometry_id: str = GEOMETRY_ID
    fmin_hz: float = 20.0
    fmax_hz: float = 20000.0
    n_channels: int = 41  # 1 ERB step, same grid as MAMSE-013
    hop_length: int = 512
    window_samples: int = 2048
    # Masking spreading model (v0.1 heuristic, deterministic):
    slope_db_per_erb: float = 15.0   # how fast masker influence decays per ERB
    offset_db: float = 6.0           # masker-level surplus required before masking
    soft_range_db: float = 6.0       # soft audibility ramp width
    # Absence vs masked: channels more than this below the loudest channel
    # carry no content and must not count as masked (silence is not masking).
    content_floor_db: float = 60.0
    # Event gates (v0.1): events fire on the fraction of channels whose
    # audibility collapsed below 0.5, not on masked spectral mass — mass
    # masking is dominated by the loud masker itself and stays small.
    event_ratio_threshold: float = 0.10
    event_min_frames: int = 5

    def __post_init__(self) -> None:
        if not 0.0 < self.fmin_hz < self.fmax_hz:
            raise ValueError("require 0 < fmin < fmax")
        if self.n_channels < 2 or self.slope_db_per_erb <= 0 or self.offset_db <= 0:
            raise ValueError("invalid masking model parameters")
        if not 0.0 < self.event_ratio_threshold <= 1.0 or self.event_min_frames < 1:
            raise ValueError("invalid event gate parameters")

    def center_frequencies(self) -> np.ndarray:
        erbs = hz_to_erb(self.fmin_hz) + np.arange(self.n_channels) * (
            hz_to_erb(self.fmax_hz) - hz_to_erb(self.fmin_hz)
        ) / (self.n_channels - 1)
        return erb_to_hz(erbs)

    def to_dict(self) -> dict:
        return asdict(self)

    def sha256(self) -> str:
        payload = json.dumps(self.to_dict(), sort_keys=True, ensure_ascii=True).encode("utf-8")
        return hashlib.sha256(payload).hexdigest()


DEFAULT_CONFIG = MaskConfig()
