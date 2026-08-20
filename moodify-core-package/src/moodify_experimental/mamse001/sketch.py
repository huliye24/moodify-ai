"""Fixed-width streaming spectral sketch per resolution.

Each frame is RFFT-transformed, projected into a fixed feature vector, then
released — no dense spectrogram is retained. Payload size therefore depends
on frame count and feature count, not FFT bin count.

Band definitions are imported from the canonical representation feature
registry (moodify.auditory.representation.feature_registry.BANDS); this
package creates no competing band set.
"""

from __future__ import annotations

from typing import Any

import hashlib
import numpy as np

from moodify.auditory.representation.feature_registry import BANDS

from .registry import FEATURE_SCHEMA_VERSION, RESOLUTIONS, ResolutionSpec, get_resolution
from .stft import as_mono, iter_frames, local_peak_frequencies, power_spectrum

FEATURE_NAMES: tuple[str, ...] = (
    "rms_dbfs",
    "peak_dbfs",
    "spectral_centroid_hz",
    "spectral_spread_hz",
    "spectral_flatness",
    "spectral_flux",
    "dominant_frequency_hz",
    "secondary_peak_hz",
    "peak_gap_hz",
) + tuple(f"band_{name}" for name, _, _ in BANDS)


def _safe_db(value: float) -> float:
    return float(20.0 * np.log10(max(float(value), 1e-12)))


def compute_resolution_sketch(
    samples: np.ndarray,
    sample_rate: int,
    spec: ResolutionSpec,
) -> dict[str, Any]:
    mono = as_mono(samples)
    window = np.hanning(spec.n_fft).astype(np.float32)
    freqs = np.fft.rfftfreq(spec.n_fft, 1.0 / sample_rate)
    rows: list[list[float]] = []
    centers_ms: list[float] = []
    prev_mag: np.ndarray | None = None

    for start, frame in iter_frames(mono, spec.n_fft, spec.hop_length):
        mag, power = power_spectrum(frame, spec.n_fft, window)
        total_power = float(np.sum(power) + 1e-24)
        rms = float(np.sqrt(np.mean(frame.astype(np.float64) ** 2)))
        peak = float(np.max(np.abs(frame)))

        centroid = float(np.sum(freqs * power) / total_power)
        spread = float(np.sqrt(np.sum(((freqs - centroid) ** 2) * power) / total_power))
        positive_power = power[1:] + 1e-24
        flatness = float(np.exp(np.mean(np.log(positive_power))) / np.mean(positive_power))

        if prev_mag is None:
            flux = 0.0
        else:
            prev_energy = float(np.sum(prev_mag))
            # relative flux needs an energy reference; a silent previous frame
            # makes the ratio meaningless (would explode toward 1e24)
            flux = 0.0 if prev_energy < 1e-9 else float(
                np.sum(np.maximum(mag - prev_mag, 0.0)) / prev_energy
            )
        prev_mag = mag

        peaks = local_peak_frequencies(mag, freqs, top_k=2)
        p1 = peaks[0] if peaks else 0.0
        p2 = peaks[1] if len(peaks) > 1 else 0.0
        gap = abs(p1 - p2) if p2 > 0.0 else 0.0

        band_values: list[float] = []
        for _, lo, hi in BANDS:
            mask = (freqs >= lo) & (freqs < hi)
            band_values.append(float(np.sum(power[mask]) / total_power))

        rows.append([
            _safe_db(rms),
            _safe_db(peak),
            centroid,
            spread,
            flatness,
            flux,
            p1,
            p2,
            gap,
            *band_values,
        ])
        centers_ms.append(1000.0 * (start + spec.n_fft / 2) / sample_rate)

    values = np.asarray(rows, dtype=np.float32)
    if values.size == 0:
        values = np.empty((0, len(FEATURE_NAMES)), dtype=np.float32)

    return {
        "resolution_id": spec.resolution_id,
        "window": spec.window,
        "window_ms": spec.window_ms(sample_rate),
        "hop_ms": spec.hop_ms(sample_rate),
        "bin_hz": spec.bin_hz(sample_rate),
        "n_frames": int(values.shape[0]),
        "frame_centers_ms": np.asarray(centers_ms, dtype=np.float64),
        "feature_names": FEATURE_NAMES,
        "values": values,
        "payload_bytes": int(values.nbytes + np.asarray(centers_ms, dtype=np.float64).nbytes),
        "dense_spectrogram_retained": False,
    }


def compute_multiresolution_sketch(
    samples: np.ndarray,
    sample_rate: int,
    source_sha256: str | None = None,
) -> dict[str, Any]:
    x = np.asarray(samples)
    if source_sha256 is None:
        source_sha256 = hashlib.sha256(np.ascontiguousarray(x).tobytes()).hexdigest()
    return {
        "schema_version": FEATURE_SCHEMA_VERSION,
        "operator_id": "MAMSE-001",
        "source_sha256": source_sha256,
        "sample_rate": int(sample_rate),
        "duration_s": float(len(x) / sample_rate),
        "axis_semantics": {
            "S": "Moodify semantic temporal scale; existing canonical authority",
            "R": "MAMSE-001 spectral-analysis resolution; orthogonal experimental axis",
        },
        "band_source": "moodify.auditory.representation.feature_registry.BANDS (canonical)",
        "resolutions": {
            rid: compute_resolution_sketch(x, sample_rate, get_resolution(rid))
            for rid in (spec.resolution_id for spec in RESOLUTIONS)
        },
    }
