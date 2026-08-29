#!/usr/bin/env python3
"""Emit a small JSON capacity snapshot for 2C2G production evidence."""

from __future__ import annotations

import json
import os
import shutil
from pathlib import Path


def meminfo() -> dict[str, int]:
    values: dict[str, int] = {}
    for line in Path('/proc/meminfo').read_text(encoding='utf-8').splitlines():
        key, raw = line.split(':', 1)
        token = raw.strip().split()[0]
        if token.isdigit():
            values[key] = int(token)  # KiB
    return values


def main() -> int:
    target = Path(os.getenv('MOODIFY_NODE_OUTPUT_ROOT', '/var/lib/moodify/data_factory'))
    target.mkdir(parents=True, exist_ok=True)
    mem = meminfo()
    disk = shutil.disk_usage(target)
    payload = {
        'cpu_count': os.cpu_count(),
        'load_1_5_15': list(os.getloadavg()) if hasattr(os, 'getloadavg') else None,
        'memory_total_mb': round(mem.get('MemTotal', 0) / 1024, 1),
        'memory_available_mb': round(mem.get('MemAvailable', mem.get('MemFree', 0)) / 1024, 1),
        'swap_total_mb': round(mem.get('SwapTotal', 0) / 1024, 1),
        'swap_free_mb': round(mem.get('SwapFree', 0) / 1024, 1),
        'disk_free_gb': round(disk.free / (1024**3), 2),
        'disk_total_gb': round(disk.total / (1024**3), 2),
        'output_root': str(target),
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
