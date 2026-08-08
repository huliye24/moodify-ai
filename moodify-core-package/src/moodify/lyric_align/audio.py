from __future__ import annotations

import audioop
import json
import math
import os
import shutil
import subprocess
import sys
import wave
from pathlib import Path
from statistics import median


def _win_command(name: str) -> str | None:
    """Windows fallbacks for ffmpeg installed outside PATH (winget / Program Files)."""
    if sys.platform != "win32":
        return None
    for base in (
        Path(os.environ.get("LOCALAPPDATA", "")) / "Microsoft" / "WinGet" / "Packages",
        Path("C:/Program Files/ffmpeg/bin"),
    ):
        for candidate in base.rglob(f"{name}.exe"):
            return str(candidate)
    return None


def require_command(name: str) -> str:
    path = shutil.which(name) or _win_command(name)
    if path is None:
        raise RuntimeError(f"Required command '{name}' was not found in PATH.")
    return path


def ffprobe_duration(audio_path: str | Path) -> float:
    ffprobe = require_command("ffprobe")
    cmd = [
        ffprobe,
        "-v", "error",
        "-show_entries", "format=duration",
        "-of", "json",
        str(audio_path),
    ]
    completed = subprocess.run(cmd, check=True, capture_output=True, text=True)
    payload = json.loads(completed.stdout)
    duration = float(payload["format"]["duration"])
    if not math.isfinite(duration) or duration <= 0:
        raise RuntimeError(f"Invalid audio duration: {duration}")
    return duration


def normalize_audio(audio_path: str | Path, output_wav: str | Path, sample_rate: int = 16000) -> Path:
    ffmpeg = require_command("ffmpeg")
    output = Path(output_wav)
    output.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        ffmpeg,
        "-y",
        "-v", "error",
        "-i", str(audio_path),
        "-ac", "1",
        "-ar", str(sample_rate),
        "-sample_fmt", "s16",
        str(output),
    ]
    subprocess.run(cmd, check=True)
    return output


def separate_vocals_demucs(audio_path: str | Path, workdir: str | Path, model: str = "htdemucs") -> Path:
    outdir = Path(workdir) / "demucs"
    outdir.mkdir(parents=True, exist_ok=True)
    cmd = [
        sys.executable,
        "-m", "demucs.separate",
        "--two-stems", "vocals",
        "-n", model,
        "-o", str(outdir),
        str(audio_path),
    ]
    subprocess.run(cmd, check=True)
    stem = Path(audio_path).stem
    candidates = list(outdir.glob(f"**/{stem}/vocals.*"))
    if not candidates:
        raise RuntimeError("Demucs completed but no vocals stem was found.")
    return candidates[0]


def detect_active_intervals(
    wav_path: str | Path,
    frame_ms: int = 30,
    hop_ms: int = 10,
    threshold_ratio: float = 0.20,
    merge_gap_seconds: float = 0.45,
    min_active_seconds: float = 0.12,
) -> list[tuple[float, float]]:
    with wave.open(str(wav_path), "rb") as wav:
        channels = wav.getnchannels()
        width = wav.getsampwidth()
        rate = wav.getframerate()
        if channels != 1 or width != 2:
            raise ValueError("Active-region detection expects mono 16-bit PCM WAV.")
        raw = wav.readframes(wav.getnframes())

    frame = max(1, int(rate * frame_ms / 1000))
    hop = max(1, int(rate * hop_ms / 1000))
    energies: list[float] = []
    starts: list[int] = []
    total_samples = len(raw) // width
    for sample_start in range(0, max(1, total_samples - frame + 1), hop):
        byte_start = sample_start * width
        chunk = raw[byte_start: byte_start + frame * width]
        if not chunk:
            break
        energies.append(float(audioop.rms(chunk, width)))
        starts.append(sample_start)

    if not energies or max(energies) <= 0:
        return []

    nonzero = [e for e in energies if e > 0]
    floor = median(nonzero) if nonzero else 0.0
    threshold = max(floor * 1.35, max(energies) * threshold_ratio)
    active = [e >= threshold for e in energies]

    intervals: list[tuple[float, float]] = []
    open_start: float | None = None
    for i, is_active in enumerate(active):
        t = starts[i] / rate
        if is_active and open_start is None:
            open_start = t
        if not is_active and open_start is not None:
            end = (starts[i] + frame) / rate
            if end - open_start >= min_active_seconds:
                intervals.append((open_start, end))
            open_start = None
    if open_start is not None:
        intervals.append((open_start, total_samples / rate))

    merged: list[tuple[float, float]] = []
    for start, end in intervals:
        if merged and start - merged[-1][1] <= merge_gap_seconds:
            merged[-1] = (merged[-1][0], max(merged[-1][1], end))
        else:
            merged.append((start, end))
    return merged
