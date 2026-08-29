"""MAMSE-003 resource benchmark (T5): first-order vs first+second order.

Usage: python scripts/mamse003_benchmark.py <wav> <out.json>
Measures 10 s / 30 s / 45 s slices (mono downmix, 24 kHz analysis).
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np
import soundfile as sf

from moodify_experimental.mamse003 import TextureConfig, analyze_texture

try:
    import resource  # POSIX only
except ImportError:  # Windows
    resource = None


def _swap_kb() -> float:
    try:
        with open("/proc/meminfo") as f:
            lines = {k.strip(): v for k, v in (ln.split(":") for ln in f)}
        return int(lines["SwapTotal"].split()[0]) - int(lines["SwapFree"].split()[0])
    except Exception:
        return float("nan")


def measure(samples: np.ndarray, sr: int, label: str, second_order: bool) -> dict:
    before_swap = _swap_kb()
    t0 = time.perf_counter()
    cpu0 = time.process_time()
    rss_metric = {"rss0_kb": None}
    if resource is not None:
        rss_metric["rss0_kb"] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    cfg = TextureConfig() if second_order else TextureConfig(modulation_rates_hz=())
    result = analyze_texture(samples, sr, cfg)
    cpu1 = time.process_time()
    wall = time.perf_counter() - t0
    rss1 = None
    rss_delta = None
    if resource is not None:
        rss1 = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        rss_delta = rss1 - rss_metric["rss0_kb"]
    after_swap = _swap_kb()
    return {
        "label": label,
        "second_order_included": second_order,
        "duration_s": round(len(samples) / sr, 3),
        "wall_time_s": round(wall, 3),
        "cpu_time_s": round(cpu1 - cpu0, 3),
        "peak_rss_kb": rss1,
        "rss_delta_kb": rss_delta,
        "swap_before_kb": before_swap,
        "swap_after_kb": after_swap,
        "swap_delta_kb": after_swap - before_swap,
        "config_hash": cfg.config_hash[:16],
        "carriers": len(result.carrier_centers_hz),
        "frames": len(result.frame_texture_matrix),
        "tracemalloc_peak_mb": result.peak_memory_mb,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("wav")
    ap.add_argument("out_json")
    args = ap.parse_args()

    samples, sr = sf.read(args.wav, always_2d=True)
    samples = samples.astype(np.float32)
    results = {
        "schema_version": "mamse-003-benchmark-v1",
        "source": args.wav,
        "sample_rate": sr,
        "measurements": [],
    }
    # first-order only: envelope decimation skipped by using a short config path
    for secs in (10, 30, 45):
        if len(samples) < sr * secs:
            continue
        results["measurements"].append(measure(samples[: sr * secs], sr, f"first_order_{secs}s", False))
        results["measurements"].append(measure(samples[: sr * secs], sr, f"second_order_{secs}s", True))

    Path(args.out_json).write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    for m in results["measurements"]:
        print(json.dumps(m, ensure_ascii=False)[:230])


if __name__ == "__main__":
    main()
