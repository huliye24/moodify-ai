"""MAMSE-016 — pitch / harmonicity evidence (experimental, Chapter II §10A).

Conditional experimental operator: multi-candidate F0 with confidence,
voicing evidence, harmonic support and stable-pitch-run events.
Off by default (see policy.py). Not part of the canonical production
loop; no compatibility guarantees.
"""

from .config import (
    DEFAULT_CONFIG,
    EVIDENCE_SCHEMA_VERSION,
    FEATURE_SCHEMA_VERSION,
    GEOMETRY_ID,
    MANIFEST_SCHEMA_VERSION,
    OPERATOR_ID,
    OPERATOR_VERSION,
    PitchConfig,
)
from .evidence import (
    build_manifest,
    geometry_evidence,
    load_case,
    observation_evidence,
    save_case,
    source_sha256,
)
from .pitch import PitchCandidate, PitchObservation, PitchRunEvent, compute_pitch_observation
from .policy import PolicySuggestion, need_pitch_evidence
from .sketch import FEATURE_AUTHORITY, FEATURE_NAMES, PitchSketch, build_pitch_sketch

__all__ = [
    "OPERATOR_ID",
    "OPERATOR_VERSION",
    "GEOMETRY_ID",
    "FEATURE_SCHEMA_VERSION",
    "EVIDENCE_SCHEMA_VERSION",
    "MANIFEST_SCHEMA_VERSION",
    "PitchConfig",
    "DEFAULT_CONFIG",
    "PitchCandidate",
    "PitchObservation",
    "PitchRunEvent",
    "compute_pitch_observation",
    "FEATURE_NAMES",
    "FEATURE_AUTHORITY",
    "PitchSketch",
    "build_pitch_sketch",
    "build_manifest",
    "geometry_evidence",
    "observation_evidence",
    "save_case",
    "load_case",
    "source_sha256",
    "PolicySuggestion",
    "need_pitch_evidence",
]
