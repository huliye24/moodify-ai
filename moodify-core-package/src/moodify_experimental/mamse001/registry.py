"""MAMSE-001 spectral resolution registry (R-axis).

Orthogonal to the canonical S0/S1/S2/S3 semantic temporal scales
(moodify.auditory.representation.scales): R selects the spectral analysis
kernel, S selects the semantic aggregation window. Nothing here may alter
the canonical scale registry.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass

OPERATOR_ID = "MAMSE-001"
OPERATOR_VERSION = "0.1.0"
REGISTRY_VERSION = "mamse-001-resolutions-v1"
FEATURE_SCHEMA_VERSION = "mamse-001-sketch-features-v1"
EVIDENCE_SCHEMA_VERSION = "mamse-001-evidence-v1"


@dataclass(frozen=True)
class ResolutionSpec:
    resolution_id: str
    name: str
    n_fft: int
    hop_length: int
    window: str = "hann"
    purpose: str = ""

    def __post_init__(self) -> None:
        if not self.resolution_id:
            raise ValueError("resolution_id must be non-empty")
        if self.n_fft <= 0 or self.n_fft & (self.n_fft - 1):
            raise ValueError("n_fft must be a positive power of two")
        if self.hop_length <= 0 or self.hop_length > self.n_fft:
            raise ValueError("hop_length must be in (0, n_fft]")
        if self.window != "hann":
            raise ValueError("MAMSE-001 v0.1 only accepts Hann")

    def window_ms(self, sample_rate: int) -> float:
        return 1000.0 * self.n_fft / sample_rate

    def hop_ms(self, sample_rate: int) -> float:
        return 1000.0 * self.hop_length / sample_rate

    def bin_hz(self, sample_rate: int) -> float:
        return sample_rate / self.n_fft


RESOLUTIONS: tuple[ResolutionSpec, ...] = (
    ResolutionSpec("R0", "TRANSIENT", 512, 128,
                   purpose="transient/click/clipping-edge observation at high time resolution"),
    ResolutionSpec("R1", "LOCAL", 2048, 512,
                   purpose="local spectral state; adjacent to the current scan baseline"),
    ResolutionSpec("R2", "HARMONIC", 8192, 2048,
                   purpose="harmonic structure, narrowband peaks, pitch neighborhoods"),
    ResolutionSpec("R3", "MACRO", 32768, 8192,
                   purpose="low-frequency detail, close-frequency resolution, sustained resonance"),
)


def get_resolution(resolution_id: str) -> ResolutionSpec:
    for spec in RESOLUTIONS:
        if spec.resolution_id == resolution_id:
            return spec
    raise ValueError(f"unknown resolution: {resolution_id}")


def registry_hash() -> str:
    """Deterministic hash of the resolution registry (canonical JSON)."""
    payload = json.dumps(
        [asdict(spec) for spec in RESOLUTIONS],
        ensure_ascii=False, sort_keys=True, separators=(",", ":"),
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()
