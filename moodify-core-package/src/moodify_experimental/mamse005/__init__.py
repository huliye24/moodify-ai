"""MAMSE-005 — cepstral structure / source-filter decomposition (experimental).

Real cepstrum -> low/high quefrency liftering -> spectral envelope + fine
structure; cepstral periodicity (F0 candidate) and resonance candidates.
All outputs are EXPERIMENTAL descriptors: f0 is not ground-truth pitch,
resonance candidates are not formants, and silence/short inputs are
UNAVAILABLE rather than fabricated.
"""

from .cepstrum import (
    cepstral_decompose_frame,
    frame_signal,
    low_quefrency_lifter,
    real_cepstrum_frame,
    reconstruct_logmag_from_cepstrum,
)
from .config import (
    CONFIG_VERSION,
    MANIFEST_SCHEMA_VERSION,
    OPERATOR_ID,
    OPERATOR_VERSION,
    CepstrumConfig,
)
from .envelope import resonance_candidates, roughness_measure
from .evidence import build_manifest, load_result, save_result
from .periodicity import estimate_periodicity, rms_dbfs
from .sketch import analyze_cepstral_structure, logical_json

__all__ = [
    "OPERATOR_ID",
    "OPERATOR_VERSION",
    "CONFIG_VERSION",
    "MANIFEST_SCHEMA_VERSION",
    "CepstrumConfig",
    "analyze_cepstral_structure",
    "frame_signal",
    "real_cepstrum_frame",
    "low_quefrency_lifter",
    "reconstruct_logmag_from_cepstrum",
    "cepstral_decompose_frame",
    "estimate_periodicity",
    "rms_dbfs",
    "resonance_candidates",
    "roughness_measure",
    "build_manifest",
    "save_result",
    "load_result",
    "logical_json",
]
