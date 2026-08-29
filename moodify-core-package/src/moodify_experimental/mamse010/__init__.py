"""MAMSE-010 — auditory tensor representation (experimental).

Versioned tensor *views* over auditory data: named axes, explicit validity
masks, interval-overlap alignment, homogeneous channel-spectral view for
multilinear research (HOSVD/Tucker). Does NOT replace the canonical
AuditoryRepresentation; dense materialization is guarded.
"""

from .contracts import (
    EPS,
    OPERATOR_ID,
    SCHEMA_VERSION,
    AuditoryTensorBundle,
    AxisSpec,
    TensorContractError,
    TensorField,
    build_scale_feature_tensor,
    interval_overlap_weighted,
    regular_time_grid,
)
from .evidence import MANIFEST_SCHEMA_VERSION, load_bundle, save_bundle
from .multilinear import (
    TuckerModel,
    fold,
    hosvd,
    mode_dot,
    mode_singular_values,
    project_tucker,
    relative_residual_by_time,
    unfold,
)
from .resources import (
    MaterializationGuardError,
    estimate_dense_bytes,
    guard_materialization,
    iter_tiles,
)
from .views import build_channel_spectral_tensor, log_frequency_axis

__all__ = [
    "OPERATOR_ID",
    "SCHEMA_VERSION",
    "MANIFEST_SCHEMA_VERSION",
    "EPS",
    "AxisSpec",
    "TensorField",
    "AuditoryTensorBundle",
    "TensorContractError",
    "interval_overlap_weighted",
    "regular_time_grid",
    "build_scale_feature_tensor",
    "build_channel_spectral_tensor",
    "log_frequency_axis",
    "unfold",
    "fold",
    "mode_dot",
    "hosvd",
    "TuckerModel",
    "project_tucker",
    "relative_residual_by_time",
    "mode_singular_values",
    "estimate_dense_bytes",
    "iter_tiles",
    "guard_materialization",
    "MaterializationGuardError",
    "save_bundle",
    "load_bundle",
]
