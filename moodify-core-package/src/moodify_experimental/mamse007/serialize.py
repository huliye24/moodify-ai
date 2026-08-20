"""MAMSE-007 serialization: basis JSON round-trip, NPZ arrays, manifest."""

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
from .models import PCABasis, PCAResult


def _git_commit() -> str:
    try:
        out = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, timeout=5)
        return out.stdout.strip() if out.returncode == 0 else "unknown"
    except Exception:
        return "unknown"


def basis_to_dict(b: PCABasis) -> dict:
    return {
        "basis_id": b.basis_id,
        "basis_version": b.basis_version,
        "mode": b.mode,
        "input_feature_names": list(b.input_feature_names),
        "retained_feature_names": list(b.retained_feature_names),
        "dropped_features": list(b.dropped_features),
        "center": b.center.tolist(),
        "scale": b.scale.tolist(),
        "components": b.components.tolist(),
        "singular_values": b.singular_values.tolist(),
        "explained_variance": b.explained_variance.tolist(),
        "explained_variance_ratio": b.explained_variance_ratio.tolist(),
        "feature_schema_hash": b.feature_schema_hash,
        "preprocessing": b.preprocessing,
    }


def basis_from_dict(d: dict) -> PCABasis:
    return PCABasis(
        basis_id=d["basis_id"], basis_version=d["basis_version"], mode=d["mode"],
        input_feature_names=tuple(d["input_feature_names"]),
        retained_feature_names=tuple(d["retained_feature_names"]),
        dropped_features=tuple(d["dropped_features"]),
        center=np.asarray(d["center"], dtype=float), scale=np.asarray(d["scale"], dtype=float),
        components=np.asarray(d["components"], dtype=float),
        singular_values=np.asarray(d["singular_values"], dtype=float),
        explained_variance=np.asarray(d["explained_variance"], dtype=float),
        explained_variance_ratio=np.asarray(d["explained_variance_ratio"], dtype=float),
        feature_schema_hash=d["feature_schema_hash"], preprocessing=d["preprocessing"],
    )


def build_manifest(result: PCAResult, git_commit: str | None = None) -> dict[str, Any]:
    return {
        "schema_version": MANIFEST_SCHEMA_VERSION,
        "operator_id": "MAMSE-007",
        "operator_version": "0.1.0",
        "basis_id": result.basis.basis_id,
        "basis_version": result.basis.basis_version,
        "mode": result.basis.mode,
        "config_hash": result.evidence.get("config_hash"),
        "feature_schema_hash": result.basis.feature_schema_hash,
        "source_sha256": (result.evidence.get("source_meta") or {}).get("source_sha256"),
        "git_commit": git_commit or _git_commit(),
        "runtime": {
            "python": sys.version.split()[0],
            "numpy": np.__version__,
            "scipy": scipy.__version__,
        },
        "resource": {"runtime_seconds": result.evidence.get("runtime_seconds")},
        "generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }


def save_result(result: PCAResult, directory: str | Path) -> None:
    out = Path(directory)
    out.mkdir(parents=True, exist_ok=True)
    payload = {"basis": basis_to_dict(result.basis), "evidence": result.evidence}
    (out / "pca_evidence.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    np.savez_compressed(
        out / "mamse007_arrays.npz",
        scores=result.scores,
        reconstruction=result.reconstruction,
        residual_norm=result.residual_norm,
        imputation_mask=result.imputation_mask,
        retained_matrix=result.retained_matrix,
        standardized_matrix=result.standardized_matrix,
    )
    (out / "mamse007_manifest.json").write_text(
        json.dumps(build_manifest(result), ensure_ascii=False, indent=2), encoding="utf-8"
    )


def load_basis(path: str | Path) -> PCABasis:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    return basis_from_dict(payload["basis"])


def load_result(directory: str | Path) -> dict[str, Any]:
    out = Path(directory)
    payload = json.loads((out / "pca_evidence.json").read_text(encoding="utf-8"))
    z = np.load(out / "mamse007_arrays.npz")
    return {"basis": basis_from_dict(payload["basis"]), "evidence": payload["evidence"],
            "arrays": {k: z[k] for k in z.files}}
