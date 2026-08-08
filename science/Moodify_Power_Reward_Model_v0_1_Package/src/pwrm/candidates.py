from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import numpy as np
from scipy.signal import butter, sosfilt

from .audio import measure_array, match_loudness, read_audio, sha256_file, write_audio


@dataclass(frozen=True)
class CandidateResult:
    candidate_id: str
    output_path: str
    processing_chain: list[dict[str, Any]]
    loudness_match_gain_db: float
    loudness_delta_lu: float
    clarity_delta: float
    loudness_pass: bool
    true_peak_pass: bool
    clarity_gate: str
    metrics: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _channelwise_filter(audio: np.ndarray, sos: np.ndarray) -> np.ndarray:
    return np.stack([sosfilt(sos, audio[:, channel]) for channel in range(audio.shape[1])], axis=1)


def _low_shelf_proxy(audio: np.ndarray, sample_rate: int, gain_db: float, cutoff_hz: float) -> np.ndarray:
    sos = butter(2, cutoff_hz, btype="lowpass", fs=sample_rate, output="sos")
    low = _channelwise_filter(audio, sos)
    gain = 10.0 ** (gain_db / 20.0) - 1.0
    return audio + gain * low


def _transient_emphasis(audio: np.ndarray, sample_rate: int, amount: float) -> np.ndarray:
    release = max(1, int(sample_rate * 0.030))
    kernel = np.ones(release, dtype=float) / release
    envelope = np.stack(
        [np.convolve(np.abs(audio[:, c]), kernel, mode="same") for c in range(audio.shape[1])],
        axis=1,
    )
    onset = np.maximum(np.abs(audio) - envelope, 0.0)
    return audio + amount * np.sign(audio) * onset


def _saturate(audio: np.ndarray, drive: float) -> np.ndarray:
    if drive <= 0:
        return audio
    scale = 1.0 + drive
    return np.tanh(audio * scale) / np.tanh(scale)


def _compress(audio: np.ndarray, threshold_db: float, ratio: float) -> np.ndarray:
    threshold = 10.0 ** (threshold_db / 20.0)
    magnitude = np.abs(audio)
    above = magnitude > threshold
    compressed = audio.copy()
    target_mag = threshold + (magnitude[above] - threshold) / max(ratio, 1.0)
    compressed[above] = np.sign(audio[above]) * target_mag
    return compressed


def apply_processing_chain(
    audio: np.ndarray,
    sample_rate: int,
    chain: list[dict[str, Any]],
) -> np.ndarray:
    output = audio.copy()
    for step in chain:
        operation = step.get("op")
        if operation == "low_shelf":
            output = _low_shelf_proxy(
                output,
                sample_rate,
                float(step.get("gain_db", 0.0)),
                float(step.get("cutoff_hz", 180.0)),
            )
        elif operation == "transient":
            output = _transient_emphasis(output, sample_rate, float(step.get("amount", 0.0)))
        elif operation == "saturation":
            output = _saturate(output, float(step.get("drive", 0.0)))
        elif operation == "compression":
            output = _compress(
                output,
                float(step.get("threshold_db", -12.0)),
                float(step.get("ratio", 2.0)),
            )
        else:
            raise ValueError(f"unsupported processing operation: {operation!r}")
    return output


def generate_candidates(
    source_path: Path,
    plan_path: Path,
    output_dir: Path,
    *,
    loudness_tolerance_lu: float = 0.1,
    true_peak_ceiling_dbtp: float = -1.0,
    clarity_drop_tolerance: float = 0.08,
) -> list[CandidateResult]:
    source, sample_rate = read_audio(source_path)
    source_metrics = measure_array(source, sample_rate, sha256_file(source_path))
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    results: list[CandidateResult] = []

    for item in plan.get("candidates", []):
        candidate_id = str(item["candidate_id"])
        chain = list(item.get("processing_chain", []))
        processed = apply_processing_chain(source, sample_rate, chain)
        matched, gain_db = match_loudness(source, processed, sample_rate)
        metrics = measure_array(matched, sample_rate)
        loudness_delta = metrics.lufs_i - source_metrics.lufs_i
        clarity_delta = metrics.clarity_proxy - source_metrics.clarity_proxy
        loudness_pass = abs(loudness_delta) <= loudness_tolerance_lu
        peak_pass = metrics.true_peak_dbTP <= true_peak_ceiling_dbtp
        clarity_gate = "pass" if clarity_delta >= -clarity_drop_tolerance else "fail"
        if not peak_pass:
            clarity_gate = "review"

        output_path = output_dir / f"{candidate_id}.wav"
        write_audio(output_path, matched, sample_rate)
        results.append(
            CandidateResult(
                candidate_id=candidate_id,
                output_path=str(output_path),
                processing_chain=chain,
                loudness_match_gain_db=gain_db,
                loudness_delta_lu=loudness_delta,
                clarity_delta=clarity_delta,
                loudness_pass=loudness_pass,
                true_peak_pass=peak_pass,
                clarity_gate=clarity_gate,
                metrics=metrics.to_dict(),
            )
        )

    manifest = {
        "source_path": str(source_path),
        "source_metrics": source_metrics.to_dict(),
        "candidate_count": len(results),
        "candidates": [result.to_dict() for result in results],
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "candidate_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return results
