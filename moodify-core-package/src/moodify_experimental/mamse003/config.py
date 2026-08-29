"""MAMSE-003 texture operator configuration.

Scattering-inspired prototype: Morlet-like analytic carrier bank + envelope
decimation + low-frequency modulation bank. NOT numerically equivalent to
Kymatio/Mallat scattering; that equivalence would be assessed at R4+.
"""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import asdict, dataclass

OPERATOR_ID = "mamse003-texture"
OPERATOR_VERSION = "0.1"
CONFIG_VERSION = "mamse003-texture-v0.1"
FEATURE_SCHEMA_VERSION = "mamse-003-texture-features-v1"
MANIFEST_SCHEMA_VERSION = "mamse-003-manifest-v1"


@dataclass(frozen=True)
class TextureConfig:
    operator_id: str = OPERATOR_ID
    operator_version: str = OPERATOR_VERSION
    analysis_sample_rate: int = 24000
    carrier_f_min: float = 80.0
    carrier_f_max: float = 8000.0
    carrier_bands_per_octave: int = 4
    carrier_q: float = 6.0
    envelope_sample_rate: int = 200
    modulation_rates_hz: tuple[float, ...] = (1.0, 2.0, 4.0, 8.0, 16.0)
    modulation_q: float = 2.0
    frame_ms: int = 500
    hop_ms: int = 250
    eps: float = 1e-12

    def validate(self) -> None:
        if self.analysis_sample_rate <= 0:
            raise ValueError("analysis_sample_rate must be positive")
        if not (0 < self.carrier_f_min < self.carrier_f_max < self.analysis_sample_rate / 2):
            raise ValueError("carrier frequency range must be inside Nyquist")
        if self.carrier_bands_per_octave <= 0 or self.carrier_q <= 0:
            raise ValueError("carrier bank parameters must be positive")
        if self.modulation_rates_hz and self.envelope_sample_rate <= 2 * max(self.modulation_rates_hz):
            raise ValueError("envelope_sample_rate must exceed modulation Nyquist")
        if self.frame_ms <= 0 or self.hop_ms <= 0 or self.hop_ms > self.frame_ms:
            raise ValueError("invalid frame/hop")

    @property
    def carrier_centers_hz(self) -> tuple[float, ...]:
        n = int(math.floor(self.carrier_bands_per_octave * math.log2(self.carrier_f_max / self.carrier_f_min))) + 1
        centers = tuple(self.carrier_f_min * 2 ** (k / self.carrier_bands_per_octave) for k in range(n))
        return tuple(f for f in centers if f <= self.carrier_f_max * (1 + 1e-12))

    def to_dict(self) -> dict:
        d = asdict(self)
        d["modulation_rates_hz"] = list(self.modulation_rates_hz)
        d["carrier_centers_hz"] = list(self.carrier_centers_hz)
        return d

    @property
    def config_hash(self) -> str:
        payload = json.dumps(self.to_dict(), sort_keys=True, separators=(",", ":"), ensure_ascii=True)
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()
