"""MAMSE-015 soft-auditory-object geometry (Chapter II §10).

Hearing organizes mixtures into streams and events without perfect
separation. A soft object is a time-frequency region carrying a
probability profile over acoustic-role hypotheses (TONAL_CORE,
NOISE_TEXTURE, PERCUSSIVE, UNRESOLVED). Probabilities are independent
soft indicators derived from deterministic acoustic cues — they are
ESTIMATORs, never source identities (vocal/bass/etc. are out of v0.1
scope). UNRESOLVED is the honest output when evidence is weak.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass

OPERATOR_ID = "MAMSE-015"
OPERATOR_VERSION = "mamse-015-v0.1"
GEOMETRY_ID = "soft-role-cues-v0.1"
FEATURE_SCHEMA_VERSION = "mamse-015-soft-object-features-v1"
EVIDENCE_SCHEMA_VERSION = "mamse-015-evidence-v1"
MANIFEST_SCHEMA_VERSION = "mamse-015-manifest-v1"

HYPOTHESES: tuple[str, ...] = ("TONAL_CORE", "NOISE_TEXTURE", "PERCUSSIVE", "UNRESOLVED")


@dataclass(frozen=True)
class SoftObjectConfig:
    operator_id: str = OPERATOR_ID
    operator_version: str = OPERATOR_VERSION
    geometry_id: str = GEOMETRY_ID
    hop_length: int = 512
    n_fft: int = 2048
    # Sigmoid gates per cue (deterministic, no learned parameters):
    cue_sharpness: float = 8.0
    tonal_midpoint: float = 0.35   # on (1 - spectral flatness)
    texture_midpoint: float = 0.35  # on spectral flatness
    percussive_sharpness: float = 10.0
    percussive_midpoint: float = 0.5  # on normalized spectral flux
    label_confidence_gate: float = 0.55  # below -> UNRESOLVED
    min_region_frames: int = 2
    max_objects: int = 32

    def __post_init__(self) -> None:
        if self.hop_length <= 0 or self.n_fft < self.hop_length:
            raise ValueError("invalid hop/window configuration")
        if not 0.0 < self.label_confidence_gate <= 1.0:
            raise ValueError("label gate must be in (0, 1]")
        if self.min_region_frames < 1 or self.max_objects < 1:
            raise ValueError("region/object limits must be positive")

    def to_dict(self) -> dict:
        return asdict(self)

    def sha256(self) -> str:
        payload = json.dumps(self.to_dict(), sort_keys=True, ensure_ascii=True).encode("utf-8")
        return hashlib.sha256(payload).hexdigest()


DEFAULT_CONFIG = SoftObjectConfig()
