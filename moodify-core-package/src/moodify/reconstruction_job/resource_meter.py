"""Resource accounting and budgets for reconstruction jobs (MFY-CR-P08).

Windows has no getrusage RSS; peak_memory uses tracemalloc when enabled and is
honestly reported as 0.0 otherwise. Budgets are conservative: exceeding them
defers rather than retrying blindly.
"""

from __future__ import annotations

import time
from dataclasses import dataclass

from .contract import ResourceUsage


class ResourceMeter:
    def __init__(self) -> None:
        self._wall_start = time.perf_counter()
        self._cpu_start = time.process_time()
        self._peak_memory_mb = 0.0

    def note_memory(self) -> None:
        try:
            import tracemalloc
            if tracemalloc.is_tracing():
                current, peak = tracemalloc.get_traced_memory()
                self._peak_memory_mb = max(self._peak_memory_mb, peak / (1024 * 1024))
        except Exception:
            pass

    def snapshot(self, **extra: object) -> ResourceUsage:
        wall = time.perf_counter() - self._wall_start
        cpu = time.process_time() - self._cpu_start
        return ResourceUsage(
            cpu_time_s=cpu,
            wall_time_s=wall,
            peak_memory_mb=self._peak_memory_mb,
            disk_temp_usage_mb=float(extra.get("disk_temp_usage_mb", 0.0)),
            external_api_usage=int(extra.get("external_api_usage", 0)),
            candidate_count=int(extra.get("candidate_count", 0)),
            stem_count=int(extra.get("stem_count", 0)),
        )


@dataclass(frozen=True)
class ResourceBudget:
    max_wall_time_s: float = 1800.0
    max_candidates: int = 4
    max_stems: int = 0

    def exceeded(self, usage: ResourceUsage, candidate_count: int = 0) -> str | None:
        """Return the budget code that failed, or None when within budget."""
        if usage.wall_time_s > self.max_wall_time_s:
            return "WALL_TIME_EXCEEDED"
        if (candidate_count or usage.candidate_count) > self.max_candidates:
            return "CANDIDATE_COUNT_EXCEEDED"
        if (usage.stem_count or 0) > self.max_stems:
            return "STEM_COUNT_EXCEEDED"
        return None
