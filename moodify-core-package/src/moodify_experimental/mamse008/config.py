"""MAMSE-008 NMF configuration.

Versioned factorization choices: rank, beta-divergence, iterations,
regularization, deterministic init (NNDSVD/random), W normalization. All
choices are part of the basis identity via config_hash.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from typing import Any

OPERATOR_ID = "MAMSE-008"
ALGORITHM_VERSION = "mamse008-nmf-v0.1"
MANIFEST_SCHEMA_VERSION = "mamse-008-manifest-v1"


@dataclass(frozen=True)
class NMFConfig:
    rank: int = 3
    beta: float = 2.0
    max_iter: int = 500
    tol: float = 1e-6
    l1_h: float = 0.0
    l1_w: float = 0.0
    seed: int = 0
    init: str = "nndsvd"
    normalize_w: bool = True

    def validate(self) -> None:
        if self.rank < 1:
            raise ValueError("rank must be >= 1")
        if self.beta not in (0.0, 1.0, 2.0):
            raise ValueError("v0.1 supports beta in {0, 1, 2}")
        if self.max_iter < 1 or self.tol <= 0:
            raise ValueError("invalid iteration/tolerance")
        if self.l1_h < 0 or self.l1_w < 0:
            raise ValueError("regularization must be nonnegative")
        if self.init not in ("nndsvd", "random"):
            raise ValueError("init must be 'nndsvd' or 'random'")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @property
    def config_hash(self) -> str:
        payload = json.dumps(self.to_dict(), sort_keys=True, separators=(",", ":"), ensure_ascii=True)
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()
