"""MAMSE-001 — multi-resolution time-frequency auditory representation (experimental).

Experimental research operator: adds a spectral-resolution axis R0/R1/R2/R3
orthogonal to the canonical S0/S1/S2/S3 semantic temporal scales. Not part of
the canonical production loop; no compatibility guarantees (see
docs/LEGACY_AND_EXPERIMENTAL_POLICY.md).
"""

from .registry import (
    OPERATOR_ID,
    OPERATOR_VERSION,
    REGISTRY_VERSION,
    RESOLUTIONS,
    ResolutionSpec,
    get_resolution,
    registry_hash,
)
from .sketch import FEATURE_NAMES, compute_multiresolution_sketch, compute_resolution_sketch
from .evidence import (
    build_cross_resolution_evidence,
    build_manifest,
    load_case,
    run_case,
    save_case,
)
from .events import narrowband_events

__all__ = [
    "OPERATOR_ID",
    "OPERATOR_VERSION",
    "REGISTRY_VERSION",
    "RESOLUTIONS",
    "ResolutionSpec",
    "get_resolution",
    "registry_hash",
    "FEATURE_NAMES",
    "compute_multiresolution_sketch",
    "compute_resolution_sketch",
    "build_cross_resolution_evidence",
    "build_manifest",
    "load_case",
    "run_case",
    "save_case",
    "narrowband_events",
]
