"""MAMSE-014 resource benchmark: wall/CPU, RSS, swap, dense intermediate.

Usage: python scripts/mamse014_benchmark.py <wav> <out.json>
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

from moodify_experimental.mamse014 import (
    DEFAULT_CONFIG,
    build_masking_sketch,
    compute_masking_observation,
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
    obs = compute_masking_observation(samples, sr, DEFAULT_CONFIG)
    build_masking_sketch(obs, DEFAULT_CONFIG)
    cpu1 = time.process_time()
    wall = time.perf_counter() - t0
    rss1 = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    after_swap = _swap_kb()
    return {
        "label": label,
        "duration_s": float(len(samples) / sr),
        "wall_s": round(wall, 3),
        "cpu_s": round(cpu1 - cpu0, 3),
        "rss_max_kb": rss1,
        "rss_delta_kb": rss1 - rss0,
        "swap_delta_kb": after_swap - before_swap,
        "n_channels": int(obs.channel_power_db.shape[0]),
        "n_frames": int(obs.channel_power_db.shape[1]),
        "status": obs.status,
        "masked_channel_ratio_mean": obs.masked_channel_ratio_mean,
        "n_events": len(obs.events),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("wav")
    ap.add_argument("out")
    args = ap.parse_args()

    samples, sr = sf.read(args.wav, dtype="float32", always_2d=False)
    if samples.ndim > 1:
        samples = samples.mean(axis=1)
    samples = np.ascontiguousarray(samples, dtype=np.float32)

    results = [measure(samples[:10 * sr], sr, "10s")]
    if len(samples) >= 45 * sr:
        results.append(measure(samples[:45 * sr], sr, "45s"))
    results.append(measure(samples, sr, "full"))

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
