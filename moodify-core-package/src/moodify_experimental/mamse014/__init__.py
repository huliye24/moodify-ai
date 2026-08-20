"""MAMSE-014 — masking inference (experimental, Chapter II §9).

Conditional experimental operator: probabilistic spectral-competition
masking inference over ERB channels. Off by default (see policy.py).
Not part of the canonical production loop; no compatibility guarantees.
"""

from .config import (
    DEFAULT_CONFIG,
    EVIDENCE_SCHEMA_VERSION,
    FEATURE_SCHEMA_VERSION,
    GEOMETRY_ID,
    MANIFEST_SCHEMA_VERSION,
    OPERATOR_ID,
    OPERATOR_VERSION,
    MaskConfig,
    erb_bandwidth_hz,
    erb_to_hz,
    hz_to_erb,
)
from .evidence import (
    build_manifest,
    geometry_evidence,
    load_case,
    observation_evidence,
    save_case,
    source_sha256,
)
from .masking import MaskingEvent, MaskingObservation, compute_masking_observation
from .policy import PolicySuggestion, need_masking_inference
from .sketch import FEATURE_AUTHORITY, FEATURE_NAMES, MaskingSketch, build_masking_sketch

__all__ = [
    "OPERATOR_ID",
    "OPERATOR_VERSION",
    "GEOMETRY_ID",
    "FEATURE_SCHEMA_VERSION",
    "EVIDENCE_SCHEMA_VERSION",
    "MANIFEST_SCHEMA_VERSION",
    "MaskConfig",
    "DEFAULT_CONFIG",
    "erb_bandwidth_hz",
    "hz_to_erb",
    "erb_to_hz",
    "MaskingObservation",
    "MaskingEvent",
    "compute_masking_observation",
    "FEATURE_NAMES",
    "FEATURE_AUTHORITY",
    "MaskingSketch",
    "build_masking_sketch",
    "build_manifest",
    "geometry_evidence",
    "observation_evidence",
    "save_case",
    "load_case",
    "source_sha256",
    "PolicySuggestion",
    "need_masking_inference",
]
