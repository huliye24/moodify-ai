"""Auditory sensor contracts (Ocean Listen absorption, DSK-MFY-OCEAN-ABSORPTION-001).

A sensor produces raw auditory evidence during the ANALYZING stage. It is
never an authority: it must not approve artistic decisions, invoke an
intervention engine, or move a case to TECHNICALLY_VALIDATED.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol


@dataclass(frozen=True)
class AudioSource:
    source_path: Path
    sha256: str


@dataclass(frozen=True)
class AnalysisSpecification:
    spec_hash: str
    profile: str = "shallow"
    mode: str = "auto"
    lyrics_mode: str = "disabled"


@dataclass(frozen=True)
class RunIdentity:
    run_id: str
    upstream_commit: str
    configuration_hash: str


@dataclass(frozen=True)
class EvidenceArtifact:
    artifact_type: str
    path: str
    artifact_sha256: str
    case_id: str = ""
    run_id: str = ""
    source_sha256: str = ""
    specification_hash: str = ""
    upstream_commit: str = ""
    configuration_hash: str = ""
    created_at: str = ""
    producer: str = ""


class AuditorySensorPort(Protocol):
    def analyze(
        self,
        source: AudioSource,
        specification: AnalysisSpecification,
        run_identity: RunIdentity,
    ) -> EvidenceArtifact:
        ...
