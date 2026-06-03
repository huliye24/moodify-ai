"""bands.py — Unified frequency band definitions.

Single source of truth for frequency bands used across Moodify.
Used by: v01_analyzer.py, reality_metrics.py, v01_inspector.py, and future modules.

Convention:
  - Edge frequencies in Hz
  - Name: short lowercase identifier
  - Display name: human-readable label
  - Band 6 = standard 6-band analysis (no gap between presence and air)
  - Band 7 = extended 7-band with explicit brilliance band
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar


@dataclass(frozen=True)
class FrequencyBand:
    """Single frequency band definition."""
    name: str           # short id: sub, bass, low_mid, mid, presence, brilliance, air
    display: str        # human-readable: Sub, Bass, Low-Mid, Mid, Presence, Brilliance, Air
    low_hz: float       # lower edge in Hz
    high_hz: float      # upper edge in Hz
    color: str = "#888888"  # matplotlib hex color


# — Standard 6-band definition (v01 mainline) —
BAND_6: ClassVar[dict[str, FrequencyBand]] = {
    "sub":      FrequencyBand("sub",      "Sub",       20,   60,   "#4a0e4e"),
    "bass":     FrequencyBand("bass",     "Bass",      60,  250,   "#6b2fa0"),
    "low_mid":  FrequencyBand("low_mid",  "Low-Mid",  250,  500,   "#3a7ca5"),
    "mid":      FrequencyBand("mid",      "Mid",      500, 2000,   "#2d9c6b"),
    "presence": FrequencyBand("presence", "Presence", 2000, 5000,   "#c4a43e"),
    "air":      FrequencyBand("air",      "Air",      8000,16000,   "#d4756b"),
}

# — Extended 7-band definition (MRS + future) —
BAND_7: ClassVar[dict[str, FrequencyBand]] = {
    **BAND_6,
    "brilliance": FrequencyBand("brilliance", "Brilliance", 5000, 8000, "#e8a87c"),
}

# — Convenience: ordered lists —
BAND_6_NAMES: ClassVar[list[str]] = ["sub", "bass", "low_mid", "mid", "presence", "air"]
BAND_6_EDGES: ClassVar[list[tuple[str, float, float]]] = [
    (b.name, b.low_hz, b.high_hz) for b in BAND_6.values()
]
BAND_6_DISPLAYS: ClassVar[list[str]] = [b.display for b in BAND_6.values()]
BAND_6_COLORS: ClassVar[list[str]] = [b.color for b in BAND_6.values()]

BAND_7_NAMES: ClassVar[list[str]] = ["sub", "bass", "low_mid", "mid", "presence", "brilliance", "air"]
BAND_7_EDGES: ClassVar[list[tuple[str, float, float]]] = [
    (b.name, b.low_hz, b.high_hz) for b in BAND_7.values()
]
BAND_7_DISPLAYS: ClassVar[list[str]] = [b.display for b in BAND_7.values()]
BAND_7_COLORS: ClassVar[list[str]] = [b.color for b in BAND_7.values()]

# Default: 6-band for v01 compatibility
DEFAULT_BANDS: ClassVar[dict] = BAND_6
DEFAULT_EDGES: ClassVar[list] = BAND_6_EDGES
DEFAULT_NAMES: ClassVar[list] = BAND_6_NAMES


def get_band_edges(band_spec: str = "6") -> list[tuple[str, float, float]]:
    """Return ordered [(name, low_hz, high_hz), ...] for the given band spec."""
    if band_spec == "7":
        return list(BAND_7_EDGES)
    return list(BAND_6_EDGES)


def get_band(name: str, band_spec: str = "6") -> FrequencyBand | None:
    """Look up a single band by name."""
    bands = BAND_7 if band_spec == "7" else BAND_6
    return bands.get(name)


def band_mask(freqs, low_hz: float, high_hz: float):
    """Convenience: boolean mask for numpy frequency array."""
    return (freqs >= low_hz) & (freqs <= high_hz)
