"""MAMSE-015 soft-auditory-object operator.

Acoustic cues (spectral flatness, spectral centroid, spectral flux) ->
independent soft probabilities per frame over role hypotheses ->
contiguous regions of stable dominant label -> soft objects carrying a
probability profile and confidence. Weak evidence yields UNRESOLVED,
never a confident label.
"""

from __future__ import annotations

from dataclasses import dataclass

import librosa
import numpy as np

from .config import HYPOTHESES, SoftObjectConfig

MIN_ENERGY = 1e-12


@dataclass(frozen=True)
class SoftObject:
    object_id: str
    label: str
    start_ms: int
    end_ms: int
    probabilities: dict[str, float]  # independent soft indicators
    confidence: float  # dominant indicator value

    def to_dict(self) -> dict:
        return {
            "object_id": self.object_id,
            "label": self.label,
            "start_ms": self.start_ms,
            "end_ms": self.end_ms,
            "probabilities": dict(self.probabilities),
            "confidence": self.confidence,
        }


@dataclass
class SoftObjectObservation:
    status: str  # VALID | EMPTY | DEGRADED
    notes: tuple[str, ...]
    times_s: np.ndarray
    frame_probabilities: np.ndarray  # n_frames x 3 (TONAL, TEXTURE, PERCUSSIVE)
    frame_unresolved: np.ndarray  # n_frames
    frame_labels: np.ndarray  # n_frames, index into HYPOTHESES
    objects: tuple[SoftObject, ...]
    sr: int
    config_hash: str

    @property
    def unresolved_fraction(self) -> float:
        return float(np.mean(self.frame_unresolved)) if self.frame_unresolved.size else 1.0

    @property
    def mean_confidence(self) -> float:
        return float(np.mean(np.max(self.frame_probabilities, axis=1))) \
            if self.frame_probabilities.size else 0.0

    def to_dict(self) -> dict:
        return {
            "status": self.status,
            "notes": list(self.notes),
            "n_frames": int(self.times_s.size),
            "n_objects": len(self.objects),
            "unresolved_fraction": self.unresolved_fraction,
            "mean_confidence": self.mean_confidence,
            "config_hash": self.config_hash,
        }


def _sig(p: np.ndarray, sharpness: float, midpoint: float) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-sharpness * (p - midpoint)))


def compute_soft_object_observation(
    samples: np.ndarray,
    sr: int,
    config: SoftObjectConfig | None = None,
) -> SoftObjectObservation:
    config = config or SoftObjectConfig()
    x = np.asarray(samples, dtype=np.float64)
    if x.ndim != 1:
        raise ValueError("MAMSE-015 v0.1 is mono-only; stereo input rejected")
    if np.all(~np.isfinite(x)):
        raise ValueError("signal contains no finite samples")

    notes: list[str] = []
    if x.size < config.n_fft:
        notes.append("signal shorter than analysis window")

    hop = config.hop_length
    flatness = librosa.feature.spectral_flatness(y=x, n_fft=config.n_fft, hop_length=hop)[0]
    flux = librosa.onset.onset_strength(y=x, sr=sr, hop_length=hop, n_fft=config.n_fft,
                                        aggregate=np.mean)

    n = len(flatness)
    flatness = flatness[:n]
    flux = flux[:n]

    flat = np.nan_to_num(flatness, nan=1.0, posinf=1.0)
    flux_n = np.nan_to_num(flux, nan=0.0)
    # Onset envelopes are single-frame spikes; smooth so percussive
    # regions survive run extraction.
    if flux_n.size >= 5:
        flux_n = np.convolve(flux_n, np.ones(5) / 5.0, mode="same")
    flux_scale = max(float(np.max(flux_n)) if flux_n.size else 0.0, MIN_ENERGY)

    # Hypothesis probabilities couple cues (flatness alone cannot separate
    # a steady tone from an ON/OFF percussive pulse); the OUTPUT indicators
    # stay independent in the chapter's sense (0.86 vocal AND 0.44 texture).
    steady = _sig(flux_n / flux_scale, -config.percussive_sharpness, config.percussive_midpoint)
    p_tonal = _sig(1.0 - flat, config.cue_sharpness, config.tonal_midpoint) * steady
    p_texture = _sig(flat, config.cue_sharpness, config.texture_midpoint)
    p_percussive = _sig(flux_n / flux_scale, config.percussive_sharpness,
                        config.percussive_midpoint)

    # Weak evidence (near-silence) forces UNRESOLVED: silence is not texture.
    rms = librosa.feature.rms(y=x, frame_length=config.n_fft, hop_length=hop)[0][:n]
    rms_norm = rms / max(float(np.percentile(rms, 95)) if rms.size else 0.0, MIN_ENERGY)
    weak = (rms_norm < 0.01) | (rms < 1e-6)
    p_tonal = np.where(weak, 0.0, p_tonal)
    p_texture = np.where(weak, 0.0, p_texture)
    p_percussive = np.where(weak, 0.0, p_percussive)

    # Silence and weak evidence: all indicators low -> UNRESOLVED dominates.
    p_unresolved = np.clip(1.0 - np.maximum.reduce([p_tonal, p_texture, p_percussive]), 0.0, 1.0)

    profile = np.column_stack([p_tonal, p_texture, p_percussive])
    max_p = np.max(profile, axis=1)
    labels = np.argmax(profile, axis=1)
    labels[max_p < config.label_confidence_gate] = HYPOTHESES.index("UNRESOLVED")

    times_s = np.arange(n, dtype=np.float64) * hop / sr
    objects = _extract_objects(labels, profile, p_unresolved, times_s, sr, config)

    raw_energy = float(np.sum(np.abs(x) ** 2))
    status = "EMPTY" if raw_energy < MIN_ENERGY else "VALID"
    if notes:
        status = "DEGRADED" if status != "EMPTY" else status

    return SoftObjectObservation(
        status=status,
        notes=tuple(notes),
        times_s=times_s,
        frame_probabilities=profile,
        frame_unresolved=p_unresolved,
        frame_labels=labels,
        objects=tuple(objects),
        sr=sr,
        config_hash=config.sha256(),
    )


def _extract_objects(
    labels: np.ndarray,
    profile: np.ndarray,
    p_unresolved: np.ndarray,
    times_s: np.ndarray,
    sr: int,
    config: SoftObjectConfig,
) -> list[SoftObject]:
    """Contiguous runs of a stable non-UNRESOLVED label become soft objects."""
    objects: list[SoftObject] = []
    start: int | None = None
    label = -1
    for i, lab in enumerate(labels):
        if lab != HYPOTHESES.index("UNRESOLVED"):
            if start is None:
                start, label = i, lab
            elif lab != label:
                _close_region(objects, labels, profile, p_unresolved, times_s, sr, start, i,
                              label, config)
                start, label = i, lab
        elif start is not None:
            _close_region(objects, labels, profile, p_unresolved, times_s, sr, start, i,
                          label, config)
            start = None
    if start is not None:
        _close_region(objects, labels, profile, p_unresolved, times_s, sr, start, len(labels),
                      label, config)
    return objects[: config.max_objects]


def _close_region(objects, labels, profile, p_unresolved, times_s, sr, start, end, label, config):
    if end - start < config.min_region_frames:
        return
    seg = profile[start:end]
    probs = {HYPOTHESES[k]: float(np.mean(seg[:, k])) for k in range(3)}
    probs["UNRESOLVED"] = float(np.mean(p_unresolved[start:end]))
    objects.append(SoftObject(
        object_id=f"obj-{len(objects):03d}",
        label=HYPOTHESES[label],
        start_ms=int(start * config.hop_length * 1000 / sr),
        end_ms=int((end - 1) * config.hop_length * 1000 / sr),
        probabilities=probs,
        confidence=float(np.mean(seg[:, label])),
    ))
