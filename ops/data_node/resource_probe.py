#!/usr/bin/env python3
"""Append a lightweight resource snapshot for the 2C2G Moodify node."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def meminfo() -> dict[str, float]:
    raw: dict[str, int] = {}
    path = Path("/proc/meminfo")
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            key, value = line.split(":", 1)
            token = value.strip().split()[0]
            if token.isdigit():
                raw[key] = int(token)  # KiB
    total = raw.get("MemTotal", 0) / 1024
    available = raw.get("MemAvailable", raw.get("MemFree", 0)) / 1024
    swap_total = raw.get("SwapTotal", 0) / 1024
    swap_free = raw.get("SwapFree", 0) / 1024
    return {
        "memory_total_mib": round(total, 2),
        "memory_available_mib": round(available, 2),
        "swap_total_mib": round(swap_total, 2),
        "swap_used_mib": round(max(0.0, swap_total - swap_free), 2),
    }


def service_state(name: str) -> str:
    try:
        p = subprocess.run(
            ["systemctl", "is-active", name],
            capture_output=True,
            text=True,
            timeout=5,
        )
        return (p.stdout or p.stderr).strip() or f"exit-{p.returncode}"
    except Exception as exc:
        return f"unknown:{type(exc).__name__}"


def snapshot(data_path: Path, worker_service: str, api_service: str) -> dict:
    data_path.mkdir(parents=True, exist_ok=True)
    disk = shutil.disk_usage(data_path)
    load1, load5, load15 = os.getloadavg() if hasattr(os, "getloadavg") else (0.0, 0.0, 0.0)
    return {
        "timestamp": utc_now(),
        **meminfo(),
        "disk_free_gib": round(disk.free / (1024**3), 3),
        "disk_total_gib": round(disk.total / (1024**3), 3),
        "load_1m": round(load1, 3),
        "load_5m": round(load5, 3),
        "load_15m": round(load15, 3),
        "worker_service": worker_service,
        "worker_state": service_state(worker_service),
        "api_service": api_service,
        "api_state": service_state(api_service),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-path", type=Path, default=Path("/var/lib/moodify"))
    parser.add_argument("--output", type=Path, default=Path("/var/lib/moodify/ops/resource_snapshots.jsonl"))
    parser.add_argument("--worker-service", default="moodify-data-worker.service")
    parser.add_argument("--api-service", default="moodify-api.service")
    args = parser.parse_args()

    snap = snapshot(args.data_path, args.worker_service, args.api_service)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("a", encoding="utf-8") as f:
        f.write(json.dumps(snap, sort_keys=True) + "\n")
    print(json.dumps(snap, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
