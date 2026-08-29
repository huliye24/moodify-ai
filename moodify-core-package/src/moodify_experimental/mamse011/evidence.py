"""MAMSE-011 evidence contract: JSON summary + NPZ model + manifest."""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import scipy

from .config import ALGORITHM_VERSION, MANIFEST_SCHEMA_VERSION, SCHEMA_VERSION
from .covariance import CovarianceModel, effective_rank, eigengap_stability

EPS = 1e-12


def _git_commit() -> str:
    try:
        out = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, timeout=5)
        return out.stdout.strip() if out.returncode == 0 else "unknown"
    except Exception:
        return "unknown"


def model_evidence(model: CovarianceModel) -> dict[str, Any]:
    vals = model.eigenvalues
    ratio = vals / (np.sum(vals) + EPS)
    return {
        "schema_version": SCHEMA_VERSION,
        "algorithm_version": ALGORITHM_VERSION,
        "config_hash": model.config.config_hash,
        "model_id": model.model_id,
        "feature_names": list(model.feature_names),
        "feature_units": list(model.feature_units),
        "config": model.config.to_dict(),
        "complete_rows": model.complete_rows,
        "total_rows": model.total_rows,
        "shrinkage_alpha": model.shrinkage_alpha,
        "condition_number": float(vals[0] / max(vals[-1], EPS)),
        "effective_rank": effective_rank(vals),
        "eigenvalues": vals.tolist(),
        "explained_variance_ratio": ratio.tolist(),
        "eigengap_stability": eigengap_stability(vals, model.config.eigengap_relative_tol),
        "reference_distance_quantiles": model.reference_distance_quantiles,
        "lag1_autocorrelation_by_feature": {
            name: float(v) for name, v in zip(model.feature_names, model.lag1_by_feature)
        },
        "effective_sample_size_by_feature": {
            name: float(v) for name, v in zip(
                model.feature_names, model.effective_sample_size_by_feature
            )
        },
        "semantic_boundary": (
            "Mahalanobis / covariance distance measures departure from a reference "
            "relationship model; it is not automatic artistic or quality authority."
        ),
    }


def save_model(model: CovarianceModel, out_dir: str | Path) -> None:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "covariance_summary.json").write_text(
        json.dumps(model_evidence(model), ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    np.savez_compressed(
        out / "covariance_model.npz",
        center=model.center,
        scale=model.scale,
        covariance=model.covariance,
        correlation=model.correlation,
        eigenvalues=model.eigenvalues,
        eigenvectors=model.eigenvectors,
        precision=model.precision,
        whitening=model.whitening,
        lag1_by_feature=model.lag1_by_feature,
        effective_sample_size_by_feature=model.effective_sample_size_by_feature,
    )
    manifest = {
        "schema_version": MANIFEST_SCHEMA_VERSION,
        "operator_id": "MAMSE-011",
        "algorithm_version": ALGORITHM_VERSION,
        "model_id": model.model_id,
        "config_hash": model.config.config_hash,
        "config": model.config.to_dict(),
        "git_commit": _git_commit(),
        "runtime": {
            "python": sys.version.split()[0],
            "numpy": np.__version__,
            "scipy": scipy.__version__,
        },
        "resource": {"runtime_seconds": model.runtime_seconds},
        "generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    (out / "mamse011_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def load_model(out_dir: str | Path) -> dict[str, Any]:
    out = Path(out_dir)
    summary = json.loads((out / "covariance_summary.json").read_text(encoding="utf-8"))
    z = np.load(out / "covariance_model.npz")
    return {"summary": summary, **{k: z[k] for k in z.files}}
