"""MAMSE-006 — modulation spectrum & spectro-temporal motion (experimental).

Log-frequency auditory surface -> 1D temporal + 2D spectro-temporal
modulation FFT -> rate/scale/orientation/ridge descriptors. All outputs are
EXPERIMENTAL descriptors: modulation peaks are not BPM, orientation is not
physical source motion, ridges are candidates, and unavailable inputs are
reported as such.
"""

from .config import (
    CONFIG_VERSION,
    MANIFEST_SCHEMA_VERSION,
    OPERATOR_ID,
    OPERATOR_VERSION,
    ModulationConfig,
)
from .evidence import build_manifest, load_evidence, save_evidence
from .features import summarize_modulation
from .modulation import analyze_surface, normalized_entropy, normalize_distribution
from .operator import run_mamse006, source_sha256
from .surface import compute_log_frequency_surface, log_frequency_axis, rms_dbfs
from .synthetic import am_signal, harmonic_broadband, ripple_surface, static_ripple_surface

__all__ = [
    "OPERATOR_ID",
    "OPERATOR_VERSION",
    "CONFIG_VERSION",
    "MANIFEST_SCHEMA_VERSION",
    "ModulationConfig",
    "run_mamse006",
    "source_sha256",
    "compute_log_frequency_surface",
    "log_frequency_axis",
    "rms_dbfs",
    "analyze_surface",
    "normalize_distribution",
    "normalized_entropy",
    "summarize_modulation",
    "build_manifest",
    "save_evidence",
    "load_evidence",
    "am_signal",
    "harmonic_broadband",
    "ripple_surface",
    "static_ripple_surface",
]
