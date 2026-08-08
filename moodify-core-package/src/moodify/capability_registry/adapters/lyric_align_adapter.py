"""Lyric alignment adapter — lyric.align (DSK-MFY-LYRIC-TEMPORAL-ALIGNMENT-001).

Wired at the case level (`case lyrics-align`) and through the API contract
(POST /api/v1/lyric-alignments); the generic invoke path is refused.
"""

from __future__ import annotations

from pathlib import Path

from moodify.capability_registry.adapters.base import AdapterResult, ControlledProcessAdapter, InvokeRequest


class LyricAlignAdapter(ControlledProcessAdapter):
    capability_id = "lyric.align"
    provider_id = "lyric_align.core"
    license_label = "Apache-2.0 (internal)"

    def _candidate_paths(self) -> tuple[str, ...]:
        return ()

    def _which_names(self) -> tuple[str, ...]:
        return ()

    def detect(self) -> bool:
        return (Path(__file__).resolve().parents[3] / "lyric_align").is_dir()

    def version(self) -> str:
        return "0.1.0" if self.detect() else ""

    def invoke(self, request: InvokeRequest) -> AdapterResult:
        return AdapterResult(
            status="unavailable",
            errors=(
                "Lyric alignment runs inside the case pipeline "
                "(case lyrics-align) or the API contract; generic invoke is not permitted.",
            ),
            error_class="policy_rejection",
        )
