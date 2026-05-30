"""v01_exporter.py — Export processed audio to WAV."""

import os
from pathlib import Path

import numpy as np
import soundfile


def export(input_audio: np.ndarray,
           sr: int,
           input_path: str,
           preset_key: str,
           output_dir: str = "outputs") -> str:
    """Export audio as 16-bit WAV.

    Args:
        input_audio: float32 audio data
        sr: sample rate
        input_path: original file path (used for naming)
        preset_key: preset identifier (e.g. "warm_vocal")
        output_dir: output directory

    Returns:
        Absolute path to the exported WAV file
    """
    os.makedirs(output_dir, exist_ok=True)

    stem = Path(input_path).stem
    filename = f"{stem}_{preset_key}.wav"
    out_path = os.path.join(output_dir, filename)

    # Ensure float32, clamp to [-1, 1]
    audio = input_audio.astype(np.float32)
    peak = np.max(np.abs(audio))
    if peak > 0.999:
        audio = audio * (0.999 / peak)

    soundfile.write(out_path, audio, sr, subtype="PCM_16")
    return os.path.abspath(out_path)
