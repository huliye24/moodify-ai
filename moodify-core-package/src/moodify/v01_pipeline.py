"""v01_pipeline.py — Moodify v0.1.0 main processing pipeline.

Scan → Analyze → Diagnose → Process → Validate → Report → Generate

This is the ONLY orchestration file the v0.1.0 mainline touches.
The v1.x WorkflowOrchestrator (938 lines) is preserved for future use.
"""

import json
import os
import time
from pathlib import Path
from typing import Any, Callable

from moodify.audio_io import load_audio
from moodify.processing.pedalboard_chain import MoodifyDSPChain
from moodify.v01_types import (
    DeliveryBundle,
    DiagnosisReport,
    ProcessResult,
    QualityGate,
    ScanResult,
)
from moodify.v01_analyzer import analyze, spectrum_png_path
from moodify.v01_diagnostics import diagnose
from moodify.v01_exporter import export
from moodify.v01_presets import get_preset, list_presets


def process_audio(input_path: str,
                  preset: str = "clean_master",
                  output_dir: str = "outputs",
                  on_stage: Callable[[str, float], None] | None = None) -> ProcessResult:
    """Run the complete v0.1.0 pipeline on one audio file.

    Args:
        input_path: path to WAV/MP3/FLAC file
        preset: key from v01_presets.PRESETS or "auto"
        output_dir: output directory
        on_stage: optional callback(stage_name, progress) fired at each
            pipeline stage boundary (S/A/D/P/V/R/G), progress in [0, 1]

    Returns:
        ProcessResult with metrics, diagnosis, and output path
    """
    t0 = time.perf_counter()
    stage_timings: dict[str, float] = {}

    def _emit(stage: str, progress: float) -> None:
        if on_stage is not None:
            on_stage(stage, round(progress, 3))

    # S: Scan audio
    _emit("scan", 0.05)
    scan_t0 = time.perf_counter()
    scan = scan_audio(input_path)
    stage_timings["S_scan_s"] = _elapsed(scan_t0)
    _emit("scan", 0.15)
    if not scan.exists:
        return ProcessResult(input_path=input_path, success=False,
                             scan=scan, stage_timings=stage_timings,
                             error=f"File not found: {input_path}")
    if not scan.readable:
        return ProcessResult(input_path=input_path, success=False,
                             scan=scan, stage_timings=stage_timings,
                             error="Audio file is not readable.")

    requested_preset = preset
    if preset != "auto" and get_preset(preset) is None:
        valid = ", ".join(["auto", *list_presets()])
        return ProcessResult(input_path=input_path, requested_preset=preset,
                             scan=scan, stage_timings=stage_timings,
                             success=False,
                             error=f"Unknown preset '{preset}'. Valid: {valid}")

    preset_info = get_preset("clean_master")
    if preset_info is None:
        valid = ", ".join(list_presets())
        return ProcessResult(input_path=input_path, success=False,
                            error=f"Unknown preset '{preset}'. Valid: {valid}")

    try:
        # A: Analyze features
        _emit("analyze", 0.15)
        analyze_t0 = time.perf_counter()
        metrics = analyze(input_path, output_dir, label="before")
        stage_timings["A_analyze_s"] = _elapsed(analyze_t0)
        _emit("analyze", 0.35)

        # D: Diagnose audio
        _emit("diagnose", 0.35)
        diagnose_t0 = time.perf_counter()
        report = diagnose(metrics)
        selected_preset = _select_preset(requested_preset, report)
        preset_info = get_preset(selected_preset)
        stage_timings["D_diagnose_s"] = _elapsed(diagnose_t0)
        _emit("diagnose", 0.45)

        # P: Process audio
        _emit("process", 0.45)
        process_t0 = time.perf_counter()
        audio, sr = load_audio(input_path, always_2d=False)
        chain = MoodifyDSPChain(preset_info["params"])
        processed = chain.process(audio, sr)
        processed = _post_process_safety(processed)
        stage_timings["P_process_s"] = _elapsed(process_t0)
        _emit("process", 0.65)

        # V: Validate output
        _emit("validate", 0.65)
        validate_t0 = time.perf_counter()
        output_path = export(processed, sr, input_path, selected_preset, output_dir)
        metrics_after = analyze(output_path, output_dir, label="after")
        quality_gate = _quality_gate(metrics, metrics_after)
        stage_timings["V_validate_s"] = _elapsed(validate_t0)
        _emit("validate", 0.80)

        elapsed = time.perf_counter() - t0
        stage_timings["total_s"] = round(elapsed, 3)

        # R: Report output
        _emit("report", 0.80)
        report_t0 = time.perf_counter()
        pdf_report_path = _save_pdf_report(
            scan=scan,
            report=report,
            output_path=output_path,
            preset=selected_preset,
            requested_preset=requested_preset,
            metrics_after=metrics_after,
            quality_gate=quality_gate,
            stage_timings=stage_timings,
        )
        stage_timings["R_report_s"] = _elapsed(report_t0)
        _emit("report", 0.90)

        # G: Generate delivery bundle
        _emit("generate", 0.90)
        generate_t0 = time.perf_counter()
        stage_timings["G_generate_s"] = 0.0
        stage_timings["total_s"] = _elapsed(t0)
        report_path = _save_report(
            scan=scan,
            report=report,
            output_path=output_path,
            preset=selected_preset,
            requested_preset=requested_preset,
            elapsed_s=elapsed,
            metrics_after=metrics_after,
            quality_gate=quality_gate,
            output_dir=output_dir,
            stage_timings=stage_timings,
            pdf_report_path=pdf_report_path,
        )
        delivery = DeliveryBundle(
            output_audio=output_path,
            json_report=report_path,
            pdf_report=pdf_report_path,
            spectrum_before=os.path.abspath(
                spectrum_png_path(input_path, output_dir, label="before")
            ),
            spectrum_after=os.path.abspath(
                spectrum_png_path(output_path, output_dir, label="after")
            ),
        )

        # MAP v0.2 delivery artifacts (MHP-875/876)
        _generate_delivery_artifacts(
            delivery=delivery,
            output_path=output_path,
            output_dir=output_dir,
            selected_preset=selected_preset,
            input_path=input_path,
            quality_gate=quality_gate,
            metrics_after=metrics_after,
            elapsed_s=elapsed,
        )

        stage_timings["G_generate_s"] = _elapsed(generate_t0)
        stage_timings["total_s"] = _elapsed(t0)
        _emit("generate", 1.0)

        return ProcessResult(
            input_path=input_path,
            output_path=output_path,
            preset=selected_preset,
            requested_preset=requested_preset,
            report_path=report_path,
            scan=scan,
            metrics_before=metrics,
            metrics_after=metrics_after,
            diagnosis=report,
            quality_gate=quality_gate,
            delivery=delivery,
            stage_timings=stage_timings,
            success=True,
        )

    except Exception as e:
        return ProcessResult(
            input_path=input_path,
            preset=preset if preset != "auto" else "",
            requested_preset=preset,
            scan=scan,
            stage_timings=stage_timings,
            success=False,
            error=str(e),
        )


def scan_audio(input_path: str) -> ScanResult:
    """Scan file availability and coarse audio readability.

    v0.2 (MHP-864): Also computes loudness, transient, stereo width,
    spectral centroid, DC offset, and clip count when audio decodes.
    """
    import numpy as np

    path = Path(input_path)
    scan = ScanResult(
        input_path=input_path,
        exists=path.exists(),
        extension=path.suffix.lower(),
        file_size_bytes=path.stat().st_size if path.exists() else 0,
    )
    if not scan.exists:
        scan.warnings.append("Input file does not exist.")
        return scan
    if scan.file_size_bytes == 0:
        scan.warnings.append("Input file is empty.")
        return scan
    try:
        audio, sr = load_audio(input_path, always_2d=False)
        scan.readable = bool(sr > 0 and getattr(audio, "size", 0) > 0)
        if not scan.readable:
            return scan

        # -- MAP v0.2 acoustic surface (MHP-864) --
        mono = audio if audio.ndim == 1 else audio.mean(axis=1)
        mono = np.asarray(mono, dtype=np.float32)
        peak = float(np.max(np.abs(mono))) if mono.size else 0.0

        # loudness_lufs: RMS → approximate LUFS
        rms = float(np.sqrt(np.mean(mono ** 2)) + 1e-12)
        scan.loudness_lufs = round(-0.691 + 20.0 * np.log10(rms + 1e-12), 1)

        # transient_ratio: peak / moving-RMS mean (100ms windows)
        win_len = int(0.1 * sr)
        if win_len >= 4 and len(mono) >= win_len:
            hop = max(1, win_len // 2)
            rms_wins = []
            for i in range(0, len(mono) - win_len, hop):
                w = mono[i : i + win_len]
                rms_wins.append(float(np.sqrt(np.mean(w ** 2)) + 1e-12))
            mean_rms = float(np.mean(rms_wins)) if rms_wins else rms
            scan.transient_ratio = round(peak / (mean_rms + 1e-12), 2)

        # stereo_width: 1 - |correlation_lr|
        if audio.ndim > 1 and audio.shape[1] >= 2:
            left = np.asarray(audio[:, 0], dtype=np.float32)
            right = np.asarray(audio[:, 1], dtype=np.float32)
            std_l, std_r = np.std(left), np.std(right)
            if std_l > 1e-12 and std_r > 1e-12:
                corr = float(np.corrcoef(left, right)[0, 1])
                scan.stereo_width = round(1.0 - abs(corr), 3)
            else:
                scan.stereo_width = 0.0
        else:
            scan.stereo_width = 0.0

        # spectral_centroid_hz: weighted mean of FFT magnitudes
        try:
            n = len(mono)
            fft = np.abs(np.fft.rfft(mono * np.hanning(n)))
            freqs = np.fft.rfftfreq(n, 1.0 / sr)
            centroid = float(np.sum(freqs * fft) / (np.sum(fft) + 1e-12))
            scan.spectral_centroid_hz = round(centroid, 0)
        except Exception:
            pass

        # dc_offset: signal mean relative to full scale
        scan.dc_offset = round(float(np.mean(mono)), 6)

        # clip_count: samples at digital ceiling
        scan.clip_count = int(np.sum(np.abs(mono) >= 0.999))

    except Exception as exc:
        scan.warnings.append(f"Audio decode failed: {exc}")
    return scan


def _select_preset(requested_preset: str, report: DiagnosisReport) -> str:
    if requested_preset != "auto":
        return requested_preset
    for candidate in report.suggested_presets:
        if get_preset(candidate) is not None:
            return candidate
    return "clean_master"


def _post_process_safety(audio):
    """Clamp extreme peaks and remove non-finite samples before export."""
    import numpy as np

    safe = np.nan_to_num(audio, nan=0.0, posinf=0.0, neginf=0.0).astype("float32")
    peak = float(np.max(np.abs(safe))) if safe.size else 0.0
    if peak > 0.98:
        safe = safe * (0.98 / peak)
    return safe


def _quality_gate(before, after) -> QualityGate:
    """Before/after safety checks for a processed file.

    v0.2 (MHP-869): Uses mrs_adapter when available; falls back to inline proxy.
    """
    from moodify.mrs_adapter import score_for_quality_gate

    # Try calibrated MRS adapter (requires file paths from AudioMetrics)
    before_path = getattr(before, "file_path", "")
    after_path = getattr(after, "file_path", "")
    if before_path and after_path:
        try:
            return score_for_quality_gate(
                before_path=before_path,
                after_path=after_path,
            )
        except Exception:
            pass  # fall back to inline proxy below

    # Inline proxy fallback (original v0.1 behavior)
    warnings: list[str] = []
    deltas = {
        "peak_db": round(after.peak_db - before.peak_db, 2),
        "crest_factor": round(after.crest_factor - before.crest_factor, 2),
        "dynamic_range_db": round(after.dynamic_range_db - before.dynamic_range_db, 2),
        "correlation_lr": round(after.correlation_lr - before.correlation_lr, 3),
        "air": round(after.rms_air - before.rms_air, 2),
        "presence": round(after.rms_presence - before.rms_presence, 2),
        "bass": round(after.rms_bass - before.rms_bass, 2),
    }
    if after.peak_db > -0.1:
        warnings.append("Output peak is too close to 0 dBFS.")
    if deltas["dynamic_range_db"] < -4.0:
        warnings.append("Processing reduced dynamic range by more than 4 dB.")
    if after.channels == 2 and after.correlation_lr < 0.05:
        warnings.append("Output stereo correlation is very low; check mono compatibility.")
    if deltas["air"] < -6.0:
        warnings.append("Processing removed substantial air-band energy.")
    mrs_before = _mrs_proxy(before)
    mrs_after = _mrs_proxy(after)
    mrs_delta = round(mrs_after - mrs_before, 2)
    damage_loss = _damage_loss(deltas, warnings)
    risk_flags = _risk_flags(deltas, warnings, mrs_delta, damage_loss)
    if mrs_delta < -1.0:
        warnings.append("MRS proxy decreased after processing.")
    passed = not warnings and damage_loss < 0.25
    return QualityGate(
        passed=passed,
        warnings=warnings,
        deltas=deltas,
        mrs_before=mrs_before,
        mrs_after=mrs_after,
        mrs_delta=mrs_delta,
        damage_loss=damage_loss,
        risk_flags=risk_flags,
    )


def _mrs_proxy(metrics) -> float:
    """Temporary v0.1 MRS proxy; replace with calibrated MRS in MAP v0.2."""
    def clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
        return max(low, min(high, value))

    dynamic = clamp(1.0 - abs(metrics.dynamic_range_db - 10.0) / 20.0)
    crest = clamp(1.0 - abs(metrics.crest_factor - 5.0) / 8.0)
    if metrics.channels == 1:
        stereo = 0.7
    else:
        stereo = clamp(1.0 - abs(metrics.correlation_lr - 0.6) / 0.8)
    air = clamp(1.0 - abs(metrics.rms_air + 18.0) / 22.0)
    presence = clamp(1.0 - abs(metrics.rms_presence + 12.0) / 22.0)
    peak = clamp(1.0 - max(0.0, metrics.peak_db + 0.2) / 6.0)
    score = 800.0 + 400.0 * ((dynamic + crest + stereo + air + presence + peak) / 6.0)
    return round(score, 2)


def _damage_loss(deltas: dict, warnings: list[str]) -> float:
    loss = 0.04 * len(warnings)
    loss += max(0.0, -deltas["dynamic_range_db"] - 2.0) * 0.03
    loss += max(0.0, -deltas["air"] - 3.0) * 0.025
    loss += max(0.0, -deltas["crest_factor"] - 1.5) * 0.025
    return round(min(loss, 1.0), 3)


def _risk_flags(deltas: dict, warnings: list[str], mrs_delta: float,
                damage_loss: float) -> list[str]:
    flags = []
    if any("peak" in warning.lower() for warning in warnings):
        flags.append("peak_risk")
    if deltas["air"] < -6.0:
        flags.append("over_dark")
    if deltas["dynamic_range_db"] < -4.0:
        flags.append("dynamic_damage")
    if mrs_delta < -1.0:
        flags.append("mrs_regression")
    if damage_loss >= 0.25:
        flags.append("damage_loss_high")
    return flags


def _save_report(scan: ScanResult, report: DiagnosisReport, output_path: str,
                 preset: str, requested_preset: str, elapsed_s: float,
                 metrics_after, quality_gate: QualityGate, output_dir: str,
                 stage_timings: dict, pdf_report_path: str = "") -> str:
    """Write a structured delivery JSON report next to the output file."""
    report_path = output_path.replace(".wav", "_report.json")
    before_spectrum = os.path.abspath(
        spectrum_png_path(scan.input_path, output_dir, label="before")
    )
    after_spectrum = os.path.abspath(
        spectrum_png_path(output_path, output_dir, label="after")
    )
    data = {
        "workflow": [
            "S_scan",
            "A_analyze",
            "D_diagnose",
            "P_process",
            "V_validate",
            "R_report",
            "G_generate",
        ],
        "preset": preset,
        "requested_preset": requested_preset,
        "elapsed_s": round(elapsed_s, 1),
        "stage_timings": stage_timings,
        "scan": scan.to_dict(),
        "feature_analysis": report.metrics.to_dict(),
        "diagnosis_report": report.to_dict(),
        "validation_result": quality_gate.to_dict(),
        "quality_gate": quality_gate.to_dict(),
        "metrics_before": report.metrics.to_dict(),
        "metrics_after": metrics_after.to_dict(),
        "delivery": {
            "output_audio": os.path.abspath(output_path),
            "json_report": os.path.abspath(report_path),
            "pdf_report": pdf_report_path,
            "spectrum_before": before_spectrum,
            "spectrum_after": after_spectrum,
        },
        **report.to_dict(),
    }
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return os.path.abspath(report_path)


def _save_pdf_report(scan: ScanResult, report: DiagnosisReport, output_path: str,
                     preset: str, requested_preset: str, metrics_after,
                     quality_gate: QualityGate, stage_timings: dict) -> str:
    """Write a compact before/after PDF report if matplotlib is available."""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        from matplotlib.backends.backend_pdf import PdfPages
        import numpy as np
    except Exception:
        return ""

    pdf_path = os.path.abspath(output_path.replace(".wav", "_report.pdf"))
    bands = ["sub", "bass", "low_mid", "mid", "presence", "air"]
    before = np.array([
        report.metrics.rms_sub,
        report.metrics.rms_bass,
        report.metrics.rms_low_mid,
        report.metrics.rms_mid,
        report.metrics.rms_presence,
        report.metrics.rms_air,
    ])
    after = np.array([
        metrics_after.rms_sub,
        metrics_after.rms_bass,
        metrics_after.rms_low_mid,
        metrics_after.rms_mid,
        metrics_after.rms_presence,
        metrics_after.rms_air,
    ])

    with PdfPages(pdf_path) as pdf:
        fig = plt.figure(figsize=(8.27, 11.69))
        fig.suptitle("Moodify Delivery Report", fontsize=18, y=0.96)
        lines = [
            f"Source: {Path(scan.input_path).name}",
            f"Requested preset: {requested_preset}",
            f"Applied preset: {preset}",
            f"Health: {report.overall_health}",
            f"Quality gate: {'pass' if quality_gate.passed else 'review'}",
            f"Output: {Path(output_path).name}",
            "",
            "Workflow:",
            "1. Scan audio",
            "2. Analyze features",
            "3. Diagnose audio",
            "4. Process audio",
            "5. Validate output",
            "6. Report output",
            "7. Generate delivery",
        ]
        fig.text(0.08, 0.88, "\n".join(lines), va="top", fontsize=11)
        if report.issues:
            fig.text(0.08, 0.42, "Issues:\n" + "\n".join(report.issues[:6]),
                     va="top", fontsize=10)
        if quality_gate.warnings:
            fig.text(0.08, 0.24,
                     "Quality warnings:\n" + "\n".join(quality_gate.warnings[:6]),
                     va="top", fontsize=10)
        pdf.savefig(fig, bbox_inches="tight")
        plt.close(fig)

        fig, axes = plt.subplots(2, 1, figsize=(8.27, 11.69))
        x = np.arange(len(bands))
        width = 0.38
        axes[0].bar(x - width / 2, before, width, label="Before")
        axes[0].bar(x + width / 2, after, width, label="After")
        axes[0].set_title("Spectrum Before / After")
        axes[0].set_ylabel("Relative dB")
        axes[0].set_xticks(x)
        axes[0].set_xticklabels(bands)
        axes[0].legend()

        delta_items = list(quality_gate.deltas.items())
        axes[1].bar([k for k, _ in delta_items], [v for _, v in delta_items])
        axes[1].axhline(0, color="black", linewidth=0.8)
        axes[1].set_title("Processing Delta")
        axes[1].set_ylabel("After - Before")
        axes[1].tick_params(axis="x", rotation=35)
        fig.tight_layout()
        pdf.savefig(fig, bbox_inches="tight")
        plt.close(fig)

        fig = plt.figure(figsize=(8.27, 11.69))
        fig.suptitle("Delivery Manifest", fontsize=16, y=0.96)
        manifest_lines = [
            f"Output audio: {os.path.abspath(output_path)}",
            f"PDF report: {pdf_path}",
            f"MRS proxy before: {quality_gate.mrs_before}",
            f"MRS proxy after: {quality_gate.mrs_after}",
            f"MRS proxy delta: {quality_gate.mrs_delta}",
            "",
            "Stage timings:",
            *[f"{key}: {value}s" for key, value in stage_timings.items()],
        ]
        fig.text(0.08, 0.9, "\n".join(manifest_lines), va="top", fontsize=9)
        pdf.savefig(fig, bbox_inches="tight")
        plt.close(fig)

    return pdf_path


def _generate_delivery_artifacts(
    delivery: DeliveryBundle,
    output_path: str,
    output_dir: str,
    selected_preset: str,
    input_path: str,
    quality_gate: QualityGate,
    metrics_after,
    elapsed_s: float,
) -> None:
    """Generate MAP v0.2 delivery artifacts (MHP-875/876/877).

    Creates: manifest.json, metadata.json, environment.txt,
    validation_report.json, MAP_CHAIN_VERSION.
    Populates delivery bundle with paths.
    """
    try:
        from moodify.v01_delivery import (
            write_delivery_manifest,
            write_metadata,
            write_validation_report,
            write_version_file,
        )
    except ImportError:
        return

    run_id = Path(output_path).stem

    # Build artifact list for manifest
    artifacts: list[dict[str, Any]] = [
        {"path": output_path, "role": "output_audio", "format": "wav"},
        {"path": delivery.json_report, "role": "json_report", "format": "json"},
        {"path": delivery.pdf_report, "role": "pdf_report", "format": "pdf"},
        {"path": delivery.spectrum_before, "role": "spectrum_before", "format": "png"},
        {"path": delivery.spectrum_after, "role": "spectrum_after", "format": "png"},
    ]

    # Manifest (MHP-875)
    delivery.manifest = write_delivery_manifest(
        output_dir=output_dir,
        run_id=run_id,
        artifacts=artifacts,
        pipeline_info={
            "version": "0.1.0",
            "stages": [
                "S_scan", "A_analyze", "D_diagnose",
                "P_process", "V_validate", "R_report", "G_generate",
            ],
            "preset": selected_preset,
            "elapsed_s": round(elapsed_s, 1),
        },
    )

    # Metadata + environment (MHP-876)
    metadata_path, env_path = write_metadata(
        output_dir=output_dir,
        run_id=run_id,
        input_path=input_path,
    )
    delivery.metadata = metadata_path
    delivery.environment = env_path

    # Standalone validation report (MHP-877)
    delivery.validation_report = write_validation_report(
        output_dir=output_dir,
        quality_gate=quality_gate.to_dict(),
    )

    # Version file
    delivery.version_file = write_version_file(output_dir)


def _elapsed(start: float) -> float:
    return round(time.perf_counter() - start, 3)
