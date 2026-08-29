"""MAMSE-003 evidence contract: manifest + NPZ + JSON.

Manifest carries operator/config hash, source identity, runtime identity
(python/numpy/scipy/git), and resource stats. Missing values are never
faked as zero.
"""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import scipy

from .config import MANIFEST_SCHEMA_VERSION
from .sketch import TextureResult


def _git_commit() -> str:
    try:
        out = subprocess.run(
            ["git", "rev-parse", "HEAD"], capture_output=True, text=True, timeout=5
        )
        return out.stdout.strip() if out.returncode == 0 else "unknown"
    except Exception:
        return "unknown"


def build_manifest(result: TextureResult, git_commit: str | None = None) -> dict[str, Any]:
    return {
        "schema_version": MANIFEST_SCHEMA_VERSION,
        "operator_id": result.config["operator_id"],
        "operator_version": result.config["operator_version"],
        "config_version": "mamse003-texture-v0.1",
        "config_hash": result.config["config_hash"],
        "config": {k: v for k, v in result.config.items() if k != "config_hash"},
        "source_sha256": result.source_sha256,
        "analysis_sample_rate": result.config["analysis_sample_rate"],
        "git_commit": git_commit or _git_commit(),
        "runtime": {
            "python": sys.version.split()[0],
            "numpy": np.__version__,
            "scipy": scipy.__version__,
        },
        "resource": {
            "runtime_seconds": result.runtime_seconds,
            "peak_memory_mb": result.peak_memory_mb,
        },
        "limitations": result.limitations,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }


def save_case(result: TextureResult, out_dir: str | Path) -> dict[str, Path]:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    manifest_path = out / "mamse003_manifest.json"
    npz_path = out / "mamse003_texture.npz"
    summary_path = out / "mamse003_texture.json"

    manifest_path.write_text(json.dumps(build_manifest(result), ensure_ascii=False, indent=2), encoding="utf-8")

    np.savez_compressed(
        npz_path,
        first_order_distribution=np.asarray(result.first_order_distribution),
        first_order_temporal_cv=np.asarray(result.first_order_temporal_cv),
        modulation_distribution=np.asarray(result.modulation_distribution),
        frame_texture_matrix=np.asarray(result.frame_texture_matrix),
        frame_starts_samples=np.asarray(result.frame_starts_samples, dtype=np.int64),
        frame_ends_samples=np.asarray(result.frame_ends_samples, dtype=np.int64),
        carrier_centers_hz=np.asarray(result.carrier_centers_hz),
        modulation_rates_hz=np.asarray(result.modulation_rates_hz),
    )

    summary = {k: v for k, v in result.to_dict().items()
               if k not in ("frame_texture_matrix", "frame_starts_samples", "frame_ends_samples",
                            "first_order_distribution", "first_order_temporal_cv",
                            "modulation_distribution", "carrier_centers_hz", "modulation_rates_hz")}
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"manifest": manifest_path, "npz": npz_path, "summary": summary_path}


def load_case(json_path: str | Path, npz_path: str | Path) -> dict[str, Any]:
    manifest = json.loads(Path(json_path).read_text(encoding="utf-8"))
    z = np.load(npz_path)
    return {
        "manifest": manifest,
        "first_order_distribution": z["first_order_distribution"],
        "modulation_distribution": z["modulation_distribution"],
        "frame_texture_matrix": z["frame_texture_matrix"],
        "frame_starts_samples": z["frame_starts_samples"],
        "frame_ends_samples": z["frame_ends_samples"],
        "carrier_centers_hz": z["carrier_centers_hz"],
        "modulation_rates_hz": z["modulation_rates_hz"],
    }
