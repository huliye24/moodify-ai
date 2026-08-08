"""Audacity adapter — waveform.region_edit.

Audacity is a GUI application (GPLv2). Headless automation is NOT assumed:
this adapter reports unavailable unless a headless mode is explicitly
configured, and never fabricates automation (no fake headless backend).
The capability is declared human_handoff; adapters are responsible for
making that honest.
"""

from __future__ import annotations

from pathlib import Path

from moodify.capability_registry.adapters.base import AdapterResult, ControlledProcessAdapter, InvokeRequest

KNOWN_FAILURE_MODES = (
    "GUI application; headless automation is not assumed available",
)

DEFAULT_CANDIDATES = (
    r"C:\Program Files\Audacity\Audacity.exe",
    "/usr/bin/audacity",
    "/usr/local/bin/audacity",
)


class AudacityAdapter(ControlledProcessAdapter):
    capability_id = "waveform.region_edit"
    provider_id = "audacity.cli"
    license_label = "GPLv2 (external process)"

    def __init__(self, timeout_s: float = 120.0, allow_headless: bool = False) -> None:
        super().__init__(timeout_s=timeout_s)
        self._allow_headless = allow_headless

    def _candidate_paths(self) -> tuple[str, ...]:
        return DEFAULT_CANDIDATES

    def _which_names(self) -> tuple[str, ...]:
        return ("audacity",)

    def detect(self) -> bool:
        found = super().detect()
        if not found:
            return False
        # headless automation is not implemented; GUI presence alone does not
        # make the adapter executable
        return self._allow_headless

    def invoke(self, request: InvokeRequest) -> AdapterResult:
        if not self._allow_headless:
            return AdapterResult(
                status="unavailable",
                errors=("Audacity is a GUI application; headless automation not implemented. "
                        "Capability declared human_handoff.",),
                error_class="policy_rejection",
            )
        return super().invoke(request)

    def build_command(self, request: InvokeRequest, work_dir: Path, out_dir: Path) -> list[str]:
        # Only reachable when headless automation is explicitly enabled;
        # left minimal and honest rather than fabricating automation.
        raise ValueError("Audacity headless automation is not implemented (human_handoff)")
