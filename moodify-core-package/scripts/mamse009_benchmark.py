"""MAMSE-009 resource benchmark: IALM runtime/memory vs matrix shape.

Usage: python scripts/mamse009_benchmark.py <wav> <out.json>
Builds the canonical S1 band-ratio matrix and runs PCP, recording
shape/rank/iterations/runtime/SVD count. Also measures a long-track
(two-row-block) case to record the long-track resource policy (G20).
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np
import soundfile as sf

from moodify.auditory.representation.build import build_representation
from moodify_experimental.mamse009 import RPCAConfig, principal_component_pursuit, save_result

BAND_COLS = ("band_sub", "band_bass", "band_low_mid", "band_mid", "band_core_mid",
             "band_presence", "band_brilliance", "band_air")


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
    idx = [names.index(c) for c in BAND_COLS]
    V = np.asarray(plane.values, dtype=np.float64)[:, idx].T

    results = {"schema_version": "mamse-009-benchmark-v1", "source": args.wav, "sample_rate": sr,
               "input": "S1 band-energy ratios", "measurements": []}
    workdir = Path(args.out_json).with_suffix("")
    workdir.mkdir(parents=True, exist_ok=True)

    cfg = RPCAConfig(max_iter=1000)
    t0 = time.perf_counter()
    cpu0 = time.process_time()
    r = principal_component_pursuit(V, cfg, space_id="benchmark")
    cpu1 = time.process_time()
    wall = time.perf_counter() - t0
    save_result(r, V, workdir / "full", space_id="benchmark")
    results["measurements"].append({
        "label": "full",
        "features": int(V.shape[0]),
        "frames": int(V.shape[1]),
        "iterations": r.iterations,
        "converged": r.converged,
        "rank_L": r.rank_L,
        "sparsity_S": r.sparsity_S,
        "lambda_used": r.lambda_used,
        "wall_time_s": round(wall, 4),
        "cpu_time_s": round(cpu1 - cpu0, 4),
        "npz_bytes": (workdir / "full" / "rpca_components.npz").stat().st_size,
        "json_bytes": (workdir / "full" / "rpca_summary.json").stat().st_size,
    })

    # long-track policy probe: doubled frames (row-block concatenation)
    V2 = np.concatenate([V, V], axis=1)
    t0 = time.perf_counter()
    r2 = principal_component_pursuit(V2, cfg, space_id="benchmark-long")
    wall2 = time.perf_counter() - t0
    results["measurements"].append({
        "label": "long_2x_frames",
        "features": int(V2.shape[0]),
        "frames": int(V2.shape[1]),
        "iterations": r2.iterations,
        "converged": r2.converged,
        "rank_L": r2.rank_L,
        "wall_time_s": round(wall2, 4),
        "resource_note": "SVD cost scales with min(rows, cols); rows fixed at 8 -> near-linear in frames",
    })

    Path(args.out_json).write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    for m in results["measurements"]:
        print(json.dumps(m, ensure_ascii=False)[:240])


if __name__ == "__main__":
    main()
