"""Observable counters for local execution."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field


@dataclass
class ExecutionDiagnostics:
    cache_hits: int = 0
    cache_misses: int = 0
    cache_invalidations: int = 0
    cache_corruptions: int = 0
    nodes_executed: int = 0
    nodes_reused: int = 0
    decoded_source_count: int = 0
    transform_compute_count: dict[str, int] = field(default_factory=dict)
    bytes_read: int = 0
    bytes_written: int = 0

    def transform_computed(self, name: str) -> None:
        self.transform_compute_count[name] = self.transform_compute_count.get(name, 0) + 1

    def to_dict(self) -> dict:
        return asdict(self)
