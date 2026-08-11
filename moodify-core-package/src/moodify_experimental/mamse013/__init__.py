"""MAMSE-013 — ERB / gammatone auditory filterbank (experimental).

Conditional experimental operator: Glasberg-Moore ERB-spaced gammatone
filterbank, the perceptual-organization view complementary to the
canonical linear-Hz path and the log-frequency path (MAMSE-002).
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
    ERBConfig,
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
from .gammatone import ErbObservation, compute_er_b_observation
from .policy import PolicySuggestion, need_auditory_filterbank
from .sketch import FEATURE_AUTHORITY, FEATURE_NAMES, ErbSketch, build_er_b_sketch

__all__ = [
    "OPERATOR_ID",
    "OPERATOR_VERSION",
    "GEOMETRY_ID",
    "FEATURE_SCHEMA_VERSION",
    "EVIDENCE_SCHEMA_VERSION",
    "MANIFEST_SCHEMA_VERSION",
    "ERBConfig",
    "DEFAULT_CONFIG",
    "erb_bandwidth_hz",
    "hz_to_erb",
    "erb_to_hz",
    "ErbObservation",
    "compute_er_b_observation",
    "FEATURE_NAMES",
    "FEATURE_AUTHORITY",
    "ErbSketch",
    "build_er_b_sketch",
    "build_manifest",
    "geometry_evidence",
    "observation_evidence",
    "save_case",
    "load_case",
    "source_sha256",
    "PolicySuggestion",
    "need_auditory_filterbank",
]
