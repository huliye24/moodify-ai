"""
perceptual.py — Mel / Bark / ERB Perceptual Spectrum (AEP-ACU-006)
===================================================================

Parallel perceptual frequency analysis that coexists with linear FFT-Hz
features. Provides three human-hearing-relevant scales:

  - Mel:      Pitch perception (Stevens 1937, Davis & Mermelstein 1980)
  - Bark:     Critical bands (Zwicker 1961) — masking model foundation
  - ERB:      Equivalent Rectangular Bandwidth (Glasberg & Moore 1990)

All outputs include a fixed JSON schema with feature_version, scale_type,
band_count, unit, and STFT metadata.

Reference:
  Zwicker, E. & Fastl, H. (2007). Psychoacoustics: Facts and Models.
  Glasberg, B. R. & Moore, B. C. J. (1990). Hearing Research.
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

import numpy as np

# ═══════════════════════════════════════════════════════════════════
# Scale mappings
# ═══════════════════════════════════════════════════════════════════


def hz_to_bark(freq_hz: np.ndarray) -> np.ndarray:
    """Zwicker (1961) Bark scale: Bark = 13*arctan(0.00076*f) + 3.5*arctan((f/7500)^2)."""
    f = np.asarray(freq_hz, dtype=np.float64)
    return 13.0 * np.arctan(0.00076 * f) + 3.5 * np.arctan((f / 7500.0) ** 2)


def hz_to_erb(freq_hz: np.ndarray) -> np.ndarray:
    """Glasberg & Moore (1990) ERB scale: ERB = 21.4*log10(4.37*f/1000 + 1)."""
    f = np.asarray(freq_hz, dtype=np.float64)
    return 21.4 * np.log10(4.37 * f / 1000.0 + 1.0)


def bark_bands(n_bands: int = 24, max_freq: float = 16000.0) -> List[Tuple[float, float]]:
    """Generate Bark critical band edges (Hz). Returns [(low, high), ...]."""
    bark_max = hz_to_bark(np.array([max_freq]))[0]
    bark_edges = np.linspace(0, bark_max, n_bands + 1)
    # Inverse: f = ... but simpler: sample uniformly in Bark then map back
    # Use the analytical inverse
    edges_hz = []
    for b in bark_edges:
        # Approximate inverse of Bark → Hz
        # f ≈ 600 * sinh(b / 6)  (rough approx)
        f = 600.0 * math.sinh(float(b) / 6.0)
        edges_hz.append(min(f, max_freq))
    # Ensure monotonic, positive
    bands = []
    for i in range(n_bands):
        lo = max(0.0, edges_hz[i])
        hi = min(max_freq, edges_hz[i + 1])
        bands.append((lo, hi))
    return bands


def erb_bands(n_bands: int = 28, max_freq: float = 16000.0) -> List[Tuple[float, float]]:
    """Generate ERB band edges (Hz)."""
    erb_max = hz_to_erb(np.array([max_freq]))[0]
    erb_edges = np.linspace(0, erb_max, n_bands + 1)
    edges_hz = []
    for e in erb_edges:
        # Inverse of ERB: f = (10^(e/21.4) - 1) * 1000 / 4.37
        f = (10.0 ** (float(e) / 21.4) - 1.0) * 1000.0 / 4.37
        edges_hz.append(min(f, max_freq))
    bands = []
    for i in range(n_bands):
        lo = max(0.0, edges_hz[i])
        hi = min(max_freq, edges_hz[i + 1])
        bands.append((lo, hi))
    return bands


# ═══════════════════════════════════════════════════════════════════
# Feature output dataclass
# ═══════════════════════════════════════════════════════════════════


@dataclass
class PerceptualScaleFeatures:
    """Features for a single perceptual scale."""
    scale_type: str  # "mel" | "bark" | "erb"
    band_count: int
    unit: str
    band_centers_hz: List[float] = field(default_factory=list)
    band_energies_db: List[float] = field(default_factory=list)
    centroid: float = 0.0     # perceptual centroid (in scale units)
    rolloff: float = 0.0      # frequency below which 85% energy
    flatness: float = 0.0     # spectral flatness
    slope: float = 0.0        # linear regression slope on band energies


@dataclass
class PerceptualFeatures:
    """Complete perceptual feature set (AEP-ACU-006)."""
    feature_version: str = "perception_v0.1"
    sample_rate: int = 44100
    n_fft: int = 2048
    hop_length: int = 512
    normalization: str = "none"
    duration_s: float = 0.0

    # Linear FFT-Hz (reference)
    fft_hz_centroid_hz: float = 0.0
    fft_hz_rolloff_hz: float = 0.0
    fft_hz_flatness: float = 0.0

    # Perceptual scales
    mel: Optional[PerceptualScaleFeatures] = None
    bark: Optional[PerceptualScaleFeatures] = None
    erb: Optional[PerceptualScaleFeatures] = None

    def to_dict(self) -> dict:
        result = {
            "feature_version": self.feature_version,
            "sample_rate": self.sample_rate,
            "n_fft": self.n_fft,
            "hop_length": self.hop_length,
            "normalization": self.normalization,
            "duration_s": round(self.duration_s, 2),
            "fft_hz": {
                "centroid_hz": round(self.fft_hz_centroid_hz, 1),
                "rolloff_hz": round(self.fft_hz_rolloff_hz, 1),
                "flatness": round(self.fft_hz_flatness, 4),
            },
        }
        for key in ["mel", "bark", "erb"]:
            pf = getattr(self, key)
            if pf is not None:
                result[key] = {
                    "scale_type": pf.scale_type,
                    "band_count": pf.band_count,
                    "unit": pf.unit,
                    "centroid": round(pf.centroid, 2),
                    "rolloff": round(pf.rolloff, 2),
                    "flatness": round(pf.flatness, 4),
                    "slope": round(pf.slope, 4),
                    "band_centers_hz": [round(c, 1) for c in pf.band_centers_hz],
                    "band_energies_db": [round(e, 2) for e in pf.band_energies_db],
                }
        return result

    def to_json(self, path: str = "") -> str:
        """Export to JSON string or file."""
        data = self.to_dict()
        if path:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        return json.dumps(data, indent=2, ensure_ascii=False)


# ═══════════════════════════════════════════════════════════════════
# PerceptualSpectrumExtractor
# ═══════════════════════════════════════════════════════════════════


class PerceptualSpectrumExtractor:
    """Parallel FFT-Hz / Mel / Bark / ERB feature extractor (AEP-ACU-006).

    Usage:
        ext = PerceptualSpectrumExtractor(sr=44100)
        features = ext.extract(audio)
        features.to_json("perceptual_features.json")
    """

    def __init__(self, sr: int = 44100, n_fft: int = 2048,
                 n_mels: int = 40, n_bark: int = 24, n_erb: int = 28):
        self.sr = sr
        self.n_fft = n_fft
        self.hop_length = n_fft // 4
        self.n_mels = n_mels
        self.n_bark = n_bark
        self.n_erb = n_erb
        self._bark_band_edges = bark_bands(n_bark)
        self._erb_band_edges = erb_bands(n_erb)

    def extract(self, audio: np.ndarray,
                normalize: str = "none") -> PerceptualFeatures:
        """Extract all perceptual features from audio (1D or 2D)."""
        if audio.ndim > 1:
            mono = audio.mean(axis=1)
        else:
            mono = audio

        mono = mono.astype(np.float32)
        duration_s = len(mono) / self.sr

        # ── STFT ──
        D = np.abs(np.array([
            np.fft.rfft(
                mono[i:i + self.n_fft] * np.hanning(self.n_fft)
            )
            for i in range(0, len(mono) - self.n_fft, self.hop_length)
        ]))
        freqs = np.fft.rfftfreq(self.n_fft, 1.0 / self.sr)

        features = PerceptualFeatures(
            sample_rate=self.sr,
            n_fft=self.n_fft,
            hop_length=self.hop_length,
            normalization=normalize,
            duration_s=duration_s,
        )

        # ── FFT-Hz baseline ──
        features.fft_hz_centroid_hz = float(_spectral_centroid(D, freqs))
        features.fft_hz_rolloff_hz = float(_spectral_rolloff(D, freqs))
        features.fft_hz_flatness = float(_spectral_flatness(D))

        # ── Mel ──
        features.mel = self._extract_mel(mono)

        # ── Bark ──
        features.bark = self._extract_bark(D, freqs)

        # ── ERB ──
        features.erb = self._extract_erb(D, freqs)

        return features

    def _extract_mel(self, mono: np.ndarray) -> PerceptualScaleFeatures:
        """Mel spectrogram + derived features via librosa."""
        try:
            import librosa
            mel_spec = librosa.feature.melspectrogram(
                y=mono, sr=self.sr, n_fft=self.n_fft,
                hop_length=self.hop_length, n_mels=self.n_mels,
            )
            mel_db = librosa.power_to_db(mel_spec, ref=np.max)
            centers = librosa.mel_frequencies(n_mels=self.n_mels, fmin=0, fmax=self.sr / 2)
        except Exception:
            # Fallback: manual mel filterbank
            import librosa as _lb
            mel_db = self._manual_mel_spectrogram(mono)
            centers = _lb.mel_frequencies(n_mels=self.n_mels, fmin=0, fmax=self.sr / 2)

        band_energies = np.mean(mel_db, axis=1)

        return PerceptualScaleFeatures(
            scale_type="mel",
            band_count=self.n_mels,
            unit="dB",
            band_centers_hz=centers.tolist(),
            band_energies_db=band_energies.tolist(),
            centroid=float(np.average(np.arange(self.n_mels), weights=np.maximum(band_energies, -80))),
            rolloff=float(_perceptual_rolloff(band_energies)),
            flatness=float(_gmean(band_energies + 80.0) / (np.mean(band_energies + 80.0) + 1e-15)),
            slope=float(np.polyfit(np.arange(self.n_mels), band_energies, 1)[0]),
        )

    def _extract_bark(self, D: np.ndarray, freqs: np.ndarray) -> PerceptualScaleFeatures:
        """Bark scale band energies via critical band aggregation."""
        band_energies = []
        centers = []
        for lo, hi in self._bark_band_edges:
            mask = (freqs >= lo) & (freqs <= hi)
            if np.any(mask):
                e = float(np.mean(D[:, mask] ** 2))
                band_energies.append(10.0 * math.log10(e + 1e-15))
            else:
                band_energies.append(-120.0)
            centers.append((lo + hi) / 2.0)

        be = np.array(band_energies)

        return PerceptualScaleFeatures(
            scale_type="bark",
            band_count=self.n_bark,
            unit="dB",
            band_centers_hz=centers,
            band_energies_db=be.tolist(),
            centroid=float(np.average(np.arange(self.n_bark), weights=np.maximum(be + 80, 0))),
            rolloff=float(_perceptual_rolloff(be)),
            flatness=float(_gmean(be + 80.0) / (np.mean(be + 80.0) + 1e-15)),
            slope=float(np.polyfit(np.arange(self.n_bark), be, 1)[0]),
        )

    def _extract_erb(self, D: np.ndarray, freqs: np.ndarray) -> PerceptualScaleFeatures:
        """ERB scale band energies via auditory filter bandwidth aggregation."""
        band_energies = []
        centers = []
        for lo, hi in self._erb_band_edges:
            mask = (freqs >= lo) & (freqs <= hi)
            if np.any(mask):
                e = float(np.mean(D[:, mask] ** 2))
                band_energies.append(10.0 * math.log10(e + 1e-15))
            else:
                band_energies.append(-120.0)
            centers.append((lo + hi) / 2.0)

        be = np.array(band_energies)

        return PerceptualScaleFeatures(
            scale_type="erb",
            band_count=self.n_erb,
            unit="dB",
            band_centers_hz=centers,
            band_energies_db=be.tolist(),
            centroid=float(np.average(np.arange(self.n_erb), weights=np.maximum(be + 80, 0))),
            rolloff=float(_perceptual_rolloff(be)),
            flatness=float(_gmean(be + 80.0) / (np.mean(be + 80.0) + 1e-15)),
            slope=float(np.polyfit(np.arange(self.n_erb), be, 1)[0]),
        )

    def _manual_mel_spectrogram(self, mono: np.ndarray) -> np.ndarray:
        """Manual mel filterbank fallback."""
        import librosa as _lb
        fft_freqs = np.fft.rfftfreq(self.n_fft, 1.0 / self.sr)
        mel_freqs = _lb.mel_frequencies(n_mels=self.n_mels, fmin=0, fmax=self.sr / 2)

        # Build triangular filterbank
        weights = np.zeros((self.n_mels, len(fft_freqs)))
        for m in range(self.n_mels):
            lo = mel_freqs[max(0, m - 1)]
            ctr = mel_freqs[m]
            hi = mel_freqs[min(self.n_mels - 1, m + 1)]
            for k, f in enumerate(fft_freqs):
                if lo <= f <= ctr and ctr > lo:
                    weights[m, k] = (f - lo) / (ctr - lo)
                elif ctr <= f <= hi and hi > ctr:
                    weights[m, k] = (hi - f) / (hi - ctr)

        result = []
        hop = self.hop_length
        for i in range(0, len(mono) - self.n_fft, hop):
            frame = mono[i:i + self.n_fft] * np.hanning(self.n_fft)
            spec = np.abs(np.fft.rfft(frame)) ** 2
            result.append(weights @ spec)

        return np.array(result).T  # (n_mels, n_frames)


# ═══════════════════════════════════════════════════════════════════
# Spectral helpers
# ═══════════════════════════════════════════════════════════════════


def _spectral_centroid(D: np.ndarray, freqs: np.ndarray) -> float:
    mean_spec = np.mean(D, axis=0)
    return float(np.sum(freqs * mean_spec) / (np.sum(mean_spec) + 1e-15))


def _spectral_rolloff(D: np.ndarray, freqs: np.ndarray, pct: float = 0.85) -> float:
    cumsum = np.cumsum(np.mean(D, axis=0))
    total = cumsum[-1] + 1e-15
    idx = np.searchsorted(cumsum, pct * total)
    return float(freqs[min(idx, len(freqs) - 1)])


def _spectral_flatness(D: np.ndarray) -> float:
    mean_spec = np.mean(D, axis=0) + 1e-15
    return float(_gmean(mean_spec) / np.mean(mean_spec))


def _perceptual_rolloff(band_energies_db: np.ndarray, pct: float = 0.85) -> float:
    shifted = band_energies_db - np.min(band_energies_db) + 1e-6
    cumsum = np.cumsum(shifted)
    total = cumsum[-1] + 1e-15
    idx = np.searchsorted(cumsum, pct * total)
    return float(idx)


def _gmean(x: np.ndarray) -> float:
    return float(np.exp(np.mean(np.log(np.maximum(x, 1e-12)))))


# ═══════════════════════════════════════════════════════════════════
# Convenience API
# ═══════════════════════════════════════════════════════════════════


def extract_perceptual_features(
    audio: np.ndarray,
    sr: int = 44100,
    n_fft: int = 2048,
    n_mels: int = 40,
) -> PerceptualFeatures:
    """One-shot perceptual feature extraction from audio array."""
    ext = PerceptualSpectrumExtractor(sr=sr, n_fft=n_fft, n_mels=n_mels)
    return ext.extract(audio)
