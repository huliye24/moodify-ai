"""MuseScore adapter — notation.render via external GPLv3 process.

Adapts the 009 score_engine knowledge (single -o, no -I, SVG page suffix)
without importing or modifying 009 implementation. This is composition of
known failure modes, not reuse of code.
"""

from __future__ import annotations

from pathlib import Path

from moodify.capability_registry.adapters.base import ControlledProcessAdapter, InvokeRequest

KNOWN_FAILURE_MODES = (
    "MuseScore 4.5.x accepts only one -o output per invocation",
    "MuseScore 4.5.x does not support -I <format> argument",
    "Multi-page SVG output appends page suffix (e.g. score-1.svg)",
)

DEFAULT_CANDIDATES = (
    r"C:\Program Files\MuseScore 4\bin\MuseScore4.exe",
    r"C:\Program Files (x86)\MuseScore 4\bin\MuseScore4.exe",
    "/usr/bin/musescore",
    "/usr/bin/mscore",
    "/usr/local/bin/musescore",
)


class MuseScoreAdapter(ControlledProcessAdapter):
    capability_id = "notation.render"
    provider_id = "musescore.cli"
    license_label = "GPLv3 (external process)"

    def _candidate_paths(self) -> tuple[str, ...]:
        return DEFAULT_CANDIDATES

    def _which_names(self) -> tuple[str, ...]:
        return ("musescore4", "musescore", "mscore")

    def build_command(self, request: InvokeRequest, work_dir: Path, out_dir: Path) -> list[str]:
        inputs = request.inputs
        if "score" not in inputs:
            raise ValueError("notation.render requires input role 'score' (musicxml)")
        source = Path(inputs["score"])
        if source.suffix.lower() not in (".musicxml", ".xml", ".mid", ".midi"):
            raise ValueError(f"unsupported score input: {source.suffix}")
        stem = request.parameters.get("output_stem", source.stem)
        target = out_dir / f"{stem}.pdf"
        return [self._binary or "", "-o", str(target), str(source)]
