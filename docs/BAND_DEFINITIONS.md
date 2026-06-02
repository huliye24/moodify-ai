# Band Definitions

Unified frequency band boundaries used across Moodify modules.

Source of truth: `moodify/bands.py`

## Standard 6-Band (v01 Mainline)

| Band | Low (Hz) | High (Hz) | Color |
|------|----------|-----------|-------|
| Sub | 20 | 60 | #4a0e4e |
| Bass | 60 | 250 | #6b2fa0 |
| Low-Mid | 250 | 500 | #3a7ca5 |
| Mid | 500 | 2,000 | #2d9c6b |
| Presence | 2,000 | 5,000 | #c4a43e |
| Air | 8,000 | 16,000 | #d4756b |

Note: There is an intentional gap between Presence (5 kHz) and Air (8 kHz). This gap avoids over-weighting the sibilance region (5-8 kHz) in spectrum analysis.

## Extended 7-Band (MRS / Future)

Same as 6-band, plus:

| Band | Low (Hz) | High (Hz) | Color |
|------|----------|-----------|-------|
| Brilliance | 5,000 | 8,000 | #e8a87c |

The 7-band definition fills the gap between Presence and Air, useful for high-resolution spectrum analysis in MRS (Moodify Reality Score) computations.

## Usage

```python
from moodify.bands import (
    BAND_6, BAND_6_EDGES, BAND_6_NAMES, BAND_6_COLORS,
    BAND_7, BAND_7_EDGES, BAND_7_NAMES,
    get_band_edges, get_band, band_mask,
)

# Iterate 6-band edges
for name, low, high in BAND_6_EDGES:
    print(f"{name}: {low}-{high} Hz")

# Look up a specific band
band = get_band("presence")  # FrequencyBand object

# Create frequency mask for numpy arrays
mask = band_mask(freqs, band.low_hz, band.high_hz)
```

## Modules Using These Bands

| Module | Band Spec | Usage |
|--------|-----------|-------|
| `v01_analyzer.py` | BAND_6 | Spectrum analysis + PNG |
| `reality_metrics.py` | BAND_6 | MRS spectrum features |
| `v01_inspector.py` | BAND_6 | Before/after comparison |
| `v01_types.py` | BAND_6 | AudioMetrics fields |
