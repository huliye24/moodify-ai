"""RubberBand adapter — audio.time_stretch via GPLv2 executable.

RubberBand is bundled under tools/third_party (GPLv2 executable, external
process only). It requires sndfile.dll next to the executable — a known
failure mode recorded here so callers understand deployment constraints.
"""

from __future__ import annotations

from pathlib import Path

from moodify.capability_registry.adapters.base import ControlledProcessAdapter, InvokeRequest

KNOWN_FAILURE_MODES = (
    "GPLv2 executable; requires sndfile.dll in the same directory",
)

LOCAL_ROOT = Path(r"E:\moodify\tools\third_party\rubberband-4.0.0")


def _local_rubberband() -> tuple[str, ...]:
    if not LOCAL_ROOT.exists():
        return ()
    return tuple(str(p) for p in LOCAL_ROOT.rglob("rubberband.exe"))


class RubberBandAdapter(ControlledProcessAdapter):
    capability_id = "audio.time_stretch"
    provider_id = "rubberband.cli"
    license_label = "GPLv2 (external process)"

    def _candidate_paths(self) -> tuple[str, ...]:
        return _local_rubberband()

    def _which_names(self) -> tuple[str, ...]:
        return ("rubberband",)

    def _version_args(self) -> tuple[str, ...]:
        return ("--version",)

    def build_command(self, request: InvokeRequest, work_dir: Path, out_dir: Path) -> list[str]:
        if "source" not in request.inputs:
            raise ValueError("audio.time_stretch requires input role 'source'")
        source = Path(request.inputs["source"])
        stem = request.parameters.get("output_stem", source.stem)
        target = out_dir / f"{stem}_stretched.wav"
        cmd = [self._binary or ""]
        if request.parameters.get("tempo"):
            cmd += ["--tempo", str(request.parameters["tempo"])]
        if request.parameters.get("pitch"):
            cmd += ["--pitch", str(request.parameters["pitch"])]
        cmd += [str(source), str(target)]
        return cmd
