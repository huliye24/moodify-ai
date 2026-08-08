"""Read-only environment detectors for external and internal capabilities.

Detection never executes processing commands, never installs, never downloads
and never modifies third-party programs. Each detector returns a fact record:
binary path (when found), version (when queryable) and known failure modes.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

DEFAULT_TIMEOUT_S = 10.0

DEFAULT_PATHS: dict[str, tuple[str, ...]] = {
    "musescore": (
        r"C:\Program Files\MuseScore 4\bin\MuseScore4.exe",
        r"C:\Program Files (x86)\MuseScore 4\bin\MuseScore4.exe",
        "/usr/bin/musescore",
        "/usr/bin/mscore",
        "/usr/local/bin/musescore",
    ),
    "audacity": (
        r"C:\Program Files\Audacity\Audacity.exe",
        "/usr/bin/audacity",
        "/usr/local/bin/audacity",
    ),
}


@dataclass(frozen=True)
class DetectionResult:
    tool: str
    found: bool
    binary_path: str | None
    version: str | None
    known_failure_modes: tuple[str, ...]
    notes: str

    def to_dict(self) -> dict:
        return {
            "tool": self.tool,
            "found": self.found,
            "binary_path": self.binary_path,
            "version": self.version,
            "known_failure_modes": list(self.known_failure_modes),
            "notes": self.notes,
        }


def _probe_version(binary: str, args: tuple[str, ...]) -> str | None:
    try:
        proc = subprocess.run(
            [binary, *args],
            capture_output=True, timeout=DEFAULT_TIMEOUT_S, check=False,
        )
        out = (proc.stdout or b"").decode("utf-8", errors="replace").strip()
        if proc.returncode == 0 and out:
            return out.splitlines()[0]
        err = (proc.stderr or b"").decode("utf-8", errors="replace").strip()
        return err.splitlines()[0] if err else None
    except (OSError, subprocess.TimeoutExpired):
        return None


def _find_binary(tool: str, candidate_paths: tuple[str, ...], which_names: tuple[str, ...]) -> str | None:
    for candidate in candidate_paths:
        if candidate and Path(candidate).is_file():
            return candidate
    for name in which_names:
        found = shutil.which(name)
        if found:
            return found
    return None


def detect_musescore() -> DetectionResult:
    binary = _find_binary("musescore", DEFAULT_PATHS["musescore"], ("musescore4", "musescore", "mscore"))
    version = _probe_version(binary, ("--version",)) if binary else None
    return DetectionResult(
        tool="musescore",
        found=binary is not None,
        binary_path=binary,
        version=version,
        known_failure_modes=(
            "MuseScore 4.5.x accepts only one -o output per invocation",
            "MuseScore 4.5.x does not support -I <format> argument",
            "Multi-page SVG output appends page suffix (e.g. score-1.svg)",
        ),
        notes="negative knowledge sourced from DSK-MFY-SCORE-ENGINE-009 FAILURE_LEDGER #3/#4",
    )


WINGET_ROOT = Path.home() / "AppData" / "Local" / "Microsoft" / "WinGet" / "Packages"


def _winget_candidate(pattern: str, exe: str) -> tuple[str, ...]:
    # WinGet layouts vary: <build>/bin/<exe> (ffmpeg) or <build>/<exe> (sox)
    for pkg in WINGET_ROOT.glob(pattern):
        if not pkg.is_dir():
            continue
        for build in pkg.glob("*"):
            if not build.is_dir():
                continue
            for candidate in (build / "bin" / exe, build / exe):
                if candidate.exists():
                    return (str(candidate),)
    return ()


def detect_ffmpeg() -> DetectionResult:
    binary = _find_binary(
        "ffmpeg",
        _winget_candidate("Gyan.FFmpeg_*", "ffmpeg.exe"),
        ("ffmpeg",),
    )
    version = _probe_version(binary, ("-version",)) if binary else None
    return DetectionResult(
        tool="ffmpeg",
        found=binary is not None,
        binary_path=binary,
        version=version,
        known_failure_modes=(),
        notes="",
    )


def detect_ffprobe() -> DetectionResult:
    # ffprobe lives in the same FFmpeg package directory as ffmpeg
    binary = None
    if (ffmpeg := detect_ffmpeg()) and ffmpeg.binary_path:
        sibling = Path(ffmpeg.binary_path).with_name("ffprobe.exe")
        if sibling.is_file():
            binary = str(sibling)
    if binary is None:
        binary = _find_binary("ffprobe", (), ("ffprobe",))
    version = _probe_version(binary, ("-version",)) if binary else None
    return DetectionResult(
        tool="ffprobe",
        found=binary is not None,
        binary_path=binary,
        version=version,
        known_failure_modes=(),
        notes="",
    )


def detect_sox() -> DetectionResult:
    candidates = list(_winget_candidate("ChrisBagwell.SoX_*", "sox.exe"))
    binary = _find_binary("sox", tuple(candidates), ("sox",))
    version = _probe_version(binary, ("--version",)) if binary else None
    if version:
        # sox --version prints "<exe>:      SoX v14.4.2" — keep the version token
        marker = "SoX v"
        if marker in version:
            version = version.split(marker, 1)[1].split()[0].strip(":,;")
    return DetectionResult(
        tool="sox",
        found=binary is not None,
        binary_path=binary,
        version=version,
        known_failure_modes=(
            "8-bit/16-bit integer conversions may reduce precision; check format before use",
        ),
        notes="",
    )


def detect_rubberband() -> DetectionResult:
    local = Path(r"E:\moodify\tools\third_party\rubberband-4.0.0")
    candidates: list[str] = []
    if local.exists():
        candidates.extend(str(p) for p in local.rglob("rubberband.exe"))
    binary = _find_binary("rubberband", tuple(candidates), ("rubberband",))
    version = _probe_version(binary, ("--version",)) if binary else None
    return DetectionResult(
        tool="rubberband",
        found=binary is not None,
        binary_path=binary,
        version=version,
        known_failure_modes=(
            "GPLv2 executable; requires sndfile.dll in the same directory",
        ),
        notes="bundled under tools/third_party (GPLv2 executable, external process only)",
    )


def detect_audacity() -> DetectionResult:
    binary = _find_binary("audacity", DEFAULT_PATHS["audacity"], ("audacity",))
    version = _probe_version(binary, ("--version",)) if binary else None
    return DetectionResult(
        tool="audacity",
        found=binary is not None,
        binary_path=binary,
        version=version,
        known_failure_modes=(
            "GUI application; headless automation is not assumed available",
        ),
        notes="capability may be human_handoff only until headless mode verified",
    )


def detect_basic_pitch() -> DetectionResult:
    """Detect the 008 transcription capability (.venv-basic-pitch)."""
    venv_python = Path(r"E:\moodify\.venv-basic-pitch\Scripts\python.exe")
    found = venv_python.is_file()
    version = None
    if found:
        try:
            proc = subprocess.run(
                [str(venv_python), "-c",
                 "import importlib.metadata as m; print(m.version('basic-pitch'))"],
                capture_output=True, timeout=DEFAULT_TIMEOUT_S, check=False,
            )
            out = (proc.stdout or b"").decode("utf-8", errors="replace").strip()
            version = out.splitlines()[-1] if out else None
        except (OSError, subprocess.TimeoutExpired):
            version = None
    return DetectionResult(
        tool="basic_pitch",
        found=found,
        binary_path=str(venv_python) if found else None,
        version=version,
        known_failure_modes=(
            "Demucs separation not installed (stem separation unavailable)",
            "No real-song ground truth; accuracy claims prohibited until benchmark",
            "Drums UNSUPPORTED for pitch transcription",
        ),
        notes="internal capability from DSK-MFY-STEM-MIDI-008; python.exe is the entry",
    )


def detect_ocean_listen() -> DetectionResult:
    """Detect the vendored Ocean Listen auditory sensor (DSK-MFY-OCEAN-ABSORPTION-001)."""
    repo_root = Path(__file__).resolve().parents[4]
    ocean_py = repo_root / "third_party" / "ocean-listen" / "ocean.py"
    found = ocean_py.is_file()
    pin = "928dfba62a2c074ccb0154f7ddd42743e4ce9e75"
    return DetectionResult(
        tool="ocean_listen",
        found=found,
        binary_path=str(ocean_py) if found else None,
        version=pin,
        known_failure_modes=(
            "Upstream not vendored (third_party/ocean-listen missing)",
            "Commit pin mismatch blocks execution (allow_unreviewed_commit=false)",
            "Sensor output is never artistic authority (quarantine semantics)",
        ),
        notes=(
            "isolated external sensor; pinned commit "
            + pin
            + "; velocity is a confidence proxy, not loudness"
        ),
    )


def detect_moodify_self() -> DetectionResult:
    """Detect Moodify's own capability modules (009 score_engine, 008 pipeline)."""
    pkg_dir = Path(__file__).resolve().parents[1]
    score_engine = (pkg_dir / "score_engine").is_dir()
    transcription = (pkg_dir / "transcription_pipeline").is_dir()
    notes = []
    if score_engine:
        notes.append("score_engine present (DSK-MFY-SCORE-ENGINE-009)")
    if transcription:
        notes.append("transcription_pipeline present (DSK-MFY-STEM-MIDI-008)")
    return DetectionResult(
        tool="moodify_self",
        found=bool(notes),
        binary_path=None,
        version=None,
        known_failure_modes=(),
        notes="; ".join(notes),
    )


def detect_all() -> dict[str, DetectionResult]:
    """Run all detectors; each is independent and read-only."""
    detectors = {
        "musescore": detect_musescore,
        "ffmpeg": detect_ffmpeg,
        "ffprobe": detect_ffprobe,
        "sox": detect_sox,
        "rubberband": detect_rubberband,
        "audacity": detect_audacity,
        "basic_pitch": detect_basic_pitch,
        "ocean_listen": detect_ocean_listen,
        "moodify_self": detect_moodify_self,
    }
    return {name: detector() for name, detector in detectors.items()}


def python_version() -> str:
    return sys.version.split()[0]
