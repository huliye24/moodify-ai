"""Primary spectrogram evidence via ffmpeg showspectrumpic (DSK-MFY-AUDITORY-SCAN-001).

Linear- and logarithmic-frequency PNGs are generated from the SAME
subprocess pattern with identical profile parameters.
"""

from __future__ import annotations

import struct
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from moodify.auditory.errors import FfmpegNotFound, SpectrogramGenerationFailed
from moodify.auditory.profiles import ScanProfile


@dataclass
class SpectrogramRun:
    view: str
    png_path: str
    command: list[str]
    stdout: str
    stderr: str
    return_code: int
    started_at: str
    completed_at: str
    ffmpeg_path: str
    ffmpeg_version: str
    sha256: str = ""
    validated: bool = False


def _ffmpeg() -> str:
    import os
    import shutil
    exe = shutil.which("ffmpeg")
    if exe is None:
        # Windows 常见安装位（winget links / scoop shims / Program Files），
        # 不在 PATH 时兜底查找，避免环境缺口导致扫描不可用。
        for probe in (
            os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\WinGet\Links\ffmpeg.exe"),
            os.path.expanduser(r"~\scoop\shims\ffmpeg.exe"),
            r"C:\Program Files\ffmpeg\bin\ffmpeg.exe",
        ):
            if os.path.isfile(probe):
                return probe
    if exe is None:
        raise FfmpegNotFound("ffmpeg not found on PATH")
    return exe


def _ffmpeg_version() -> str:
    import shutil
    try:
        out = subprocess.run(
            [shutil.which("ffmpeg") or "ffmpeg", "-version"],
            capture_output=True, text=True, timeout=15,
        ).stdout
        return out.splitlines()[0] if out else "unknown"
    except Exception:
        return "unknown"


def _valid_png(path: Path, min_width: int, min_height: int) -> bool:
    if not path.is_file() or path.stat().st_size == 0:
        return False
    with open(path, "rb") as f:
        sig = f.read(8)
    if sig != b"\x89PNG\r\n\x1a\n":
        return False
    with open(path, "rb") as f:
        header = f.read(33)
    if len(header) < 33 or header[12:16] != b"IHDR":
        return False
    width, height = struct.unpack(">II", header[16:24])
    return width >= min_width and height >= min_height


def generate_spectrogram(
    input_path: Path,
    output_path: Path,
    profile: ScanProfile,
    view: str,
    timeout_s: int = 300,
) -> SpectrogramRun:
    """One showspectrumpic render for the given frequency view (linear|logarithmic)."""
    if view not in profile.frequency_views:
        raise SpectrogramGenerationFailed(f"unknown frequency view: {view}")

    spec = profile.spectrogram
    fscale = "lin" if view == "linear" else "log"
    filter_base = (
        f"aresample={profile.analysis_sample_rate},"
        f"showspectrumpic=s={spec['width']}x{spec['height']}:"
        f"mode={spec['channel_mode']}:"
        f"color={spec['color_map']}:"
        f"scale={spec['amplitude_scale']}:"
        f"fscale={fscale}:"
        f"win_func={spec['window_function']}:"
        f"legend={1 if spec['legend'] else 0}"
    )
    filter_expr = (
        filter_base + ":"
        f"drange={spec['dynamic_range_db']}:"
        f"limit={spec['upper_limit_dbfs']}"
    )
    command = [
        _ffmpeg(), "-v", "error", "-y", "-i", str(input_path),
        "-lavfi", filter_expr,
        str(output_path),
    ]
    started_at = datetime.now(timezone.utc).isoformat()
    proc = subprocess.run(command, capture_output=True, text=True, timeout=timeout_s)
    # Ubuntu 22.04 ships FFmpeg 4.4, whose showspectrumpic filter predates
    # drange/limit. Preserve the profile values on capable runtimes, but use
    # the older filter's fixed range when it explicitly rejects those options.
    if proc.returncode != 0 and "Option 'drange' not found" in proc.stderr:
        filter_expr = filter_base
        command = [
            _ffmpeg(), "-v", "error", "-y", "-i", str(input_path),
            "-lavfi", filter_expr, str(output_path),
        ]
        proc = subprocess.run(command, capture_output=True, text=True, timeout=timeout_s)
    completed_at = datetime.now(timezone.utc).isoformat()

    run = SpectrogramRun(
        view=view,
        png_path=str(output_path),
        command=command,
        stdout=proc.stdout,
        stderr=proc.stderr,
        return_code=proc.returncode,
        started_at=started_at,
        completed_at=completed_at,
        ffmpeg_path=_ffmpeg(),
        ffmpeg_version=_ffmpeg_version(),
    )

    if proc.returncode != 0 or not _valid_png(output_path, spec["width"] // 2, spec["height"] // 2):
        raise SpectrogramGenerationFailed(
            f"showspectrumpic failed ({view}): {proc.stderr[:300]}"
        )

    import hashlib
    h = hashlib.sha256()
    with open(output_path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    run.sha256 = h.hexdigest()
    run.validated = True
    return run
