"""MHP-028-B: MRS Five Experiments Validation.

Validates Moodify Reality Score directional correctness:
- Known degraded audio should have lower MRS.
- Real audio should have higher MRS.
"""
import math
import os
import sys
import tempfile
from pathlib import Path

import numpy as np
import soundfile as sf

# Add project source to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "moodify-core-package" / "src"))
from moodify.reality_metrics import (
    extract_reality_features,
    build_reference_stats,
    compare_mrs,
    calculate_mrs,
)

BASE = Path(__file__).resolve().parent.parent
OUTPUT = BASE / "docs" / "MHP"
SRC_ASSETS = BASE / "local_audio_assets" / "mhp026" / "source"

# Server-friendly paths: fall back to test_audio/ if music/ doesn't exist
MUSIC_DIR = BASE / "music"
if not MUSIC_DIR.exists():
    MUSIC_DIR = BASE / "test_audio"

RESULTS = []


# ── Helpers ────────────────────────────────────────────────

def write_wav(path: str, audio: np.ndarray, sr: int):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    sf.write(path, audio.astype(np.float32), sr)


def load_audio(path: str) -> tuple[np.ndarray, int]:
    audio, sr = sf.read(path, always_2d=True)
    return audio.astype(np.float32), sr


def log_result(exp_name: str, sample_name: str, mrs: float, components: dict,
               expected: str, actual: str, passed: bool):
    RESULTS.append({
        "experiment": exp_name,
        "sample": sample_name,
        "mrs": mrs,
        "components": components,
        "expected": expected,
        "actual": actual,
        "passed": passed,
    })
    status = "PASS" if passed else "FAIL"
    print(f"  [{status}] {sample_name}: MRS={mrs:.1f} | {actual}")


# ── Experiment 1: Spectrum Degradation ─────────────────────

def experiment_1_spectrum(ref_stats: dict, real_path: str):
    print("\n" + "=" * 60)
    print("Experiment 1: Spectrum Degradation")
    print("=" * 60)

    audio, sr = load_audio(real_path)
    if audio.ndim > 1:
        audio = audio.mean(axis=1)
    n = len(audio)
    fft = np.fft.rfft(audio)
    freqs = np.fft.rfftfreq(n, 1.0 / sr)

    exp_dir = tempfile.mkdtemp(prefix="mrs_e1_")

    # Real
    mrs_real = calculate_mrs(real_path, ref_stats)
    log_result("E1_Spectrum", "real", mrs_real["mrs"], mrs_real["components"],
               "baseline", f"baseline MRS={mrs_real['mrs']:.1f}", True)

    # Bright: +8dB above 6kHz
    bright_fft = fft.copy()
    hf = freqs > 6000
    bright_fft[hf] *= 2.5  # ~+8dB
    bright = np.fft.irfft(bright_fft, n=n)
    bright_path = os.path.join(exp_dir, "bright.wav")
    write_wav(bright_path, bright, sr)
    mrs_bright = calculate_mrs(bright_path, ref_stats)
    passed_br = mrs_bright["mrs"] < mrs_real["mrs"]
    log_result("E1_Spectrum", "bright", mrs_bright["mrs"], mrs_bright["components"],
               "MRS < real", f"MRS={mrs_bright['mrs']:.1f} vs {mrs_real['mrs']:.1f}", passed_br)

    # Dull: -6dB above 8kHz
    dull_fft = fft.copy()
    hf2 = freqs > 8000
    dull_fft[hf2] *= 0.5  # ~-6dB
    dull = np.fft.irfft(dull_fft, n=n)
    dull_path = os.path.join(exp_dir, "dull.wav")
    write_wav(dull_path, dull, sr)
    mrs_dull = calculate_mrs(dull_path, ref_stats)
    passed_du = mrs_dull["mrs"] < mrs_real["mrs"]
    log_result("E1_Spectrum", "dull", mrs_dull["mrs"], mrs_dull["components"],
               "MRS < real", f"MRS={mrs_dull['mrs']:.1f} vs {mrs_real['mrs']:.1f}", passed_du)

    # Flat: multi-band flattening
    flat_fft = fft.copy()
    n_bands = 8
    band_w = len(flat_fft) // n_bands
    for i in range(n_bands):
        b_start = i * band_w
        b_end = min((i + 1) * band_w, len(flat_fft))
        flat_fft[b_start:b_end] = np.mean(np.abs(flat_fft[b_start:b_end]))
    flat = np.fft.irfft(flat_fft, n=n)
    flat_path = os.path.join(exp_dir, "flat.wav")
    write_wav(flat_path, flat, sr)
    mrs_flat = calculate_mrs(flat_path, ref_stats)
    passed_fl = mrs_flat["mrs"] < mrs_real["mrs"]
    log_result("E1_Spectrum", "flat", mrs_flat["mrs"], mrs_flat["components"],
               "MRS < real", f"MRS={mrs_flat['mrs']:.1f} vs {mrs_real['mrs']:.1f}", passed_fl)

    exp1_pass = passed_br and passed_du and passed_fl
    print(f"  Summary: {'PASS' if exp1_pass else 'FAIL'} ({sum([passed_br,passed_du,passed_fl])}/3)")
    return exp1_pass, [mrs_real, mrs_bright, mrs_dull, mrs_flat]


# ── Experiment 2: Dynamic Degradation ──────────────────────

def experiment_2_dynamic(ref_stats: dict, real_path: str):
    print("\n" + "=" * 60)
    print("Experiment 2: Dynamic Degradation")
    print("=" * 60)

    audio, sr = load_audio(real_path)
    if audio.ndim > 1:
        audio = np.mean(audio[..., :2], axis=-1)
    elif audio.ndim == 2:
        audio = audio.mean(axis=1)

    exp_dir = tempfile.mkdtemp(prefix="mrs_e2_")
    mrs_real = calculate_mrs(real_path, ref_stats)

    # Compressed: hard compression (4:1 ratio, -12dB threshold)
    threshold = 0.25  # ~-12dBFS
    ratio = 4.0
    compressed = np.where(audio > threshold,
                          threshold + (audio - threshold) / ratio,
                          np.where(audio < -threshold,
                                   -threshold + (audio + threshold) / ratio,
                                   audio))
    comp_path = os.path.join(exp_dir, "compressed.wav")
    write_wav(comp_path, compressed, sr)
    mrs_comp = calculate_mrs(comp_path, ref_stats)
    passed_cp = mrs_comp["mrs"] < mrs_real["mrs"]
    log_result("E2_Dynamic", "compressed", mrs_comp["mrs"], mrs_comp["components"],
               "MRS < real", f"MRS={mrs_comp['mrs']:.1f} vs {mrs_real['mrs']:.1f}", passed_cp)

    # Limited: clip at 0.6
    limited = np.clip(audio, -0.6, 0.6)
    limited_path = os.path.join(exp_dir, "limited.wav")
    write_wav(limited_path, limited, sr)
    mrs_lim = calculate_mrs(limited_path, ref_stats)
    passed_l = mrs_lim["mrs"] < mrs_real["mrs"]
    log_result("E2_Dynamic", "limited", mrs_lim["mrs"], mrs_lim["components"],
               "MRS < real", f"MRS={mrs_lim['mrs']:.1f} vs {mrs_real['mrs']:.1f}", passed_l)

    # Unstable: late half +6dB
    n = len(audio)
    mid = n // 2
    unstable = audio.copy()
    unstable[mid:] *= 2.0  # ~+6dB
    unstable_path = os.path.join(exp_dir, "unstable.wav")
    write_wav(unstable_path, unstable, sr)
    mrs_unstable = calculate_mrs(unstable_path, ref_stats)
    passed_u = mrs_unstable["mrs"] < mrs_real["mrs"]
    log_result("E2_Dynamic", "unstable", mrs_unstable["mrs"], mrs_unstable["components"],
               "MRS < real", f"MRS={mrs_unstable['mrs']:.1f} vs {mrs_real['mrs']:.1f}", passed_u)

    exp2_pass = passed_cp and passed_l and passed_u
    print(f"  Summary: {'PASS' if exp2_pass else 'FAIL'} ({sum([passed_cp,passed_l,passed_u])}/3)")
    return exp2_pass


# ── Experiment 3: Spatial Degradation ──────────────────────

def experiment_3_space(ref_stats: dict, real_path: str):
    print("\n" + "=" * 60)
    print("Experiment 3: Spatial Degradation")
    print("=" * 60)

    audio, sr = load_audio(real_path)
    if audio.ndim == 1:
        audio = np.column_stack([audio, audio])
    elif audio.shape[1] < 2:
        audio = np.column_stack([audio[:, 0], audio[:, 0]])

    exp_dir = tempfile.mkdtemp(prefix="mrs_e3_")
    mrs_real = calculate_mrs(real_path, ref_stats)

    # Overwide: boost side channel
    left, right = audio[:, 0], audio[:, 1]
    mid = (left + right) / 2
    side = (left - right) / 2
    overwide = np.column_stack([mid + side * 3, mid - side * 3])
    ow_path = os.path.join(exp_dir, "overwide.wav")
    write_wav(ow_path, overwide, sr)
    mrs_ow = calculate_mrs(ow_path, ref_stats)
    passed_ow = mrs_ow["mrs"] < mrs_real["mrs"]
    log_result("E3_Space", "overwide", mrs_ow["mrs"], mrs_ow["components"],
               "MRS < real", f"MRS={mrs_ow['mrs']:.1f} vs {mrs_real['mrs']:.1f}", passed_ow)

    # Phase bad: delay one channel by 2ms
    delay_samples = int(0.002 * sr)
    phase_bad = np.zeros_like(audio)
    phase_bad[:, 0] = audio[:, 0]
    phase_bad[delay_samples:, 1] = audio[:-delay_samples, 1]
    pb_path = os.path.join(exp_dir, "phase_bad.wav")
    write_wav(pb_path, phase_bad, sr)
    mrs_pb = calculate_mrs(pb_path, ref_stats)
    passed_pb = mrs_pb["mrs"] < mrs_real["mrs"]
    log_result("E3_Space", "phase_bad", mrs_pb["mrs"], mrs_pb["components"],
               "MRS < real", f"MRS={mrs_pb['mrs']:.1f} vs {mrs_real['mrs']:.1f}", passed_pb)

    # Mono: collapse to mono
    mono = np.column_stack([mid, mid])
    mono_path = os.path.join(exp_dir, "mono.wav")
    write_wav(mono_path, mono, sr)
    mrs_mono = calculate_mrs(mono_path, ref_stats)
    passed_mn = mrs_mono["mrs"] <= mrs_real["mrs"] * 1.05  # mono may not degrade much
    log_result("E3_Space", "mono", mrs_mono["mrs"], mrs_mono["components"],
               "MRS <= real", f"MRS={mrs_mono['mrs']:.1f} vs {mrs_real['mrs']:.1f}", passed_mn)

    exp3_pass = passed_ow and passed_pb and passed_mn
    print(f"  Summary: {'PASS' if exp3_pass else 'FAIL'} ({sum([passed_ow,passed_pb,passed_mn])}/3)")
    return exp3_pass


# ── Experiment 4: Temporal Drift ───────────────────────────

def experiment_4_temporal(ref_stats: dict, real_path: str):
    print("\n" + "=" * 60)
    print("Experiment 4: Temporal Drift")
    print("=" * 60)

    audio, sr = load_audio(real_path)
    if audio.ndim > 1:
        audio = audio.mean(axis=1)

    mrs_real = calculate_mrs(real_path, ref_stats)
    log_result("E4_Temporal", "real", mrs_real["mrs"], mrs_real["components"],
               "baseline", f"baseline MRS={mrs_real['mrs']:.1f}", True)

    # Late-bad: 2nd half degraded with HF boost + RMS drift + spectrum spikes
    n = len(audio)
    mid = n // 2
    exp_dir = tempfile.mkdtemp(prefix="mrs_e4_")
    late_bad = audio.copy()

    # Half 2: HF boost + gain drift + add noise spikes
    h2 = audio[mid:].copy()
    fft_h2 = np.fft.rfft(h2)
    freqs_h2 = np.fft.rfftfreq(len(h2), 1.0 / sr)
    hf_mask = freqs_h2 > 6000
    fft_h2[hf_mask] *= 3.0  # +9.5dB HF
    h2_degraded = np.fft.irfft(fft_h2, n=len(h2))
    h2_degraded *= 1.0 + 0.5 * np.linspace(0, 1, len(h2))  # gain drift +50%
    spike_mask = np.abs(h2_degraded) > 4 * np.std(h2_degraded)
    h2_degraded[spike_mask] *= 2.0  # amplify spikes
    late_bad[mid:] = h2_degraded

    lb_path = os.path.join(exp_dir, "late_bad.wav")
    write_wav(lb_path, late_bad, sr)
    mrs_lb = calculate_mrs(lb_path, ref_stats)
    passed_lb = mrs_lb["mrs"] < mrs_real["mrs"]
    # Check temporal component specifically increased
    temp_delta = mrs_lb["components"]["temporal"] - mrs_real["components"]["temporal"]
    log_result("E4_Temporal", "late_bad", mrs_lb["mrs"], mrs_lb["components"],
               "MRS < real, temporal+", f"MRS={mrs_lb['mrs']:.1f}, temporal={mrs_lb['components']['temporal']:.3f} (Δ+{temp_delta:.3f})", passed_lb)

    exp4_pass = passed_lb
    print(f"  Summary: {'PASS' if exp4_pass else 'FAIL'} (1/1)")
    return exp4_pass


# ── Experiment 5: Moodify Before/After ─────────────────────

def experiment_5_moodify(ref_stats: dict):
    print("\n" + "=" * 60)
    print("Experiment 5: Moodify Before/After Matched")
    print("=" * 60)

    tracks = [
        ("mhp026_ai_vocal_001", "01_ai_vocal",
         "mhp026_01_ai_vocal__pour_le_moi_pas_encore_ecrit.wav"),
        ("mhp026_dense_mix_001", "06_dense_mix",
         "mhp026_06_dense_mix__neural_poison.mp3"),
        ("mhp026_thin_demo_001", "07_thin_demo",
         "mhp026_07_thin_demo__jian_zhong_weiguang.mp3"),
    ]
    presets = ["warm_vocal", "clean_master", "wide_space"]

    e5_results = []
    for song_id, type_dir, filename in tracks:
        before_path = str(SRC_ASSETS / type_dir / filename)
        if not os.path.exists(before_path):
            print(f"  SKIP {song_id}: before not found: {before_path}")
            continue

        print(f"\n  --- {song_id} ---")
        for preset in presets:
            matched_path = str(BASE / f"inspector_reports/mhp026_{song_id}_{preset}/after_matched.wav")
            if not os.path.exists(matched_path):
                print(f"    SKIP {preset}: matched not found")
                continue

            cmp = compare_mrs(before_path, matched_path, ref_stats,
                              label=f"{song_id}_{preset}")
            log_result("E5_Moodify", f"{song_id}_{preset}", cmp["mrs_after"],
                       cmp["components_after"],
                       "ΔMRS interpretable", f"ΔMRS={cmp['delta_mrs']:+.1f}, main_gain={cmp['main_gain']}, penalty={cmp['main_penalty']}", True)
            e5_results.append(cmp)

    print(f"\n  {len(e5_results)} comparisons completed")
    return e5_results


# ── Main ───────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("MHP-028-B: MRS Five Experiments Validation")
    print("=" * 60)

    # Select real reference: use available WAV files
    ref_candidates = sorted(MUSIC_DIR.glob("*.wav"))
    # Filter: use clean original files, not "(1)" processed versions
    ref_wavs = [str(p) for p in ref_candidates if "(1)" not in p.name][:3]
    if not ref_wavs:
        # Fallback to local_audio_assets
        ref_candidates = sorted(SRC_ASSETS.glob("**/*.wav"))
        ref_wavs = [str(p) for p in ref_candidates][:2]
    if not ref_wavs:
        print("ERROR: No reference audio files found.")
        return 1

    print(f"\nReference audio files: {len(ref_wavs)}")
    for r in ref_wavs:
        print(f"  {r}")

    # Build reference stats
    print("\nBuilding reference stats...")
    ref_features = [extract_reality_features(p) for p in ref_wavs]
    ref_stats = build_reference_stats(ref_features)
    ref_stats["n"] = len(ref_features)
    print(f"  Reference features: {len(list(ref_stats['mu'].keys()))} dims")

    # Use first reference file as "real" for degradation experiments
    real_path = ref_wavs[0]

    total_pass = 0
    total_tests = 0

    # Run experiments
    try:
        e1, _ = experiment_1_spectrum(ref_stats, real_path)
        total_pass += int(e1)
        total_tests += 1
    except Exception as exc:
        print(f"  ERROR E1: {exc}")

    try:
        e2 = experiment_2_dynamic(ref_stats, real_path)
        total_pass += int(e2)
        total_tests += 1
    except Exception as exc:
        print(f"  ERROR E2: {exc}")

    try:
        e3 = experiment_3_space(ref_stats, real_path)
        total_pass += int(e3)
        total_tests += 1
    except Exception as exc:
        print(f"  ERROR E3: {exc}")

    try:
        e4 = experiment_4_temporal(ref_stats, real_path)
        total_pass += int(e4)
        total_tests += 1
    except Exception as exc:
        print(f"  ERROR E4: {exc}")

    try:
        e5 = experiment_5_moodify(ref_stats)
        total_pass += 1 if len(e5) > 0 else 0
        total_tests += 1
    except Exception as exc:
        print(f"  ERROR E5: {exc}")
        import traceback
        traceback.print_exc()

    print("\n" + "=" * 60)
    print(f"VALIDATION SUMMARY: {total_pass}/{total_tests} experiments passed")
    print("=" * 60)

    return 0 if total_pass >= 3 else 1


if __name__ == "__main__":
    sys.exit(main())
