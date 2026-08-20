"""MAMSE-011 covariance/eigenspace configuration.

Versioned modeling choices: center/scale methods, covariance estimator
(OAS/empirical/fixed), winsorization, eigen floor, missingness gates,
eigengap tolerance. All choices are part of the model identity via
config_hash.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from typing import Any

OPERATOR_ID = "MAMSE-011"
ALGORITHM_VERSION = "mamse011-covariance-v0.1"
SCHEMA_VERSION = "mamse011-eigenspace-v0.1"
MANIFEST_SCHEMA_VERSION = "mamse-011-manifest-v1"


@dataclass(frozen=True)
class CovarianceConfig:
    center_method: str = "median"      # median | mean
    scale_method: str = "mad"          # mad | std
    estimator: str = "oas"             # oas | empirical | fixed_shrinkage
    shrinkage_alpha: float = 0.10       # only fixed_shrinkage
    winsor_z: float | None = 8.0
    eigen_floor: float = 1e-8
    min_complete_rows: int = 4
    max_missing_fraction: float = 0.35
    eigengap_relative_tol: float = 1e-3

    def validate(self) -> None:
        if self.center_method not in ("median", "mean"):
            raise ValueError("center_method must be median or mean")
        if self.scale_method not in ("mad", "std"):
            raise ValueError("scale_method must be mad or std")
        if self.estimator not in ("oas", "empirical", "fixed_shrinkage"):
            raise ValueError("estimator must be oas, empirical, or fixed_shrinkage")
        if not (0 <= self.shrinkage_alpha <= 1):
            raise ValueError("shrinkage_alpha must be in [0,1]")
        if self.eigen_floor <= 0 or self.min_complete_rows < 2:
            raise ValueError("invalid eigen floor / min rows")
        if not 0 <= self.max_missing_fraction < 1.0:
            raise ValueError("max_missing_fraction must be in [0,1)")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @property
    def config_hash(self) -> str:
        payload = json.dumps(self.to_dict(), sort_keys=True, separators=(",", ":"), ensure_ascii=True)
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()
