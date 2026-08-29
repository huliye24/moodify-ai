"""Acoustic analysis facade — the engine's measurement entry point.

Delegates to the existing, tested implementation in
``moodify-core-package`` (Phase A/B boundary, see docs/MIGRATION_PLAN_AND_TASKS.md):

- ``moodify.v01_analyzer``        — band spectrum, peak, crest, dynamic range, L/R correlation
- ``moodify.auditory.loudness``   — ITU-R BS.1770-5 integrated loudness, EBU Tech 3342 LRA

The engine owns the facade contract; the legacy package owns the math.
No analysis logic is duplicated here.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from engine._compat import ensure_core_package

ensure_core_package()

# Imported lazily-visible after bootstrap; keep imports after ensure_core_package()
from moodify.audio_io import load_audio                      # noqa: E402
from moodify.auditory.loudness import (                      # noqa: E402
    integrated_loudness_lufs,
    loudness_range_lu,
)
from moodify.v01_analyzer import analyze as _v01_analyze     # noqa: E402


@dataclass
class AcousticProfile:
    """Complete acoustic measurement set for one track."""

    file_path: str
    file_name: str
    format: str
    duration_s: float
    sample_rate: int
    channels: int
    integrated_lufs: float | None
    loudness_range_lu: float | None
    peak_db: float
    crest_factor: float
    dynamic_range_db: float
    correlation_lr: float | None
    spectrum: dict[str, float] = field(default_factory=dict)

    @property
    def stereo_width_rating(self) -> str:
        """Transparent width classification from L/R correlation."""
        if self.correlation_lr is None:
            return "balanced"
        if self.correlation_lr > 0.85:
            return "narrow"
        if self.correlation_lr < 0.35:
            return "wide"
        return "balanced"

    def to_feature_dict(self) -> dict[str, Any]:
        """Flat view consumed by the scoring engine."""
        return {
            "integrated_lufs": self.integrated_lufs,
            "loudness_range_lu": self.loudness_range_lu,
            "peak_db": self.peak_db,
            "crest_factor": self.crest_factor,
            "dynamic_range_db": self.dynamic_range_db,
            "correlation_lr": self.correlation_lr,
            "spectrum": dict(self.spectrum),
        }


def analyze_track(path: str | Path) -> AcousticProfile:
    """Run the full acoustic measurement chain on one audio file.

    WAV / MP3 / FLAC via soundfile (libsndfile >= 1.1), librosa fallback
    handled by the legacy loader.
    """
    path = Path(path)
    metrics = _v01_analyze(str(path), output_dir=str(path.parent / "_tmp_spectrum"))

    # Loudness needs raw samples; reuse the same loader as v01 for consistency.
    audio, sr = load_audio(str(path), always_2d=False)
    if audio.ndim > 1:
        stereo = audio
    else:
        stereo = None

    integrated = integrated_loudness_lufs(audio, sr)
    lra = loudness_range_lu(audio, sr)

    correlation = metrics.correlation_lr if metrics.channels == 2 else None
    del stereo  # reserved for future stereo-specific measurement

    return AcousticProfile(
        file_path=str(path),
        file_name=path.name,
        format=path.suffix.lstrip(".").lower(),
        duration_s=metrics.duration_s,
        sample_rate=metrics.sample_rate,
        channels=metrics.channels,
        integrated_lufs=None if integrated is None else round(float(integrated), 1),
        loudness_range_lu=None if lra is None else round(float(lra), 1),
        peak_db=metrics.peak_db,
        crest_factor=metrics.crest_factor,
        dynamic_range_db=metrics.dynamic_range_db,
        correlation_lr=correlation,
        spectrum={
            "sub": metrics.rms_sub,
            "bass": metrics.rms_bass,
            "low_mid": metrics.rms_low_mid,
            "mid": metrics.rms_mid,
            "presence": metrics.rms_presence,
            "air": metrics.rms_air,
        },
    )
