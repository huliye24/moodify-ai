"""Execute one versioned intervention plan using Moodify's existing DSP chain."""

from __future__ import annotations

import hashlib
from pathlib import Path

import numpy as np
import soundfile as sf

from moodify.audio_io import load_audio
from moodify.processing.pedalboard_chain import MoodifyDSPChain

from .models import InterventionPlan, InterventionResult


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def execute_intervention(
    input_path: Path,
    output_path: Path,
    plan: InterventionPlan,
) -> InterventionResult:
    """Process source audio without modifying the source file."""
    input_path = Path(input_path)
    output_path = Path(output_path)
    if not input_path.is_file():
        raise FileNotFoundError(input_path)
    if output_path.suffix.lower() != ".wav":
        raise ValueError("data-factory candidate output must be WAV")

    audio, sr = load_audio(str(input_path), always_2d=True)
    chain = MoodifyDSPChain(plan.params)
    processed = chain.process(audio, sr)
    processed = np.asarray(processed, dtype=np.float32)

    if not np.all(np.isfinite(processed)):
        raise ValueError("intervention produced non-finite samples")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    sf.write(output_path, processed, sr, subtype="PCM_24")

    channels = 1 if processed.ndim == 1 else processed.shape[1]
    frames = processed.shape[0]
    return InterventionResult(
        candidate_label=plan.candidate_label,
        candidate_id=plan.candidate_id,
        output_path=str(output_path),
        output_sha256=_sha256(output_path),
        sample_rate=int(sr),
        frames=int(frames),
        channels=int(channels),
        params=plan.params,
    )
