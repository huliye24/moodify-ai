# Moodify QA — AI Music Quality Assurance

> Industrial-grade audio quality detection and compliance checking.

## Responsibilities

- **LUFS Analysis** — Loudness measurement for streaming, broadcast, and mastering compliance
- **Spectral Analysis** — Frequency balance, resonance detection, spectral irregularities
- **Dynamic Range Analysis** — DR measurement, crest factor, compression detection
- **True Peak Compliance** — ISP measurement per ITU-R BS.1770
- **MRS Scoring** — Moodify Reality Score for quality assessment
- **Defect Detection** — Clipping, noise, phase issues, stereo imbalance
- **Platform Compliance** — Spotify (-14 LUFS), Apple (-16 LUFS), YouTube (-14 LUFS), EBU R128

## Module Structure

```
products/qa/
├── analyzers/         # Analysis engines
├── standards/         # Platform & broadcast standards
├── scoring/           # QA-specific scoring
└── api/               # QA API routes
```

## Migration Source

| QA Module | Source (moodify-core-package) |
|-----------|------------------------------|
| `analyzers/lufs_analyzer.py` | `auditory/loudness.py` |
| `analyzers/spectral_analyzer.py` | `auditory/spectrogram.py` |
| `analyzers/dynamic_range.py` | `auditory/measurement_layers.py` |
| `analyzers/true_peak_checker.py` | `auditory/true_peak.py` |
| `analyzers/stereo_analyzer.py` | `auditory/stereo.py`, `icc.py` |
| `analyzers/defect_detector.py` | `diagnosis/defect_classifier.py` |
| `scoring/mrs_scorer.py` | `mrs/scoring.py` |
| `scoring/quality_gate.py` | `diagnosis/quality_gate.py` |
