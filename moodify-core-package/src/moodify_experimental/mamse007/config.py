"""MAMSE-007 PCA/SVD configuration.

Versioned preprocessing choices: scaling policy, missing-feature threshold,
minimum scale, fit mode (CASE_LOCAL / CORPUS_FROZEN), imputation policy.
All choices are part of the basis identity via config_hash.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass

OPERATOR_ID = "MAMSE-007"
OPERATOR_VERSION = "0.1.0"
CONFIG_VERSION = "mamse007-pca-v0.1"
BASIS_VERSION = "mamse007-pca-v0.1"
MANIFEST_SCHEMA_VERSION = "mamse-007-manifest-v1"


@dataclass(frozen=True)
class PCAConfig:
    n_components: int | None = None
    scaling: str = "robust"  # robust | zscore
    max_missing_fraction: float = 0.20
    min_scale: float = 1e-10
    mode: str = "CASE_LOCAL"  # CASE_LOCAL | CORPUS_FROZEN
    impute: str = "median"     # v0.1 only

    def validate(self) -> None:
        if self.n_components is not None and self.n_components < 1:
            raise ValueError("n_components must be >= 1")
        if self.scaling not in {"robust", "zscore"}:
            raise ValueError("scaling must be robust or zscore")
        if not 0.0 <= self.max_missing_fraction < 1.0:
            raise ValueError("max_missing_fraction must be in [0, 1)")
        if self.mode not in {"CASE_LOCAL", "CORPUS_FROZEN"}:
            raise ValueError("unsupported mode")
        if self.impute != "median":
            raise ValueError("v0.1 supports median imputation only")

    def to_dict(self) -> dict:
        return asdict(self)

    @property
    def config_hash(self) -> str:
        payload = json.dumps(self.to_dict(), sort_keys=True, separators=(",", ":"), ensure_ascii=True)
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()
