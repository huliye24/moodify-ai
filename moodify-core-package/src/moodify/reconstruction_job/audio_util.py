"""Source ingest helpers for reconstruction jobs (MFY-CR-P08).

Transcoding keeps the source sample rate (no blind resampling); validation
reuses the canonical auditory decode path.
"""

from __future__ import annotations

import glob
import hashlib
import os
import shutil
import subprocess
from pathlib import Path

from moodify.auditory.errors import AudioDecodeFailed, AudioEmpty

from .contract import FailureInfo

SUPPORTED_SUFFIXES = frozenset({".wav", ".flac", ".mp3", ".m4a", ".aac", ".ogg"})

FFMPEG_WIN_CANDIDATES = (
    Path(r"C:\Program Files\ffmpeg\bin\ffmpeg.exe"),
    Path(r"C:\ffmpeg\bin\ffmpeg.exe"),
)
_WINGET_FFMPEG_GLOB = (
    "C:/Users/*/AppData/Local/Microsoft/WinGet/Packages/"
    "Gyan.FFmpeg*/ffmpeg-*/bin/ffmpeg.exe"
)


def ffmpeg_path() -> str | None:
    found = shutil.which("ffmpeg")
    if found:
        return found
    for cand in FFMPEG_WIN_CANDIDATES:
        if cand.is_file():
            return str(cand)
    for hit in glob.glob(_WINGET_FFMPEG_GLOB):
        return hit
    return None


def ensure_ffmpeg_on_path() -> str | None:
    """Make the discovered ffmpeg visible to subprocess/which consumers
    (moodify.auditory.decode relies on PATH or a fixed Program Files path)."""
    exe = ffmpeg_path()
    if exe and shutil.which("ffmpeg") is None:
        os.environ["PATH"] = str(Path(exe).parent) + os.pathsep + os.environ.get("PATH", "")
    return exe


def ffmpeg_available() -> bool:
    return ffmpeg_path() is not None


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def transcode_to_wav(src: Path, dst: Path, timeout_s: int = 300) -> None:
    """Decode to PCM WAV keeping the original sample rate (no resampling)."""
    exe = ffmpeg_path()
    if exe is None:
        raise AudioDecodeFailed("ffmpeg not found on PATH")
    dst.parent.mkdir(parents=True, exist_ok=True)
    proc = subprocess.run(
        [exe, "-y", "-i", str(src), "-vn", "-acodec", "pcm_s16le", "-f", "wav", str(dst)],
        capture_output=True, timeout=timeout_s, check=False,
    )
    if proc.returncode != 0:
        dst.unlink(missing_ok=True)
        raise AudioDecodeFailed(f"ffmpeg transcode failed: {proc.stderr[:300]}")
    if not dst.is_file() or dst.stat().st_size == 0:
        dst.unlink(missing_ok=True)
        raise AudioDecodeFailed("ffmpeg produced empty output")


def classify_ingest_error(exc: Exception) -> FailureInfo:
    """Map ingest-time exceptions to product failure semantics (no stack leak)."""
    if isinstance(exc, AudioEmpty):
        return FailureInfo(
            failure_code="INVALID_INPUT",
            stage="ingest",
            retry_policy="PERMANENT",
            user_action="provide audio with actual sound content",
            internal_detail=f"{type(exc).__name__}: {exc}",
            public_message_key="reconstruction_source_invalid",
        )
    if isinstance(exc, AudioDecodeFailed):
        return FailureInfo(
            failure_code="DECODE_FAILED",
            stage="ingest",
            retry_policy="PERMANENT",
            user_action="provide a supported audio file",
            internal_detail=f"{type(exc).__name__}: {exc}",
            public_message_key="reconstruction_source_invalid",
        )
    if isinstance(exc, MemoryError):
        return FailureInfo(
            failure_code="RESOURCE_LIMIT",
            stage="ingest",
            retry_policy="PERMANENT",
            user_action="retry later",
            internal_detail="memory limit during ingest",
            public_message_key="reconstruction_resource_limit",
        )
    return FailureInfo(
        failure_code="INVALID_INPUT",
        stage="ingest",
        retry_policy="PERMANENT",
        user_action="provide a valid audio file",
        internal_detail=f"{type(exc).__name__}: {exc}",
        public_message_key="reconstruction_source_invalid",
    )
