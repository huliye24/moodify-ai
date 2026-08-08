"""Ocean Listen adapter — auditory.ocean_listen.

The sensor is wired at the case level (`case analyze --sensor ocean`,
DSK-MFY-OCEAN-ABSORPTION-001) and never through the generic invoke path:
execution requires case identity, source-hash verification and the evidence
registry. The registry adapter reports availability honestly and refuses the
generic invoke path.
"""

from __future__ import annotations

from pathlib import Path

from moodify.capability_registry.adapters.base import AdapterResult, ControlledProcessAdapter, InvokeRequest

PINNED_OCEAN_COMMIT = "928dfba62a2c074ccb0154f7ddd42743e4ce9e75"


class OceanListenAdapter(ControlledProcessAdapter):
    capability_id = "auditory.ocean_listen"
    provider_id = "ocean_listen.git"
    license_label = "MIT (external sensor)"

    def _candidate_paths(self) -> tuple[str, ...]:
        repo_root = Path(__file__).resolve().parents[4]
        return (str(repo_root / "third_party" / "ocean-listen" / "ocean.py"),)

    def _which_names(self) -> tuple[str, ...]:
        return ()

    def detect(self) -> bool:
        return Path(self._candidate_paths()[0]).is_file()

    def version(self) -> str:
        return PINNED_OCEAN_COMMIT if self.detect() else ""

    def invoke(self, request: InvokeRequest) -> AdapterResult:
        return AdapterResult(
            status="unavailable",
            errors=(
                "Ocean Listen runs only inside the case ANALYZING stage "
                "(case analyze --sensor ocean); generic invoke is not permitted.",
            ),
            error_class="policy_rejection",
        )
