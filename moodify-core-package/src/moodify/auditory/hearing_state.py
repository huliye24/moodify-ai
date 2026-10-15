"""Provider-neutral inputs to Moodify Judge.

This module deliberately contains no model integration.  It defines the seam at
which replaceable acoustic, stem, semantic, and music-representation providers
contribute observations without acquiring judgment authority.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Literal


ProviderStatus = Literal["AVAILABLE", "UNAVAILABLE", "FAILED", "NOT_RUN"]
EvidenceKind = Literal["MEASURED", "MODEL_INFERRED", "REFERENCE_COMPARISON"]


@dataclass(frozen=True)
class ProviderProvenance:
    provider_id: str
    provider_version: str
    model_id: str | None
    model_revision: str | None
    code_license: str
    weights_license: str | None
    commercial_use: Literal["ALLOWED", "RESTRICTED", "UNKNOWN"]
    source_uri: str


@dataclass(frozen=True)
class HearingObservation:
    namespace: str
    value: Any
    evidence_kind: EvidenceKind
    confidence: float | None
    provenance: ProviderProvenance
    evidence_refs: tuple[str, ...] = ()
    limitations: tuple[str, ...] = ()
    theory_refs: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.namespace or self.namespace.strip() != self.namespace:
            raise ValueError("namespace must be a non-empty canonical name")
        if self.confidence is not None and not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0 and 1")


@dataclass(frozen=True)
class ProviderRun:
    capability: Literal["ACOUSTIC", "STEM", "SEMANTIC", "MUSIC_REPRESENTATION", "AUDIO_REASONING", "QUALITY_METRIC"]
    status: ProviderStatus
    provenance: ProviderProvenance
    observations: tuple[HearingObservation, ...] = ()
    error_code: str | None = None

    def __post_init__(self) -> None:
        if self.status == "AVAILABLE" and not self.observations:
            raise ValueError("AVAILABLE provider run must contain observations")
        if self.status != "AVAILABLE" and self.observations:
            raise ValueError("non-available provider run cannot contain observations")


@dataclass(frozen=True)
class HearingState:
    """Experimental HEAR v0 envelope; it is evidence, never a Judge verdict."""

    hearing_state_version: str
    source_sha256: str
    auditory_representation_ref: str
    provider_runs: tuple[ProviderRun, ...]
    missing_capabilities: tuple[str, ...] = ()
    uncertainty: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.hearing_state_version != "hear-v0.experimental":
            raise ValueError("unsupported hearing state version")
        if len(self.source_sha256) != 64:
            raise ValueError("source_sha256 must be a 64-character SHA-256 digest")
        seen: set[tuple[str, str]] = set()
        for run in self.provider_runs:
            key = (run.capability, run.provenance.provider_id)
            if key in seen:
                raise ValueError(f"duplicate provider run: {key}")
            seen.add(key)

    @property
    def judge_ready(self) -> bool:
        """True only when the caller declared no required HEAR capability missing.

        Readiness means the evidence envelope is complete for a caller-defined
        task.  It does not mean that any perceptual or production claim is true.
        """
        return not self.missing_capabilities and all(
            run.status == "AVAILABLE" for run in self.provider_runs
        )

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["judge_ready"] = self.judge_ready
        data["authority"] = "EVIDENCE_ONLY"
        return data
