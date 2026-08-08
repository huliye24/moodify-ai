"""Musical pitch-class, key, and harmony-stability features."""
from __future__ import annotations

from typing import Any

import librosa
import numpy as np

PITCH_CLASSES = ("C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B")

# Krumhansl-Schmuckler key profiles, ordered C..B.
_MAJOR_PROFILE = np.array(
    [6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88],
    dtype=np.float64,
)
_MINOR_PROFILE = np.array(
    [6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17],
    dtype=np.float64,
)


def _as_mono(y: np.ndarray) -> np.ndarray:
    audio = np.asarray(y, dtype=np.float32)
    if audio.ndim == 1:
        return audio
    if audio.ndim != 2:
        raise ValueError("audio must be mono or stereo")
    # Accept both samples×channels and channels×samples.
    channel_axis = 1 if audio.shape[1] <= 8 else 0
    return np.mean(audio, axis=channel_axis, dtype=np.float32)


def _normalise_frames(chroma: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    frame_sums = np.sum(chroma, axis=0)
    active = frame_sums > np.finfo(np.float64).eps
    normalised = np.zeros_like(chroma, dtype=np.float64)
    normalised[:, active] = chroma[:, active] / frame_sums[active]
    return normalised, active


def _profile_correlation(observed: np.ndarray, profile: np.ndarray) -> float:
    if np.std(observed) <= 1e-12:
        return 0.0
    return float(np.corrcoef(observed, profile)[0, 1])


def detect_key(chroma: np.ndarray) -> tuple[str, float]:
    """Detect the most likely major/minor key from normalised chroma."""
    if chroma.shape[0] != 12:
        raise ValueError("chroma must have 12 pitch-class rows")
    energy = np.sum(chroma, axis=0)
    active = energy > 1e-12
    if not np.any(active):
        return "unknown", 0.0
    observed = np.mean(chroma[:, active], axis=1)
    candidates: list[tuple[float, str]] = []
    for tonic, name in enumerate(PITCH_CLASSES):
        candidates.append(
            (_profile_correlation(observed, np.roll(_MAJOR_PROFILE, tonic)), f"{name} major")
        )
        candidates.append(
            (_profile_correlation(observed, np.roll(_MINOR_PROFILE, tonic)), f"{name} minor")
        )
    strength, key = max(candidates, key=lambda item: item[0])
    return key, float(np.clip((strength + 1.0) / 2.0, 0.0, 1.0))


def harmony_stability(chroma: np.ndarray) -> float:
    """Mean cosine similarity between consecutive active chroma frames."""
    if chroma.shape[1] < 2:
        return 1.0 if chroma.shape[1] else 0.0
    left = chroma[:, :-1]
    right = chroma[:, 1:]
    denom = np.linalg.norm(left, axis=0) * np.linalg.norm(right, axis=0)
    active = denom > 1e-12
    if not np.any(active):
        return 0.0
    similarities = np.sum(left[:, active] * right[:, active], axis=0) / denom[active]
    return float(np.clip(np.mean(similarities), 0.0, 1.0))


def compute_chroma(
    y: np.ndarray,
    sr: int,
    hop_length: int = 512,
) -> dict[str, Any]:
    """Return normalised chroma, detected key, strength, and stability."""
    if sr <= 0:
        raise ValueError("sample rate must be positive")
    if hop_length <= 0:
        raise ValueError("hop_length must be positive")
    mono = _as_mono(y)
    if mono.size == 0:
        return {
            "feature_version": "chroma_v0.1",
            "chroma": np.zeros((12, 0), dtype=np.float64),
            "key": "unknown",
            "key_strength": 0.0,
            "harmony_stability": 0.0,
        }
    raw = librosa.feature.chroma_stft(y=mono, sr=sr, hop_length=hop_length, norm=None)
    chroma, _active = _normalise_frames(raw)
    key, strength = detect_key(chroma)
    return {
        "feature_version": "chroma_v0.1",
        "chroma": chroma,
        "key": key,
        "key_strength": round(strength, 6),
        "harmony_stability": round(harmony_stability(chroma), 6),
    }
