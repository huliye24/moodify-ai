"""MHP-007-A: Moodify Inspector — before/after audio comparison tool.

Generates 6 comparison charts, a metrics JSON, and a markdown report
for a pair of original + processed audio files.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from moodify.audio_io import load_audio

BAND_EDGES = [
    ("sub",      20,   60),
    ("bass",     60,  250),
    ("low_mid", 250,  500),
    ("mid",     500, 2000),
    ("presence",2000, 5000),
    ("air",    8000, 16000),
]

DELTA_INTERPRETATIONS = {
    "peak_delta_db":         "负值=峰值降低，正值=峰值提高",
    "rms_delta_db":          "负值=整体更安静，正值=整体更响",
    "crest_delta":           "负值=动态收紧，正值=动态增强",
    "dynamic_range_delta_db":"负值=响度变化变小，正值=响度变化变大",
    "correlation_delta":     "负值=空间变宽，正值=空间变窄",
    "mid_side_ratio_delta_db":"正值=侧向信息增强，空间更宽",
    "presence_delta_db":     "正值=人声存在感/清晰度可能增强",
    "air_delta_db":          "正值=空气感/高频亮度可能增强",
    "bass_delta_db":         "正值=低频厚度可能增强",
}


# ═══════════════════════════════════════════════════
#  Audio loading
# ═══════════════════════════════════════════════════

def load_stereo(path: str) -> tuple[np.ndarray, int]:
    return load_audio(path, always_2d=True)


def to_mono(audio: np.ndarray) -> np.ndarray:
    if audio.ndim == 1:
        return audio.astype(np.float32)
    return audio.mean(axis=1).astype(np.float32)


# ═══════════════════════════════════════════════════
#  Metrics
# ═══════════════════════════════════════════════════

def compute_basic_metrics(mono: np.ndarray, sr: int) -> dict:
    peak_lin = float(np.max(np.abs(mono)))
    rms_val = float(np.sqrt(np.mean(mono ** 2)))
    return {
        "peak_db": round(20.0 * math.log10(peak_lin + 1e-12), 1),
        "rms_db": round(20.0 * math.log10(rms_val + 1e-12), 1),
        "crest_factor": round(peak_lin / (rms_val + 1e-12), 2),
        "dynamic_range_db": round(_compute_dynamic_range(mono, sr), 1),
    }


def compute_spatial_metrics(audio: np.ndarray) -> dict:
    if audio.ndim < 2 or audio.shape[1] < 2:
        return {"correlation_lr": 1.0, "mid_side_ratio_db": -99.0}

    left = audio[:, 0].astype(np.float64)
    right = audio[:, 1].astype(np.float64)
    corr = float(np.corrcoef(left, right)[0, 1])

    mid = (left + right) / 2.0
    side = (left - right) / 2.0
    rms_mid = np.sqrt(np.mean(mid ** 2)) + 1e-12
    rms_side = np.sqrt(np.mean(side ** 2)) + 1e-12
    ms_ratio = float(20.0 * math.log10(rms_side / rms_mid))

    return {"correlation_lr": round(corr, 3), "mid_side_ratio_db": round(ms_ratio, 1)}


def compute_band_energy(mono: np.ndarray, sr: int) -> dict:
    n = len(mono)
    fft = np.abs(np.fft.rfft(mono * np.hanning(n)))
    freqs = np.fft.rfftfreq(n, 1.0 / sr)
    total = np.sum(fft ** 2) + 1e-12

    bands = {}
    for name, f1, f2 in BAND_EDGES:
        mask = (freqs >= f1) & (freqs <= f2)
        ratio = np.sum(fft[mask] ** 2) / total
        bands[f"{name}_db"] = round(float(20.0 * math.log10(np.sqrt(ratio + 1e-12))), 1)
    return bands


def compute_spectrum_curve(mono: np.ndarray, sr: int) -> tuple[np.ndarray, np.ndarray]:
    n = len(mono)
    fft = np.abs(np.fft.rfft(mono * np.hanning(n)))
    freqs = np.fft.rfftfreq(n, 1.0 / sr)
    db = 20.0 * np.log10(fft / (np.max(fft) + 1e-12) + 1e-12)
    return freqs, db


def compute_spectral_features(mono: np.ndarray, sr: int) -> dict:
    n = len(mono)
    spec = np.abs(np.fft.rfft(mono * np.hanning(n)))
    freqs = np.fft.rfftfreq(n, 1.0 / sr)

    total = np.sum(spec) + 1e-12
    centroid = float(np.sum(freqs * spec) / total)

    cumsum = np.cumsum(spec)
    rolloff_idx = np.searchsorted(cumsum, 0.95 * cumsum[-1])
    rolloff = float(freqs[min(rolloff_idx, len(freqs) - 1)])

    geo_mean = np.exp(np.mean(np.log(spec + 1e-12)))
    arith_mean = np.mean(spec) + 1e-12
    flatness = float(geo_mean / arith_mean)

    return {
        "spectral_centroid": round(centroid, 1),
        "spectral_rolloff_95": round(rolloff, 1),
        "spectral_flatness": round(flatness, 4),
    }


def collect_metrics(audio: np.ndarray, sr: int) -> dict:
    mono = to_mono(audio)
    basic = compute_basic_metrics(mono, sr)
    spatial = compute_spatial_metrics(audio)
    bands = compute_band_energy(mono, sr)
    spectral = compute_spectral_features(mono, sr)
    return {
        "duration_s": round(len(mono) / sr, 1),
        "sample_rate": sr,
        "channels": audio.shape[1] if audio.ndim > 1 else 1,
        "num_samples": len(mono),
        **basic,
        **spatial,
        "bands": bands,
        **spectral,
    }


# ═══════════════════════════════════════════════════
#  Delta
# ═══════════════════════════════════════════════════

def compute_delta(before: dict, after: dict) -> dict:
    delta: dict = {}
    scalar_keys = [
        "peak_db", "rms_db", "crest_factor", "dynamic_range_db",
        "correlation_lr", "mid_side_ratio_db",
        "spectral_centroid", "spectral_rolloff_95", "spectral_flatness",
    ]
    for k in scalar_keys:
        if k in before and k in after:
            dk = k if k.endswith("_db") else k
            if k == "crest_factor" or k == "spectral_flatness":
                delta_key = f"{k}_delta" if not k.endswith("_delta") else k
                delta_key = f"{k}_delta" if "_delta" not in k else k
            else:
                delta_key = f"{k}_delta_db" if not (k.endswith("_db") or k.endswith("_delta")) else f"{k.replace('_db', '_delta_db')}"
            # Simplify: use a simple naming convention
            delta[simple_delta_key(k)] = round(after[k] - before[k], 2)

    for band in ["sub_db", "bass_db", "low_mid_db", "mid_db", "presence_db", "air_db"]:
        if band in before.get("bands", {}) and band in after.get("bands", {}):
            delta[f"{band.replace('_db', '')}_delta_db"] = round(
                after["bands"][band] - before["bands"][band], 1)

    return delta


def simple_delta_key(k: str) -> str:
    if k == "crest_factor":
        return "crest_delta"
    if k == "spectral_flatness":
        return "spectral_flatness_delta"
    if k.endswith("_db"):
        return k.replace("_db", "_delta_db")
    return f"{k}_delta"


# ═══════════════════════════════════════════════════
#  Plots
# ═══════════════════════════════════════════════════

def plot_waveform(before_audio, after_audio, sr_before, sr_after, out_path: str,
                  max_sec: int = 60):
    b_mono = to_mono(before_audio)
    a_mono = to_mono(after_audio)

    b_n = min(len(b_mono), int(max_sec * sr_before))
    a_n = min(len(a_mono), int(max_sec * sr_after))

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 5), sharex=False)

    t_b = np.arange(b_n) / sr_before
    t_a = np.arange(a_n) / sr_after
    ax1.plot(t_b, b_mono[:b_n], color="#3a7ca5", linewidth=0.3)
    ax1.set_ylabel("Before")
    ax1.set_title("Waveform Before → After")
    ax1.set_xlim(0, t_b[-1])

    ax2.plot(t_a, a_mono[:a_n], color="#d4756b", linewidth=0.3)
    ax2.set_ylabel("After")
    ax2.set_xlabel("Time (s)")
    ax2.set_xlim(0, t_a[-1])

    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


def plot_spectrum_overlay(freqs_b, db_b, freqs_a, db_a, out_path: str):
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.semilogx(freqs_b, db_b, color="#3a7ca5", alpha=0.7, linewidth=0.6, label="Before")
    ax.semilogx(freqs_a, db_a, color="#d4756b", alpha=0.7, linewidth=0.6, label="After")
    ax.set_xlabel("Frequency (Hz)")
    ax.set_ylabel("Magnitude (dB, normalized)")
    ax.set_title("Spectrum Overlay")
    ax.legend()
    ax.set_xlim(20, 20000)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


def plot_spectrum_delta(freqs, db_before, db_after, out_path: str):
    # Match length
    n = min(len(db_before), len(db_after))
    delta_curve = db_after[:n] - db_before[:n]

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.semilogx(freqs[:n], delta_curve, color="#6b2fa0", linewidth=0.8)
    ax.axhline(y=0, color="gray", linestyle="--", linewidth=0.8)
    ax.set_xlabel("Frequency (Hz)")
    ax.set_ylabel("Delta (dB)")
    ax.set_title("Spectrum Delta (After − Before)")
    ax.set_xlim(20, 20000)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


def plot_spectrogram(audio, sr: int, out_path: str, title: str = ""):
    mono = to_mono(audio)
    fig, ax = plt.subplots(figsize=(10, 5))
    Pxx, freqs, bins, im = ax.specgram(
        mono, NFFT=2048, Fs=sr, noverlap=1536,
        cmap="inferno", scale="dB", vmin=-80, vmax=0,
    )
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Frequency (Hz)")
    ax.set_ylim(0, 16000)
    ax.set_title(title or "Spectrogram")
    fig.colorbar(im, ax=ax, label="dB").set_label("dB")
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


def plot_band_energy(before_bands: dict, after_bands: dict, out_path: str):
    labels = ["Sub", "Bass", "Low-Mid", "Mid", "Presence", "Air"]
    keys = ["sub_db", "bass_db", "low_mid_db", "mid_db", "presence_db", "air_db"]
    b_vals = [before_bands.get(k, -99) for k in keys]
    a_vals = [after_bands.get(k, -99) for k in keys]

    x = np.arange(len(labels))
    width = 0.35

    fig, ax = plt.subplots(figsize=(8, 5))
    bars_b = ax.bar(x - width / 2, b_vals, width, label="Before",
                    color="#3a7ca5", edgecolor="white")
    bars_a = ax.bar(x + width / 2, a_vals, width, label="After",
                    color="#d4756b", edgecolor="white")

    ax.set_ylabel("dB (relative)")
    ax.set_title("Band Energy Comparison")
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.legend()
    ax.axhline(y=0, color="gray", linestyle="--", linewidth=0.8)

    for bar, val in zip(bars_b, b_vals):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.5,
                f"{val:.1f}", ha="center", fontsize=7)
    for bar, val in zip(bars_a, a_vals):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.5,
                f"{val:.1f}", ha="center", fontsize=7)

    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


# ═══════════════════════════════════════════════════
#  Reports
# ═══════════════════════════════════════════════════

def write_json_report(data: dict, out_path: str):
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _fmt(val, prec: int = 1) -> str:
    if isinstance(val, float):
        return f"{val:+.{prec}f}"
    return str(val)


def write_markdown_report(data: dict, out_path: str):
    before = data["before"]
    after = data["after"]
    delta = data["delta"]
    warnings = data.get("warnings", [])

    lines = [
        "# Moodify Inspector Report",
        "",
        "## Summary",
        "",
        f"- **Preset**: {data.get('preset', '—')}",
        f"- **Before**: `{data['before_path']}`",
        f"- **After**: `{data['after_path']}`",
        f"- **Duration**: {before['duration_s']}s → {after['duration_s']}s",
        f"- **Sample rate**: {before['sample_rate']}Hz → {after['sample_rate']}Hz",
    ]
    if warnings:
        lines.append(f"- **Warnings**: {', '.join(warnings)}")

    # Core metrics table
    metric_rows = [
        ("Peak (dB)", "peak_db", "dB"),
        ("RMS (dB)", "rms_db", "dB"),
        ("Crest Factor", "crest_factor", ""),
        ("Dynamic Range (dB)", "dynamic_range_db", "dB"),
        ("L/R Correlation", "correlation_lr", ""),
        ("Mid/Side Ratio (dB)", "mid_side_ratio_db", "dB"),
    ]
    delta_rows = [
        ("crest_delta", ""),
        ("dynamic_range_delta_db", "dB"),
        ("peak_delta_db", "dB"),
        ("rms_delta_db", "dB"),
        ("correlation_delta", ""),
        ("mid_side_ratio_delta_db", "dB"),
    ]
    lines += [
        "",
        "## Core Metrics",
        "",
        "| Metric | Before | After | Delta | Interpretation |",
        "|--------|--------|-------|-------|---------------|",
    ]
    for label, key, unit in metric_rows:
        bv = _fmt(before.get(key, "—"))
        av = _fmt(after.get(key, "—"))
        # Find matching delta
        dk = simple_delta_key(key)
        dv = _fmt(delta.get(dk, "—"))
        interp = DELTA_INTERPRETATIONS.get(dk, "")
        lines.append(f"| {label} | {bv} | {av} | {dv} | {interp} |")

    # Band energy table
    band_keys = ["sub_db", "bass_db", "low_mid_db", "mid_db", "presence_db", "air_db"]
    band_labels = ["Sub", "Bass", "Low-mid", "Mid", "Presence", "Air"]
    lines += [
        "",
        "## Band Energy (dB)",
        "",
        "| Band | Before | After | Delta |",
        "|------|--------|-------|-------|",
    ]
    for bl, bk in zip(band_labels, band_keys):
        bv = _fmt(before["bands"].get(bk, "—"))
        av = _fmt(after["bands"].get(bk, "—"))
        dk = f"{bk.replace('_db', '')}_delta_db"
        dv = _fmt(delta.get(dk, "—"))
        lines.append(f"| {bl} | {bv} | {av} | {dv} |")

    # Spectral features
    lines += [
        "",
        "## Spectral Features",
        "",
        "| Feature | Before | After | Delta |",
        "|---------|--------|-------|-------|",
    ]
    for key, label in [
        ("spectral_centroid", "Centroid (Hz)"),
        ("spectral_rolloff_95", "Rolloff 95% (Hz)"),
        ("spectral_flatness", "Flatness"),
    ]:
        bv = _fmt(before.get(key, "—"))
        av = _fmt(after.get(key, "—"))
        dk = simple_delta_key(key)
        dv = _fmt(delta.get(dk, "—"))
        lines.append(f"| {label} | {bv} | {av} | {dv} |")

    # Visualizations
    lines += [
        "",
        "## Visualizations",
        "",
    ]
    for fname in [
        "waveform_before_after.png",
        "spectrum_overlay.png",
        "spectrum_delta.png",
        "spectrogram_before.png",
        "spectrogram_after.png",
        "band_energy_comparison.png",
    ]:
        lines.append(f"- [{fname}]({fname})")

    # Listening checklist
    lines += [
        "",
        "## Listening Checklist",
        "",
        "| Item | Score (1–5) | Notes |",
        "|------|------------|-------|",
        "| Clarity | — | |",
        "| Warmth | — | |",
        "| Space | — | |",
        "| Harshness | — | |",
        "| Plastic feel | — | |",
        "| Artifacts | — | |",
        "| **Better than before?** | yes / no / uncertain | |",
        "",
        "## Notes",
        "",
    ]

    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


# ═══════════════════════════════════════════════════
#  Internal helpers
# ═══════════════════════════════════════════════════

def _compute_dynamic_range(mono: np.ndarray, sr: int) -> float:
    win_len = int(0.1 * sr)
    hop = win_len // 2
    if len(mono) < win_len:
        return 0.0
    rms_vals = []
    for i in range(0, len(mono) - win_len, hop):
        win = mono[i:i + win_len]
        rms_vals.append(20.0 * math.log10(np.sqrt(np.mean(win ** 2)) + 1e-12))
    if len(rms_vals) < 3:
        return 0.0
    rms_arr = np.array(rms_vals)
    return float(np.percentile(rms_arr, 95) - np.percentile(rms_arr, 5))


# ═══════════════════════════════════════════════════
#  Main
# ═══════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="MHP-007-A: Moodify Inspector — before/after audio comparison"
    )
    parser.add_argument("--before", required=True, help="Path to original audio file")
    parser.add_argument("--after", required=True, help="Path to processed audio file")
    parser.add_argument("--output-dir", required=True, help="Output directory for reports")
    parser.add_argument("--preset", default="", help="Preset name (optional)")
    parser.add_argument("--title", default="Moodify Inspector", help="Report title")
    args = parser.parse_args()

    if not Path(args.before).exists():
        print(f"ERROR: before file not found: {args.before}")
        sys.exit(1)
    if not Path(args.after).exists():
        print(f"ERROR: after file not found: {args.after}")
        sys.exit(1)

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"\nMoodify Inspector")
    print(f"  Before: {args.before}")
    print(f"  After:  {args.after}")
    print(f"  Output: {out_dir}\n")

    # Load
    audio_b, sr_b = load_stereo(args.before)
    audio_a, sr_a = load_stereo(args.after)
    print(f"  Loaded: {audio_b.shape} @ {sr_b}Hz  |  {audio_a.shape} @ {sr_a}Hz")

    # Warnings
    warnings = []
    if sr_b != sr_a:
        warnings.append(f"Sample rate mismatch: {sr_b} vs {sr_a}")
    dur_b = len(audio_b) / sr_b
    dur_a = len(audio_a) / sr_a
    if abs(dur_b - dur_a) > 0.05:
        warnings.append(f"Duration mismatch: {dur_b:.1f}s vs {dur_a:.1f}s")
    if warnings:
        for w in warnings:
            print(f"  WARNING: {w}")

    # Compute
    print("  Computing before metrics...")
    metrics_b = collect_metrics(audio_b, sr_b)
    print("  Computing after metrics...")
    metrics_a = collect_metrics(audio_a, sr_a)
    print("  Computing deltas...")
    delta = compute_delta(metrics_b, metrics_a)

    # Plots
    mono_b = to_mono(audio_b)
    mono_a = to_mono(audio_a)
    freqs_b, curve_b = compute_spectrum_curve(mono_b, sr_b)
    freqs_a, curve_a = compute_spectrum_curve(mono_a, sr_a)

    print("  Generating plots...")
    plot_waveform(audio_b, audio_a, sr_b, sr_a, str(out_dir / "waveform_before_after.png"))
    print("    waveform_before_after.png")
    plot_spectrum_overlay(freqs_b, curve_b, freqs_a, curve_a, str(out_dir / "spectrum_overlay.png"))
    print("    spectrum_overlay.png")
    plot_spectrum_delta(freqs_b, curve_b, curve_a, str(out_dir / "spectrum_delta.png"))
    print("    spectrum_delta.png")
    plot_spectrogram(audio_b, sr_b, str(out_dir / "spectrogram_before.png"), "Spectrogram — Before")
    print("    spectrogram_before.png")
    plot_spectrogram(audio_a, sr_a, str(out_dir / "spectrogram_after.png"), "Spectrogram — After")
    print("    spectrogram_after.png")
    plot_band_energy(metrics_b["bands"], metrics_a["bands"], str(out_dir / "band_energy_comparison.png"))
    print("    band_energy_comparison.png")

    # Reports
    report_data = {
        "title": args.title,
        "preset": args.preset,
        "before_path": args.before,
        "after_path": args.after,
        "warnings": warnings,
        "before": metrics_b,
        "after": metrics_a,
        "delta": delta,
    }

    json_path = out_dir / "metrics_comparison.json"
    write_json_report(report_data, str(json_path))
    print(f"    metrics_comparison.json")

    md_path = out_dir / "report.md"
    write_markdown_report(report_data, str(md_path))
    print(f"    report.md")

    print(f"\n  Done. {out_dir}/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
