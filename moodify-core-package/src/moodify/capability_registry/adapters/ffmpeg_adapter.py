"""FFmpeg / FFprobe adapters — media.transcode and media.probe.

FFmpeg and FFprobe are external programs (GPLv3/LGPL). Commands use argv
arrays only; container/format behavior is provider-specific knowledge that
stays in these adapters.
"""

from __future__ import annotations

from pathlib import Path

from moodify.capability_registry.adapters.base import ControlledProcessAdapter, InvokeRequest

WINGET_ROOT = Path.home() / "AppData" / "Local" / "Microsoft" / "WinGet" / "Packages"


def _winget_bin(exe: str) -> tuple[str, ...]:
    for pkg in WINGET_ROOT.glob("Gyan.FFmpeg_*"):
        if not pkg.is_dir():
            continue
        for build in pkg.glob("*"):
            candidate = build / "bin" / exe
            if candidate.exists():
                return (str(candidate),)
    return ()


class FfmpegAdapter(ControlledProcessAdapter):
    capability_id = "media.transcode"
    provider_id = "ffmpeg.cli"
    license_label = "GPLv3/LGPL (external process)"

    def _candidate_paths(self) -> tuple[str, ...]:
        return _winget_bin("ffmpeg.exe")

    def _which_names(self) -> tuple[str, ...]:
        return ("ffmpeg",)

    def build_command(self, request: InvokeRequest, work_dir: Path, out_dir: Path) -> list[str]:
        if "source" not in request.inputs:
            raise ValueError("media.transcode requires input role 'source'")
        source = Path(request.inputs["source"])
        fmt = request.parameters.get("format", "wav")
        stem = request.parameters.get("output_stem", source.stem)
        target = out_dir / f"{stem}.{fmt}"
        cmd = [self._binary or "", "-y", "-i", str(source)]
        if request.parameters.get("sample_rate"):
            cmd += ["-ar", str(request.parameters["sample_rate"])]
        if request.parameters.get("channels"):
            cmd += ["-ac", str(request.parameters["channels"])]
        cmd.append(str(target))
        return cmd


class FfprobeAdapter(ControlledProcessAdapter):
    capability_id = "media.probe"
    provider_id = "ffprobe.cli"
    license_label = "GPLv3/LGPL (external process)"

    def _candidate_paths(self) -> tuple[str, ...]:
        return _winget_bin("ffprobe.exe")

    def _which_names(self) -> tuple[str, ...]:
        return ("ffprobe",)

    def build_command(self, request: InvokeRequest, work_dir: Path, out_dir: Path) -> list[str]:
        if "source" not in request.inputs:
            raise ValueError("media.probe requires input role 'source'")
        source = Path(request.inputs["source"])
        return [
            self._binary or "",
            "-v", "error",
            "-show_format",
            "-show_streams",
            "-of", "json",
            str(source),
        ]

    def stdout_target(self, request: InvokeRequest, out_dir: Path) -> Path | None:
        source = Path(request.inputs.get("source", "media"))
        stem = request.parameters.get("output_stem", source.stem)
        return out_dir / f"{stem}.json"
