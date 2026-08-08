"""Backend-neutral processing contracts."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Protocol


@dataclass(frozen=True)
class EngineProbe:
    engine_id: str
    available: bool
    version: str = ""
    executable: str = ""
    capabilities: tuple[str, ...] = ()
    error: str = ""


@dataclass(frozen=True)
class ProcessingRequest:
    source: Path
    output: Path
    params: dict[str, Any] = field(default_factory=dict)
    reference: Path | None = None


@dataclass(frozen=True)
class ProcessingResult:
    engine_id: str
    output: Path
    command: tuple[str, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)


class ProcessingPort(Protocol):
    engine_id: str

    def probe(self) -> EngineProbe: ...
    def execute(self, request: ProcessingRequest) -> ProcessingResult: ...
