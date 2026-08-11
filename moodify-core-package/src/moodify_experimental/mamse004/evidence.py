"""MAMSE-004 evidence contract: manifest + evidence JSON + NPZ sketch.

Manifest carries operator/config hash, source identity, runtime identity
(python/numpy/scipy/git) and resource stats. Missing values are never faked
as zero. JSON holds the summary only; 2D arrays live in the NPZ.
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


def _git_commit() -> str:
    try:
        out = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, timeout=5)
        return out.stdout.strip() if out.returncode == 0 else "unknown"
    except Exception:
        return "unknown"


def build_manifest(result: dict, git_commit: str | None = None) -> dict[str, Any]:
    s = result["summary"]
    return {
        "schema_version": MANIFEST_SCHEMA_VERSION,
        "operator_id": s["operator_id"],
        "operator_version": s["operator_version"],
        "config_version": s["config_version"],
        "config_hash": s["config_hash"],
        "config": s["config"],
        "source_sha256": s["source_sha256"],
        "sample_rate": s["sample_rate"],
        "git_commit": git_commit or _git_commit(),
        "runtime": {
            "python": sys.version.split()[0],
            "numpy": np.__version__,
            "scipy": scipy.__version__,
        },
        "resource": {"runtime_seconds": s["runtime_seconds"]},
        "authority_class": s["authority_class"],
        "judgment_eligible": s["judgment_eligible"],
        "limitations": s["limitations"],
        "generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }


_TARGET_SKETCH_FRAMES = 512
_TARGET_SKETCH_BINS = 1024


def _decimate_2d(a: np.ndarray, max_frames: int, max_bins: int) -> np.ndarray:
    """Sub-sample a [time, freq] array to a bounded sketch size (every k-th row/col).

    The full-resolution arrays are analysis intermediates and are NOT
    persisted; only this fixed-width sketch is saved.
    """
    a = np.asarray(a)
    if a.ndim != 2:
        return a
    fr = max(1, int(np.ceil(a.shape[0] / max_frames)))
    fc = max(1, int(np.ceil(a.shape[1] / max_bins)))
    out = a[::fr, ::fc]
    if out.dtype == np.float64:
        out = out.astype(np.float32)
    return out


def save_result(result: dict, out_dir: str | Path) -> tuple[Path, Path, Path]:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    evidence_path = out / "phase_geometry_evidence.json"
    npz_path = out / "mamse004_phase_geometry.npz"
    manifest_path = out / "mamse004_manifest.json"

    evidence_path.write_text(
        json.dumps(result["summary"], ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8"
    )
    m = result["mono_raw"]
    s = result["stereo_raw"]
    gd_full = m["group_delay_s"]
    gd_sketch = _decimate_2d(gd_full, _TARGET_SKETCH_FRAMES, _TARGET_SKETCH_BINS)
    payload = {
        "freq_hz": m["frequency_hz"],
        "frame_time_s": m["frame_time_s"],
        "group_delay_s": gd_sketch,
        "phase_curvature_s2": _decimate_2d(m["phase_curvature_s2"], _TARGET_SKETCH_FRAMES, _TARGET_SKETCH_BINS),
        "valid_mask": _decimate_2d(m["valid_mask"], _TARGET_SKETCH_FRAMES, _TARGET_SKETCH_BINS),
        "sketch_full_shape": np.asarray(gd_full.shape, dtype=np.int64),
        "decimation": np.asarray(
            [np.ceil(gd_full.shape[0] / gd_sketch.shape[0]),
             np.ceil(gd_full.shape[1] / gd_sketch.shape[1])], dtype=np.int64),
    }
    if s is not None:
        payload.update({
            "stereo_freq_hz": s["frequency_hz"],
            "stereo_frame_time_s": s["frame_time_s"],
            "ipd_rad": _decimate_2d(s["ipd_rad"], _TARGET_SKETCH_FRAMES, _TARGET_SKETCH_BINS),
            "interchannel_delay_s": _decimate_2d(s["interchannel_delay_s"], _TARGET_SKETCH_FRAMES, _TARGET_SKETCH_BINS),
            "stereo_valid_mask": _decimate_2d(s["valid_mask"], _TARGET_SKETCH_FRAMES, _TARGET_SKETCH_BINS),
        })
    np.savez_compressed(npz_path, **payload)
    manifest_path.write_text(json.dumps(build_manifest(result), ensure_ascii=False, indent=2), encoding="utf-8")
    return evidence_path, npz_path, manifest_path


def load_result(evidence_json: str | Path, npz_path: str | Path) -> dict[str, Any]:
    summary = json.loads(Path(evidence_json).read_text(encoding="utf-8"))
    z = np.load(npz_path)
    return {"summary": summary, "npz": {k: z[k] for k in z.files}}
