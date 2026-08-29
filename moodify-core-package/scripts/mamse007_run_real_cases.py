"""Run MAMSE-007 on real cases via the canonical ScalePlane (read-only).

Usage: python scripts/mamse007_run_real_cases.py <source.wav ...> --out <dir>
Builds S1 planes with the canonical builder, runs semantic preflight
(excluding the audited S1/S2 conflicts), fits CASE_LOCAL PCA, saves
basis/evidence per case, and writes a summary with residual + variance
descriptors. No threshold tuning; no canonical judgment.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import soundfile as sf

from moodify.auditory.representation.build import build_representation
from moodify_experimental.mamse007 import (
    PCAConfig,
    basis_eligible_feature_names,
    fit_pca,
    preflight_features,
    save_result,
)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("sources", nargs="+")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    out_root = Path(args.out)
    out_root.mkdir(parents=True, exist_ok=True)
    summary: dict = {"schema_version": "mamse-007-real-cases-v1", "cases": []}

    for src in args.sources:
        path = Path(src)
        samples, sr = sf.read(path, always_2d=True)
        samples = samples.astype(np.float32)
        case_name = path.stem
        case_dir = out_root / case_name
        case_dir.mkdir(parents=True, exist_ok=True)
        rep = build_representation(samples, sr, source_sha256=f"real:{case_name}")
        plane = rep.planes["S1"]
        x = np.asarray(plane.values, dtype=np.float64)
        feature_names = tuple(plane.feature_names)
        records = preflight_features(feature_names)
        retained, dropped = basis_eligible_feature_names(records, allow_unresolved=True)
        kept_idx = [feature_names.index(n) for n in retained]
        result = fit_pca(x[:, kept_idx], retained, PCAConfig(n_components=3, mode="CASE_LOCAL"),
                         source_meta={"source_sha256": f"real:{case_name}", "case": case_name,
                                      "plane": "S1", "window_ms": plane.window_ms})
        save_result(result, case_dir)
        entry = {
            "case": case_name,
            "source": str(path),
            "duration_s": round(len(samples) / sr, 3),
            "plane": "S1",
            "n_windows": int(x.shape[0]),
            "input_features": len(feature_names),
            "semantic_conflict_dropped": [d for d in dropped if d["reason"] != "UNIT_UNRESOLVED_ALLOWED_EXPLORATORY"],
            "retained_features": result.basis.retained_feature_names,
            "basis_id": result.basis.basis_id,
            "mode": result.basis.mode,
            "explained_variance_ratio": result.basis.explained_variance_ratio.tolist(),
            "cumulative_explained": result.evidence["cumulative_explained_variance"],
            "mean_residual_standardized": result.evidence["mean_reconstruction_residual_standardized"],
            "max_residual_standardized": result.evidence["max_reconstruction_residual_standardized"],
            "imputed_cells": result.evidence["imputed_cells"],
            "runtime_seconds": result.evidence["runtime_seconds"],
        }
        summary["cases"].append(entry)
        print(f"done {case_name}: n={entry['n_windows']} retained={len(entry['retained_features'])} "
              f"cum3={entry['cumulative_explained'][2] if len(entry['cumulative_explained']) > 2 else None:.3f}"
              if len(entry["cumulative_explained"]) > 2 else
              f"done {case_name}: n={entry['n_windows']} retained={len(entry['retained_features'])}")

    (out_root / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"summary -> {out_root / 'summary.json'}")


if __name__ == "__main__":
    main()
