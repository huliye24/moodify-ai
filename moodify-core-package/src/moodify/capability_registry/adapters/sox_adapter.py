"""SoX adapter — audio.measure_loudness (statistics subset).

SoX is LGPL external program. The version probe prints "<exe>: SoX vX.Y.Z";
this adapter extracts the version token. Integer bit-depth conversions may
lose precision — that is recorded as a known failure mode, not hidden.
"""

from __future__ import annotations

from pathlib import Path

from moodify.capability_registry.adapters.base import ControlledProcessAdapter, InvokeRequest

KNOWN_FAILURE_MODES = (
    "8-bit/16-bit integer conversions may reduce precision; check format before use",
)

WINGET_ROOT = Path.home() / "AppData" / "Local" / "Microsoft" / "WinGet" / "Packages"


def _winget_sox() -> tuple[str, ...]:
    for pkg in WINGET_ROOT.glob("ChrisBagwell.SoX_*"):
        if not pkg.is_dir():
            continue
        for build in pkg.glob("*"):
            candidate = build / "sox.exe"
            if candidate.exists():
                return (str(candidate),)
    return ()


class SoxAdapter(ControlledProcessAdapter):
    capability_id = "audio.measure_loudness"
    provider_id = "sox.cli"
    license_label = "LGPL (external process)"

    def _candidate_paths(self) -> tuple[str, ...]:
        return _winget_sox()

    def _which_names(self) -> tuple[str, ...]:
        return ("sox",)

    def version(self) -> str | None:
        raw = super().version()
        if raw and "SoX v" in raw:
            return raw.split("SoX v", 1)[1].split()[0].strip(":,;")
        return raw

    def build_command(self, request: InvokeRequest, work_dir: Path, out_dir: Path) -> list[str]:
        if "source" not in request.inputs:
            raise ValueError("audio.measure_loudness requires input role 'source'")
        source = Path(request.inputs["source"])
        return [self._binary or "", "--norm=-1", str(source), "-n", "stat"]

    def stdout_target(self, request: InvokeRequest, out_dir: Path) -> Path | None:
        source = Path(request.inputs.get("source", "audio"))
        stem = request.parameters.get("output_stem", source.stem)
        return out_dir / f"{stem}_stats.txt"
