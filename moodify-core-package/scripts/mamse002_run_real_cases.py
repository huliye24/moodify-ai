"""Run MAMSE-002 on real cases (T10) and emit evidence + events.

Usage: python scripts/mamse002_run_real_cases.py <source.wav ...> --out <dir>
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import soundfile as sf

from moodify_experimental.mamse002 import (
    DEFAULT_CONFIG,
    build_log_frequency_sketch,
    compute_cqt_observation,
    low_register_adjacent_tonal_events,
    save_case,
)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("sources", nargs="+")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    out_root = Path(args.out)
    out_root.mkdir(parents=True, exist_ok=True)
    summary: dict = {"cases": []}

    for src in args.sources:
        path = Path(src)
        samples, sr = sf.read(path, always_2d=True)
        samples = samples.astype(np.float32)
        case_name = path.stem
        case_dir = out_root / case_name
        case_dir.mkdir(parents=True, exist_ok=True)

        obs = compute_cqt_observation(samples, sr, DEFAULT_CONFIG)
        sketch = build_log_frequency_sketch(obs, DEFAULT_CONFIG)
        save_case(samples, sr, DEFAULT_CONFIG, obs, sketch, case_dir)
        events = low_register_adjacent_tonal_events(obs, sketch, DEFAULT_CONFIG)
        (case_dir / "mamse002_events.json").write_text(
            json.dumps({"events": events}, ensure_ascii=False, indent=2), encoding="utf-8"
        )

        names = sketch.feature_names
        dom = sketch.values[:, names.index("dominant_frequency_hz")]
        dom_midi = sketch.values[:, names.index("dominant_midi")]
        cents = sketch.values[:, names.index("tuning_deviation_cents")]
        entry = {
            "case": case_name,
            "source": str(path),
            "duration_s": round(len(samples) / sr, 3),
            "sample_rate": sr,
            "source_sha256": None,
            "cqt_status": obs.status,
            "frames": len(obs.times_s),
            "median_dominant_hz": round(float(np.nanmedian(dom)), 2) if np.isfinite(dom).any() else None,
            "median_dominant_midi": round(float(np.nanmedian(dom_midi)), 2) if np.isfinite(dom_midi).any() else None,
            "median_tuning_deviation_cents": round(float(np.nanmedian(cents)), 2) if np.isfinite(cents).any() else None,
            "mean_tonal_peakiness": round(float(np.nanmean(sketch.values[:, names.index("tonal_peakiness")])), 4),
            "mean_log_spectral_entropy": round(float(np.nanmean(sketch.values[:, names.index("log_spectral_entropy")])), 4),
            "events": events,
        }
        summary["cases"].append(entry)
        print(f"done {case_name}: {entry['median_dominant_hz']} Hz dom, {len(events)} events")

    (out_root / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"summary -> {out_root / 'summary.json'}")


if __name__ == "__main__":
    main()
