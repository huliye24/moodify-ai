"""MAMSE-016 pitch-evidence geometry (Chapter II §10A).

Pitch is valuable as an organizing cue, never as a binary fact. A useful
pitch state contains candidate frequencies, confidence, voicing
evidence, harmonic consistency and time continuity. In polyphonic music
multiple concurrent pitch structures exist and a single F0 estimate may
be actively misleading — v0.1 keeps up to three candidates per frame.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass

OPERATOR_ID = "MAMSE-016"
OPERATOR_VERSION = "mamse-016-v0.1"
GEOMETRY_ID = "yin-lite-multicandidate-v0.1"
FEATURE_SCHEMA_VERSION = "mamse-016-pitch-features-v1"
EVIDENCE_SCHEMA_VERSION = "mamse-016-evidence-v1"
MANIFEST_SCHEMA_VERSION = "mamse-016-manifest-v1"


@dataclass(frozen=True)
class PitchConfig:
    operator_id: str = OPERATOR_ID
    operator_version: str = OPERATOR_VERSION
    geometry_id: str = GEOMETRY_ID
    hop_length: int = 512
    frame_samples: int = 2048
    fmin_hz: float = 60.0
    fmax_hz: float = 1600.0
    cmndf_threshold: float = 0.2  # YIN: below this = candidate
    max_candidates: int = 3
    # Pitch-run event gates:
    event_min_frames: int = 8
    event_stability_cents: float = 100.0  # candidates within 1 semitone

    def __post_init__(self) -> None:
        if not 0.0 < self.fmin_hz < self.fmax_hz:
            raise ValueError("require 0 < fmin < fmax")
        if self.hop_length <= 0 or self.frame_samples < self.hop_length:
            raise ValueError("invalid hop/window configuration")
        if not 0.0 < self.cmndf_threshold < 1.0 or self.max_candidates < 1:
            raise ValueError("invalid YIN parameters")

    def lag_range(self, sr: int) -> tuple[int, int]:
        lo = int(sr / self.fmax_hz)
        hi = int(sr / self.fmin_hz)
        return max(lo, 1), min(hi, self.frame_samples - 1)

    def to_dict(self) -> dict:
        return asdict(self)

    def sha256(self) -> str:
        payload = json.dumps(self.to_dict(), sort_keys=True, ensure_ascii=True).encode("utf-8")
        return hashlib.sha256(payload).hexdigest()


DEFAULT_CONFIG = PitchConfig()
