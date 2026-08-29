"""MAMSE-013 auditory filterbank geometry (Chapter II §4).

Perceptual frequency organization via Glasberg-Moore ERB spacing.
Human-inspired, not adopted by ideology: it coexists with the canonical
linear-Hz path (MAMSE-001) and log-frequency path (MAMSE-002) as a third
parallel view. All formulas are versioned and hashable.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass

import numpy as np

OPERATOR_ID = "MAMSE-013"
OPERATOR_VERSION = "mamse-013-v0.1"
GEOMETRY_ID = "glasberg-moore-erb-1erbstep-v0.1"
FEATURE_SCHEMA_VERSION = "mamse-013-erb-features-v1"
EVIDENCE_SCHEMA_VERSION = "mamse-013-evidence-v1"
MANIFEST_SCHEMA_VERSION = "mamse-013-manifest-v1"

# Glasberg & Moore (1990): ERB bandwidth of the human auditory filter.
def erb_bandwidth_hz(f_hz: np.ndarray | float) -> np.ndarray | float:
    arr = np.asarray(f_hz, dtype=np.float64)
    return 24.7 * (4.37 * arr / 1000.0 + 1.0)


# ERB rate (spacing) — Slaney-style inverse pair.
def hz_to_erb(f_hz: np.ndarray | float) -> np.ndarray | float:
    arr = np.asarray(f_hz, dtype=np.float64)
    return 21.4 * np.log10(1.0 + 4.37 * arr / 1000.0)


def erb_to_hz(erb: np.ndarray | float) -> np.ndarray | float:
    arr = np.asarray(erb, dtype=np.float64)
    return (10.0 ** (arr / 21.4) - 1.0) * 1000.0 / 4.37


@dataclass(frozen=True)
class ERBConfig:
    operator_id: str = OPERATOR_ID
    operator_version: str = OPERATOR_VERSION
    geometry_id: str = GEOMETRY_ID
    fmin_hz: float = 20.0
    fmax_hz: float = 20000.0
    channels_per_erb: float = 1.0
    gamma_order: int = 4
    bandwidth_scale: float = 1.019  # Patterson & Holdsworth constant
    hop_length: int = 512
    window: str = "hann"
    window_samples: int = 1024
    max_filter_length_s: float = 0.5  # cap for the lowest channel's IR

    def __post_init__(self) -> None:
        if not 0.0 < self.fmin_hz < self.fmax_hz:
            raise ValueError("require 0 < fmin < fmax")
        if self.channels_per_erb <= 0 or self.gamma_order < 1:
            raise ValueError("channels_per_erb and gamma_order must be positive")
        if self.bandwidth_scale <= 0:
            raise ValueError("bandwidth_scale must be positive")
        if self.hop_length <= 0 or self.window_samples < self.hop_length:
            raise ValueError("invalid hop/window configuration")

    @property
    def n_channels(self) -> int:
        span = hz_to_erb(self.fmax_hz) - hz_to_erb(self.fmin_hz)
        return int(np.ceil(span * self.channels_per_erb))

    def center_frequencies(self) -> np.ndarray:
        erbs = hz_to_erb(self.fmin_hz) + np.arange(self.n_channels) / self.channels_per_erb
        return erb_to_hz(erbs)

    def to_dict(self) -> dict:
        d = asdict(self)
        d["n_channels"] = self.n_channels
        return d

    def sha256(self) -> str:
        payload = json.dumps(self.to_dict(), sort_keys=True, ensure_ascii=True).encode("utf-8")
        return hashlib.sha256(payload).hexdigest()


DEFAULT_CONFIG = ERBConfig()
