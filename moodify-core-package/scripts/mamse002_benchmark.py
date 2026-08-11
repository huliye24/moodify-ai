"""MAMSE-002 resource benchmark (T9): wall/CPU, RSS, swap, dense intermediate.

Usage: python scripts/mamse002_benchmark.py <wav> <out.json>
Measures 10 s / 45 s / full-length slices.
"""

from __future__ import annotations

import argparse
import json
import resource
import time
from pathlib import Path

import numpy as np
import soundfile as sf

from moodify_experimental.mamse002 import (
    DEFAULT_CONFIG,
    build_log_frequency_sketch,
    compute_cqt_observation,
)


def _swap_kb() -> float:
    try:
        with open("/proc/meminfo") as f:
            lines = {k.strip(): v for k, v in (ln.split(":") for ln in f)}
        return int(lines["SwapTotal"].split()[0]) - int(lines["SwapFree"].split()[0])
    except Exception:
        return float("nan")


def measure(samples: np.ndarray, sr: int, label: str) -> dict:
    before_swap = _swap_kb()
    t0 = time.perf_counter()
    cpu0 = time.process_time()
    rss0 = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    obs = compute_cqt_observation(samples, sr, DEFAULT_CONFIG)
    sketch = build_log_frequency_sketch(obs, DEFAULT_CONFIG)
    cpu1 = time.process_time()
    wall = time.perf_counter() - t0
    rss1 = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    after_swap = _swap_kb()

    dense_bytes = int(obs.magnitude.nbytes + obs.power.nbytes) if obs.status in ("OK", "SILENCE") else 0
    sketch_bytes = int(sketch.values.nbytes + sketch.times_s.nbytes)
    return {
        "label": label,
        "duration_s": round(len(samples) / sr, 3),
        "wall_time_s": round(wall, 3),
        "cpu_time_s": round(cpu1 - cpu0, 3),
        "peak_rss_kb": rss1,
        "rss_delta_kb": rss1 - rss0,
        "swap_before_kb": before_swap,
        "swap_after_kb": after_swap,
        "swap_delta_kb": after_swap - before_swap,
        "status": obs.status,
        "bins": int(len(obs.frequencies_hz)),
        "frames": int(len(obs.times_s)),
        "dense_intermediate_bytes": dense_bytes,
        "persisted_sketch_bytes": sketch_bytes,
        "config_sha256": DEFAULT_CONFIG.sha256()[:16],
        "geometry_id": DEFAULT_CONFIG.geometry_id,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("wav")
    ap.add_argument("out_json")
    args = ap.parse_args()

    samples, sr = sf.read(args.wav, always_2d=True)
    samples = samples.astype(np.float32)
    results = {
        "schema_version": "mamse-002-benchmark-v1",
        "source": args.wav,
        "sample_rate": sr,
        "measurements": [
            measure(samples[: sr * 10], sr, "slice_10s"),
            measure(samples[: sr * 45], sr, "slice_45s"),
            measure(samples, sr, "full"),
        ],
    }
    Path(args.out_json).write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    for m in results["measurements"]:
        print(json.dumps(m, ensure_ascii=False)[:260])


if __name__ == "__main__":
    main()
