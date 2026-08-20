"""MAMSE-009 RPCA configuration.

Versioned IALM-PCP solver choices. All choices are part of the model
identity via config_hash.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from typing import Any

OPERATOR_ID = "MAMSE-009"
ALGORITHM_VERSION = "mamse009-rpca-ialm-v0.1"
MANIFEST_SCHEMA_VERSION = "mamse-009-manifest-v1"


@dataclass(frozen=True)
class RPCAConfig:
    lam: float | None = None
    tol: float = 1e-7
    max_iter: int = 1000
    rho: float = 1.5
    mu_factor: float = 1.25
    max_mu_factor: float = 1e7

    def validate(self) -> None:
        if self.tol <= 0 or self.max_iter < 1:
            raise ValueError("invalid tolerance/iterations")
        if self.rho < 1.0 or self.mu_factor <= 0 or self.max_mu_factor < 1.0:
            raise ValueError("invalid solver parameters")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @property
    def config_hash(self) -> str:
        payload = json.dumps(self.to_dict(), sort_keys=True, separators=(",", ":"), ensure_ascii=True)
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()
