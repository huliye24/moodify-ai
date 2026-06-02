from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Optional

from .config import RuntimeConfig


def classify_error(error: str) -> str:
    e = (error or "").lower()
    if not e:
        return "unknown"
    if "no such file" in e or "not found" in e:
        return "path_missing"
    if "permission" in e:
        return "permission"
    if "timeout" in e or "timed out" in e:
        return "timeout"
    if "argument" in e or "usage:" in e or "unrecognized" in e:
        return "cli_argument"
    if "memory" in e or "killed" in e:
        return "resource"
    if "codec" in e or "format" in e or "ffmpeg" in e:
        return "audio_format"
    return "other"


def analyze_failures(cfg: RuntimeConfig, run_id: Optional[str] = None) -> Dict[str, Any]:
    cfg = cfg.resolved()
    if run_id is None:
        runs = sorted([p for p in cfg.output_root.iterdir() if p.is_dir()]) if cfg.output_root.exists() else []
        if not runs:
            raise FileNotFoundError(f"No run directories in {cfg.output_root}")
        run_dir = runs[-1]
        run_id = run_dir.name
    else:
        run_dir = cfg.output_root / run_id

    manifest = run_dir / "manifest.csv"
    if not manifest.exists():
        return {"run_id": run_id, "total_failures": 0, "classes": {}}

    with manifest.open("r", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))

    failed = [r for r in rows if r.get("status") == "failed"]
    counts = Counter(classify_error(r.get("error", "")) for r in failed)
    return {
        "run_id": run_id,
        "total_failures": len(failed),
        "classes": dict(counts),
        "examples": failed[:20],
    }
