"""MAMSE-007 resource benchmark: exact SVD runtime/memory vs N windows.

Usage: python scripts/mamse007_benchmark.py <wav> <out.json>
Builds a ScalePlane-style matrix (S1 features via canonical builder) and
fits CASE_LOCAL PCA, recording N/D/K/runtime/memory/artifact size.
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np
import soundfile as sf

from moodify.auditory.representation.build import build_representation
from moodify_experimental.mamse007 import PCAConfig, basis_eligible_feature_names, fit_pca, preflight_features, save_result

N_COMPONENTS = 3


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("wav")
    ap.add_argument("out_json")
    args = ap.parse_args()

    samples, sr = sf.read(args.wav, always_2d=True)
    samples = samples.astype(np.float32)
    rep = build_representation(samples, sr, source_sha256="benchmark")
    plane = rep.planes["S1"]
    x = np.asarray(plane.values, dtype=np.float64)
    feature_names = tuple(plane.feature_names)
    records = preflight_features(feature_names)
    sem_retained, sem_dropped = basis_eligible_feature_names(records, allow_unresolved=True)
    kept_idx = [feature_names.index(n) for n in sem_retained]

    results = {"schema_version": "mamse-007-benchmark-v1", "source": args.wav, "sample_rate": sr,
               "input_features": len(feature_names), "semantic_retained": list(sem_retained),
               "measurements": []}
    workdir = Path(args.out_json).with_suffix("")
    workdir.mkdir(parents=True, exist_ok=True)

    # full matrix, plus row-subsampled variants to show N scaling
    for label, rows in (("full", slice(None)), ("half", slice(None, None, 2)), ("quarter", slice(None, None, 4))):
        xr = x[rows][:, kept_idx]
        t0 = time.perf_counter()
        cpu0 = time.process_time()
        result = fit_pca(xr, sem_retained, PCAConfig(n_components=N_COMPONENTS, mode="CASE_LOCAL"),
                         source_meta={"source_sha256": "benchmark", "label": label})
        cpu1 = time.process_time()
        wall = time.perf_counter() - t0
        save_result(result, workdir / label)
        npz = workdir / label / "mamse007_arrays.npz"
        results["measurements"].append({
            "label": label,
            "n_windows": int(xr.shape[0]),
            "d_input_features": int(xr.shape[1]),
            "d_retained": len(result.basis.retained_feature_names),
            "k_components": N_COMPONENTS,
            "wall_time_s": round(wall, 4),
            "cpu_time_s": round(cpu1 - cpu0, 4),
            "explained_variance_ratio": result.basis.explained_variance_ratio.tolist(),
            "npz_bytes": npz.stat().st_size,
            "json_bytes": (workdir / label / "pca_evidence.json").stat().st_size,
        })

    results["semantic_dropped"] = sem_dropped
    Path(args.out_json).write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    for m in results["measurements"]:
        print(json.dumps(m, ensure_ascii=False)[:240])


if __name__ == "__main__":
    main()
