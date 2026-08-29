"""Run-scoped immutable registry for shared computed intermediates."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np


@dataclass(frozen=True)
class FeatureRecord:
    value: Any
    producer_node: str
    version: str
    dependencies: tuple[str, ...]
    bytes_estimate: int


class FeatureBus:
    def __init__(self) -> None:
        self._records: dict[str, FeatureRecord] = {}

    def publish(self, key: str, value: Any, producer_node: str, version: str,
                dependencies: tuple[str, ...] = ()) -> None:
        if key in self._records:
            raise ValueError(f"feature already published: {key}")
        self._records[key] = FeatureRecord(
            value=value, producer_node=producer_node, version=version,
            dependencies=dependencies, bytes_estimate=_size(value),
        )

    def get(self, key: str) -> Any:
        return self._records[key].value

    def record(self, key: str) -> FeatureRecord:
        return self._records[key]

    def release(self, key: str) -> None:
        self._records.pop(key, None)

    @property
    def bytes_estimate(self) -> int:
        return sum(record.bytes_estimate for record in self._records.values())


def _size(value: Any) -> int:
    if isinstance(value, np.ndarray):
        return int(value.nbytes)
    if isinstance(value, (bytes, bytearray)):
        return len(value)
    return 0
