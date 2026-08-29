"""MAMSE-015 — soft auditory objects (experimental, Chapter II §10).

Conditional experimental operator: time-frequency regions organized as
soft objects carrying probability profiles over acoustic-role hypotheses.
Off by default (see policy.py). Not part of the canonical production
loop; no compatibility guarantees.
"""

from .config import (
    DEFAULT_CONFIG,
    EVIDENCE_SCHEMA_VERSION,
    FEATURE_SCHEMA_VERSION,
    GEOMETRY_ID,
    HYPOTHESES,
    MANIFEST_SCHEMA_VERSION,
    OPERATOR_ID,
    OPERATOR_VERSION,
    SoftObjectConfig,
)
from .evidence import (
    build_manifest,
    geometry_evidence,
    load_case,
    observation_evidence,
    save_case,
    source_sha256,
)
from .objects import SoftObject, SoftObjectObservation, compute_soft_object_observation
from .policy import PolicySuggestion, need_soft_objects
from .sketch import FEATURE_AUTHORITY, FEATURE_NAMES, SoftObjectSketch, build_soft_object_sketch

__all__ = [
    "OPERATOR_ID",
    "OPERATOR_VERSION",
    "GEOMETRY_ID",
    "HYPOTHESES",
    "FEATURE_SCHEMA_VERSION",
    "EVIDENCE_SCHEMA_VERSION",
    "MANIFEST_SCHEMA_VERSION",
    "SoftObjectConfig",
    "DEFAULT_CONFIG",
    "SoftObject",
    "SoftObjectObservation",
    "compute_soft_object_observation",
    "FEATURE_NAMES",
    "FEATURE_AUTHORITY",
    "SoftObjectSketch",
    "build_soft_object_sketch",
    "build_manifest",
    "geometry_evidence",
    "observation_evidence",
    "save_case",
    "load_case",
    "source_sha256",
    "PolicySuggestion",
    "need_soft_objects",
]
