"""MAMSE-011 resource benchmark: covariance fit runtime/memory vs N/P.

Usage: python scripts/mamse011_benchmark.py <wav> <out.json>
Builds the S1 clean-subset matrix and fits the covariance model, recording
N/P/runtime/estimator/shrinkage.
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np
import soundfile as sf

from moodify.auditory.representation.build import build_representation
from moodify_experimental.mamse011 import CovarianceConfig, fit_covariance_model, save_model

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
    plane = rep.planes["S1"]
    names = list(plane.feature_names)
    idx = [names.index(c) for c in CLEAN_FEATURES]
    X = np.asarray(plane.values, dtype=np.float64)[:, idx]

    results = {"schema_version": "mamse-011-benchmark-v1", "source": args.wav, "sample_rate": sr,
               "input": "S1 clean subset (12 features)", "measurements": []}
    workdir = Path(args.out_json).with_suffix("")
    workdir.mkdir(parents=True, exist_ok=True)

    for label, est in (("oas", "oas"), ("empirical", "empirical"), ("fixed", "fixed_shrinkage")):
        cfg = CovarianceConfig(estimator=est)
        t0 = time.perf_counter()
        cpu0 = time.process_time()
        m = fit_covariance_model(X, CLEAN_FEATURES, config=cfg)
        cpu1 = time.process_time()
        wall = time.perf_counter() - t0
        save_model(m, workdir / label)
        results["measurements"].append({
            "label": label,
            "estimator": est,
            "n_rows": m.total_rows,
            "n_complete": m.complete_rows,
            "p_features": len(m.feature_names),
            "shrinkage_alpha": m.shrinkage_alpha,
            "effective_rank": float(np.exp(-np.sum(
                np.where(m.eigenvalues / (m.eigenvalues.sum() + 1e-12) > 0,
                         m.eigenvalues / (m.eigenvalues.sum() + 1e-12) * np.log(m.eigenvalues / (m.eigenvalues.sum() + 1e-12) + 1e-12), 0)))),
            "wall_time_s": round(wall, 4),
            "cpu_time_s": round(cpu1 - cpu0, 4),
            "npz_bytes": (workdir / label / "covariance_model.npz").stat().st_size,
            "json_bytes": (workdir / label / "covariance_summary.json").stat().st_size,
        })

    Path(args.out_json).write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    for m in results["measurements"]:
        print(json.dumps(m, ensure_ascii=False)[:240])


if __name__ == "__main__":
    main()
