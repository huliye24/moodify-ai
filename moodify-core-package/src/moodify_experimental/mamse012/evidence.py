"""MAMSE-012 evidence contract: graph JSON + NPZ + manifest."""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import scipy

from .contracts import ALGORITHM_VERSION, SCHEMA_VERSION
from .gsp import dirichlet_energy, graph_spectral_energy, local_variation, spectral_decomposition

MANIFEST_SCHEMA_VERSION = "mamse-012-manifest-v1"


def _git_commit() -> str:
    try:
        out = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, timeout=5)
        return out.stdout.strip() if out.returncode == 0 else "unknown"
    except Exception:
        return "unknown"


def graph_evidence(graph, signal: np.ndarray | None = None) -> dict[str, Any]:
    degree = graph.degree()
    ncomp, labels = graph.connected_components()
    vals, _ = spectral_decomposition(graph, max_dense_nodes=512)
    out = {
        "schema_version": SCHEMA_VERSION,
        "algorithm_version": ALGORITHM_VERSION,
        "graph_id": graph.graph_id,
        "graph_family": graph.graph_family,
        "edge_semantic": graph.edge_semantic,
        "edge_authority": graph.edge_authority,
        "node_count": len(graph.nodes),
        "edge_count": len(graph.edges),
        "connected_components": int(ncomp),
        "component_labels": labels.tolist(),
        "degree_min": float(degree.min()),
        "degree_max": float(degree.max()),
        "degree_mean": float(degree.mean()),
        "laplacian_eigenvalues": vals.tolist(),
        "zero_eigenvalue_count": int(np.sum(vals < 1e-9)),
        "algebraic_connectivity": float(vals[1]) if len(vals) > 1 else 0.0,
        "provenance": graph.provenance,
        "semantic_boundaries": [
            "graph frequency is topology frequency, not acoustic Hz",
            "edges express selected relation, not causality",
            "high graph-frequency energy is structural variation candidate, not bad audio",
        ],
    }
    if signal is not None:
        x = np.asarray(signal, dtype=float)
        out["signal"] = {
            "dirichlet_energy": dirichlet_energy(graph, x),
            "local_variation": local_variation(graph, x).tolist(),
            **graph_spectral_energy(graph, x),
        }
    return out


def save_graph_evidence(graph, out_dir: str | Path, *, signal: np.ndarray | None = None) -> None:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "graph_summary.json").write_text(
        json.dumps(graph_evidence(graph, signal), ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    arrays = {"adjacency": graph.adjacency(), "laplacian": graph.laplacian()}
    if signal is not None:
        arrays["signal"] = np.asarray(signal, dtype=float)
    np.savez_compressed(out / "graph_arrays.npz", **arrays)
    manifest = {
        "schema_version": MANIFEST_SCHEMA_VERSION,
        "operator_id": "MAMSE-012",
        "schema_version_graph": SCHEMA_VERSION,
        "graph_id": graph.graph_id,
        "graph_family": graph.graph_family,
        "edge_semantic": graph.edge_semantic,
        "edge_authority": graph.edge_authority,
        "git_commit": _git_commit(),
        "runtime": {
            "python": sys.version.split()[0],
            "numpy": np.__version__,
            "scipy": scipy.__version__,
        },
        "generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    (out / "mamse012_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )
