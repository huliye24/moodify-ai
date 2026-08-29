"""MAMSE-004 phase geometry configuration.

Versioned parameter set for the phase operator: FFT/hop/window, frequency
range, magnitude reliability floor, unwrap axis, stereo cross-spectrum sign
convention, GCC-PHAT search range. All conventions are part of the result
identity via config_hash.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass

OPERATOR_ID = "mamse004-phase-geometry"
OPERATOR_VERSION = "mamse004-phase-geometry-v0.1"
CONFIG_VERSION = "mamse004-phase-geometry-v0.1"
MANIFEST_SCHEMA_VERSION = "mamse-004-manifest-v1"


@dataclass(frozen=True)
class PhaseGeometryConfig:
    n_fft: int = 8192
    hop_length: int = 2048
    window: str = "hann"
    f_min_hz: float = 80.0
    f_max_hz: float = 18000.0
    magnitude_floor_db: float = -45.0
    unwrap_axis: str = "frequency"
    stereo_cross_convention: str = "R*conj(L)"
    gcc_max_delay_ms: float = 5.0

    def validate(self) -> None:
        if self.n_fft < 16 or (self.n_fft & (self.n_fft - 1)) != 0:
            raise ValueError("n_fft must be a power of two >= 16")
        if not (0 < self.hop_length <= self.n_fft):
            raise ValueError("hop_length must be in (0, n_fft]")
        if not (0 < self.f_min_hz < self.f_max_hz):
            raise ValueError("frequency range must be positive and ordered")
        if self.magnitude_floor_db >= 0:
            raise ValueError("magnitude_floor_db must be negative (relative dB)")

    def to_dict(self) -> dict:
        return asdict(self)

    @property
    def config_hash(self) -> str:
        payload = json.dumps(self.to_dict(), sort_keys=True, separators=(",", ":"), ensure_ascii=True)
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()
