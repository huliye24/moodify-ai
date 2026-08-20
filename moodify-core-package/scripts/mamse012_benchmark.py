"""MAMSE-012 resource benchmark: graph spectrum runtime/memory vs N/E.

Usage: python scripts/mamse012_benchmark.py <wav> <out.json>
Builds the three graphs from a real track and records N/E/runtime for
dense and sparse spectral paths.
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np
import soundfile as sf

from moodify.auditory.events.engine import run_temporal_hearing
from moodify.auditory.representation.build import build_representation
from moodify_experimental.mamse012 import (
    build_band_adjacency_graph,
    build_positive_correlation_graph,
    build_temporal_event_graph,
    save_graph_evidence,
    spectral_decomposition,
)

BANDS = [
    ("sub", 20, 60), ("bass", 60, 120), ("low_mid", 120, 250), ("mid", 250, 500),
    ("core_mid", 500, 2000), ("presence", 2000, 5000), ("brilliance", 5000, 10000),
    ("air", 10000, 16000),
]
CLEAN_FEATURES = ["rms_db", "peak_db", "stereo_correlation", "spectral_centroid_hz",
                  "band_sub", "band_bass", "band_low_mid", "band_mid", "band_core_mid",
                  "band_presence", "band_brilliance", "band_air"]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("wav")
    ap.add_argument("out_json")
    args = ap.parse_args()

    samples, sr = sf.read(args.wav, always_2d=True)
    samples = samples.astype(np.float32)
    rep = build_representation(samples, sr, source_sha256="benchmark")
    hearing = run_temporal_hearing(samples, sr)
    events = [e.to_dict() if hasattr(e, "to_dict") else e for e in hearing.events]

    results = {"schema_version": "mamse-012-benchmark-v1", "source": args.wav, "sample_rate": sr,
               "measurements": []}
    workdir = Path(args.out_json).with_suffix("")
    workdir.mkdir(parents=True, exist_ok=True)

    # band graph
    g_band = build_band_adjacency_graph(BANDS)
    t0 = time.perf_counter()
    spectral_decomposition(g_band)
    results["measurements"].append({
        "label": "band_path_graph",
        "nodes": len(g_band.nodes),
        "edges": len(g_band.edges),
        "spectrum_wall_time_s": round(time.perf_counter() - t0, 4),
    })

    # event graph
    g_event = build_temporal_event_graph(events)
    t0 = time.perf_counter()
    spectral_decomposition(g_event)
    results["measurements"].append({
        "label": "temporal_event_graph",
        "nodes": len(g_event.nodes),
        "edges": len(g_event.edges),
        "spectrum_wall_time_s": round(time.perf_counter() - t0, 4),
    })

    # correlation graph (MAMSE-011 style, clean subset)
    plane = rep.planes["S1"]
    names = list(plane.feature_names)
    idx = [names.index(c) for c in CLEAN_FEATURES]
    X = np.asarray(plane.values, dtype=np.float64)[:, idx]
    Z = (X - np.median(X, axis=0)) / (1.4826 * np.median(np.abs(X - np.median(X, axis=0)), axis=0) + 1e-12)
    C = np.corrcoef(Z, rowvar=False)
    g_corr = build_positive_correlation_graph(C, CLEAN_FEATURES, threshold=0.5)
    t0 = time.perf_counter()
    spectral_decomposition(g_corr)
    results["measurements"].append({
        "label": "positive_correlation_graph",
        "nodes": len(g_corr.nodes),
        "edges": len(g_corr.edges),
        "spectrum_wall_time_s": round(time.perf_counter() - t0, 4),
    })

    # sparse path guard probe on a large synthetic path graph
    from moodify_experimental.mamse012 import GraphEdge, GraphNode, canonical_graph
    nodes = [GraphNode(f"n{i}", "x") for i in range(800)]
    edges = [GraphEdge(f"n{i}", f"n{i + 1}", 1) for i in range(799)]
    g_big = canonical_graph(nodes, edges, graph_family="p", edge_semantic="path")
    t0 = time.perf_counter()
    vals, vecs = spectral_decomposition(g_big, max_dense_nodes=512, k=8)
    results["measurements"].append({
        "label": "sparse_path_800_k8",
        "nodes": 800,
        "edges": 799,
        "k": 8,
        "spectrum_wall_time_s": round(time.perf_counter() - t0, 4),
        "vals_shape": list(vals.shape),
        "vecs_shape": list(vecs.shape),
    })

    save_graph_evidence(g_band, workdir / "band")
    Path(args.out_json).write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    for m in results["measurements"]:
        print(json.dumps(m, ensure_ascii=False)[:220])


if __name__ == "__main__":
    main()
