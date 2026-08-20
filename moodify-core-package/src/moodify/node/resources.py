"""Dependency-free resource guard for a 2C2G Linux node."""

from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ResourceSnapshot:
    available_memory_mb: float
    free_disk_gb: float


def _available_memory_mb() -> float:
    meminfo = Path("/proc/meminfo")
    if not meminfo.exists():
        return float("inf")
    values: dict[str, int] = {}
    for line in meminfo.read_text(encoding="utf-8").splitlines():
        key, raw = line.split(":", 1)
        value = raw.strip().split()[0]
        if value.isdigit():
            values[key] = int(value)
    kb = values.get("MemAvailable", values.get("MemFree", 0))
    return kb / 1024.0


def snapshot(path: Path) -> ResourceSnapshot:
    path.mkdir(parents=True, exist_ok=True)
    disk = shutil.disk_usage(path)
    return ResourceSnapshot(
        available_memory_mb=_available_memory_mb(),
        free_disk_gb=disk.free / (1024**3),
    )


def safe_to_start(path: Path, min_memory_mb: int, min_disk_gb: float) -> tuple[bool, ResourceSnapshot, str]:
    snap = snapshot(path)
    if snap.available_memory_mb < min_memory_mb:
        return False, snap, f"available memory {snap.available_memory_mb:.0f} MiB < {min_memory_mb} MiB"
    if snap.free_disk_gb < min_disk_gb:
        return False, snap, f"free disk {snap.free_disk_gb:.2f} GiB < {min_disk_gb:.2f} GiB"
    return True, snap, "OK"
