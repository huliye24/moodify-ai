"""Before/after comparison (DSK-MFY-AUDITORY-SCAN-001).

Raw deltas AND loudness-normalized spectral deltas are both produced.
Delta spectrograms derive from STFT magnitude data (analysis_data.npz),
never from subtracting rendered PNGs.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

from moodify.auditory.errors import (
    ComparisonChannelMismatch,
    ComparisonDurationMismatch,
    ComparisonInvalid,
    ScanProfileMismatch,
)
from moodify.auditory.profiles import ScanProfile

DURATION_TOLERANCE_S = 0.050


@dataclass
class ScanEvidence:
    """One completed scan's loadable evidence."""

    case_id: str
    profile: ScanProfile
    profile_hash: str
    duration_s: float
    channels: int
    metrics: dict
    timeline: list[dict]
    arrays: dict  # npz contents: stft_linear, stft_log, freqs_*
    scan_dir: Path | None = None


@dataclass
class DeltaResult:
    metric_delta: dict = field(default_factory=dict)
    raw_band_deltas: dict = field(default_factory=dict)
    normalized_band_deltas: dict = field(default_factory=dict)
    normalization_gain_db: float = 0.0
    normalization_valid: bool = False
    normalized_method: str = "gain-to-before-LUFS"


def _load_arrays(npy_paths: dict) -> dict:
    arrays = {}
    for key, path in npy_paths.items():
        arrays[key] = np.load(path)
    return arrays


def validate_pair(before: ScanEvidence, after: ScanEvidence) -> None:
    if before.case_id != after.case_id:
        raise ComparisonInvalid("case IDs differ between scans")
    if before.profile_hash != after.profile_hash:
        raise ScanProfileMismatch("before/after scan profile hashes differ")
    if abs(before.duration_s - after.duration_s) > DURATION_TOLERANCE_S:
        raise ComparisonDurationMismatch(
            f"duration mismatch: before={before.duration_s:.3f}s after={after.duration_s:.3f}s"
        )
    if before.channels != after.channels:
        raise ComparisonChannelMismatch(
            f"channel mismatch: before={before.channels} after={after.channels}"
        )


def _metric_value(metrics: dict, key: str) -> float | None:
    entry = metrics.get(key)
    if not isinstance(entry, dict):
        return None
    return entry.get("value")


def compute_deltas(before: ScanEvidence, after: ScanEvidence) -> DeltaResult:
    result = DeltaResult()

    # loudness normalization gain: bring AFTER down/up to BEFORE integrated LUFS
    before_lufs = _metric_value(before.metrics, "integrated_lufs")
    after_lufs = _metric_value(after.metrics, "integrated_lufs")
    if before_lufs is not None and after_lufs is not None and after_lufs > -70.0:
        result.normalization_gain_db = round(before_lufs - after_lufs, 3)
        result.normalization_valid = True
    else:
        result.normalization_valid = False
        result.normalized_method = "UNAVAILABLE"

    # metric-level deltas (raw)
    all_keys = set(before.metrics) | set(after.metrics)
    for key in sorted(all_keys):
        if key.startswith("_"):
            continue
        b = _metric_value(before.metrics, key)
        a = _metric_value(after.metrics, key)
        if b is None or a is None:
            continue
        if not isinstance(b, (int, float)) or not isinstance(a, (int, float)):
            continue  # non-numeric values (hashes, labels) are not delta-able
        abs_delta = a - b
        unit = before.metrics[key].get("unit", "")
        direction = "INCREASE" if abs_delta > 0 else ("DECREASE" if abs_delta < 0 else "UNCHANGED")
        entry = {
            "before": b,
            "after": a,
            "absolute_delta": round(abs_delta, 6),
            "unit": unit,
            "direction": direction,
            "significance_threshold": None,
            "significant": None,
        }
        # relative delta where safe (avoid unstable percentages near zero)
        if abs(b) > 1e-9:
            entry["relative_delta"] = round(abs_delta / abs(b), 6)
        else:
            entry["relative_delta"] = None
            entry["relative_delta_reason"] = "baseline near zero"
        result.metric_delta[key] = entry

    # band energy deltas: raw ratios and loudness-normalized ratios.
    # Normalization happens in the ENERGY domain (gain^2 on absolute band
    # energy), then ratios are recomputed — a pure gain change must yield
    # near-zero normalized deltas.
    band_keys = [k for k in before.metrics if k.startswith("band_energy_")]
    for key in band_keys:
        b_e = _metric_value(before.metrics, key)
        a_e = _metric_value(after.metrics, key)
        if b_e is None or a_e is None:
            continue
        ratio_key = key[len("band_energy_"):]
        b_r = _metric_value(before.metrics, ratio_key)
        a_r = _metric_value(after.metrics, ratio_key)
        result.raw_band_deltas[ratio_key] = round(a_r - b_r, 8) if a_r is not None and b_r is not None else None
        if result.normalization_valid and result.normalization_gain_db != 0.0:
            gain2 = 10 ** (2 * result.normalization_gain_db / 20)
            a_norm_e = a_e * gain2
            total_b = sum(_metric_value(before.metrics, k) or 0.0 for k in band_keys) + 1e-12
            total_a = sum(_metric_value(after.metrics, k) or 0.0 for k in band_keys) + 1e-12
            b_ratio = b_e / total_b
            a_norm_ratio = a_norm_e / (total_a * gain2 + 1e-12)
            result.normalized_band_deltas[ratio_key] = round(a_norm_ratio - b_ratio, 8)
        else:
            result.normalized_band_deltas[ratio_key] = None
    return result


def _normalized_after_spectrogram(after_arrays: dict, gain_db: float) -> np.ndarray:
    gain = 10 ** (gain_db / 20)
    return after_arrays["stft_log"] * gain


def build_delta_spectrograms(
    before_arrays: dict,
    after_arrays: dict,
    gain_db: float,
    out_linear: Path,
    out_log: Path,
    dynamic_range_db: float = 30.0,
) -> None:
    """Render delta spectrograms from numerical STFT arrays.

    Uses loudness-normalized after data by default (gain_db applied to after).
    """
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    for view, out_path in (("linear", out_linear), ("log", out_log)):
        b = before_arrays[f"stft_{view}"]
        a = after_arrays[f"stft_{view}"]
        a_norm = a * (10 ** (gain_db / 20))
        delta_db = 20 * np.log10((a_norm + 1e-12) / (b + 1e-12))
        delta_db = np.clip(delta_db, -dynamic_range_db, dynamic_range_db)

        fig, ax = plt.subplots(figsize=(12, 4.5))
        im = ax.imshow(
            delta_db.T, aspect="auto", origin="lower",
            cmap="RdBu_r", vmin=-dynamic_range_db, vmax=dynamic_range_db,
        )
        ax.set_title(f"Delta spectrogram ({view} frequency) — after-normalized")
        ax.set_xlabel("frame")
        ax.set_ylabel("frequency bin")
        fig.colorbar(im, ax=ax, label="dB change")
        fig.tight_layout()
        fig.savefig(out_path, dpi=110)
        plt.close(fig)
