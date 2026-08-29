"""MAMSE-006 modulation spectrum configuration.

Versioned modeling choices: audio STFT frame, log-frequency axis
(bands_per_octave), modulation window/hop, log floor, rate/scale search
bounds, energy gate. All choices are part of the result identity via
profile_hash.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass

OPERATOR_ID = "MAMSE-006"
OPERATOR_VERSION = "0.1.0"
CONFIG_VERSION = "mamse006-modulation-v0.1"
MANIFEST_SCHEMA_VERSION = "mamse-006-manifest-v1"


@dataclass(frozen=True)
class ModulationConfig:
    sample_rate: int = 48_000
    audio_n_fft: int = 2048
    audio_hop: int = 256
    fmin_hz: float = 55.0
    fmax_hz: float = 16_000.0
    bands_per_octave: int = 12
    modulation_window_seconds: float = 4.0
    modulation_hop_seconds: float = 2.0
    log_floor_db: float = -80.0
    temporal_min_hz: float = 0.25
    temporal_max_hz: float = 40.0
    spectral_max_cpo: float = 4.0
    min_audio_seconds: float = 1.5
    low_energy_rms_dbfs: float = -70.0

    def validate(self) -> None:
        if self.sample_rate <= 0:
            raise ValueError("sample_rate must be positive")
        if self.audio_n_fft < 256 or self.audio_n_fft % 2:
            raise ValueError("audio_n_fft must be even and >=256")
        if not (0 < self.audio_hop <= self.audio_n_fft):
            raise ValueError("audio_hop out of range")
        if not (0 < self.fmin_hz < self.fmax_hz < self.sample_rate / 2):
            raise ValueError("invalid frequency range")
        if self.bands_per_octave < 4:
            raise ValueError("bands_per_octave too small")
        if self.modulation_window_seconds <= 0 or self.modulation_hop_seconds <= 0:
            raise ValueError("modulation window/hop must be positive")
        frame_rate = self.sample_rate / self.audio_hop
        if self.temporal_max_hz >= frame_rate / 2:
            raise ValueError("temporal_max_hz exceeds modulation Nyquist")
        if self.spectral_max_cpo >= self.bands_per_octave / 2:
            raise ValueError("spectral_max_cpo exceeds log-frequency Nyquist")

    @property
    def frame_rate_hz(self) -> float:
        return self.sample_rate / self.audio_hop

    def to_dict(self) -> dict:
        return asdict(self)

    @property
    def profile_hash(self) -> str:
        payload = json.dumps(asdict(self), sort_keys=True, separators=(",", ":")).encode()
        return hashlib.sha256(payload).hexdigest()
