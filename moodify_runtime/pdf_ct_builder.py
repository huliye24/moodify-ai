"""MHP-647-664: Acoustic CT PDF Page Builders.

Integrates the acoustic_ct.py diagnostic plates with the pdf_report.py
multi-page PDF writer. Generates branded single-scan and comparison PDFs.

Part of ECHAIN-MOODIFY-PDF-REPORT-011 / NEM-PDF-ACOUSTIC-CT-BUILD-034.
"""

from __future__ import annotations

import math
import wave
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from .pdf_assets import BrandAssets
from .pdf_report import (
    PdfReportConfig,
    PdfReportManifest,
    PdfReportWriter,
    build_operator_friendly_filename,
    build_report_output_path,
    compute_ct_quality_score,
    generate_report_id,
)
from .pdf_templates import (
    DEFAULT_THEME,
    PageTemplate,
    PdfTheme,
    export_figure_to_image,
    render_summary_text_page,
)
from .utils import utc_now_iso


# ═══════════════════════════════════════════════════════════════════════════
# Audio I/O (shared with acoustic_ct.py)
# ═══════════════════════════════════════════════════════════════════════════

def _read_wav(path: str) -> Tuple[np.ndarray, int, int]:
    """Read WAV -> (float64 mono samples, sample_rate, channels)."""
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


# ═══════════════════════════════════════════════════════════════════════════
# MHP-651: Risk-Band Visual Grammar
# ═══════════════════════════════════════════════════════════════════════════

RISK_BANDS = [
    {"name": "sub_bass", "low": 20, "high": 60, "label": "Sub-Bass Risk",
     "color": "red", "alpha": 0.15},
    {"name": "bass", "low": 60, "high": 150, "label": "Bass Body",
     "color": "green", "alpha": 0.08},
    {"name": "low_mid", "low": 150, "high": 350, "label": "Low-Mid Mud Risk",
     "color": "orange", "alpha": 0.12},
    {"name": "mid", "low": 350, "high": 2000, "label": "Mid Presence",
     "color": "cyan", "alpha": 0.06},
    {"name": "presence", "low": 2000, "high": 8000, "label": "Presence/Harshness",
     "color": "yellow", "alpha": 0.10},
    {"name": "air", "low": 8000, "high": 20000, "label": "Air",
     "color": "blue", "alpha": 0.08},
]


def draw_risk_band_overlays(ax: plt.Axes, theme: PdfTheme) -> None:
    """Draw risk-band visual overlays on a frequency-domain plot.

    MHP-651: Risk-band visual grammar with documented colors.
    """
    for band in RISK_BANDS:
        ax.axvspan(
            band["low"], band["high"],
            alpha=band["alpha"], color=band["color"],
            label=band["label"],
        )


# ═══════════════════════════════════════════════════════════════════════════
# MHP-647: Spectrogram Report Page
# ═══════════════════════════════════════════════════════════════════════════

def build_spectrogram_page(
    wav_path: str,
    template: PageTemplate,
    title: str = "Spectrogram Scan",
    label: str = "",
) -> plt.Figure:
    """Build a spectrogram report page using the PDF template system.

    MHP-647: Spectrogram page resembles current CT visual but uses template.
    """
    samples, sr, nch = _read_wav(wav_path)
    if len(samples) == 0:
        raise ValueError(f"Could not read audio: {wav_path}")

    fig = template.create_figure(title, label)
    theme = template.theme

    ax = template.full_body_axes(fig)
    Pxx, freqs, bins, im = ax.specgram(
        samples, NFFT=1024, Fs=sr, noverlap=512,
        cmap="magma", scale="dB", vmin=-80, vmax=0,
    )
    ax.set_xlabel("Time (s)", color=theme.text_color, fontsize=theme.body_size)
    ax.set_ylabel("Frequency (Hz)", color=theme.text_color, fontsize=theme.body_size)
    ax.set_yscale("log")
    ax.set_ylim(20, sr / 2)
    template.style_axes(ax)

    # Risk band overlays
    draw_risk_band_overlays(ax, theme)
    ax.legend(loc="upper right", fontsize=6, facecolor=theme.bg_dark,
              edgecolor=theme.grid_color, labelcolor=theme.text_color)

    return fig


# ═══════════════════════════════════════════════════════════════════════════
# MHP-648: Frequency Balance Page
# ═══════════════════════════════════════════════════════════════════════════

def build_frequency_balance_page(
    wav_path: str,
    template: PageTemplate,
    title: str = "Frequency Balance Curve",
    label: str = "",
) -> plt.Figure:
    """Build a frequency balance page with standardized axes and band labels.

    MHP-648: Uses standardized axes and band labels.
    """
    samples, sr, _ = _read_wav(wav_path)
    if len(samples) == 0:
        raise ValueError(f"Could not read audio: {wav_path}")

    theme = template.theme

    # FFT spectrum
    n = len(samples)
    window = np.hanning(n)
    fft = np.fft.rfft(samples * window)
    mag = np.abs(fft)
    freqs = np.fft.rfftfreq(n, d=1.0 / sr)

    # 1/3 octave bands
    bands_hz = [20, 31.5, 40, 50, 63, 80, 100, 125, 160, 200, 250, 315, 400, 500,
                630, 800, 1000, 1250, 1600, 2000, 2500, 3150, 4000, 5000, 6300, 8000,
                10000, 12500, 16000, 20000]
    band_energy = []
    for i, low in enumerate(bands_hz[:-1]):
        high = bands_hz[i + 1]
        mask = (freqs >= low) & (freqs < high)
        band_energy.append(float(np.mean(mag[mask])) if mask.any() else 0.0)

    band_centers = [(bands_hz[i] + bands_hz[i + 1]) / 2 for i in range(len(bands_hz) - 1)]

    fig = template.create_figure(title, label)
    ax = template.full_body_axes(fig)

    ax.fill_between(band_centers, band_energy, alpha=0.4, color=theme.accent_color)
    ax.plot(band_centers, band_energy, color=theme.accent_color, linewidth=1.5)
    ax.set_xscale("log")
    ax.set_xlabel("Frequency (Hz)", color=theme.text_color, fontsize=theme.body_size)
    ax.set_ylabel("Energy", color=theme.text_color, fontsize=theme.body_size)
    template.style_axes(ax)

    # Key range annotations
    range_names = [("sub", 20, 60), ("bass", 60, 150), ("low-mid", 150, 350),
                   ("mid", 350, 2000), ("presence", 2000, 8000), ("air", 8000, 20000)]
    for name, low, high in range_names:
        mid = math.sqrt(low * high)
        ax.axvline(low, color=theme.grid_color, alpha=0.3, linestyle="--", linewidth=0.5)
        y_pos = max(band_energy) * 0.92 if band_energy else 1
        ax.text(mid, y_pos, name, fontsize=6, color=theme.text_muted, ha="center")

    # Risk band overlays
    draw_risk_band_overlays(ax, theme)

    return fig


# ═══════════════════════════════════════════════════════════════════════════
# MHP-649: Waveform Dynamics Page
# ═══════════════════════════════════════════════════════════════════════════

def build_waveform_dynamics_page(
    wav_path: str,
    template: PageTemplate,
    title: str = "Waveform Dynamics",
    label: str = "",
) -> plt.Figure:
    """Build waveform + RMS envelope page.

    MHP-649: Waveform and RMS panels fit without overlap.
    """
    samples, sr, _ = _read_wav(wav_path)
    if len(samples) == 0:
        raise ValueError(f"Could not read audio: {wav_path}")

    theme = template.theme
    time_axis = np.arange(len(samples)) / sr

    fig = template.create_figure(title, label)

    # Waveform (top)
    ax1 = fig.add_axes([0.08, 0.52, 0.84, 0.36])
    ax1.plot(time_axis, samples, color=theme.text_color, linewidth=0.3, alpha=0.8)
    ax1.set_ylabel("Amplitude", color=theme.text_color, fontsize=theme.small_size)
    template.style_axes(ax1)

    # RMS envelope (bottom)
    window_ms = 50
    window_samples = int(sr * window_ms / 1000)
    if window_samples > 1:
        rms_env = np.array([np.sqrt(np.mean(samples[max(0, i - window_samples):i] ** 2))
                            for i in range(1, len(samples), window_samples)])
        rms_time = time_axis[::window_samples][:len(rms_env)]

        ax2 = fig.add_axes([0.08, 0.10, 0.84, 0.34])
        ax2.fill_between(rms_time, rms_env, alpha=0.5, color=theme.accent_color)
        ax2.plot(rms_time, rms_env, color=theme.accent_color, linewidth=1.0)
        ax2.set_xlabel("Time (s)", color=theme.text_color, fontsize=theme.small_size)
        ax2.set_ylabel("RMS Energy", color=theme.text_color, fontsize=theme.small_size)
        template.style_axes(ax2)

    return fig


# ═══════════════════════════════════════════════════════════════════════════
# MHP-650: Summary / Diagnosis Page
# ═══════════════════════════════════════════════════════════════════════════

def build_summary_diagnosis_page(
    template: PageTemplate,
    sample_id: str = "",
    genre: str = "",
    preset: str = "",
    defect_flags: Optional[List[str]] = None,
    mrs_before: Optional[float] = None,
    mrs_after: Optional[float] = None,
    processing_chain: Optional[List[Dict[str, Any]]] = None,
    duration_s: float = 0.0,
    sample_rate: int = 0,
    channels: int = 0,
) -> plt.Figure:
    """Build a summary/diagnosis page with human-readable findings.

    MHP-650: Human-readable findings and gate result appear.
    MHP-656: Audio identity block shows input id, output id, duration, sample rate.
    MHP-655: Processing chain section lists preset, process passes, params, overrides.
    """
    theme = template.theme
    title = "Acoustic CT — Summary & Diagnosis"
    fig = template.create_figure(title, "Scan Results")

    lines = []

    # ── Audio Identity Block ──
    lines.append("=== AUDIO IDENTITY ===")
    if sample_id:
        lines.append(f"Sample ID: {sample_id}")
    if genre:
        lines.append(f"Genre: {genre}")
    if preset:
        lines.append(f"Preset: {preset}")
    if duration_s > 0:
        lines.append(f"Duration: {duration_s:.1f} s")
    if sample_rate > 0:
        lines.append(f"Sample Rate: {sample_rate} Hz | Channels: {channels}")
    lines.append("")

    # ── MRS Scores ──
    lines.append("=== MRS SCORES ===")
    if mrs_before is not None:
        lines.append(f"MRS Before: {mrs_before:.1f}")
    if mrs_after is not None:
        lines.append(f"MRS After: {mrs_after:.1f}")
    if mrs_before is not None and mrs_after is not None:
        delta = mrs_after - mrs_before
        direction = "IMPROVED" if delta > 0 else ("DEGRADED" if delta < 0 else "UNCHANGED")
        lines.append(f"Delta MRS: {delta:+.1f} — {direction}")
    lines.append("")

    # ── Defect Flags ──
    lines.append("=== DEFECT FLAGS ===")
    if defect_flags:
        for f in defect_flags:
            lines.append(f"[!] {f}")
    else:
        lines.append("No defects detected — scan passed.")
    lines.append("")

    # ── Processing Chain ──
    if processing_chain:
        lines.append("=== PROCESSING CHAIN ===")
        for step in processing_chain:
            op_name = step.get("operation", step.get("name", "unknown"))
            op_params = step.get("params", {})
            param_str = ", ".join(f"{k}={v}" for k, v in op_params.items())
            lines.append(f"  - {op_name}: {param_str}" if param_str else f"  - {op_name}")
        lines.append("")

    # ── Gate Result ──
    lines.append("=== GATE RESULT ===")
    critical_defects = [f for f in (defect_flags or []) if "clipping" in f.lower() or "over" in f.lower()]
    if critical_defects:
        lines.append("GATE: FAIL — Critical defects detected")
    elif defect_flags:
        lines.append("GATE: PASS with warnings — Non-critical defects noted")
    else:
        lines.append("GATE: PASS — Scan clean")

    render_summary_text_page(fig, lines, title="Acoustic CT Diagnosis", start_y=0.80, line_height=0.030)
    return fig


# ═══════════════════════════════════════════════════════════════════════════
# MHP-653: Diagnostic Callouts
# ═══════════════════════════════════════════════════════════════════════════

def annotate_diagnostic_callouts(
    ax: plt.Axes,
    findings: List[Dict[str, Any]],
    theme: Optional[PdfTheme] = None,
) -> None:
    """Annotate a plot with diagnostic callouts.

    MHP-653: Top risks and improvements are annotated on pages.

    Args:
        ax: The matplotlib axes to annotate.
        findings: List of {x, y, text, severity} dicts.
        theme: PdfTheme for styling.
    """
    theme = theme or DEFAULT_THEME

    for finding in findings:
        x = finding.get("x", 0)
        y = finding.get("y", 0)
        text = finding.get("text", "")
        severity = finding.get("severity", "info")

        color = {
            "critical": theme.accent_color,
            "warning": theme.warn_color,
            "info": theme.text_muted,
        }.get(severity, theme.text_muted)

        ax.annotate(
            text,
            xy=(x, y),
            xytext=(10, 10),
            textcoords="offset points",
            fontsize=6,
            color=color,
            arrowprops=dict(
                arrowstyle="->",
                color=color,
                alpha=0.6,
                lw=0.8,
            ),
            bbox=dict(
                boxstyle="round,pad=0.3",
                facecolor=theme.bg_dark,
                edgecolor=color,
                alpha=0.8,
            ),
        )


# ═══════════════════════════════════════════════════════════════════════════
# Full Single-Scan PDF Generator
# ═══════════════════════════════════════════════════════════════════════════

def generate_single_scan_pdf(
    wav_path: str,
    output_dir: Optional[Path] = None,
    sample_id: str = "",
    genre: str = "",
    preset: str = "",
    defect_flags: Optional[List[str]] = None,
    mrs_before: Optional[float] = None,
    mrs_after: Optional[float] = None,
    processing_chain: Optional[List[Dict[str, Any]]] = None,
    config: Optional[PdfReportConfig] = None,
) -> PdfReportManifest:
    """Generate a complete single-scan Acoustic CT PDF.

    MHP-662: Cloud produces one polished single CT report.

    Returns a PdfReportManifest with full metadata.
    """
    cfg = (config or PdfReportConfig()).resolved()

    if output_dir is None:
        output_dir = cfg.output_dir / "ct_scan"
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    report_id = generate_report_id("CT")
    label = f"{sample_id} | {genre} | {preset}" if sample_id else Path(wav_path).name

    # Get audio info
    samples, sr, nch = _read_wav(wav_path)
    duration = len(samples) / sr if sr > 0 and len(samples) > 0 else 0

    template = PageTemplate(theme=cfg.theme, brand=cfg.brand)
    writer = PdfReportWriter(cfg)

    # ── Cover Page ──
    cover_lines = [
        f"Report ID: {report_id}",
        f"Sample: {sample_id or Path(wav_path).name}",
        f"Genre: {genre or 'N/A'}",
        f"Preset: {preset or 'N/A'}",
        f"Duration: {duration:.1f} s | {sr} Hz | {nch}ch",
        f"Generated: {utc_now_iso()}",
    ]
    if mrs_before is not None:
        cover_lines.append(f"MRS Before: {mrs_before:.1f}")
    writer.add_cover_page("Moodify Acoustic CT", "Single Scan Report", cover_lines)

    # ── Spectrogram Plate ──
    fig = build_spectrogram_page(wav_path, template, label=label)
    writer.add_figure(fig)

    # ── Frequency Balance Plate ──
    fig = build_frequency_balance_page(wav_path, template, label=label)
    writer.add_figure(fig)

    # ── Waveform Dynamics Plate ──
    fig = build_waveform_dynamics_page(wav_path, template, label=label)
    writer.add_figure(fig)

    # ── Summary / Diagnosis Page ──
    fig = build_summary_diagnosis_page(
        template,
        sample_id=sample_id or Path(wav_path).name,
        genre=genre,
        preset=preset,
        defect_flags=defect_flags or [],
        mrs_before=mrs_before,
        mrs_after=mrs_after,
        processing_chain=processing_chain or [],
        duration_s=duration,
        sample_rate=sr,
        channels=nch,
    )
    writer.add_figure(fig)

    # ── Write PDF ──
    filename = build_operator_friendly_filename(sample_id, preset, "ct_scan")
    pdf_path = output_dir / filename
    writer.write_pdf(str(pdf_path))

    # ── Build Manifest ──
    manifest = PdfReportManifest(
        report_id=report_id,
        report_type="single",
        source_audio=wav_path,
        preset=preset,
        genre=genre,
        pdf_path=str(pdf_path),
        pages=writer.page_count,
        plates=["spectrogram", "frequency_balance", "waveform_dynamics", "summary"],
        mrs_before=mrs_before,
        mrs_after=mrs_after,
        mrs_delta=(mrs_after - mrs_before) if (mrs_before is not None and mrs_after is not None) else None,
        defect_flags=defect_flags or [],
        processing_chain=processing_chain or [],
    )
    manifest.quality_score = compute_ct_quality_score(manifest)
    manifest.write()

    writer.clear()
    return manifest


# ═══════════════════════════════════════════════════════════════════════════
# MHP-654/655: Before/After Comparison PDF Generator
# ═══════════════════════════════════════════════════════════════════════════

def generate_comparison_pdf(
    before_wav: str,
    after_wav: str,
    output_dir: Optional[Path] = None,
    sample_id: str = "",
    genre: str = "",
    preset: str = "",
    defect_flags: Optional[List[str]] = None,
    mrs_before: Optional[float] = None,
    mrs_after: Optional[float] = None,
    processing_chain: Optional[List[Dict[str, Any]]] = None,
    config: Optional[PdfReportConfig] = None,
) -> PdfReportManifest:
    """Generate a before/after comparison Acoustic CT PDF.

    MHP-663: Cloud produces one polished before/after PDF.

    Returns a PdfReportManifest.
    """
    cfg = (config or PdfReportConfig()).resolved()

    if output_dir is None:
        output_dir = cfg.output_dir / "comparison"
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    report_id = generate_report_id("CTCOMP")
    label = f"{sample_id} | {genre} | {preset}" if sample_id else ""

    template = PageTemplate(theme=cfg.theme, brand=cfg.brand)
    writer = PdfReportWriter(cfg)

    # ── Cover Page ──
    cover_lines = [
        f"Report ID: {report_id}",
        f"Sample: {sample_id or 'N/A'}",
        f"Genre: {genre or 'N/A'}",
        f"Preset: {preset or 'N/A'}",
        f"Generated: {utc_now_iso()}",
    ]
    if mrs_before is not None and mrs_after is not None:
        delta = mrs_after - mrs_before
        cover_lines.append(f"MRS: {mrs_before:.1f} → {mrs_after:.1f} (Δ {delta:+.1f})")
    writer.add_cover_page("Moodify Acoustic CT", "Before/After Comparison Report", cover_lines)

    # ── Before Spectrogram ──
    fig = build_spectrogram_page(before_wav, template,
                                 title="BEFORE — Spectrogram Scan", label=f"{label} (before)")
    writer.add_figure(fig)

    # ── After Spectrogram ──
    fig = build_spectrogram_page(after_wav, template,
                                 title="AFTER — Spectrogram Scan", label=f"{label} (after)")
    writer.add_figure(fig)

    # ── Before Frequency Balance ──
    fig = build_frequency_balance_page(before_wav, template,
                                       title="BEFORE — Frequency Balance", label=f"{label} (before)")
    writer.add_figure(fig)

    # ── After Frequency Balance ──
    fig = build_frequency_balance_page(after_wav, template,
                                       title="AFTER — Frequency Balance", label=f"{label} (after)")
    writer.add_figure(fig)

    # ── Before Waveform ──
    fig = build_waveform_dynamics_page(before_wav, template,
                                       title="BEFORE — Waveform Dynamics", label=f"{label} (before)")
    writer.add_figure(fig)

    # ── After Waveform ──
    fig = build_waveform_dynamics_page(after_wav, template,
                                       title="AFTER — Waveform Dynamics", label=f"{label} (after)")
    writer.add_figure(fig)

    # ── Summary / Diagnosis ──
    before_samples, sr_before, nch_before = _read_wav(before_wav)
    after_samples, sr_after, nch_after = _read_wav(after_wav)
    duration_before = len(before_samples) / sr_before if sr_before > 0 else 0

    fig = build_summary_diagnosis_page(
        template,
        sample_id=sample_id or Path(before_wav).name,
        genre=genre,
        preset=preset,
        defect_flags=defect_flags or [],
        mrs_before=mrs_before,
        mrs_after=mrs_after,
        processing_chain=processing_chain or [],
        duration_s=duration_before,
        sample_rate=sr_before,
        channels=nch_before,
    )
    writer.add_figure(fig)

    # ── Write PDF ──
    filename = build_operator_friendly_filename(sample_id, preset, "comparison")
    pdf_path = output_dir / filename
    writer.write_pdf(str(pdf_path))

    # ── Build Manifest ──
    manifest = PdfReportManifest(
        report_id=report_id,
        report_type="comparison",
        source_audio=before_wav,
        processed_audio=after_wav,
        preset=preset,
        genre=genre,
        pdf_path=str(pdf_path),
        pages=writer.page_count,
        plates=["spectrogram_before", "spectrogram_after",
                "frequency_balance_before", "frequency_balance_after",
                "waveform_before", "waveform_after",
                "summary"],
        mrs_before=mrs_before,
        mrs_after=mrs_after,
        mrs_delta=(mrs_after - mrs_before) if (mrs_before is not None and mrs_after is not None) else None,
        defect_flags=defect_flags or [],
        processing_chain=processing_chain or [],
    )
    manifest.quality_score = compute_ct_quality_score(manifest)
    manifest.write()

    writer.clear()
    return manifest
