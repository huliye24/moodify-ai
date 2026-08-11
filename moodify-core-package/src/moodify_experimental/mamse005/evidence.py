"""MAMSE-005 evidence contract: manifest + evidence JSON + NPZ sketch.

JSON holds summary/provenance/config/limitations only; per-frame 2D arrays
are saved as a decimated float32 sketch (dense intermediates are never
persisted). Missing values are never faked as zero.
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

_TARGET_SKETCH_FRAMES = 512


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
        "availability": s["availability"],
        "authority_class": s["authority_class"],
        "judgment_eligible": s["judgment_eligible"],
        "limitations": s["limitations"],
        "generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }


def _decimate_rows(a: np.ndarray, max_rows: int) -> np.ndarray:
    a = np.asarray(a)
    if a.ndim != 2:
        return a
    fr = max(1, int(np.ceil(a.shape[0] / max_rows)))
    out = a[::fr]
    if out.dtype == np.float64:
        out = out.astype(np.float32)
    return out


def save_result(result: dict, out_dir: str | Path) -> tuple[Path, Path, Path]:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    evidence_path = out / "cepstrum_evidence.json"
    npz_path = out / "mamse005_cepstrum.npz"
    manifest_path = out / "mamse005_manifest.json"

    evidence_path.write_text(
        json.dumps(result["summary"], ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8"
    )
    raw = result.get("raw")
    if raw is None:
        np.savez_compressed(npz_path, frame_time_s=np.array([], dtype=np.float64))
    else:
        cep_full = raw["cepstrum"]
        cep_sketch = _decimate_rows(cep_full, _TARGET_SKETCH_FRAMES)
        payload = {
            "frame_time_s": raw["frame_time_s"],
            "quefrency_s": raw["quefrency_s"],
            "cepstrum": cep_sketch,
            "envelope_logmag": _decimate_rows(raw["envelope_logmag"], _TARGET_SKETCH_FRAMES),
            "fine_logmag": _decimate_rows(raw["fine_logmag"], _TARGET_SKETCH_FRAMES),
            "f0_candidate_hz": raw["f0_candidate_hz"],
            "periodicity_score": raw["periodicity_score"],
            "periodicity_available": raw["periodicity_available"],
            "rms_dbfs": raw["rms_dbfs"],
            "sketch_full_rows": np.asarray(cep_full.shape[0], dtype=np.int64),
            "decimation_rows": np.asarray(int(np.ceil(cep_full.shape[0] / cep_sketch.shape[0])), dtype=np.int64),
        }
        np.savez_compressed(npz_path, **payload)
    manifest_path.write_text(json.dumps(build_manifest(result), ensure_ascii=False, indent=2), encoding="utf-8")
    return evidence_path, npz_path, manifest_path


def load_result(evidence_json: str | Path, npz_path: str | Path) -> dict[str, Any]:
    summary = json.loads(Path(evidence_json).read_text(encoding="utf-8"))
    z = np.load(npz_path)
    return {"summary": summary, "npz": {k: z[k] for k in z.files}}
