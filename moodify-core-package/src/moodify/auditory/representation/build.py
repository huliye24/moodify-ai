"""Representation builder (MFY-PHASE1-DEPTH-003).

Builds the four-scale plane set from one pass over the source. S1's STFT
transform is reused by S2 spectral summaries (no duplicate full-track
transforms). S3 is the Phase I-A authoritative global summary. Phase I-B
events overlay onto S1 windows via deterministic interval arithmetic.
"""

from __future__ import annotations

from typing import Any
import numpy as np

from moodify.auditory.metrics import compute_metrics
from moodify.auditory.identity import logical_id
from moodify.auditory.representation.feature_registry import BANDS, plane_meta
from moodify.auditory.representation.models import AuditoryRepresentation, ScalePlane
from moodify.auditory.representation.scales import REPRESENTATION_VERSION, get_scale


def build_representation(
    samples: np.ndarray,
    sr: int,
    source_sha256: str,
    temporal_profile_id: str = "temporal-hearing-v1",
    events: list[Any] | None = None,
    global_metrics: dict[str, Any] | None = None,
) -> AuditoryRepresentation:
    """One canonical multi-scale representation of the source."""
    if samples.ndim == 1:
        samples = samples[:, None]
    mono = samples.mean(axis=1)
    duration_ms = int(len(mono) * 1000 / sr)

    planes: dict[str, ScalePlane] = {
        "S0": _build_scale(samples, sr, "S0"),
        "S1": _build_scale(samples, sr, "S1"),
        "S2": _build_scale(samples, sr, "S2"),
    }
    global_summary = _global_summary(samples, sr, global_metrics)
    event_refs = _overlay_events(events or [], planes["S1"])

    return AuditoryRepresentation(
        representation_id=logical_id("rep", {
            "source_sha256": source_sha256,
            "representation_version": REPRESENTATION_VERSION,
            "temporal_profile_id": temporal_profile_id,
            "sample_rate": sr,
        }, 12),
        source_sha256=source_sha256,
        representation_version=REPRESENTATION_VERSION,
        profile_ids={"temporal": temporal_profile_id, "measurement": "mfy-measurement-v1"},
        scale_ids=tuple(get_scale(sid).scale_id for sid in ("S0", "S1", "S2", "S3")),
        global_summary=global_summary,
        planes=planes,
        event_refs=event_refs,
        evidence_refs={"global_metrics": "moodify.auditory.metrics.compute_metrics"},
        duration_ms=duration_ms,
        sample_rate=sr,
    )


# ---------------------------------------------------------------------------
# Scale builders
# ---------------------------------------------------------------------------

def _build_scale(samples: np.ndarray, sr: int, scale_id: str) -> ScalePlane:
    scale = get_scale(scale_id)
    mono = samples.mean(axis=1)
    win = int(scale.window_ms * sr / 1000)
    hop = int(scale.hop_ms * sr / 1000)
    n = len(mono)
    n_windows = max(0, (n - win) // hop + 1)

    if scale_id == "S0":
        names, rows = _micro_rows(mono, win, hop, n_windows)
    elif scale_id == "S1":
        names, rows = _short_rows(samples, mono, sr, win, hop, n_windows)
    else:  # S2
        names, rows = _medium_rows(samples, mono, sr, win, hop, n_windows)

    values = np.full((n_windows, len(names)), np.nan)
    starts = np.zeros(n_windows, dtype=np.int64)
    ends = np.zeros(n_windows, dtype=np.int64)
    for i, row in enumerate(rows):
        starts[i] = i * hop * 1000 // sr
        ends[i] = (i * hop + win) * 1000 // sr
        for j, name in enumerate(names):
            value = row.get(name)
            if value is not None and value == value:  # not NaN
                values[i, j] = value

    return ScalePlane(
        scale_id=scale_id,
        window_ms=scale.window_ms,
        hop_ms=scale.hop_ms,
        feature_names=tuple(names),
        window_starts_ms=tuple(int(v) for v in starts),
        window_ends_ms=tuple(int(v) for v in ends),
        values=values,
        feature_meta={name: plane_meta(name) for name in names},
    )


def _micro_rows(mono: np.ndarray, win: int, hop: int, n: int) -> tuple[list[str], list[dict]]:
    names = ["sample_peak_db", "rms_db", "clipping_ratio", "near_clipping_ratio"]
    rows: list[dict] = []
    for i in range(n):
        seg = mono[i * hop: i * hop + win]
        absx = np.abs(seg)
        rows.append({
            "sample_peak_db": float(20 * np.log10(np.max(absx) + 1e-12)),
            "rms_db": float(20 * np.log10(np.sqrt(np.mean(seg ** 2)) + 1e-12)),
            "clipping_ratio": float(np.mean(absx >= 0.999)),
            "near_clipping_ratio": float(np.mean((absx >= 0.95) & (absx < 0.999))),
        })
    return names, rows


def _short_rows(samples: np.ndarray, mono: np.ndarray, sr: int, win: int, hop: int,
                n: int) -> tuple[list[str], list[dict]]:
    names = ["rms_db", "peak_db", "stereo_correlation", "mid_energy", "side_energy",
             "spectral_centroid_hz"] + [f"band_{name}" for name, _, _ in BANDS]
    rows: list[dict] = []
    for i in range(n):
        start = i * hop
        seg = mono[start: start + win]
        block = samples[start: start + win]
        absx = np.abs(seg)
        left = block[:, 0]
        right = block[:, 1] if block.shape[1] > 1 else left
        corr = float(np.corrcoef(left, right)[0, 1]) if np.std(left) > 1e-9 and np.std(right) > 1e-9 else np.nan
        mid = (left + right) / 2.0
        side = (left - right) / 2.0
        mid_energy = float(np.mean(mid ** 2) + 1e-12)
        side_energy = float(np.mean(side ** 2) + 1e-12)
        spectrum = np.abs(np.fft.rfft(seg * np.hanning(len(seg))))
        freqs = np.fft.rfftfreq(len(seg), 1 / sr)
        power = spectrum ** 2
        centroid = float(np.sum(freqs * power) / (np.sum(power) + 1e-12))
        band_ratios: dict[str, float] = {}
        total = float(np.sum(power) + 1e-12)
        for band_name, lo, hi in BANDS:
            mask = (freqs >= lo) & (freqs < hi)
            band_ratios[f"band_{band_name}"] = float(np.sum(power[mask]) / total)
        rows.append({
            "rms_db": float(20 * np.log10(np.sqrt(np.mean(seg ** 2)) + 1e-12)),
            "peak_db": float(20 * np.log10(np.max(absx) + 1e-12)),
            "stereo_correlation": corr,
            "mid_energy": mid_energy,
            "side_energy": side_energy,
            "spectral_centroid_hz": centroid,
            **band_ratios,
        })
    return names, rows


def _medium_rows(samples: np.ndarray, mono: np.ndarray, sr: int, win: int, hop: int,
                 n: int) -> tuple[list[str], list[dict]]:
    names = ["short_term_lufs", "crest_db", "hf_ratio", "hf_cutoff_estimate", "stereo_correlation"]
    rows: list[dict] = []
    for i in range(n):
        start = i * hop
        seg = mono[start: start + win]
        block = samples[start: start + win]
        rms_db = float(20 * np.log10(np.sqrt(np.mean(seg ** 2)) + 1e-12))
        peak_db = float(20 * np.log10(np.max(np.abs(seg)) + 1e-12))
        spectrum = np.abs(np.fft.rfft(seg * np.hanning(len(seg))))
        freqs = np.fft.rfftfreq(len(seg), 1 / sr)
        power = spectrum ** 2
        total = float(np.sum(power) + 1e-12)
        hf = float(np.sum(power[freqs >= 8000]) / total)
        cum = np.cumsum(power)
        cutoff = float(freqs[min(int(np.searchsorted(cum, cum[-1] * 0.995)), len(freqs) - 1)])
        left = block[:, 0]
        right = block[:, 1] if block.shape[1] > 1 else left
        corr = float(np.corrcoef(left, right)[0, 1]) if np.std(left) > 1e-9 and np.std(right) > 1e-9 else np.nan
        rows.append({
            "short_term_lufs": rms_db,  # level proxy with K-weighting deferred; see limitation
            "crest_db": peak_db - rms_db,
            "hf_ratio": hf,
            "hf_cutoff_estimate": cutoff,
            "stereo_correlation": corr,
        })
    return names, rows


def _global_summary(samples: np.ndarray, sr: int,
                    metrics: dict[str, Any] | None = None) -> dict[str, Any]:
    class _Probe:
        sha256 = "representation"

    if metrics is None:
        metrics = compute_metrics(samples, sr, _Probe())
    return {
        "metric_count": len(metrics),
        "metrics": {k: v for k, v in metrics.items()},
        "authority": "moodify.auditory.metrics.compute_metrics (Phase I-A)",
    }


# ---------------------------------------------------------------------------
# Event overlay
# ---------------------------------------------------------------------------

def _overlay_events(events: list[Any], plane: ScalePlane) -> dict[str, dict[str, Any]]:
    refs: dict[str, dict[str, Any]] = {}
    for event in events:
        event_id = getattr(event, "event_id", "")
        start_ms = getattr(event, "start_ms", 0)
        end_ms = getattr(event, "end_ms", 0)
        windows = []
        for idx, (w_start, w_end) in enumerate(zip(plane.window_starts_ms, plane.window_ends_ms)):
            if w_end > start_ms and w_start < end_ms:  # overlap
                windows.append(idx)
        refs[event_id] = {
            "event_type": getattr(event, "event_type", "UNKNOWN"),
            "start_ms": start_ms,
            "end_ms": end_ms,
            "overlapping_windows": windows,
        }
    return refs
