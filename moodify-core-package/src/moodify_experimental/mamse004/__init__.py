"""MAMSE-004 — phase geometry & group delay (experimental).

Mono: unwrap -> group delay (seconds, rad/s axis) -> phase curvature.
Stereo: cross-spectrum IPD (R*conj(L)) -> interchannel delay + GCC-PHAT
cross-check. All outputs are EXPERIMENTAL descriptors; nonzero group delay
is never automatically a defect; low-magnitude bins are masked, not faked.
"""

from .config import (
    CONFIG_VERSION,
    MANIFEST_SCHEMA_VERSION,
    OPERATOR_ID,
    OPERATOR_VERSION,
    PhaseGeometryConfig,
)
from .evidence import build_manifest, load_result, save_result
from .phase import (
    analyze_mono_phase,
    complex_stft,
    group_delay_from_phase,
    group_delay_from_response,
    magnitude_mask,
    phase_curvature_from_group_delay,
    unwrap_phase,
)
from .sketch import analyze_phase_geometry, logical_json
from .stereo import analyze_stereo_phase, gcc_phat_delay

__all__ = [
    "OPERATOR_ID",
    "OPERATOR_VERSION",
    "CONFIG_VERSION",
    "MANIFEST_SCHEMA_VERSION",
    "PhaseGeometryConfig",
    "analyze_phase_geometry",
    "analyze_mono_phase",
    "analyze_stereo_phase",
    "group_delay_from_phase",
    "group_delay_from_response",
    "phase_curvature_from_group_delay",
    "magnitude_mask",
    "unwrap_phase",
    "complex_stft",
    "gcc_phat_delay",
    "build_manifest",
    "save_result",
    "load_result",
    "logical_json",
]
