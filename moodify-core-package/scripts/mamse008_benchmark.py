"""MAMSE-008 resource benchmark: NMF runtime vs matrix shape / rank.

Usage: python scripts/mamse008_benchmark.py <wav> <out.json>
Builds the canonical S1 band-ratio matrix (nonnegative simplex columns) and
fits NMF at rank 2/3, recording shape/rank/iterations/runtime/memory.
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np
import soundfile as sf

from moodify.auditory.representation.build import build_representation
from moodify_experimental.mamse008 import NMFConfig, fit_nmf, save_result

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
    V = np.asarray(plane.values, dtype=np.float64)[:, idx].T  # [bands, frames]

    results = {"schema_version": "mamse-008-benchmark-v1", "source": args.wav, "sample_rate": sr,
               "input": "S1 band-energy ratios (nonnegative simplex)", "measurements": []}
    workdir = Path(args.out_json).with_suffix("")
    workdir.mkdir(parents=True, exist_ok=True)

    for rank in (2, 3):
        t0 = time.perf_counter()
        cpu0 = time.process_time()
        r = fit_nmf(V, NMFConfig(rank=rank, max_iter=300))
        cpu1 = time.process_time()
        wall = time.perf_counter() - t0
        save_result(r, workdir / f"rank{rank}")
        results["measurements"].append({
            "rank": rank,
            "features": int(V.shape[0]),
            "frames": int(V.shape[1]),
            "iterations": r.iterations,
            "relative_error": r.relative_error,
            "wall_time_s": round(wall, 4),
            "cpu_time_s": round(cpu1 - cpu0, 4),
            "basis_id": r.basis_id,
            "npz_bytes": (workdir / f"rank{rank}" / "nmf_factors.npz").stat().st_size,
            "json_bytes": (workdir / f"rank{rank}" / "nmf_summary.json").stat().st_size,
        })

    Path(args.out_json).write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    for m in results["measurements"]:
        print(json.dumps(m, ensure_ascii=False)[:240])


if __name__ == "__main__":
    main()
