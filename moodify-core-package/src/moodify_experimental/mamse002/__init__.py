"""MAMSE-002 — Constant-Q / log-frequency hearing (experimental).

Conditional experimental operator: log-frequency frequency geometry
(24 bins/octave, C1 fmin, 216 bins) complementary to the canonical
linear-Hz path. Off by default (see policy.py). Not part of the canonical
production loop; no compatibility guarantees.
"""

from .config import (
    CQTConfig,
    DEFAULT_CONFIG,
    EVIDENCE_SCHEMA_VERSION,
    FEATURE_SCHEMA_VERSION,
    GEOMETRY_ID,
    MANIFEST_SCHEMA_VERSION,
    OPERATOR_ID,
    OPERATOR_VERSION,
    cents_from_nearest_equal_temperament,
    hz_to_midi,
    midi_to_hz,
)
from .cqt import (
    CQTObservation,
    compute_cqt_observation,
    dominant_frequency_from_mean,
    local_peaks_from_mean,
)
from .sketch import FEATURE_AUTHORITY, FEATURE_NAMES, LogFrequencySketch, build_log_frequency_sketch
from .evidence import (
    build_manifest,
    geometry_evidence,
    load_case,
    observation_evidence,
    save_case,
    source_sha256,
)
from .policy import PolicySuggestion, need_log_frequency
from .events import low_register_adjacent_tonal_events

__all__ = [
    "OPERATOR_ID",
    "OPERATOR_VERSION",
    "GEOMETRY_ID",
    "FEATURE_SCHEMA_VERSION",
    "EVIDENCE_SCHEMA_VERSION",
    "MANIFEST_SCHEMA_VERSION",
    "CQTConfig",
    "DEFAULT_CONFIG",
    "hz_to_midi",
    "midi_to_hz",
    "cents_from_nearest_equal_temperament",
    "CQTObservation",
    "compute_cqt_observation",
    "dominant_frequency_from_mean",
    "local_peaks_from_mean",
    "FEATURE_NAMES",
    "FEATURE_AUTHORITY",
    "LogFrequencySketch",
    "build_log_frequency_sketch",
    "build_manifest",
    "geometry_evidence",
    "observation_evidence",
    "load_case",
    "save_case",
    "source_sha256",
    "PolicySuggestion",
    "need_log_frequency",
    "low_register_adjacent_tonal_events",
]
