"""craft_slider.py — 滑动工艺探针：逐层叠加 → 峰值 + 强度微调。

Usage:
  python craft_slider.py <audio.wav> [--output-dir outputs] [--no-finetune]

Algorithm:
  1. Layer stacking: L1(clean) → L2(warm/wide) → L3(...) → until MRS drops
  2. Intensity sweep: at peak, try last preset at [25%, 50%, 75%, 100%, 125%]
  3. Report best intensity + deliver final output
"""

import json
import sys
import time
from pathlib import Path

import numpy as np
import soundfile as sf

from moodify.audio_io import load_audio
from moodify.processing.pedalboard_chain import MoodifyDSPChain
from moodify.v01_analyzer import analyze
from moodify.v01_pipeline import process_audio
from moodify.v01_presets import get_preset

# ── Neutral params: "zero effect" baseline for intensity interpolation ──
NEUTRAL_PARAMS: dict[str, float] = {
    "P01_vocal_presence_freq": 3000.0,
    "P02_vocal_presence_gain": 0.0,
    "P03_vocal_presence_q": 0.5,
    "P04_proximity_low_freq": 200.0,
    "P05_proximity_low_gain": 0.0,
    "P06_compression_ratio": 1.0,
    "P07_compression_attack": 35.0,
    "P08_compression_release": 250.0,
    "P09_compression_threshold": 0.0,
    "P10_reverb_t60": 0.0,
    "P11_reverb_dry_wet": 0.0,
    "P12_reverb_width": 1.0,
    "P13_harmonic_drive": 0.0,
    "P14_high_shelf_freq": 12000.0,
    "P15_high_shelf_gain": 0.0,
}


def _extract_mrs(report_path: str) -> float | None:
    try:
        with open(report_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return float(data["quality_gate"]["mrs_after"])
    except Exception:
        return None


def _extract_damage(report_path: str) -> float | None:
    try:
        with open(report_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return float(data["quality_gate"]["damage_loss"])
    except Exception:
        return None


def _compute_mrs_proxy(metrics) -> float:
    """Inline MRS proxy — matches v01_pipeline._mrs_proxy."""
    def clamp(v, lo=0.0, hi=1.0):
        return max(lo, min(hi, v))
    dynamic = clamp(1.0 - abs(metrics.dynamic_range_db - 10.0) / 20.0)
    crest = clamp(1.0 - abs(metrics.crest_factor - 5.0) / 8.0)
    if metrics.channels == 1:
        stereo = 0.7
    else:
        stereo = clamp(1.0 - abs(metrics.correlation_lr - 0.6) / 0.8)
    air = clamp(1.0 - abs(metrics.rms_air + 18.0) / 22.0)
    presence = clamp(1.0 - abs(metrics.rms_presence + 12.0) / 22.0)
    peak = clamp(1.0 - max(0.0, metrics.peak_db + 0.2) / 6.0)
    return round(800.0 + 400.0 * ((dynamic + crest + stereo + air + presence + peak) / 6.0), 1)


def _blend_params(full_params: dict[str, float], intensity: float) -> dict[str, float]:
    """Interpolate between NEUTRAL (0%) and full_params (100%)."""
    return {
        key: NEUTRAL_PARAMS[key] + (full_params[key] - NEUTRAL_PARAMS[key]) * intensity
        for key in full_params
    }


def _intensity_sweep(input_path: str, preset_key: str, output_dir: str,
                     intensities: list[float] | None = None,
                     base_label: str = "") -> list[dict]:
    """Try a preset at multiple intensities on the same input audio.

    Args:
        input_path: the audio to process (penultimate layer output)
        preset_key: which preset to sweep (e.g. "warm_vocal", "wide_space")
        output_dir: where to write output WAVs
        intensities: list of intensity fractions (default: 0.25, 0.50, 0.75, 1.00, 1.25)
        base_label: prefix for output filenames

    Returns list of {intensity, mrs, path, preset}
    """
    if intensities is None:
        intensities = [0.25, 0.50, 0.75, 1.00, 1.25]

    preset_info = get_preset(preset_key)
    if preset_info is None:
        print(f"  ERROR: unknown preset '{preset_key}'")
        return []
    full_params = preset_info["params"]

    audio, sr = load_audio(input_path, always_2d=False)
    stem = Path(input_path).stem

    results = []
    for intensity in intensities:
        blended = _blend_params(full_params, intensity)
        chain = MoodifyDSPChain(blended)
        processed = chain.process(audio, sr)
        processed = np.nan_to_num(processed, nan=0.0, posinf=0.0, neginf=0.0).astype("float32")

        pct_label = f"{intensity:.0%}".replace("%", "pct")
        label = f"{base_label}_{preset_key}_{pct_label}" if base_label else f"{stem}_{preset_key}_{pct_label}"
        out_path = str(Path(output_dir) / f"{label}.wav")
        sf.write(out_path, processed, sr)

        metrics = analyze(out_path, output_dir, label=f"sweep_{pct_label}")
        mrs = _compute_mrs_proxy(metrics)

        results.append({
            "intensity": intensity,
            "mrs": mrs,
            "path": out_path,
            "preset": preset_key,
        })

    return results


def slide(input_path: str, output_dir: str = "outputs",
          fine_tune: bool = True) -> dict:
    """Run iterative layer stacking + optional intensity sweep.

    Returns dict with keys: optimal_path, optimal_mrs, optimal_layer, curve,
    sweep_results, total_elapsed_s
    """
    t_start = time.perf_counter()
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    presets = ["warm_vocal", "wide_space"]

    curve: list[dict] = []
    current_input = input_path
    chain_label = Path(input_path).stem

    # ── L1: clean_master baseline ──
    print(f"\n{'='*60}")
    print(f"CRAFT SLIDER — {Path(input_path).name}")
    print(f"{'='*60}")

    print("\n[L1] clean_master (baseline)")
    result = process_audio(current_input, "clean_master", output_dir)
    if not result.success:
        print(f"  FAILED: {result.error}")
        return {"optimal_path": "", "optimal_mrs": 0, "optimal_layer": 0,
                "curve": curve, "sweep_results": [], "total_elapsed_s": 0}

    mrs = _extract_mrs(result.report_path) or 0
    damage = _extract_damage(result.report_path) or 0
    curve.append({"layer": 1, "chain": "clean_master", "mrs": mrs, "damage": damage,
                  "path": result.output_path, "preset": "clean_master"})
    current_input = result.output_path
    chain_label += "_clean"
    best_mrs = mrs
    best_path = result.output_path
    best_layer = 1
    best_preset = "clean_master"
    prev_input = input_path  # input to the best layer
    print(f"  MRS={mrs:.0f}  damage={damage:.3f}  gate={'PASS' if result.quality_gate.passed else 'review'}")

    # ── Iterative layer stacking ──
    layer = 1
    used_presets: list[str] = []  # ordered list of presets used

    while True:
        layer += 1
        last_preset = used_presets[-1] if used_presets else "clean_master"
        candidates = []
        for preset in presets:
            if preset == last_preset:
                continue
            print(f"\n[L{layer}] trying {preset} on L{layer-1} output...")
            result = process_audio(current_input, preset, output_dir)
            if not result.success:
                print(f"  FAILED: {result.error}")
                continue
            mrs_after = _extract_mrs(result.report_path) or 0
            damage_after = _extract_damage(result.report_path) or 0
            print(f"  MRS={mrs_after:.0f}  damage={damage_after:.3f}  gate={'PASS' if result.quality_gate.passed else 'review'}")
            candidates.append((preset, result.output_path, result.report_path,
                             mrs_after, damage_after))

        if not candidates:
            print(f"\n  No valid candidates at L{layer}, stopping.")
            break

        best_candidate = max(candidates, key=lambda x: x[3])
        preset_name, cand_path, cand_report, cand_mrs, cand_damage = best_candidate

        if cand_mrs < best_mrs:
            print(f"\n  *** MRS REGRESSION: {best_mrs:.0f} -> {cand_mrs:.0f} (delta={cand_mrs - best_mrs:+.0f})")
            print(f"  *** PEAK found at L{best_layer}: MRS={best_mrs:.0f}")
            break

        # Improvement — accept
        prev_input = current_input
        best_mrs = cand_mrs
        best_path = cand_path
        best_layer = layer
        best_preset = preset_name
        current_input = cand_path
        chain_label += f"_{preset_name[:4]}"
        used_presets.append(preset_name)
        curve.append({"layer": layer, "chain": chain_label, "mrs": cand_mrs,
                      "damage": cand_damage, "path": cand_path, "preset": preset_name})
        print(f"  -> ACCEPTED (MRS +{cand_mrs - curve[-2]['mrs']:.0f})")

        if layer >= 8:
            print("\n  Max layers (8) reached, stopping.")
            break

    # ── Intensity Sweep (fine-tune the last layer) ──
    sweep_results: list[dict] = []
    if fine_tune and best_layer >= 2:
        print(f"\n{'='*60}")
        print(f"INTENSITY SWEEP — fine-tuning L{best_layer} ({best_preset})")
        print(f"{'='*60}")
        print(f"\n  Sweeping {best_preset} at [25%, 50%, 75%, 100%, 125%] on L{best_layer-1} output...")

        sweep_results = _intensity_sweep(
            input_path=prev_input,
            preset_key=best_preset,
            output_dir=output_dir,
            base_label=chain_label.replace(f"_{best_preset[:4]}", ""),
        )

        # Find best intensity
        if sweep_results:
            best_sweep = max(sweep_results, key=lambda x: x["mrs"])
            print("\n  Intensity curve:")
            for r in sweep_results:
                marker = " <-- BEST" if r is best_sweep else ""
                print(f"    {r['intensity']:.0%}:  MRS={r['mrs']:.0f}{marker}")

            if best_sweep["mrs"] > best_mrs:
                print(f"\n  *** INTENSITY WIN: {best_sweep['intensity']:.0%} beats 100% by +{best_sweep['mrs'] - best_mrs:.0f} MRS")
                best_mrs = best_sweep["mrs"]
                best_path = best_sweep["path"]
            elif best_sweep["mrs"] == best_mrs and best_sweep["intensity"] < 1.0:
                print(f"\n  *** EFFICIENCY WIN: {best_sweep['intensity']:.0%} = same MRS with less processing")
                best_path = best_sweep["path"]
            else:
                print("\n  Full intensity (100%) is optimal — no gain from tweaking.")

    # ── Report ──
    elapsed = time.perf_counter() - t_start
    print(f"\n{'='*60}")
    print(f"SLIDE COMPLETE — {elapsed:.0f}s")
    print(f"{'='*60}")
    print("\n  Curve:")
    for entry in curve:
        marker = " <-- PEAK LAYER" if entry["layer"] == best_layer else ""
        print(f"    L{entry['layer']}: {entry['chain']:50s}  MRS={entry['mrs']:.0f}  damage={entry['damage']:.3f}{marker}")
    print(f"\n  Best: L{best_layer} — {best_path}")
    print(f"  MRS: {best_mrs:.0f}")
    print(f"  Total elapsed: {elapsed:.0f}s")

    return {
        "optimal_path": best_path,
        "optimal_mrs": best_mrs,
        "optimal_layer": best_layer,
        "optimal_chain": chain_label,
        "curve": curve,
        "sweep_results": sweep_results,
        "total_elapsed_s": elapsed,
    }


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Craft Slider — 滑动探针 + 强度微调")
    parser.add_argument("audio_path", help="input audio file path")
    parser.add_argument("--output-dir", default="outputs", help="output directory")
    parser.add_argument("--no-finetune", action="store_true",
                        help="skip intensity sweep phase")
    args = parser.parse_args()

    if not Path(args.audio_path).exists():
        print(f"ERROR: File not found: {args.audio_path}")
        return 1

    slide(args.audio_path, args.output_dir, fine_tune=not args.no_finetune)
    return 0


if __name__ == "__main__":
    sys.exit(main())
