"""Run MAMSE-003 on real cases (T6) and emit evidence.

Usage: python scripts/mamse003_run_real_cases.py <source.wav ...> --out <dir>
With --pair <a.wav> <b.wav> --pair-label <name>, also emits an A/B texture
delta comparison.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import soundfile as sf

from moodify_experimental.mamse003 import TextureConfig, analyze_texture, save_case


def _cosine(a, b) -> float:
    a = np.asarray(a)
    b = np.asarray(b)
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-12))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("sources", nargs="+")
    ap.add_argument("--out", required=True)
    ap.add_argument("--pair", nargs=2, metavar=("A", "B"))
    ap.add_argument("--pair-label", default="ab")
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
        result = analyze_texture(samples, sr, TextureConfig())
        save_case(result, case_dir)
        entry = {
            "case": case_name,
            "source": str(path),
            "duration_s": round(len(samples) / sr, 3),
            "source_sha256": result.source_sha256,
            "high_modulation_ratio": result.high_modulation_ratio,
            "texture_entropy": result.texture_entropy,
            "texture_sparsity": result.texture_sparsity,
            "stationarity_index": result.stationarity_index,
            "order_ratio": result.order_ratio,
            "modulation_distribution": result.modulation_distribution,
            "first_order_distribution": result.first_order_distribution,
            "runtime_seconds": result.runtime_seconds,
            "peak_memory_mb": result.peak_memory_mb,
        }
        summary["cases"].append(entry)
        print(f"done {case_name}: hmr={entry['high_modulation_ratio']:.3f} entropy={entry['texture_entropy']:.3f}")

    if args.pair:
        a_path, b_path = (Path(p) for p in args.pair)
        a, _ = sf.read(a_path, always_2d=True)
        b, _ = sf.read(b_path, always_2d=True)
        ra = analyze_texture(a.astype(np.float32), 48000, TextureConfig())
        rb = analyze_texture(b.astype(np.float32), 48000, TextureConfig())
        pair = {
            "label": args.pair_label,
            "a": {
                "path": str(a_path),
                "sha256": ra.source_sha256,
                "high_modulation_ratio": ra.high_modulation_ratio,
                "texture_entropy": ra.texture_entropy,
                "stationarity_index": ra.stationarity_index,
                "texture_sparsity": ra.texture_sparsity,
            },
            "b": {
                "path": str(b_path),
                "sha256": rb.source_sha256,
                "high_modulation_ratio": rb.high_modulation_ratio,
                "texture_entropy": rb.texture_entropy,
                "stationarity_index": rb.stationarity_index,
                "texture_sparsity": rb.texture_sparsity,
            },
            "first_order_cosine": _cosine(ra.first_order_distribution, rb.first_order_distribution),
            "modulation_cosine": _cosine(ra.modulation_distribution, rb.modulation_distribution),
        }
        (out_root / f"pair_{args.pair_label}.json").write_text(json.dumps(pair, ensure_ascii=False, indent=2), encoding="utf-8")
        summary["pair"] = pair
        print(f"pair {args.pair_label}: first_cos={pair['first_order_cosine']:.4f} mod_cos={pair['modulation_cosine']:.4f}")

    (out_root / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"summary -> {out_root / 'summary.json'}")


if __name__ == "__main__":
    main()
