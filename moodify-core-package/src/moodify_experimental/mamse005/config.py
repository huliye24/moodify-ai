"""MAMSE-005 cepstral structure configuration.

Versioned modeling choices: frame/window, magnitude log floor, lifter cutoff
(source-filter split), F0 search range and acceptance, resonance candidate
limits, and the RMS energy gate below which frames are UNAVAILABLE. All
choices are part of the result identity via config_hash.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass

OPERATOR_ID = "mamse005-cepstrum"
OPERATOR_VERSION = "mamse005-cepstrum-v0.1"
CONFIG_VERSION = "mamse005-cepstrum-v0.1"
MANIFEST_SCHEMA_VERSION = "mamse-005-manifest-v1"


@dataclass(frozen=True)
class CepstrumConfig:
    n_fft: int = 4096
    hop_length: int = 1024
    window: str = "hann"
    magnitude_floor: float = 1e-10
    lifter_cutoff_ms: float = 2.5
    f0_min_hz: float = 60.0
    f0_max_hz: float = 500.0
    min_rms_dbfs: float = -55.0
    min_periodicity_score: float = 0.85
    max_resonance_hz: float = 6000.0
    resonance_prominence_db: float = 1.5
    max_resonance_candidates: int = 8

    def validate(self) -> None:
        if self.n_fft < 512 or self.n_fft & (self.n_fft - 1):
            raise ValueError("n_fft must be a power of two >= 512")
        if self.hop_length <= 0 or self.hop_length > self.n_fft:
            raise ValueError("invalid hop_length")
        if not (0 < self.lifter_cutoff_ms < 20):
            raise ValueError("invalid lifter cutoff")
        if not (0 < self.f0_min_hz < self.f0_max_hz):
            raise ValueError("invalid f0 range")

    def to_dict(self) -> dict:
        return asdict(self)

    @property
    def config_hash(self) -> str:
        payload = json.dumps(self.to_dict(), sort_keys=True, separators=(",", ":"), ensure_ascii=True)
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()
