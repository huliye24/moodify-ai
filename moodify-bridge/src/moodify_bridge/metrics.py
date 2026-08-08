"""Deterministic metric adapters; undefined quantities are explicit ``None``."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import numpy.typing as npt

FloatArray = npt.NDArray[np.float64]
EPSILON = np.finfo(np.float64).eps


@dataclass(frozen=True)
class MetricOutput:
    values: dict[str, float | None]
    units: dict[str, str]
    warnings: tuple[str, ...] = ()


def _mono(samples: FloatArray) -> FloatArray:
    array = np.asarray(samples, dtype=np.float64)
    return array.mean(axis=1) if array.ndim == 2 else array


def level_metrics(samples: FloatArray) -> MetricOutput:
    x = _mono(samples)
    if x.size == 0:
        return MetricOutput({"peak": None, "rms": None, "crest_factor": None}, {}, ("empty signal",))
    peak = float(np.max(np.abs(x)))
    rms = float(np.sqrt(np.mean(x * x)))
    crest = None if rms == 0 else peak / rms
    return MetricOutput({"peak": peak, "rms": rms, "crest_factor": crest}, {"peak": "linear", "rms": "linear", "crest_factor": "ratio"}, (() if crest is not None else ("crest factor undefined for silence",)))


def spectral_metrics(samples: FloatArray, sample_rate: int, frame_size: int = 2048,
                     hop_size: int = 1024) -> MetricOutput:
    x = _mono(samples)
    if x.size < frame_size:
        return MetricOutput({"spectral_entropy": None, "spectral_centroid_hz": None, "spectral_flux": None}, {}, ("signal too short for one spectral frame",))
    frames = np.lib.stride_tricks.sliding_window_view(x, frame_size)[::hop_size]
    magnitudes = np.abs(np.fft.rfft(frames * np.hanning(frame_size), axis=1))
    power = magnitudes * magnitudes
    totals = power.sum(axis=1, keepdims=True)
    probability = np.divide(power, totals, out=np.zeros_like(power), where=totals > 0)
    entropy = -np.sum(np.where(probability > 0, probability * np.log2(probability + EPSILON), 0), axis=1) / np.log2(power.shape[1])
    frequencies = np.fft.rfftfreq(frame_size, 1 / sample_rate)
    centroid = np.divide((magnitudes * frequencies).sum(axis=1), magnitudes.sum(axis=1), out=np.full(frames.shape[0], np.nan), where=magnitudes.sum(axis=1) > 0)
    norm = np.divide(magnitudes, magnitudes.sum(axis=1, keepdims=True), out=np.zeros_like(magnitudes), where=magnitudes.sum(axis=1, keepdims=True) > 0)
    flux = np.sqrt(np.sum(np.diff(norm, axis=0) ** 2, axis=1))
    return MetricOutput({"spectral_entropy": float(np.mean(entropy)), "spectral_centroid_hz": None if np.all(np.isnan(centroid)) else float(np.nanmean(centroid)), "spectral_flux": None if flux.size == 0 else float(np.mean(flux))}, {"spectral_entropy": "normalized", "spectral_centroid_hz": "Hz", "spectral_flux": "normalized"})


def band_fractions(samples: FloatArray, sample_rate: int,
                   bands: tuple[tuple[float, float], ...] = ((20, 250), (250, 2000), (2000, 8000), (8000, 20000))) -> MetricOutput:
    x = _mono(samples)
    if x.size == 0 or not np.any(x):
        return MetricOutput({f"band_{low:g}_{high:g}_fraction": None for low, high in bands}, {}, ("band fractions undefined for empty or silent signal",))
    power = np.abs(np.fft.rfft(x)) ** 2
    freq = np.fft.rfftfreq(x.size, 1 / sample_rate)
    total = float(power.sum())
    values: dict[str, float | None] = {f"band_{low:g}_{high:g}_fraction": float(power[(freq >= low) & (freq < high)].sum() / total) for low, high in bands}
    return MetricOutput(values, {key: "fraction" for key in values})


def comparison_metrics(reference: FloatArray, candidate: FloatArray) -> MetricOutput:
    a, b = _mono(reference), _mono(candidate)
    if a.shape != b.shape or a.size == 0:
        return MetricOutput({name: None for name in ("waveform_correlation", "fitted_scalar_gain", "relative_residual", "difference_snr_db")}, {}, ("comparison requires non-empty signals of equal length",))
    denom = float(np.dot(a, a))
    gain = None if denom == 0 else float(np.dot(a, b) / denom)
    corr = None if np.std(a) == 0 or np.std(b) == 0 else float(np.corrcoef(a, b)[0, 1])
    residual = None if gain is None or np.linalg.norm(b) == 0 else float(np.linalg.norm(b - gain * a) / np.linalg.norm(b))
    noise_power = float(np.sum((b - a) ** 2))
    signal_power = float(np.sum(a ** 2))
    snr = None if signal_power == 0 else (float("inf") if noise_power == 0 else float(10 * np.log10(signal_power / noise_power)))
    return MetricOutput({"waveform_correlation": corr, "fitted_scalar_gain": gain, "relative_residual": residual, "difference_snr_db": snr}, {"waveform_correlation": "correlation", "fitted_scalar_gain": "ratio", "relative_residual": "ratio", "difference_snr_db": "dB"})


def left_right_correlation(samples: FloatArray) -> MetricOutput:
    x = np.asarray(samples, dtype=np.float64)
    value = None if x.ndim != 2 or x.shape[1] != 2 or x.shape[0] == 0 or np.std(x[:, 0]) == 0 or np.std(x[:, 1]) == 0 else float(np.corrcoef(x[:, 0], x[:, 1])[0, 1])
    return MetricOutput({"left_right_correlation": value}, {"left_right_correlation": "correlation"}, (() if value is not None else ("stereo correlation requires non-constant two-channel audio",)))


def loudness_metrics(samples: FloatArray, sample_rate: int) -> MetricOutput:
    try:
        import pyloudnorm as pyln  # type: ignore[import-not-found]
    except ImportError:
        return MetricOutput({"loudness_lufs": None, "lra_lu": None, "true_peak_dbtp": None}, {"loudness_lufs": "LUFS", "lra_lu": "LU", "true_peak_dbtp": "dBTP"}, ("optional pyloudnorm dependency is not installed; no values inferred",))
    x = np.asarray(samples, dtype=np.float64)
    if x.size == 0:
        return MetricOutput({"loudness_lufs": None, "lra_lu": None, "true_peak_dbtp": None}, {}, ("empty signal",))
    meter = pyln.Meter(sample_rate)
    loudness = float(meter.integrated_loudness(x))
    # pyloudnorm provides integrated loudness only; never substitute approximate LRA/true peak.
    return MetricOutput({"loudness_lufs": loudness, "lra_lu": None, "true_peak_dbtp": None}, {"loudness_lufs": "LUFS", "lra_lu": "LU", "true_peak_dbtp": "dBTP"}, ("LRA and true peak require a standards-compliant backend and remain null",))
