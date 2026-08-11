"""MAMSE-009 evidence contract: JSON summary + NPZ components + manifest.

Sparse component is a structural deviation candidate (EXPERIMENTAL_UNKNOWN),
never a defect/artifact label. Dense residual is stored separately from S.
Known P0 events and RPCA candidates coexist via overlap reports.
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
from .rpca import RPCAResult, candidate_intervals, robust_zscore, sparse_frame_score, sparse_feature_score

EVIDENCE_SCHEMA_VERSION = "mamse009-evidence-v1"


def _git_commit() -> str:
    try:
        out = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, timeout=5)
        return out.stdout.strip() if out.returncode == 0 else "unknown"
    except Exception:
        return "unknown"


def evidence_summary(result: RPCAResult, X: np.ndarray, *, space_id: str,
                     frame_times_s: np.ndarray | None = None) -> dict[str, Any]:
    fs = sparse_frame_score(X, result.S)
    fz = robust_zscore(fs)
    intervals = candidate_intervals(fs)
    for e in intervals:
        if frame_times_s is not None:
            e["start_time_s"] = float(frame_times_s[min(e["start_frame"], len(frame_times_s) - 1)])
            e["end_time_s"] = float(frame_times_s[min(e["end_frame"], len(frame_times_s) - 1)])
    return {
        "schema_version": EVIDENCE_SCHEMA_VERSION,
        "operator_id": OPERATOR_ID,
        "algorithm_version": ALGORITHM_VERSION,
        "config_hash": result.config.config_hash,
        "space_id": space_id,
        "model_id": result.model_id,
        "status": "OK" if result.converged else "PARTIAL",
        "config": result.config.to_dict(),
        "lambda_used": result.lambda_used,
        "iterations": result.iterations,
        "converged": result.converged,
        "rank_L": result.rank_L,
        "sparsity_S": result.sparsity_S,
        "relative_constraint_error": result.relative_constraint_error,
        "sparse_frame_score_summary": {
            "median": float(np.median(fs)),
            "max": float(np.max(fs)),
            "max_robust_z": float(np.max(fz)),
        },
        "candidate_intervals": intervals,
        "semantic_boundary": "Sparse component is a structural deviation candidate, not an automatic defect or artistic judgment.",
    }


def build_manifest(result: RPCAResult, git_commit: str | None = None) -> dict[str, Any]:
    return {
        "schema_version": MANIFEST_SCHEMA_VERSION,
        "operator_id": OPERATOR_ID,
        "algorithm_version": ALGORITHM_VERSION,
        "model_id": result.model_id,
        "config_hash": result.config.config_hash,
        "config": result.config.to_dict(),
        "converged": result.converged,
        "git_commit": git_commit or _git_commit(),
        "runtime": {
            "python": sys.version.split()[0],
            "numpy": np.__version__,
            "scipy": scipy.__version__,
        },
        "resource": {"runtime_seconds": result.runtime_seconds, "iterations": result.iterations},
        "generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }


def save_result(result: RPCAResult, X: np.ndarray, out_dir: str | Path, *, space_id: str,
                frame_times_s: np.ndarray | None = None, axis: np.ndarray | None = None) -> None:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    summary = evidence_summary(result, X, space_id=space_id, frame_times_s=frame_times_s)
    (out / "rpca_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8"
    )
    np.savez_compressed(
        out / "rpca_components.npz",
        X=X, L=result.L, S=result.S, dense_residual=result.dense_residual,
        sparse_frame_score=sparse_frame_score(X, result.S),
        sparse_feature_score=sparse_feature_score(X, result.S),
        frame_times_s=np.asarray(frame_times_s) if frame_times_s is not None else np.array([]),
        axis=np.asarray(axis) if axis is not None else np.array([]),
    )
    (out / "mamse009_manifest.json").write_text(
        json.dumps(build_manifest(result), ensure_ascii=False, indent=2), encoding="utf-8"
    )


def load_result(out_dir: str | Path) -> dict[str, Any]:
    out = Path(out_dir)
    summary = json.loads((out / "rpca_summary.json").read_text(encoding="utf-8"))
    z = np.load(out / "rpca_components.npz")
    return {"summary": summary, **{k: z[k] for k in z.files}}


def event_overlap_report(candidates_s: list[dict], canonical_events: list[dict]) -> dict[str, Any]:
    """Overlap between RPCA candidate intervals and canonical P0 events.

    Both sides are preserved; this is a report, not a merge or overwrite.
    candidate: {start_time_s, end_time_s}; event: {start_ms, end_ms or start_ms, event_type}.
    """
    overlaps = []
    for c in candidates_s:
        c0, c1 = c["start_time_s"], c["end_time_s"]
        hits = []
        for e in canonical_events:
            e0 = e.get("start_ms", 0) / 1000.0
            e1 = e.get("end_ms", e0) / 1000.0
            lo = max(c0, e0)
            hi = min(c1, e1)
            if lo < hi:
                hits.append({"event_type": e.get("event_type"), "domain": e.get("domain"),
                             "overlap_s": round(hi - lo, 3)})
        overlaps.append({"candidate": c, "overlapping_events": hits})
    return {"candidate_count": len(candidates_s), "overlap_rows": overlaps,
            "note": "Known P0 events and RPCA candidates coexist; no overwrite, no merge."}
