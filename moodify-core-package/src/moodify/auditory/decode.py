"""Audio probing and decoding via ffmpeg/ffprobe (DSK-MFY-AUDITORY-SCAN-001).

Subprocess argument arrays only — never shell command strings.
"""

from __future__ import annotations

import json
import logging
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

import numpy as np

logger = logging.getLogger(__name__)

from moodify.auditory.errors import (
    AudioDecodeFailed,
    AudioEmpty,
    AudioInvalidSamples,
    FfmpegNotFound,
    FfprobeNotFound,
)
from moodify.auditory.models import FileProbe


@dataclass(frozen=True)
class DecodedAudio:
    samples: np.ndarray  # float32, shape (n,) mono or (n, ch) stereo
    sample_rate: int
    probe: FileProbe


def _win_exe(name: str) -> str | None:
    """Windows 常见安装位兜底（winget links / scoop shims / Program Files）。"""
    import os
    for probe in (
        os.path.expandvars(rf"%LOCALAPPDATA%\Microsoft\WinGet\Links\{name}.exe"),
        os.path.expanduser(rf"~\scoop\shims\{name}.exe"),
        rf"C:\Program Files\ffmpeg\bin\{name}.exe",
    ):
        if os.path.isfile(probe):
            return probe
    return None


def _which_ffmpeg() -> str:
    exe = shutil.which("ffmpeg") or _win_exe("ffmpeg")
    if exe is None:
        raise FfmpegNotFound("ffmpeg not found on PATH")
    return exe


def _which_ffprobe() -> str:
    exe = shutil.which("ffprobe") or _win_exe("ffprobe")
    if exe is None:
        raise FfprobeNotFound("ffprobe not found on PATH")
    return exe


def ffmpeg_version() -> str:
    try:
        out = subprocess.run(
            [_which_ffmpeg(), "-version"],
            capture_output=True, text=True, timeout=15,
        ).stdout
        return out.splitlines()[0] if out else "unknown"
    except Exception:
        return "unknown"


def probe(path: Path) -> FileProbe:
    """ffprobe -> FileProbe with SHA-256 of the file."""
    import hashlib

    exe = _which_ffprobe()
    proc = subprocess.run(
        [
            exe, "-v", "error",
            "-show_format", "-show_streams",
            "-of", "json",
            str(path),
        ],
        capture_output=True, text=True, timeout=60,
    )
    if proc.returncode != 0:
        raise AudioDecodeFailed(f"ffprobe failed: {proc.stderr[:300]}")
    try:
        info = json.loads(proc.stdout)
    except json.JSONDecodeError:
        raise AudioDecodeFailed("ffprobe returned invalid JSON") from None

    streams = info.get("streams", [])
    audio_stream = next((s for s in streams if s.get("codec_type") == "audio"), None)
    fmt = info.get("format", {})
    if audio_stream is None:
        raise AudioDecodeFailed("no audio stream found")

    duration = float(audio_stream.get("duration") or fmt.get("duration") or 0.0)
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)

    return FileProbe(
        filename=path.name,
        absolute_path=str(path.resolve()),
        sha256=h.hexdigest(),
        duration_seconds=duration,
        container=fmt.get("format_name", ""),
        codec=audio_stream.get("codec_name", ""),
        sample_rate=int(audio_stream.get("sample_rate") or 0),
        bit_depth=int(audio_stream["bits_per_sample"]) if audio_stream.get("bits_per_sample") else None,
        channels=int(audio_stream.get("channels") or 0),
        channel_layout=audio_stream.get("channel_layout", ""),
        file_size_bytes=int(fmt.get("size") or path.stat().st_size),
    )


def _best_effort_cleanup(path: Path) -> None:
    """Remove a temp decode file; failure is logged, never fatal."""
    try:
        path.unlink()
    except OSError as exc:
        logger.warning("temp decode cleanup failed for %s: %s", path, exc)


def decode(path: Path, analysis_sample_rate: int, timeout_s: int = 300) -> DecodedAudio:
    """Decode to float32 via ffmpeg, resampling to the analysis rate.

    The source file itself is never modified or rewritten.
    """
    import hashlib

    exe = _which_ffmpeg()
    out_path = path.parent / f".auditory_decode_{hashlib.md5(str(path).encode()).hexdigest()[:8]}.f32"
    args = [
        exe, "-v", "error", "-y", "-i", str(path),
        "-vn", "-acodec", "pcm_f32le",
        "-ar", str(analysis_sample_rate),
        "-f", "f32le", str(out_path),
    ]
    proc = subprocess.run(args, capture_output=True, text=True, timeout=timeout_s)
    if proc.returncode != 0:
        _best_effort_cleanup(out_path)
        raise AudioDecodeFailed(f"ffmpeg decode failed: {proc.stderr[:300]}")

    data = np.fromfile(out_path, dtype=np.float32)
    _best_effort_cleanup(out_path)

    if data.size == 0:
        raise AudioEmpty(f"audio decoded to zero samples: {path}")

    # channel layout from probe
    info = probe(path)
    if info.channels > 1:
        usable = (data.size // info.channels) * info.channels
        samples = data[:usable].reshape(-1, info.channels)
    else:
        samples = data

    if not np.all(np.isfinite(samples)):
        raise AudioInvalidSamples(f"non-finite samples present: {path}")

    return DecodedAudio(samples=samples.astype(np.float32), sample_rate=analysis_sample_rate, probe=info)
