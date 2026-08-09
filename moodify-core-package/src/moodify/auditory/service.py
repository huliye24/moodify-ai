"""Auditory scan service — orchestration layer (DSK-MFY-AUDITORY-SCAN-001).

scan_audio / register_candidate / compare_scans / build_comparison_report /
verify_evidence_bundle. The source file is never modified; all outputs are
written atomically into a per-case evidence directory.
"""

from __future__ import annotations

import json
import shutil
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

from moodify.auditory.comparison import (
    ScanEvidence,
    build_delta_spectrograms,
    compute_deltas,
    validate_pair,
)
from moodify.auditory.decode import decode
from moodify.auditory.errors import (
    CandidateHashMismatch,
    CandidateNotRegistered,
    ComparisonEvidenceIncomplete,
    EvidenceHashMismatch,
    MetricsComputationFailed,
)
from moodify.auditory.judgment import (
    evaluate_risk_flags,
    judge,
    write_judgment_rules,
)
from moodify.auditory.manifests import (
    sha256_file,
    verify_manifest_hashes,
    write_comparison_manifest,
    write_scan_manifest,
)
from moodify.auditory.metrics import compute_metrics
from moodify.auditory.models import Candidate
from moodify.auditory.profiles import ScanProfile, get_profile
from moodify.auditory.reports import (
    build_auditory_report,
    build_comparison_report,
    build_contact_sheet,
)
from moodify.auditory.spectrogram import SpectrogramRun, generate_spectrogram
from moodify.auditory.stereo import compute_stereo_metrics
from moodify.auditory.timeline import compute_timeline, write_timeline_jsonl


@dataclass
class ScanOutput:
    case_id: str
    stage: str  # before | after
    scan_dir: Path
    metrics: dict
    timeline: list[dict]
    arrays: dict
    spectrograms: dict[str, SpectrogramRun]
    manifest: dict
    duration_s: float
    channels: int
    profile: ScanProfile
    profile_hash: str


def _environment() -> dict:
    import platform
    import sys
    return {
        "python_version": sys.version.split()[0],
        "platform": platform.platform(),
        "numpy_version": np.__version__,
        "ffmpeg": shutil.which("ffmpeg"),
    }


def _stft_views(mono: np.ndarray, sr: int, n_fft: int = 8192, hop: int = 2048, n_bins: int = 256) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Streamed STFT -> two downsampled views (linear/log) with frequency axes.

    Vectorized re-binning (bincount) so full-length songs stay fast.
    """
    freqs = np.fft.rfftfreq(n_fft, 1 / sr)
    n_frames = max(1, (len(mono) - n_fft) // hop + 1)
    win = np.hanning(n_fft)

    log_bins = np.geomspace(20.0, min(sr / 2, 24000.0), n_bins + 1)
    log_bins[0] = 0.0
    lin_edges = np.linspace(0.0, sr / 2, n_bins + 1)

    lin_idx = np.clip(np.searchsorted(lin_edges, freqs, side="right") - 1, 0, n_bins - 1)
    log_idx = np.clip(np.searchsorted(log_bins, freqs, side="right") - 1, 0, n_bins - 1)

    linear = np.zeros((n_frames, n_bins), dtype=np.float32)
    log = np.zeros((n_frames, n_bins), dtype=np.float32)
    for i in range(n_frames):
        seg = mono[i * hop: i * hop + n_fft]
        if len(seg) < n_fft:
            seg = np.pad(seg, (0, n_fft - len(seg)))
        spec = np.abs(np.fft.rfft(seg * win))
        power = spec.astype(np.float64) ** 2
        counts_lin = np.bincount(lin_idx, minlength=n_bins)
        energy_lin = np.bincount(lin_idx, weights=power, minlength=n_bins)
        with np.errstate(divide="ignore", invalid="ignore"):
            mean_lin = np.where(counts_lin > 0, energy_lin / np.maximum(counts_lin, 1), 0.0)
        linear[i] = np.sqrt(mean_lin + 1e-12).astype(np.float32)
        counts_log = np.bincount(log_idx, minlength=n_bins)
        energy_log = np.bincount(log_idx, weights=power, minlength=n_bins)
        with np.errstate(divide="ignore", invalid="ignore"):
            mean_log = np.where(counts_log > 0, energy_log / np.maximum(counts_log, 1), 0.0)
        log[i] = np.sqrt(mean_log + 1e-12).astype(np.float32)

    lin_centers = (lin_edges[:-1] + lin_edges[1:]) / 2
    log_centers = np.sqrt(log_bins[:-1] * log_bins[1:])
    return linear, log, lin_centers, log_centers


def scan_audio(
    case_id: str,
    stage: str,
    input_path: Path,
    scan_dir: Path,
    profile: ScanProfile | None = None,
    timeout_s: int = 300,
) -> ScanOutput:
    """Full before/after scan: spectrograms + metrics + timeline + arrays."""
    profile = profile or get_profile("MFY-WSE-SCAN-PROFILE-001")
    input_path = Path(input_path)
    if not input_path.is_file():
        from moodify.auditory.errors import AuditoryScanInputNotFound
        raise AuditoryScanInputNotFound(f"input not found: {input_path}", case_id=case_id)

    scan_dir.mkdir(parents=True, exist_ok=True)
    log_dir = scan_dir / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    # primary spectrograms (FFmpeg showspectrumpic)
    linear_path = scan_dir / "spectrum_linear.png"
    log_path = scan_dir / "spectrum_log.png"
    linear_run = generate_spectrogram(input_path, linear_path, profile, "linear", timeout_s)
    log_run = generate_spectrogram(input_path, log_path, profile, "logarithmic", timeout_s)

    # decode + measure
    audio = decode(input_path, profile.analysis_sample_rate, timeout_s)
    mono = audio.samples.mean(axis=1) if audio.samples.ndim > 1 else audio.samples
    channels = audio.samples.shape[1] if audio.samples.ndim > 1 else 1

    try:
        metrics = compute_metrics(audio.samples, audio.sample_rate, audio.probe)
        metrics.update(compute_stereo_metrics(audio.samples))
        metrics["duration"] = {"value": round(audio.probe.duration_seconds, 3), "unit": "s",
                               "method": "ffprobe", "status": "VALID", "warnings": []}
        metrics["channels"] = {"value": channels, "unit": "ch", "method": "ffprobe",
                               "status": "VALID", "warnings": []}
        metrics["sample_rate"] = {"value": audio.probe.sample_rate, "unit": "Hz", "method": "ffprobe",
                                  "status": "VALID", "warnings": []}
        metrics["source_sha256"] = {"value": audio.probe.sha256, "unit": "", "method": "sha256",
                                    "status": "VALID", "warnings": []}
    except Exception as exc:
        raise MetricsComputationFailed(str(exc), case_id=case_id, cause=exc) from exc

    # timeline
    rows = compute_timeline(
        audio.samples, audio.sample_rate,
        profile.timeline_window_seconds, profile.timeline_hop_seconds,
    )
    timeline_path = scan_dir / "timeline_metrics.jsonl"
    write_timeline_jsonl(rows, timeline_path)

    # numerical arrays for comparison
    linear_arr, log_arr, lin_freqs, log_freqs = _stft_views(mono, audio.sample_rate)
    npz_path = scan_dir / "analysis_data.npz"
    np.savez_compressed(
        npz_path,
        stft_linear=linear_arr,
        stft_log=log_arr,
        freqs_linear=lin_freqs,
        freqs_log=log_freqs,
    )

    # metrics.json
    metrics_path = scan_dir / "metrics.json"
    metrics_path.write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")

    # manifest
    manifest_path = scan_dir / "scan_manifest.json"
    write_scan_manifest(
        manifest_path,
        case_id=case_id,
        stage=stage,
        input_path=input_path,
        input_sha256=audio.probe.sha256,
        profile_id=profile.profile_id,
        profile_hash=profile.hash(),
        artifacts={
            "spectrum_linear": linear_path,
            "spectrum_log": log_path,
            "metrics": metrics_path,
            "timeline": timeline_path,
            "analysis_data": npz_path,
        },
        environment=_environment(),
        commands=[
            {"command": " ".join(str(x) for x in linear_run.command), "return_code": linear_run.return_code},
            {"command": " ".join(str(x) for x in log_run.command), "return_code": log_run.return_code},
        ],
    )
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    return ScanOutput(
        case_id=case_id,
        stage=stage,
        scan_dir=scan_dir,
        metrics=metrics,
        timeline=rows,
        arrays={
            "stft_linear": linear_arr,
            "stft_log": log_arr,
            "freqs_linear": lin_freqs,
            "freqs_log": log_freqs,
        },
        spectrograms={"linear": linear_run, "log": log_run},
        manifest=manifest,
        duration_s=audio.probe.duration_seconds,
        channels=channels,
        profile=profile,
        profile_hash=profile.hash(),
    )


def load_scan_evidence(scan_dir: Path, profile: ScanProfile) -> ScanEvidence:
    """Reload a completed scan directory as comparison-ready evidence."""
    metrics_path = scan_dir / "metrics.json"
    npz_path = scan_dir / "analysis_data.npz"
    if not metrics_path.is_file() or not npz_path.is_file():
        raise ComparisonEvidenceIncomplete(f"scan evidence incomplete: {scan_dir}")

    manifest = json.loads((scan_dir / "scan_manifest.json").read_text(encoding="utf-8"))
    problems = verify_manifest_hashes(manifest)
    if problems:
        raise EvidenceHashMismatch("; ".join(problems))

    metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
    arrays = np.load(npz_path)
    case_id = manifest.get("case_id", "")
    profile_hash = manifest.get("scan_profile_hash", "")
    return ScanEvidence(
        case_id=case_id,
        profile=profile,
        profile_hash=profile_hash,
        duration_s=metrics.get("duration", {}).get("value", 0.0),
        channels=metrics.get("channels", {}).get("value", 1),
        metrics=metrics,
        timeline=list(metrics_path.parent.glob("timeline_metrics.jsonl")),
        arrays={k: arrays[k] for k in arrays.files},
        scan_dir=scan_dir,
    )


def register_candidate(
    case_id: str,
    candidate_id: str,
    source_case_id: str,
    candidate_path: Path,
    parent_source_sha256: str,
    producing_application: str = "Audacity",
    producing_application_version: str | None = None,
    processing_operator: str = "",
    processing_method: str = "EXTERNAL_GUI_PROCESSING",
    processing_notes: str = "",
    registry_path: Path | None = None,
) -> Candidate:
    candidate_path = Path(candidate_path)
    if not candidate_path.is_file():
        raise CandidateNotRegistered(f"candidate file not found: {candidate_path}", case_id=case_id)
    candidate = Candidate(
        case_id=case_id,
        candidate_id=candidate_id,
        source_case_id=source_case_id,
        candidate_path=str(candidate_path.resolve()),
        candidate_sha256=sha256_file(candidate_path),
        created_at=datetime.now(timezone.utc).isoformat(),
        producing_application=producing_application,
        producing_application_version=producing_application_version,
        processing_operator=processing_operator,
        processing_method=processing_method,
        processing_notes=processing_notes,
        parent_source_sha256=parent_source_sha256,
    )
    if registry_path is not None:
        registry_path.mkdir(parents=True, exist_ok=True)
        (registry_path / f"{candidate_id}.json").write_text(
            json.dumps(candidate.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8"
        )
    return candidate


def load_candidate(registry_path: Path, candidate_id: str) -> Candidate:
    path = registry_path / f"{candidate_id}.json"
    if not path.is_file():
        raise CandidateNotRegistered(f"candidate not registered: {candidate_id}")
    data = json.loads(path.read_text(encoding="utf-8"))
    return Candidate(**data)


def verify_candidate_audio(candidate: Candidate) -> None:
    path = Path(candidate.candidate_path)
    if not path.is_file():
        raise CandidateNotRegistered(f"candidate file missing: {path}")
    actual = sha256_file(path)
    if actual != candidate.candidate_sha256:
        raise CandidateHashMismatch(
            f"candidate hash mismatch: recorded {candidate.candidate_sha256[:12]} != actual {actual[:12]}"
        )


def compare_scans(
    before: ScanEvidence,
    after: ScanEvidence,
    plan: dict | None,
    comparison_dir: Path,
    *,
    case_id: str,
    candidate_id: str,
    source_sha256: str,
    candidate_sha256: str,
) -> dict:
    """Full comparison: deltas + delta spectrograms + judgment + report."""
    validate_pair(before, after)
    comparison_dir.mkdir(parents=True, exist_ok=True)

    deltas = compute_deltas(before, after)

    # delta spectrograms from numerical data (loudness-normalized by default)
    linear_delta = comparison_dir / "delta_spectrum_linear.png"
    log_delta = comparison_dir / "delta_spectrum_log.png"
    build_delta_spectrograms(
        before.arrays, after.arrays,
        gain_db=deltas.normalization_gain_db if deltas.normalization_valid else 0.0,
        out_linear=linear_delta,
        out_log=log_delta,
    )

    # metrics delta file
    delta_path = comparison_dir / "metrics_delta.json"
    delta_payload = {
        "metric_deltas": deltas.metric_delta,
        "normalization": {
            "before_integrated_lufs": before.metrics.get("integrated_lufs", {}).get("value"),
            "after_integrated_lufs": after.metrics.get("integrated_lufs", {}).get("value"),
            "normalization_gain_db": deltas.normalization_gain_db,
            "normalization_valid": deltas.normalization_valid,
            "method": deltas.normalized_method,
        },
        "raw_band_deltas": deltas.raw_band_deltas,
        "normalized_band_deltas": deltas.normalized_band_deltas,
    }
    delta_path.write_text(json.dumps(delta_payload, ensure_ascii=False, indent=2), encoding="utf-8")

    # judgment
    risk_flags = evaluate_risk_flags(deltas.metric_delta, before.metrics, after.metrics)
    judgment = judge(deltas.metric_delta, before.metrics, after.metrics, plan, risk_flags)
    judgment_rules_path = comparison_dir / "judgment_rules.json"
    write_judgment_rules(judgment_rules_path)

    # contact sheet
    sheet = comparison_dir / "comparison_contact_sheet.png"
    build_contact_sheet(
        before.scan_dir / "spectrum_linear.png",
        after.scan_dir / "spectrum_linear.png",
        before.scan_dir / "spectrum_log.png",
        after.scan_dir / "spectrum_log.png",
        sheet,
        case_id=case_id,
        source_sha_short=source_sha256[:10],
        candidate_sha_short=candidate_sha256[:10],
        profile_id=before.profile.profile_id,
    )

    # comparison report
    report_path = comparison_dir / "comparison_report.json"
    build_comparison_report(
        report_path,
        case_id=case_id,
        candidate_id=candidate_id,
        profile_id=before.profile.profile_id,
        profile_hash=before.profile_hash,
        metric_delta=deltas.metric_delta,
        judgment=judgment.to_dict(),
        normalization=delta_payload["normalization"],
        raw_band_deltas=deltas.raw_band_deltas,
        normalized_band_deltas=deltas.normalized_band_deltas,
        plan_id=plan.get("plan_id") if plan else None,
        judgment_rules=json.loads(judgment_rules_path.read_text(encoding="utf-8")),
        source_sha256=source_sha256,
        candidate_sha256=candidate_sha256,
    )

    auditory_report_path = comparison_dir / "auditory_report.json"
    evidence_index = {
        "metrics.json": {
            "before": str(before.scan_dir / "metrics.json"),
            "after": str(after.scan_dir / "metrics.json"),
        },
        "scan_manifest.json": {
            "before": str(before.scan_dir / "scan_manifest.json"),
            "after": str(after.scan_dir / "scan_manifest.json"),
        },
        "judgment_rules.json": str(judgment_rules_path),
        "metrics_delta.json": str(delta_path),
        "comparison_report.json": str(report_path),
    }
    build_auditory_report(
        auditory_report_path,
        source_name=before.scan_dir.name,
        case_id=case_id,
        source_sha256=source_sha256,
        analysis_version=before.profile.profile_id,
        overall_status="OK",
        metrics=after.metrics,
        findings=[flag.to_dict() for flag in risk_flags],
        evidence_index=evidence_index,
        summary=(
            "Machine auditory comparison completed; human listening authority is required "
            f"before artistic approval. Technical decision: {judgment.workflow_decision}."
        ),
        overall_confidence=min(
            (flag.confidence for flag in risk_flags if flag.confidence is not None),
            default=None,
        ),
    )

    manifest_path = comparison_dir / "comparison_manifest.json"
    write_comparison_manifest(
        manifest_path,
        case_id=case_id,
        candidate_id=candidate_id,
        artifacts={
            "metrics_delta": delta_path,
            "delta_spectrum_linear": linear_delta,
            "delta_spectrum_log": log_delta,
            "comparison_contact_sheet": sheet,
            "comparison_report": report_path,
            "auditory_report": auditory_report_path,
            "judgment_rules": judgment_rules_path,
        },
        judgment_decision=judgment.workflow_decision,
    )

    return {
        "deltas": deltas,
        "judgment": judgment,
        "report_path": report_path,
        "auditory_report_path": auditory_report_path,
        "manifest_path": manifest_path,
    }
