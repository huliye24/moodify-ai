"""Run MAMSE-011 on real cases: covariance models + relation-break probe.

Usage: python scripts/mamse011_run_real_cases.py <source.wav ...> --out <dir>
Input = S1 clean subset (12 features; mid/side + short_term_lufs blocked).
For each case: fit reference model on the first half, project the second
half (Mahalanobis trajectory + quantile fractions). Then a relation-break
injection probe (flip one pair of columns on a copy) demonstrates G29:
combinational anomalies the single metrics cannot see. Cross-case
covariance drift is recorded between tracks.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import soundfile as sf

from moodify.auditory.representation.build import build_representation
from moodify_experimental.mamse011 import (
    CovarianceConfig,
    covariance_drift,
    fit_covariance_model,
    save_model,
)

CLEAN_FEATURES = ["rms_db", "peak_db", "stereo_correlation", "spectral_centroid_hz",
                  "band_sub", "band_bass", "band_low_mid", "band_mid", "band_core_mid",
                  "band_presence", "band_brilliance", "band_air"]
RELATION_BREAK_PAIR = ("rms_db", "band_bass")


def _plane_matrix(rep, scale_id: str) -> tuple[np.ndarray, list[str]]:
    plane = rep.planes[scale_id]
    names = list(plane.feature_names)
    idx = [names.index(c) for c in CLEAN_FEATURES]
    return np.asarray(plane.values, dtype=np.float64)[:, idx], CLEAN_FEATURES


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("sources", nargs="+")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    out_root = Path(args.out)
    out_root.mkdir(parents=True, exist_ok=True)
    summary: dict = {"schema_version": "mamse-011-real-cases-v1", "input": "S1 clean subset", "cases": []}
    models: dict[str, object] = {}

    for src in args.sources:
        path = Path(src)
        samples, sr = sf.read(path, always_2d=True)
        samples = samples.astype(np.float32)
        case_name = path.stem
        case_dir = out_root / case_name
        case_dir.mkdir(parents=True, exist_ok=True)
        rep = build_representation(samples, sr, source_sha256=f"real:{case_name}")
        X, names = _plane_matrix(rep, "S1")
        n = len(X)
        half = n // 2

        # reference model on first half
        ref = fit_covariance_model(X[:half], names, config=CovarianceConfig(estimator="oas"))
        save_model(ref, case_dir / "reference")

        # frozen projection on second half
        Y = X[half:]
        d2 = ref.mahalanobis_squared(Y)
        q = ref.reference_distance_quantiles
        frac_above_q95 = float(np.mean(d2 > q["q95"]))
        frac_above_q99 = float(np.mean(d2 > q["q99"]))

        # relation-break injection: same second half, but flip the sign of
        # one feature's deviations from its median (breaks its joint
        # relationship with band_bass while leaving marginals unchanged)
        Yb = Y.copy()
        col = names.index(RELATION_BREAK_PAIR[0])
        Yb[:, col] = 2 * np.median(Y[:, col]) - Y[:, col]
        d2b = ref.mahalanobis_squared(Yb)
        frac_b_above_q95 = float(np.mean(d2b > q["q95"]))
        frac_b_above_q99 = float(np.mean(d2b > q["q99"]))

        entry = {
            "case": case_name,
            "source": str(path),
            "duration_s": round(len(samples) / sr, 3),
            "n_rows": n,
            "reference_model_id": ref.model_id,
            "complete_rows": ref.complete_rows,
            "shrinkage_alpha": ref.shrinkage_alpha,
            "effective_rank": float(np.exp(-np.sum(
                np.where(ref.eigenvalues / (ref.eigenvalues.sum() + 1e-12) > 0,
                         ref.eigenvalues / (ref.eigenvalues.sum() + 1e-12) * np.log(ref.eigenvalues / (ref.eigenvalues.sum() + 1e-12) + 1e-12), 0)))),
            "lag1_by_feature": {k: round(v, 3) for k, v in
                                json.loads((case_dir / "reference" / "covariance_summary.json").read_text(encoding="utf-8"))["lag1_autocorrelation_by_feature"].items()},
            "neff_ratio_min": round(float(np.min(ref.effective_sample_size_by_feature) / max(ref.total_rows, 1)), 3),
            "mahalanobis_second_half": {
                "median_d2": round(float(np.median(d2)), 3),
                "frac_above_q95": round(frac_above_q95, 4),
                "frac_above_q99": round(frac_above_q99, 4),
            },
            "relation_break_injection": {
                "feature": RELATION_BREAK_PAIR[0],
                "median_d2": round(float(np.median(d2b)), 3),
                "frac_above_q95": round(frac_b_above_q95, 4),
                "frac_above_q99": round(frac_b_above_q99, 4),
                "increment": "RELATION_BREAK_CANDIDATE" if frac_b_above_q99 > frac_above_q99 + 0.1 else "NO_INCREMENT",
            },
        }
        summary["cases"].append(entry)
        (case_dir / "mamse011_projection.json").write_text(json.dumps(entry, ensure_ascii=False, indent=2), encoding="utf-8")
        models[case_name] = ref
        print(f"done {case_name}: ref={ref.model_id[:12]} eff_rank={entry['effective_rank']:.1f} "
              f"d2_med={entry['mahalanobis_second_half']['median_d2']} "
              f"inject_d2_med={entry['relation_break_injection']['median_d2']}")

    # cross-case drift table
    names_cases = [c["case"] for c in summary["cases"]]
    drift_rows = []
    for i in range(len(names_cases)):
        for j in range(i + 1, len(names_cases)):
            d = covariance_drift(models[names_cases[i]], models[names_cases[j]], top_k=3)
            drift_rows.append({"a": names_cases[i], "b": names_cases[j],
                               "covariance_relative_frobenius": round(d["covariance_relative_frobenius"], 4),
                               "correlation_relative_frobenius": round(d["correlation_relative_frobenius"], 4),
                               "principal_angles_deg": [round(x, 2) for x in d["principal_angles_deg"]],
                               "projector_distance": round(d["projector_distance"], 4)})
    summary["cross_case_drift"] = drift_rows
    (out_root / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    for row in drift_rows:
        print(f"drift {row['a']} vs {row['b']}: corr_frob={row['correlation_relative_frobenius']} "
              f"angles={row['principal_angles_deg']}")
    print(f"summary -> {out_root / 'summary.json'}")


if __name__ == "__main__":
    main()
