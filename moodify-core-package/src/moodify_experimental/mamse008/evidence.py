"""MAMSE-008 evidence contract: JSON summary + NPZ factors + manifest.

Components are always anonymous (semantic_label=None); scale/permutation
canonicalized; basis_id + config_hash + runtime identity recorded.
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

from .config import ALGORITHM_VERSION, MANIFEST_SCHEMA_VERSION, OPERATOR_ID
from .nmf import EPS, NMFResult, activation_sparsity

EVIDENCE_SCHEMA_VERSION = "mamse008-evidence-v1"


def _git_commit() -> str:
    try:
        out = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, timeout=5)
        return out.stdout.strip() if out.returncode == 0 else "unknown"
    except Exception:
        return "unknown"


def evidence_summary(
    result: NMFResult,
    *,
    axis: np.ndarray | None = None,
    frame_times_s: np.ndarray | None = None,
) -> dict[str, Any]:
    W, H = result.W, result.H
    components = []
    for k in range(W.shape[1]):
        wk = W[:, k]
        hk = H[k]
        centroid = None
        if axis is not None and len(axis) == len(wk):
            centroid = float(np.sum(np.asarray(axis) * wk) / (np.sum(wk) + EPS))
        peak_i = int(np.argmax(hk))
        components.append({
            "component_id": f"C{k:02d}",
            "semantic_label": None,
            "basis_centroid": centroid,
            "top_bin_indices": np.argsort(wk)[-5:][::-1].astype(int).tolist(),
            "activation_peak_index": peak_i,
            "activation_peak_time_s": (
                float(frame_times_s[peak_i])
                if frame_times_s is not None and peak_i < len(frame_times_s)
                else None
            ),
            "activation_sparsity_hoyer": activation_sparsity(hk),
            "total_activation": float(np.sum(hk)),
        })
    return {
        "schema_version": EVIDENCE_SCHEMA_VERSION,
        "operator_id": OPERATOR_ID,
        "algorithm_version": ALGORITHM_VERSION,
        "config_hash": result.config.config_hash,
        "status": result.status,
        "basis_id": result.basis_id,
        "config": result.config.to_dict(),
        "iterations": result.iterations,
        "objective_history": [float(x) for x in result.objective_history],
        "relative_reconstruction_error": result.relative_error,
        "component_count": int(W.shape[1]),
        "component_semantics": "anonymous mathematical factors; not source labels",
        "components": components,
    }


def build_manifest(result: NMFResult, git_commit: str | None = None) -> dict[str, Any]:
    return {
        "schema_version": MANIFEST_SCHEMA_VERSION,
        "operator_id": OPERATOR_ID,
        "algorithm_version": ALGORITHM_VERSION,
        "basis_id": result.basis_id,
        "config_hash": result.config.config_hash,
        "config": result.config.to_dict(),
        "status": result.status,
        "git_commit": git_commit or _git_commit(),
        "runtime": {
            "python": sys.version.split()[0],
            "numpy": np.__version__,
            "scipy": scipy.__version__,
        },
        "resource": {"runtime_seconds": result.runtime_seconds, "iterations": result.iterations},
        "generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }


def save_result(
    result: NMFResult,
    out_dir: str | Path,
    *,
    axis: np.ndarray | None = None,
    frame_times_s: np.ndarray | None = None,
) -> None:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    summary = evidence_summary(result, axis=axis, frame_times_s=frame_times_s)
    (out / "nmf_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    np.savez_compressed(
        out / "nmf_factors.npz",
        W=result.W,
        H=result.H,
        mask=result.mask,
        axis=np.asarray(axis) if axis is not None else np.array([]),
        frame_times_s=np.asarray(frame_times_s) if frame_times_s is not None else np.array([]),
    )
    (out / "mamse008_manifest.json").write_text(
        json.dumps(build_manifest(result), ensure_ascii=False, indent=2), encoding="utf-8"
    )


def load_result(out_dir: str | Path) -> dict[str, Any]:
    out = Path(out_dir)
    summary = json.loads((out / "nmf_summary.json").read_text(encoding="utf-8"))
    z = np.load(out / "nmf_factors.npz")
    return {
        "summary": summary,
        "W": z["W"],
        "H": z["H"],
        "mask": z["mask"],
        "axis": z["axis"],
        "frame_times_s": z["frame_times_s"],
    }
