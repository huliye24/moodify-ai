"""Verify an exported master (e.g. from Audition handoff) against its source.

Usage:
    python scripts/verify_exported_master.py <before.wav> <after.wav> [--out report.md]

Outputs JSON (stdout) + optional markdown report with:
  LUFS (pyloudnorm integrated), True Peak dBTP (ITU-R BS.1771 4x oversampling),
  peak/RMS/crest, pseudo-MRS + MRS Open delta, 6-band spectral deltas,
  and a PASS / REPROCESS verdict.

Verdict rules (configurable):
  - true peak after  <= tp_ceiling_dbtp        (default -1.0)
  - LUFS after       in [lufs_min, lufs_max]   (default [-16, -9])
  - MRS delta        >= mrs_min_delta          (default -0.5, no regression)
  - duration match   |dt| < 0.5 s
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "moodify-core-package" / "src"))

BANDS = {"sub": (20, 60), "bass": (60, 250), "low_mid": (250, 500),
         "mid": (500, 2000), "presence": (2000, 6000), "air": (6000, 20000)}


@dataclass
class Verdict:
    decision: str
    reasons: list = field(default_factory=list)
    measurements: dict = field(default_factory=dict)


def _load(path: Path) -> tuple[np.ndarray, int]:
    import soundfile as sf
    y, sr = sf.read(str(path), dtype="float64")
    if y.ndim == 1:
        y = np.column_stack([y, y])
    return y, int(sr)


def _lufs(y: np.ndarray, sr: int) -> float | None:
    try:
        import pyloudnorm as pn
        meter = pn.Meter(sr)
        return round(float(meter.integrated_loudness(y)), 1)
    except Exception:
        return None


def _true_peak(y: np.ndarray, sr: int) -> float:
    from moodify.processing.limiter import measure_true_peak
    return round(measure_true_peak(y, sr), 2)


def _band_energies(y: np.ndarray, sr: int) -> dict[str, float]:
    import librosa
    mono = y.mean(axis=1)
    spec = np.abs(librosa.stft(mono, n_fft=2048)) ** 2
    freqs = librosa.fft_frequencies(sr=sr, n_fft=2048)
    out = {}
    for name, (lo, hi) in BANDS.items():
        mask = (freqs >= lo) & (freqs <= hi)
        energy = float(np.sum(spec[mask]))
        out[name] = round(10.0 * np.log10(max(energy, 1e-12)), 2)
    return out


def _mrs(before_path: str, after_path: str) -> dict:
    from moodify_runtime.mrs_engine import score_audio
    result = score_audio(before_path=before_path, after_path=after_path)
    return {k: result.to_dict()[k] for k in (
        "pseudo_mrs_before", "pseudo_mrs_after", "pseudo_mrs_delta",
        "mrs_open_before", "mrs_open_after", "mrs_open_delta",
        "mrs_open_available", "over_dark_level", "over_dark_affected_bands",
        "gate_decision", "gate_reasons")}


def verify(before: Path, after: Path, *,
           tp_ceiling: float = -1.0,
           lufs_range: tuple[float, float] = (-16.0, -9.0),
           mrs_min_delta: float = -0.5) -> Verdict:
    y_b, sr_b = _load(before)
    y_a, sr_a = _load(after)
    measurements: dict = {
        "before": {"path": str(before), "sample_rate": sr_b,
                   "duration_s": round(len(y_b) / sr_b, 3)},
        "after": {"path": str(after), "sample_rate": sr_a,
                  "duration_s": round(len(y_a) / sr_a, 3)},
    }
    for side, y, sr in (("before", y_b, sr_b), ("after", y_a, sr_a)):
        peak = float(np.max(np.abs(y)))
        rms = float(np.sqrt(np.mean(y.astype(np.float64) ** 2)))
        measurements[side].update({
            "peak_db": round(20 * np.log10(max(peak, 1e-12)), 2),
            "rms_db": round(20 * np.log10(max(rms, 1e-12)), 2),
            "crest_factor": round(20 * np.log10(max(peak, 1e-12)) - 20 * np.log10(max(rms, 1e-12)), 2),
            "lufs": _lufs(y, sr),
            "true_peak_dbtp": _true_peak(y, sr),
        })
    measurements["bands_before"] = _band_energies(y_b, sr_b)
    measurements["bands_after"] = _band_energies(y_a, sr_a)
    measurements["band_deltas"] = {name: round(
        measurements["bands_after"][name] - measurements["bands_before"][name], 2)
        for name in BANDS}
    measurements["mrs"] = _mrs(str(before), str(after))

    reasons: list[str] = []
    duration_diff = abs(len(y_a) / sr_a - len(y_b) / sr_b)
    if duration_diff > 0.5:
        reasons.append(f"duration_mismatch:{round(duration_diff, 2)}s")
    tp_after = measurements["after"]["true_peak_dbtp"]
    if tp_after > tp_ceiling:
        reasons.append(f"true_peak_above_ceiling:{tp_after}dbtp(>={tp_ceiling})")
    lufs_after = measurements["after"]["lufs"]
    if lufs_after is not None and not (lufs_range[0] <= lufs_after <= lufs_range[1]):
        reasons.append(f"lufs_out_of_range:{lufs_after}(target {lufs_range[0]}..{lufs_range[1]})")
    mrs_delta = measurements["mrs"].get("pseudo_mrs_delta")
    if mrs_delta is not None and mrs_delta < mrs_min_delta:
        reasons.append(f"mrs_delta_below_floor:{round(mrs_delta, 2)}(>={mrs_min_delta})")
    if measurements["mrs"].get("over_dark_level") not in (None, "none"):
        reasons.append(f"over_dark:{measurements['mrs'].get('over_dark_level')}")

    decision = "PASS" if not reasons else "REPROCESS"
    return Verdict(decision=decision, reasons=reasons, measurements=measurements)


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify an exported master against its source")
    parser.add_argument("before")
    parser.add_argument("after")
    parser.add_argument("--out", default="", help="optional markdown report path")
    parser.add_argument("--tp-ceiling", type=float, default=-1.0)
    parser.add_argument("--lufs-min", type=float, default=-16.0)
    parser.add_argument("--lufs-max", type=float, default=-9.0)
    parser.add_argument("--mrs-min-delta", type=float, default=-0.5)
    args = parser.parse_args()

    result = verify(Path(args.before), Path(args.after),
                    tp_ceiling=args.tp_ceiling,
                    lufs_range=(args.lufs_min, args.lufs_max),
                    mrs_min_delta=args.mrs_min_delta)
    print(json.dumps({"decision": result.decision, "reasons": result.reasons,
                      "measurements": result.measurements}, indent=2, ensure_ascii=False))
    if args.out:
        _write_report(Path(args.out), result, args)
    return 0 if result.decision == "PASS" else 2


def _write_report(path: Path, result: Verdict, args: argparse.Namespace) -> None:
    m = result.measurements
    lines = [
        "# Master Verification Report",
        "",
        f"- decision: **{result.decision}**",
        f"- reasons: {result.reasons or 'none'}",
        "",
        "| metric | before | after |",
        "|---|---:|---:|",
    ]
    for key in ("peak_db", "rms_db", "crest_factor", "lufs", "true_peak_dbtp"):
        lines.append(f"| {key} | {m['before'].get(key)} | {m['after'].get(key)} |")
    lines.append("")
    lines.append("## Band deltas (dB)")
    lines.append("| band | delta |")
    lines.append("|---|---:|")
    for name, delta in m["band_deltas"].items():
        lines.append(f"| {name} | {delta} |")
    lines.append("")
    lines.append("## MRS")
    for key, value in m["mrs"].items():
        lines.append(f"- {key}: {value}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
