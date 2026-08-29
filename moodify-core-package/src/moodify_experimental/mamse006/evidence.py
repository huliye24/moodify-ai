"""MAMSE-006 evidence contract: manifest + evidence JSON + NPZ arrays.

JSON holds summary/provenance/config/limitations; machine arrays are saved
as NPZ with the full-resolution auditory surface decimated along time
(dense intermediates are never persisted). Missing values are never faked.
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

_TARGET_SURFACE_FRAMES = 2048


def _git_commit() -> str:
    try:
        out = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, timeout=5)
        return out.stdout.strip() if out.returncode == 0 else "unknown"
    except Exception:
        return "unknown"


def build_manifest(summary: dict, git_commit: str | None = None) -> dict[str, Any]:
    return {
        "schema_version": summary.get("schema_version", MANIFEST_SCHEMA_VERSION),
        "operator_id": summary["operator_id"],
        "operator_version": summary["operator_version"],
        "config_version": summary["config_version"],
        "profile_hash": summary["profile_hash"],
        "config": summary["config"],
        "source_sha256": summary["source_sha256"],
        "status": summary["status"],
        "git_commit": git_commit or _git_commit(),
        "runtime": {
            "python": sys.version.split()[0],
            "numpy": np.__version__,
            "scipy": scipy.__version__,
        },
        "resource": {"runtime_seconds": summary["runtime_seconds"]},
        "authority": summary.get("authority", "EXPERIMENTAL_DESCRIPTOR"),
        "judgment_eligible": summary.get("judgment_eligible", False),
        "limitations": summary["limitations"],
        "generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }


def save_evidence(summary: dict, arrays: dict | None, out_dir: str | Path) -> tuple[Path, Path | None]:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    j = out / "modulation_evidence.json"
    j.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    if arrays is None:
        return j, None
    pack = {}
    for k, v in arrays.items():
        if not isinstance(v, np.ndarray):
            continue
        if v.ndim == 2 and k == "auditory_surface_db" and v.shape[1] > _TARGET_SURFACE_FRAMES:
            step = int(np.ceil(v.shape[1] / _TARGET_SURFACE_FRAMES))
            v = v[:, ::step]
            pack["auditory_surface_decimation"] = np.asarray(step, dtype=np.int64)
            pack["auditory_surface_full_frames"] = np.asarray(arrays["auditory_surface_db"].shape[1], dtype=np.int64)
        pack[k] = v
    n = out / "mamse006_modulation_arrays.npz"
    np.savez_compressed(n, **pack)
    manifest_path = out / "mamse006_manifest.json"
    manifest_path.write_text(json.dumps(build_manifest(summary), ensure_ascii=False, indent=2), encoding="utf-8")
    return j, n


def load_evidence(evidence_json: str | Path, npz_path: str | Path | None) -> dict[str, Any]:
    summary = json.loads(Path(evidence_json).read_text(encoding="utf-8"))
    arrays = None
    if npz_path is not None and Path(npz_path).exists():
        z = np.load(npz_path)
        arrays = {k: z[k] for k in z.files}
    return {"summary": summary, "arrays": arrays}
