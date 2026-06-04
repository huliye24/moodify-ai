"""MHP-419→423 + 431→440: Acoustic CT PDF Visualization Engine.

Generates CT-style diagnostic PDFs for audio before & after DSP treatment.
Plates: spectrogram, frequency balance, waveform dynamics, stereo image,
loudness envelope, transient risk, defect annotations.

Brand: includes Moodify logo on cover and headers.
"""

from __future__ import annotations

import io
import math
import struct
import uuid
import wave
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from .utils import utc_now_iso

# ── Brand constants ────────────────────────────────────────────────────
BRAND_LOGO = Path(__file__).resolve().parent.parent / "assets" / "brand" / "moodify_logo_symbol_original_white_canvas_1254.png"
BRAND_COLOR = "#1a1a2e"
ACCENT_COLOR = "#e94560"
GRID_COLOR = "#333355"
TEXT_COLOR = "#eaeaea"
BG_DARK = "#0f0f1a"


# ═══════════════════════════════════════════════════════════════════════
# Audio I/O
# ═══════════════════════════════════════════════════════════════════════


def _read_wav(path: str) -> Tuple[np.ndarray, int, int]:
    """Read WAV → (float64 mono samples, sample_rate, channels)."""
    with wave.open(path, "rb") as wf:
        sr = wf.getframerate()
        nch = wf.getnchannels()
        sw = wf.getsampwidth()
        nf = wf.getnframes()
        raw = wf.readframes(nf)

    if sw == 2:
        samples = np.frombuffer(raw[:nf * nch * 2], dtype=np.int16).astype(np.float64)
    elif sw == 1:
        samples = (np.frombuffer(raw[:nf * nch], dtype=np.uint8).astype(np.float64) - 128) * 256
    else:
        return np.array([]), sr, nch

    if nch > 1:
        samples = samples.reshape(-1, nch).mean(axis=1)
    return samples / 32768.0, sr, nch


# ═══════════════════════════════════════════════════════════════════════
# MHP-419: Spectrogram Plate
# ═══════════════════════════════════════════════════════════════════════


def _draw_brand_header(fig, title: str, subtitle: str = ""):
    """Draw brand header with logo if available."""
    if BRAND_LOGO.exists():
        from PIL import Image
        logo_img = plt.imread(str(BRAND_LOGO))
        ax_logo = fig.add_axes([0.02, 0.93, 0.06, 0.06], zorder=10)
        ax_logo.imshow(logo_img)
        ax_logo.axis("off")

    fig.text(0.12, 0.96, "MOODIFY ACOUSTIC CT", fontsize=12, fontweight="bold",
             color=ACCENT_COLOR, fontfamily="monospace")
    if subtitle:
        fig.text(0.12, 0.93, subtitle, fontsize=8, color=TEXT_COLOR, fontfamily="monospace")


def generate_spectrogram_plate(
    wav_path: str,
    output_path: str,
    title: str = "Spectrogram Scan",
    label: str = "",
) -> str:
    """MHP-419: Generate a spectrogram plate from a WAV file."""
    samples, sr, nch = _read_wav(wav_path)
    if len(samples) == 0:
        raise ValueError(f"Could not read audio: {wav_path}")

    fig = plt.figure(figsize=(12, 8), facecolor=BG_DARK)
    _draw_brand_header(fig, title, label)

    # Spectrogram
    ax = fig.add_axes([0.08, 0.12, 0.84, 0.72])
    Pxx, freqs, bins, im = ax.specgram(
        samples, NFFT=1024, Fs=sr, noverlap=512,
        cmap="magma", scale="dB", vmin=-80, vmax=0,
    )
    ax.set_xlabel("Time (s)", color=TEXT_COLOR, fontsize=9)
    ax.set_ylabel("Frequency (Hz)", color=TEXT_COLOR, fontsize=9)
    ax.set_yscale("log")
    ax.set_ylim(20, sr / 2)
    ax.tick_params(colors=TEXT_COLOR, labelsize=8)
    ax.set_facecolor(BG_DARK)
    for spine in ax.spines.values():
        spine.set_color(GRID_COLOR)

    # Over-dark band overlay
    ax.axhspan(20, 60, alpha=0.15, color="red", label="sub_bass risk")
    ax.axhspan(100, 300, alpha=0.1, color="orange", label="low_mid risk")
    ax.legend(loc="upper right", fontsize=7, facecolor=BG_DARK, edgecolor=GRID_COLOR,
              labelcolor=TEXT_COLOR)

    # Footer
    fig.text(0.5, 0.04, f"Moodify Acoustic CT | {label or wav_path} | {utc_now_iso()}",
             ha="center", fontsize=7, color=GRID_COLOR, fontfamily="monospace")

    fig.savefig(output_path, dpi=150, facecolor=BG_DARK, bbox_inches="tight")
    plt.close(fig)
    return output_path


# ═══════════════════════════════════════════════════════════════════════
# MHP-420: Frequency Balance Curve
# ═══════════════════════════════════════════════════════════════════════


def generate_frequency_balance_plate(
    wav_path: str,
    output_path: str,
    title: str = "Frequency Balance Curve",
    label: str = "",
) -> str:
    """MHP-420: Frequency balance curve showing energy distribution."""
    samples, sr, _ = _read_wav(wav_path)
    if len(samples) == 0:
        raise ValueError(f"Could not read audio: {wav_path}")

    # FFT spectrum
    n = len(samples)
    window = np.hanning(n)
    fft = np.fft.rfft(samples * window)
    mag = np.abs(fft)
    freqs = np.fft.rfftfreq(n, d=1.0 / sr)

    # Downsample to 1/3 octave bands for readability
    bands_hz = [20, 31.5, 40, 50, 63, 80, 100, 125, 160, 200, 250, 315, 400, 500,
                630, 800, 1000, 1250, 1600, 2000, 2500, 3150, 4000, 5000, 6300, 8000,
                10000, 12500, 16000, 20000]
    band_energy = []
    for i, low in enumerate(bands_hz[:-1]):
        high = bands_hz[i + 1]
        mask = (freqs >= low) & (freqs < high)
        if mask.any():
            band_energy.append(float(np.mean(mag[mask])))
        else:
            band_energy.append(0.0)

    band_centers = [(bands_hz[i] + bands_hz[i + 1]) / 2 for i in range(len(bands_hz) - 1)]

    fig = plt.figure(figsize=(12, 8), facecolor=BG_DARK)
    _draw_brand_header(fig, title, label)

    ax = fig.add_axes([0.08, 0.15, 0.84, 0.70])
    ax.fill_between(band_centers, band_energy, alpha=0.4, color=ACCENT_COLOR)
    ax.plot(band_centers, band_energy, color=ACCENT_COLOR, linewidth=1.5)
    ax.set_xscale("log")
    ax.set_xlabel("Frequency (Hz)", color=TEXT_COLOR, fontsize=9)
    ax.set_ylabel("Energy", color=TEXT_COLOR, fontsize=9)
    ax.tick_params(colors=TEXT_COLOR, labelsize=8)
    ax.set_facecolor(BG_DARK)
    for spine in ax.spines.values():
        spine.set_color(GRID_COLOR)
    ax.grid(True, alpha=0.15, color=GRID_COLOR)

    # Annotate key ranges
    for low, high, name in [(20, 60, "sub"), (100, 300, "low-mid"), (300, 2000, "mid"),
                              (2000, 8000, "presence"), (8000, 20000, "air")]:
        mid = math.sqrt(low * high)
        ax.axvline(low, color=GRID_COLOR, alpha=0.3, linestyle="--", linewidth=0.5)
        ax.text(mid, max(band_energy) * 0.95, name, fontsize=6, color=GRID_COLOR, ha="center")

    fig.text(0.5, 0.04, f"Moodify Acoustic CT | Frequency Balance | {utc_now_iso()}",
             ha="center", fontsize=7, color=GRID_COLOR, fontfamily="monospace")
    fig.savefig(output_path, dpi=150, facecolor=BG_DARK, bbox_inches="tight")
    plt.close(fig)
    return output_path


# ═══════════════════════════════════════════════════════════════════════
# MHP-421: Waveform Dynamics Plate
# ═══════════════════════════════════════════════════════════════════════


def generate_waveform_dynamics_plate(
    wav_path: str,
    output_path: str,
    title: str = "Waveform Dynamics",
    label: str = "",
) -> str:
    """MHP-421: Waveform overview + RMS envelope showing dynamic range."""
    samples, sr, _ = _read_wav(wav_path)
    if len(samples) == 0:
        raise ValueError(f"Could not read audio: {wav_path}")

    time_axis = np.arange(len(samples)) / sr

    fig = plt.figure(figsize=(12, 8), facecolor=BG_DARK)
    _draw_brand_header(fig, title, label)

    # Waveform (top)
    ax1 = fig.add_axes([0.08, 0.52, 0.84, 0.38])
    ax1.plot(time_axis, samples, color=TEXT_COLOR, linewidth=0.3, alpha=0.8)
    ax1.set_ylabel("Amplitude", color=TEXT_COLOR, fontsize=8)
    ax1.tick_params(colors=TEXT_COLOR, labelsize=7)
    ax1.set_facecolor(BG_DARK)
    for spine in ax1.spines.values():
        spine.set_color(GRID_COLOR)

    # RMS envelope (bottom)
    window_ms = 50
    window_samples = int(sr * window_ms / 1000)
    if window_samples > 1:
        rms_env = np.array([np.sqrt(np.mean(samples[max(0, i - window_samples):i] ** 2))
                            for i in range(1, len(samples), window_samples)])
        rms_time = time_axis[::window_samples][:len(rms_env)]

        ax2 = fig.add_axes([0.08, 0.10, 0.84, 0.35])
        ax2.fill_between(rms_time, rms_env, alpha=0.5, color=ACCENT_COLOR)
        ax2.plot(rms_time, rms_env, color=ACCENT_COLOR, linewidth=1.0)
        ax2.set_xlabel("Time (s)", color=TEXT_COLOR, fontsize=8)
        ax2.set_ylabel("RMS Energy", color=TEXT_COLOR, fontsize=8)
        ax2.tick_params(colors=TEXT_COLOR, labelsize=7)
        ax2.set_facecolor(BG_DARK)
        for spine in ax2.spines.values():
            spine.set_color(GRID_COLOR)

    fig.text(0.5, 0.04, f"Moodify Acoustic CT | Waveform Dynamics | {utc_now_iso()}",
             ha="center", fontsize=7, color=GRID_COLOR, fontfamily="monospace")
    fig.savefig(output_path, dpi=150, facecolor=BG_DARK, bbox_inches="tight")
    plt.close(fig)
    return output_path


# ═══════════════════════════════════════════════════════════════════════
# MHP-422: Stereo Image Plate
# ═══════════════════════════════════════════════════════════════════════


def generate_stereo_image_plate(
    wav_path: str,
    output_path: str,
    title: str = "Stereo Image",
    label: str = "",
) -> str:
    """MHP-422: Stereo field visualization (goniometer-style scatter)."""
    with wave.open(wav_path, "rb") as wf:
        sr = wf.getframerate()
        nch = wf.getnchannels()
        sw = wf.getsampwidth()
        nf = wf.getnframes()
        raw = wf.readframes(nf)

    if nch < 2 or sw != 2:
        # Mono fallback
        fig = plt.figure(figsize=(8, 8), facecolor=BG_DARK)
        fig.text(0.5, 0.5, "MONO INPUT\nStereo analysis not applicable",
                 ha="center", color=TEXT_COLOR, fontsize=14, fontfamily="monospace")
        fig.savefig(output_path, dpi=150, facecolor=BG_DARK, bbox_inches="tight")
        plt.close(fig)
        return output_path

    samples = np.frombuffer(raw[:nf * nch * 2], dtype=np.int16).astype(np.float64) / 32768.0
    samples = samples.reshape(-1, nch)
    left = samples[:, 0]
    right = samples[:, 1]

    # Subsample for scatter (too many points)
    step = max(1, len(left) // 8000)
    left_sub = left[::step]
    right_sub = right[::step]

    fig = plt.figure(figsize=(8, 8), facecolor=BG_DARK)
    _draw_brand_header(fig, title, label)

    ax = fig.add_axes([0.10, 0.10, 0.80, 0.80])
    ax.scatter(left_sub, right_sub, s=0.5, c=ACCENT_COLOR, alpha=0.3)
    ax.axhline(0, color=GRID_COLOR, alpha=0.3, linewidth=0.5)
    ax.axvline(0, color=GRID_COLOR, alpha=0.3, linewidth=0.5)
    ax.plot([-1, 1], [-1, 1], color=GRID_COLOR, alpha=0.2, linestyle="--", linewidth=0.5)
    ax.plot([-1, 1], [1, -1], color=GRID_COLOR, alpha=0.2, linestyle="--", linewidth=0.5)
    ax.set_xlim(-1, 1)
    ax.set_ylim(-1, 1)
    ax.set_xlabel("Left", color=TEXT_COLOR, fontsize=9)
    ax.set_ylabel("Right", color=TEXT_COLOR, fontsize=9)
    ax.tick_params(colors=TEXT_COLOR, labelsize=8)
    ax.set_facecolor(BG_DARK)
    for spine in ax.spines.values():
        spine.set_color(GRID_COLOR)

    fig.text(0.5, 0.04, f"Moodify Acoustic CT | Stereo Image | {utc_now_iso()}",
             ha="center", fontsize=7, color=GRID_COLOR, fontfamily="monospace")
    fig.savefig(output_path, dpi=150, facecolor=BG_DARK, bbox_inches="tight")
    plt.close(fig)
    return output_path


# ═══════════════════════════════════════════════════════════════════════
# MHP-423: Full CT Report Generator (all plates → single PDF-like directory)
# ═══════════════════════════════════════════════════════════════════════


@dataclass
class CTReport:
    """A complete acoustic CT report for one audio file."""
    ct_id: str
    sample_id: str = ""
    genre: str = ""
    preset: str = ""
    spectrogram_path: str = ""
    freq_balance_path: str = ""
    waveform_dynamics_path: str = ""
    stereo_image_path: str = ""
    defect_flags: List[str] = field(default_factory=list)
    mrs_before: Optional[float] = None
    mrs_after: Optional[float] = None
    mrs_delta: Optional[float] = None
    generated_at: str = field(default_factory=utc_now_iso)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ct_id": self.ct_id, "sample_id": self.sample_id,
            "genre": self.genre, "preset": self.preset,
            "plates": {
                "spectrogram": self.spectrogram_path,
                "frequency_balance": self.freq_balance_path,
                "waveform_dynamics": self.waveform_dynamics_path,
                "stereo_image": self.stereo_image_path,
            },
            "defect_flags": self.defect_flags,
            "mrs_before": self.mrs_before,
            "mrs_after": self.mrs_after,
            "mrs_delta": self.mrs_delta,
            "generated_at": self.generated_at,
        }


def generate_ct_scan(
    wav_path: str,
    output_dir: Path,
    sample_id: str = "",
    genre: str = "",
    preset: str = "",
    defect_flags: Optional[List[str]] = None,
    mrs_before: Optional[float] = None,
    mrs_after: Optional[float] = None,
) -> CTReport:
    """Generate a complete Acoustic CT scan — all 4 diagnostic plates.

    Returns a CTReport with paths to all generated images.
    """
    ct_id = f"CT_{uuid.uuid4().hex[:8].upper()}"
    scan_dir = output_dir / ct_id
    scan_dir.mkdir(parents=True, exist_ok=True)

    label = f"{sample_id} | {genre} | {preset}" if sample_id else wav_path

    report = CTReport(
        ct_id=ct_id, sample_id=sample_id, genre=genre, preset=preset,
        defect_flags=defect_flags or [],
        mrs_before=mrs_before, mrs_after=mrs_after,
        mrs_delta=(mrs_after - mrs_before) if (mrs_before is not None and mrs_after is not None) else None,
    )

    report.spectrogram_path = generate_spectrogram_plate(
        wav_path, str(scan_dir / "spectrogram.png"), label=label)
    report.freq_balance_path = generate_frequency_balance_plate(
        wav_path, str(scan_dir / "frequency_balance.png"), label=label)
    report.waveform_dynamics_path = generate_waveform_dynamics_plate(
        wav_path, str(scan_dir / "waveform_dynamics.png"), label=label)
    report.stereo_image_path = generate_stereo_image_plate(
        wav_path, str(scan_dir / "stereo_image.png"), label=label)

    # Write report JSON
    import json
    (scan_dir / "ct_report.json").write_text(
        json.dumps(report.to_dict(), indent=2, ensure_ascii=False))

    return report


def generate_comparison_report(
    before_ct: CTReport,
    after_ct: CTReport,
    output_dir: Path,
) -> Dict[str, Any]:
    """Generate a before/after comparison CT report.

    Creates a markdown report linking both scan plates + delta analysis.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    comp_id = f"CTCOMP_{uuid.uuid4().hex[:8].upper()}"

    lines = [
        f"# Moodify Acoustic CT — Before/After Comparison",
        f"**Report ID**: {comp_id}",
        f"**Sample**: {before_ct.sample_id} | **Genre**: {before_ct.genre} | **Preset**: {after_ct.preset}",
        f"**Generated**: {utc_now_iso()}",
        "",
        "## MRS Scores",
        f"- Before: {before_ct.mrs_before:.1f}" if before_ct.mrs_before else "- Before: N/A",
        f"- After: {after_ct.mrs_after:.1f}" if after_ct.mrs_after else "- After: N/A",
        f"- Δ MRS: {before_ct.mrs_delta:+.1f}" if before_ct.mrs_delta else "- Δ MRS: N/A",
        "",
        "## Before Treatment (Raw Scan)",
        f"![Spectrogram]({before_ct.spectrogram_path})",
        f"![Frequency Balance]({before_ct.freq_balance_path})",
        f"![Waveform Dynamics]({before_ct.waveform_dynamics_path})",
        f"![Stereo Image]({before_ct.stereo_image_path})",
        "",
        "## After Treatment (Processed Scan)",
        f"![Spectrogram]({after_ct.spectrogram_path})",
        f"![Frequency Balance]({after_ct.freq_balance_path})",
        f"![Waveform Dynamics]({after_ct.waveform_dynamics_path})",
        f"![Stereo Image]({after_ct.stereo_image_path})",
        "",
        "## Defect Flags",
    ]
    if after_ct.defect_flags:
        for f in after_ct.defect_flags:
            lines.append(f"- ⚠️ {f}")
    else:
        lines.append("- ✅ No defects detected")

    lines += [
        "",
        "## Treatment Assessment",
        "",
        f"- Preset applied: **{after_ct.preset}**",
        f"- Genre: **{after_ct.genre}**",
    ]
    if before_ct.mrs_delta is not None and before_ct.mrs_delta > 0:
        lines.append("- Verdict: **IMPROVED** ✅")
    elif before_ct.mrs_delta is not None and before_ct.mrs_delta < 0:
        lines.append("- Verdict: **DEGRADED** ⚠️")
    else:
        lines.append("- Verdict: **NO SIGNIFICANT CHANGE**")

    md_path = output_dir / f"{comp_id}.md"
    md_path.write_text("\n".join(lines), encoding="utf-8")

    return {"comparison_id": comp_id, "report_path": str(md_path)}
