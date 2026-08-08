from __future__ import annotations

import hashlib
import math
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np
import pyloudnorm as pyln
import soundfile as sf
from scipy.signal import resample_poly


EPS = 1e-12


@dataclass(frozen=True)
class AudioMetrics:
    sample_rate: int
    channels: int
    frames: int
    duration_seconds: float
    lufs_i: float
    true_peak_dbTP: float
    sample_peak_dbFS: float
    rms_dbFS: float
    crest_db: float
    low_ratio: float
    mid_ratio: float
    high_ratio: float
    transient_strength: float
    clarity_proxy: float
    audio_sha256: str

    def to_dict(self) -> dict[str, float | int | str]:
        return asdict(self)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_audio(path: Path) -> tuple[np.ndarray, int]:
    audio, sample_rate = sf.read(path, always_2d=True, dtype="float64")
    if audio.size == 0:
        raise ValueError(f"empty audio: {path}")
    if not np.isfinite(audio).all():
        raise ValueError(f"non-finite audio samples: {path}")
    return audio, int(sample_rate)


def write_audio(path: Path, audio: np.ndarray, sample_rate: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    sf.write(path, np.clip(audio, -1.0, 1.0), sample_rate, subtype="PCM_24")


def _db(value: float) -> float:
    return 20.0 * math.log10(max(float(value), EPS))


def _mono(audio: np.ndarray) -> np.ndarray:
    return np.mean(audio, axis=1)


def _band_ratios(mono: np.ndarray, sample_rate: int) -> tuple[float, float, float]:
    window = np.hanning(len(mono))
    spectrum = np.abs(np.fft.rfft(mono * window)) ** 2
    freqs = np.fft.rfftfreq(len(mono), 1.0 / sample_rate)
    total = float(np.sum(spectrum)) + EPS
    low = float(np.sum(spectrum[(freqs >= 35) & (freqs < 250)])) / total
    mid = float(np.sum(spectrum[(freqs >= 250) & (freqs < 5000)])) / total
    high = float(np.sum(spectrum[(freqs >= 5000) & (freqs < min(18000, sample_rate / 2))])) / total
    return low, mid, high


def _transient_strength(mono: np.ndarray, sample_rate: int) -> float:
    frame = max(64, int(sample_rate * 0.010))
    usable = len(mono) // frame * frame
    if usable < frame * 2:
        return 0.0
    framed = mono[:usable].reshape(-1, frame)
    energy = np.sqrt(np.mean(framed * framed, axis=1) + EPS)
    positive_flux = np.maximum(np.diff(energy), 0.0)
    return float(np.percentile(positive_flux, 90) / (np.median(energy) + EPS))


def measure_array(audio: np.ndarray, sample_rate: int, source_hash: str = "") -> AudioMetrics:
    if audio.ndim != 2:
        raise ValueError("audio must use shape [frames, channels]")
    meter = pyln.Meter(sample_rate)
    loudness_input = audio[:, 0] if audio.shape[1] == 1 else audio
    lufs = float(meter.integrated_loudness(loudness_input))
    if not math.isfinite(lufs):
        raise ValueError("integrated loudness is not finite; audio may be silent or too short")

    oversampled = resample_poly(audio, 4, 1, axis=0)
    true_peak = float(np.max(np.abs(oversampled)))
    sample_peak = float(np.max(np.abs(audio)))
    rms = float(np.sqrt(np.mean(audio * audio) + EPS))
    mono = _mono(audio)
    low, mid, high = _band_ratios(mono, sample_rate)
    transient = _transient_strength(mono, sample_rate)
    clarity = float((mid + 0.35 * high) / (low + mid + high + EPS))

    return AudioMetrics(
        sample_rate=sample_rate,
        channels=int(audio.shape[1]),
        frames=int(audio.shape[0]),
        duration_seconds=float(audio.shape[0] / sample_rate),
        lufs_i=lufs,
        true_peak_dbTP=_db(true_peak),
        sample_peak_dbFS=_db(sample_peak),
        rms_dbFS=_db(rms),
        crest_db=_db(sample_peak) - _db(rms),
        low_ratio=low,
        mid_ratio=mid,
        high_ratio=high,
        transient_strength=transient,
        clarity_proxy=clarity,
        audio_sha256=source_hash,
    )


def measure_audio(path: Path) -> AudioMetrics:
    audio, sample_rate = read_audio(path)
    return measure_array(audio, sample_rate, sha256_file(path))


def match_loudness(
    reference: np.ndarray,
    candidate: np.ndarray,
    sample_rate: int,
    *,
    max_abs_gain_db: float = 12.0,
) -> tuple[np.ndarray, float]:
    if reference.shape[1] != candidate.shape[1]:
        raise ValueError("reference and candidate channel counts differ")
    meter = pyln.Meter(sample_rate)
    ref_input = reference[:, 0] if reference.shape[1] == 1 else reference
    cand_input = candidate[:, 0] if candidate.shape[1] == 1 else candidate
    ref_lufs = float(meter.integrated_loudness(ref_input))
    cand_lufs = float(meter.integrated_loudness(cand_input))
    gain_db = ref_lufs - cand_lufs
    if abs(gain_db) > max_abs_gain_db:
        raise ValueError(f"required loudness gain {gain_db:.2f} dB exceeds safety bound")
    matched = candidate * (10.0 ** (gain_db / 20.0))
    return matched, gain_db
