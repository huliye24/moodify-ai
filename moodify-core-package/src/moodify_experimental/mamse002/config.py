"""MAMSE-002 log-frequency geometry (T2).

geometry_id = log2-equal-temperament-24bpo-v0.1: fmin C1, 24 bins/octave
(2 bins per semitone), 9 octaves, 216 bins. Independent, versioned, and
hashable; it does not alter canonical BANDS and chroma/MIDI are not musical
authority.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass

import numpy as np

OPERATOR_ID = "MAMSE-002"
OPERATOR_VERSION = "mamse-002-v0.1"
GEOMETRY_ID = "log2-equal-temperament-24bpo-v0.1"
FEATURE_SCHEMA_VERSION = "mamse-002-logfreq-features-v1"
EVIDENCE_SCHEMA_VERSION = "mamse-002-evidence-v1"
MANIFEST_SCHEMA_VERSION = "mamse-002-manifest-v1"


@dataclass(frozen=True)
class CQTConfig:
    operator_id: str = OPERATOR_ID
    operator_version: str = OPERATOR_VERSION
    geometry_id: str = GEOMETRY_ID
    fmin_hz: float = 32.70319566257483  # C1
    bins_per_octave: int = 24
    n_octaves: int = 9
    hop_length: int = 512
    filter_scale: float = 1.0
    window: str = "hann"
    sparsity: float = 0.01

    @property
    def n_bins(self) -> int:
        return self.bins_per_octave * self.n_octaves

    @property
    def q_factor(self) -> float:
        return self.filter_scale / (2 ** (1 / self.bins_per_octave) - 1)

    def frequencies(self) -> np.ndarray:
        k = np.arange(self.n_bins, dtype=np.float64)
        return self.fmin_hz * (2.0 ** (k / self.bins_per_octave))

    def nominal_window_samples(self, sr: int) -> np.ndarray:
        return np.ceil(self.q_factor * sr / self.frequencies()).astype(np.int64)

    def to_dict(self) -> dict:
        d = asdict(self)
        d["n_bins"] = self.n_bins
        d["q_factor"] = self.q_factor
        return d

    def sha256(self) -> str:
        payload = json.dumps(self.to_dict(), sort_keys=True, ensure_ascii=True).encode("utf-8")
        return hashlib.sha256(payload).hexdigest()


DEFAULT_CONFIG = CQTConfig()


def hz_to_midi(f_hz: np.ndarray | float) -> np.ndarray | float:
    arr = np.asarray(f_hz, dtype=np.float64)
    out = 69.0 + 12.0 * np.log2(np.maximum(arr, 1e-12) / 440.0)
    return float(out) if np.ndim(f_hz) == 0 else out


def midi_to_hz(midi: np.ndarray | float) -> np.ndarray | float:
    arr = np.asarray(midi, dtype=np.float64)
    out = 440.0 * 2.0 ** ((arr - 69.0) / 12.0)
    return float(out) if np.ndim(midi) == 0 else out


def cents_from_nearest_equal_temperament(f_hz: float) -> float:
    midi = hz_to_midi(float(f_hz))
    nearest = round(float(midi))
    return 100.0 * (float(midi) - nearest)
