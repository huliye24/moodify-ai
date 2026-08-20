"""lalal.ai stem separation constants (LALAL-STEMS-001)."""

from __future__ import annotations

DEFAULT_BASE_URL = "https://www.lalal.ai/api/v1/"

# 10-track stem catalog exposed to callers; each stem is a separate paid task.
STEMS: tuple[str, ...] = (
    "vocals",
    "drum",
    "piano",
    "bass",
    "electric_guitar",
    "acoustic_guitar",
    "synthesizer",
    "strings",
    "wind",
    "instrumental",
)

EXTRACTION_LEVELS: tuple[str, ...] = ("deep_extraction", "clear_cut")

SPLITTERS: tuple[str, ...] = ("auto", "orion", "perseus", "phoenix", "andromeda")

DEFAULT_EXTRACTION_LEVEL = "deep_extraction"
DEFAULT_SPLITTER = "auto"

MULTIVOCAL_VALUES: tuple[str, ...] = ("lead_back",)
