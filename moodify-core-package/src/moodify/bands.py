"""bands.py — Unified frequency band definitions.

Single source of truth for frequency bands used across Moodify.
Used by: v01_analyzer.py, reality_metrics.py, v01_inspector.py, and future modules.

Convention:
  - Edge frequencies in Hz
  - Name: short lowercase identifier
  - Display name: human-readable label
  - Band 6 = standard 6-band analysis (legacy, compatibility mode)
  - Band 7 = extended 7-band with explicit brilliance band (v0.4 default)

AEP-ACU-004 (2026-07-03): DEFAULT switched from BAND_6 to BAND_7.
BAND_6 retained as legacy for compatibility via get_band_edges("6").
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
    risk_hint: str = ""     # diagnostic risk label


# ── Standard 6-band definition (legacy / compatibility) ──
BAND_6: ClassVar[dict[str, FrequencyBand]] = {
    "sub":      FrequencyBand("sub",      "Sub",       20,   60,   "#4a0e4e", "rumble"),
    "bass":     FrequencyBand("bass",     "Bass",      60,  250,   "#6b2fa0", "mud"),
    "low_mid":  FrequencyBand("low_mid",  "Low-Mid",  250,  500,   "#3a7ca5", "boxiness"),
    "mid":      FrequencyBand("mid",      "Mid",      500, 2000,   "#2d9c6b", "nasal"),
    "presence": FrequencyBand("presence", "Presence", 2000, 5000,   "#c4a43e", "harshness"),
    "air":      FrequencyBand("air",      "Air",      8000,16000,   "#d4756b", "hiss"),
}

# ── Extended 7-band definition (v0.4 default, AEP-ACU-004) ──
BAND_7: ClassVar[dict[str, FrequencyBand]] = {
    "sub": BAND_6["sub"],
    "bass": BAND_6["bass"],
    "low_mid": BAND_6["low_mid"],
    "mid": BAND_6["mid"],
    "presence": BAND_6["presence"],
    "brilliance": FrequencyBand(
        "brilliance", "Brilliance", 5000, 8000, "#e8a87c",
        "sibilance / clarity gap — AI audio often shows excess energy in 5-8 kHz"
    ),
    "air": BAND_6["air"],
}

# ── Convenience: ordered lists ──
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

# ── Default: 7-band (AEP-ACU-004) ──
DEFAULT_BANDS: ClassVar[dict] = BAND_7
DEFAULT_EDGES: ClassVar[list] = BAND_7_EDGES
DEFAULT_NAMES: ClassVar[list] = BAND_7_NAMES
DEFAULT_DISPLAYS: ClassVar[list] = BAND_7_DISPLAYS
DEFAULT_COLORS: ClassVar[list] = BAND_7_COLORS


def get_band_edges(band_spec: str = "7") -> list[tuple[str, float, float]]:
    """Return ordered [(name, low_hz, high_hz), ...] for the given band spec.

    band_spec="7" (default since AEP-ACU-004): 7-band with Brilliance.
    band_spec="6": legacy 6-band compatibility.
    """
    if band_spec == "6":
        return list(BAND_6_EDGES)
    return list(BAND_7_EDGES)


def get_band(name: str, band_spec: str = "7") -> FrequencyBand | None:
    """Look up a single band by name. Default: 7-band map."""
    bands = BAND_6 if band_spec == "6" else BAND_7
    return bands.get(name)


def band_mask(freqs, low_hz: float, high_hz: float):
    """Convenience: boolean mask for numpy frequency array."""
    return (freqs >= low_hz) & (freqs <= high_hz)


def get_risk_hints(band_spec: str = "7") -> dict[str, str]:
    """Return {band_name: risk_hint} for diagnostic labelling."""
    bands = BAND_6 if band_spec == "6" else BAND_7
    return {b.name: b.risk_hint for b in bands.values() if b.risk_hint}
