"""Run MAMSE-008 on real cases via canonical S1 band ratios (read-only).

Usage: python scripts/mamse008_run_real_cases.py <source.wav ...> --out <dir>
Input = S1 band-energy ratios (nonnegative simplex columns; mid/side and
short_term_lufs conflicts excluded per baseline audit). Components are
anonymous factors; activation peak times map to the source clock for
human-checkable evidence.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import soundfile as sf

from moodify.auditory.representation.build import build_representation
from moodify_experimental.mamse008 import NMFConfig, fit_nmf, save_result

BAND_COLS = ("band_sub", "band_bass", "band_low_mid", "band_mid", "band_core_mid",
             "band_presence", "band_brilliance", "band_air")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("sources", nargs="+")
    ap.add_argument("--out", required=True)
    ap.add_argument("--rank", type=int, default=3)
    args = ap.parse_args()

    out_root = Path(args.out)
    out_root.mkdir(parents=True, exist_ok=True)
    summary: dict = {"schema_version": "mamse-008-real-cases-v1", "input": "S1 band-energy ratios", "cases": []}

    for src in args.sources:
        path = Path(src)
        samples, sr = sf.read(path, always_2d=True)
        samples = samples.astype(np.float32)
        case_name = path.stem
        case_dir = out_root / case_name
        case_dir.mkdir(parents=True, exist_ok=True)
        rep = build_representation(samples, sr, source_sha256=f"real:{case_name}")
        plane = rep.planes["S1"]
        names = list(plane.feature_names)
        idx = [names.index(c) for c in BAND_COLS]
        V = np.asarray(plane.values, dtype=np.float64)[:, idx].T
        hop_ms = plane.hop_ms
        n_frames = V.shape[1]
        frame_times_s = np.arange(n_frames) * hop_ms / 1000.0
        r = fit_nmf(V, NMFConfig(rank=args.rank, max_iter=300))
        save_result(r, case_dir, axis=np.asarray(idx), frame_times_s=frame_times_s)
        entry = {
            "case": case_name,
            "source": str(path),
            "duration_s": round(len(samples) / sr, 3),
            "input": "S1 band-energy ratios",
            "features": int(V.shape[0]),
            "frames": int(V.shape[1]),
            "rank": args.rank,
            "iterations": r.iterations,
            "relative_error": r.relative_error,
            "basis_id": r.basis_id,
            "runtime_seconds": r.runtime_seconds,
            "components": [
                {
                    "component_id": c["component_id"],
                    "semantic_label": c["semantic_label"],
                    "activation_peak_time_s": c["activation_peak_time_s"],
                    "activation_sparsity_hoyer": c["activation_sparsity_hoyer"],
                    "total_activation": c["total_activation"],
                }
                for c in json.loads((case_dir / "nmf_summary.json").read_text(encoding="utf-8"))["components"]
            ],
        }
        summary["cases"].append(entry)
        peaks = ", ".join(f"{c['component_id']}@{c['activation_peak_time_s']:.1f}s" for c in entry["components"])
        print(f"done {case_name}: err={r.relative_error:.4f} | {peaks}")

    (out_root / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"summary -> {out_root / 'summary.json'}")


if __name__ == "__main__":
    main()
