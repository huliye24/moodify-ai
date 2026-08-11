"""Run MAMSE-010 on real cases: scale-feature view + HOSVD localization.

Usage: python scripts/mamse010_run_real_cases.py <source.wav ...> --out <dir>
Emits the AuditoryTensorBundle (scale_feature_view + channel_spectral_view)
plus a HOSVD time-residual curve for cross-scale/channel localization
evidence. Recording only; no canonical change.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import soundfile as sf

from moodify.auditory.representation.build import build_representation
from moodify_experimental.mamse010 import (
    AuditoryTensorBundle,
    build_channel_spectral_tensor,
    build_scale_feature_tensor,
    hosvd,
    relative_residual_by_time,
    save_bundle,
)

FEATURE_NAMES = ["rms_db", "peak_db", "stereo_correlation", "spectral_centroid_hz",
                 "band_sub", "band_bass", "band_low_mid", "band_mid", "band_core_mid",
                 "band_presence", "band_brilliance", "band_air"]
HOSVD_RANKS = (8, 8, 2)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("sources", nargs="+")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    out_root = Path(args.out)
    out_root.mkdir(parents=True, exist_ok=True)
    summary: dict = {"schema_version": "mamse-010-real-cases-v1", "cases": []}

    for src in args.sources:
        path = Path(src)
        samples, sr = sf.read(path, always_2d=True)
        samples = samples.astype(np.float32)
        case_name = path.stem
        case_dir = out_root / case_name
        case_dir.mkdir(parents=True, exist_ok=True)
        duration_ms = int(len(samples) / sr * 1000)
        rep = build_representation(samples, sr, source_sha256=f"real:{case_name}")
        planes = {sid: {
            "values": np.asarray(rep.planes[sid].values),
            "feature_names": list(rep.planes[sid].feature_names),
            "window_starts_ms": np.asarray(rep.planes[sid].window_starts_ms),
            "window_ends_ms": np.asarray(rep.planes[sid].window_ends_ms),
        } for sid in ("S0", "S1", "S2")}

        sfv = build_scale_feature_tensor(planes, feature_names=FEATURE_NAMES, duration_ms=duration_ms)
        csv = build_channel_spectral_tensor(samples, sr)
        bundle = AuditoryTensorBundle(
            source_sha256=f"real:{case_name}",
            fields={"scale_feature_view": sfv, "channel_spectral_view": csv},
            profile_ids={"tensor": "mamse010-tensor-v0.1", "representation": rep.representation_version},
        )
        save_bundle(bundle, case_dir)

        model = hosvd(csv.data, HOSVD_RANKS)
        rec = model.reconstruct()
        residual_by_time = relative_residual_by_time(csv.data, csv.data - rec, time_mode=0)
        time_s = np.asarray(csv.axes[0].values)
        # top-3 localization candidates by residual (anonymous)
        order = np.argsort(residual_by_time)[::-1][:3]
        localizations = [
            {"time_s": float(time_s[i]), "relative_residual": float(residual_by_time[i])}
            for i in sorted(order.tolist())
        ]
        entry = {
            "case": case_name,
            "source": str(path),
            "duration_s": round(len(samples) / sr, 3),
            "tensor_id": bundle.tensor_id,
            "scale_feature_shape": list(sfv.data.shape),
            "scale_feature_valid_fraction": round(float(np.mean(sfv.valid_mask)), 4),
            "channel_spectral_shape": list(csv.data.shape),
            "hosvd_ranks": list(HOSVD_RANKS),
            "hosvd_model_id": model.model_id,
            "hosvd_relative_error": float(np.linalg.norm(csv.data - rec) / np.linalg.norm(csv.data)),
            "localization_candidates": localizations,
        }
        summary["cases"].append(entry)
        (case_dir / "tensor_summary.json").write_text(
            json.dumps(entry, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        loc = ", ".join(f"{item['time_s']:.1f}s(r={item['relative_residual']:.3f})" for item in localizations)
        print(f"done {case_name}: tensor={bundle.tensor_id[:12]} sfv={sfv.data.shape} "
              f"csv={csv.data.shape} hosvd_err={entry['hosvd_relative_error']:.4f} | top: {loc}")

    (out_root / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"summary -> {out_root / 'summary.json'}")


if __name__ == "__main__":
    main()
