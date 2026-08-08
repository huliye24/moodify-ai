"""Deterministic before/after spectral analysis engine."""
from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from pathlib import Path

import librosa
import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402


@dataclass
class AnalysisParams:
    sample_rate: int = 22050
    n_fft: int = 2048
    hop_length: int = 512
    window: str = "hann"
    db_min: float = -80.0
    db_max: float = 0.0
    diff_db_range: float = 40.0


@dataclass
class TrackSpec:
    track_id: str
    role: str
    before_path: str
    after_path: str


@dataclass
class CaseSpec:
    case_id: str
    title: str
    tracks: list[TrackSpec] = field(default_factory=list)


@dataclass
class TrackMetrics:
    track_id: str
    role: str
    before_hash: str = ""
    after_hash: str = ""
    before_duration_s: float = 0.0
    after_duration_s: float = 0.0
    sample_rate: int = 0
    before_original_sample_rate: int = 0
    after_original_sample_rate: int = 0
    before_channels: int = 0
    after_channels: int = 0
    analysis_actions: list[str] = field(default_factory=list)
    before_peak_db: float | None = None
    after_peak_db: float | None = None
    before_rms_db: float | None = None
    after_rms_db: float | None = None
    rms_delta_db: float | None = None
    before_crest_factor: float | None = None
    after_crest_factor: float | None = None
    spectral_diff_mean_db: float | None = None
    spectral_diff_min_db: float | None = None
    spectral_diff_max_db: float | None = None
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass
class BandMetrics:
    track_id: str
    band: str
    freq_range_hz: str
    before_energy_db: float | None = None
    after_energy_db: float | None = None
    delta_db: float | None = None


def _hash_file(path: str) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _compute_db(samples: np.ndarray) -> float:
    rms = np.sqrt(np.mean(samples.astype(np.float64) ** 2))
    if rms <= 0:
        return -120.0
    return float(20.0 * np.log10(rms))


def _compute_peak_db(samples: np.ndarray) -> float:
    peak = float(np.max(np.abs(samples)))
    if peak <= 0:
        return -120.0
    return float(20.0 * np.log10(peak))


BANDS = {
    "sub": (20, 60),
    "bass": (60, 250),
    "low_mid": (250, 500),
    "mid": (500, 2000),
    "presence": (2000, 6000),
    "air": (6000, 20000),
}


def _stft_amplitude(y: np.ndarray, params: AnalysisParams) -> np.ndarray:
    window = librosa.filters.get_window(params.window, params.n_fft, fftbins=True)
    scale = max(float(np.sum(window)) / 2.0, 1e-12)
    return np.abs(librosa.stft(
        y, n_fft=params.n_fft, hop_length=params.hop_length, window=params.window,
    )) / scale


def _amplitude_db(amplitude: np.ndarray) -> np.ndarray:
    return librosa.amplitude_to_db(amplitude + 1e-12, ref=1.0, top_db=None)


def _band_energy(y: np.ndarray, sr: int, low: float, high: float, params: AnalysisParams) -> float:
    amplitude = _stft_amplitude(y, params)
    freqs = librosa.fft_frequencies(sr=sr, n_fft=params.n_fft)
    mask = (freqs >= low) & (freqs <= high)
    energy = float(np.mean(amplitude[mask, :] ** 2)) if np.any(mask) else 0.0
    return 10.0 * np.log10(max(energy, 1e-12))


def _generate_spectrogram(
    db_spectrogram: np.ndarray, sr: int, params: AnalysisParams, title: str, output_path: Path,
    db_min: float | None = None, db_max: float | None = None,
) -> None:
    fig, ax = plt.subplots(figsize=(12, 6))
    vmin = db_min if db_min is not None else params.db_min
    vmax = db_max if db_max is not None else params.db_max
    img = librosa.display.specshow(
        db_spectrogram, sr=sr, hop_length=params.hop_length, x_axis="time", y_axis="hz",
        ax=ax, vmin=vmin, vmax=vmax, cmap="magma",
    )
    fig.colorbar(img, ax=ax, format="%+2.0f dB")
    ax.set_title(title)
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)


def analyze_track(track: TrackSpec, params: AnalysisParams, output_dir: Path) -> TrackMetrics:
    """Generate before/after/difference spectrograms and metrics."""
    metrics = TrackMetrics(track_id=track.track_id, role=track.role)
    output_dir.mkdir(parents=True, exist_ok=True)

    metrics.before_hash = _hash_file(track.before_path)
    metrics.after_hash = _hash_file(track.after_path)

    # Load without implicit resampling or mono conversion.
    try:
        raw_before, sr_before = librosa.load(track.before_path, sr=None, mono=False)
        raw_after, sr_after = librosa.load(track.after_path, sr=None, mono=False)
    except Exception as exc:
        metrics.errors.append(f"Failed to load audio: {exc}")
        return metrics

    channels_before = 1 if raw_before.ndim == 1 else int(raw_before.shape[0])
    channels_after = 1 if raw_after.ndim == 1 else int(raw_after.shape[0])
    metrics.before_original_sample_rate = int(sr_before)
    metrics.after_original_sample_rate = int(sr_after)
    metrics.before_channels = channels_before
    metrics.after_channels = channels_after

    if sr_before != sr_after:
        metrics.errors.append(f"Source sample-rate mismatch: before={sr_before} after={sr_after}")
        return metrics
    if channels_before != channels_after:
        metrics.errors.append(
            f"Source channel-count mismatch: before={channels_before} after={channels_after}"
        )
        return metrics

    y_before = np.mean(raw_before, axis=0) if raw_before.ndim > 1 else raw_before
    y_after = np.mean(raw_after, axis=0) if raw_after.ndim > 1 else raw_after
    if channels_before > 1:
        metrics.analysis_actions.append(f"explicit_equal_weight_mono_mix:{channels_before}ch")
    if sr_before != params.sample_rate:
        y_before = librosa.resample(y_before, orig_sr=sr_before, target_sr=params.sample_rate)
        y_after = librosa.resample(y_after, orig_sr=sr_after, target_sr=params.sample_rate)
        metrics.analysis_actions.append(f"explicit_resample:{sr_before}->{params.sample_rate}")

    metrics.sample_rate = params.sample_rate
    metrics.before_duration_s = round(float(len(y_before)) / params.sample_rate, 3)
    metrics.after_duration_s = round(float(len(y_after)) / params.sample_rate, 3)
    if len(y_before) != len(y_after):
        metrics.errors.append(
            f"Timeline mismatch: before_samples={len(y_before)} after_samples={len(y_after)}"
        )
        return metrics

    # Metrics
    metrics.before_peak_db = round(_compute_peak_db(y_before), 2)
    metrics.after_peak_db = round(_compute_peak_db(y_after), 2)
    metrics.before_rms_db = round(_compute_db(y_before), 2)
    metrics.after_rms_db = round(_compute_db(y_after), 2)
    metrics.rms_delta_db = round(metrics.after_rms_db - metrics.before_rms_db, 2)
    metrics.before_crest_factor = round(metrics.before_peak_db - metrics.before_rms_db, 2)
    metrics.after_crest_factor = round(metrics.after_peak_db - metrics.after_rms_db, 2)

    # Spectrograms
    before_db = _amplitude_db(_stft_amplitude(y_before, params))
    after_db = _amplitude_db(_stft_amplitude(y_after, params))
    _generate_spectrogram(before_db, params.sample_rate, params,
                          f"{track.track_id} — Before", output_dir / f"{track.track_id}_before.png")
    _generate_spectrogram(after_db, params.sample_rate, params,
                          f"{track.track_id} — After", output_dir / f"{track.track_id}_after.png")

    # Difference spectrogram
    D_diff = after_db - before_db
    active_mask = np.maximum(before_db, after_db) >= params.db_min
    finite_diff = D_diff[np.isfinite(D_diff) & active_mask]
    metrics.spectral_diff_mean_db = round(float(np.mean(finite_diff)), 4)
    metrics.spectral_diff_min_db = round(float(np.min(finite_diff)), 4)
    metrics.spectral_diff_max_db = round(float(np.max(finite_diff)), 4)

    fig, ax = plt.subplots(figsize=(12, 6))
    img = librosa.display.specshow(
        D_diff, sr=params.sample_rate, hop_length=params.hop_length,
        x_axis="time", y_axis="hz", ax=ax,
        vmin=-params.diff_db_range, vmax=params.diff_db_range, cmap="RdBu_r",
    )
    cbar = fig.colorbar(img, ax=ax, format="%+2.0f")
    cbar.set_label("Δ dB (after − before)")
    ax.set_title(f"{track.track_id} — Difference")
    fig.tight_layout()
    fig.savefig(output_dir / f"{track.track_id}_difference.png", dpi=150)
    plt.close(fig)

    # Save metrics
    (output_dir / f"{track.track_id}_metrics.json").write_text(
        json.dumps(asdict(metrics), indent=2), encoding="utf-8",
    )

    return metrics


def compute_band_metrics(track: TrackSpec, params: AnalysisParams, track_dir: Path) -> list[BandMetrics]:
    """Compute per-band energy metrics."""
    results: list[BandMetrics] = []
    try:
        raw_before, sr_before = librosa.load(track.before_path, sr=None, mono=False)
        raw_after, sr_after = librosa.load(track.after_path, sr=None, mono=False)
    except Exception:
        return results
    channels_before = 1 if raw_before.ndim == 1 else raw_before.shape[0]
    channels_after = 1 if raw_after.ndim == 1 else raw_after.shape[0]
    if sr_before != sr_after or channels_before != channels_after:
        return results
    y_before = np.mean(raw_before, axis=0) if raw_before.ndim > 1 else raw_before
    y_after = np.mean(raw_after, axis=0) if raw_after.ndim > 1 else raw_after
    if sr_before != params.sample_rate:
        y_before = librosa.resample(y_before, orig_sr=sr_before, target_sr=params.sample_rate)
        y_after = librosa.resample(y_after, orig_sr=sr_after, target_sr=params.sample_rate)
    sr = params.sample_rate
    if len(y_before) != len(y_after):
        return results

    for band_name, (low, high) in BANDS.items():
        bm = BandMetrics(
            track_id=track.track_id, band=band_name,
            freq_range_hz=f"{low}-{high}",
            before_energy_db=round(_band_energy(y_before, sr, low, high, params), 2),
            after_energy_db=round(_band_energy(y_after, sr, low, high, params), 2),
        )
        bm.delta_db = round((bm.after_energy_db or 0) - (bm.before_energy_db or 0), 2)
        results.append(bm)

    # Save to CSV in track directory
    csv_path = track_dir / f"{track.track_id}_band_metrics.csv"
    with open(csv_path, "w", encoding="utf-8") as f:
        f.write("track_id,band,freq_range_hz,before_energy_db,after_energy_db,delta_db\n")
        for bm in results:
            f.write(f"{bm.track_id},{bm.band},{bm.freq_range_hz},"
                    f"{bm.before_energy_db},{bm.after_energy_db},{bm.delta_db}\n")

    return results
