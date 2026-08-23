# Moodify Intelligence Engine

> The shared AI auditory capability layer for all Moodify products.

## Overview

The Engine is the core of the Moodify Intelligence Platform. It provides the auditory intelligence that powers all product modules — QA, Master, Rating, and Supply.

## Modules

| Module | Responsibility |
|--------|---------------|
| `acoustic_analysis` | Acoustic measurement: LUFS, true peak, spectrum, stereo, dynamics |
| `audio_features` | Feature extraction: waveform, spectral, rhythm, timbre features |
| `music_understanding` | Musical semantics: structure, emotion, genre, instruments |
| `scoring_engine` | Scoring: MRS, quality scores, reference metrics, uncertainty |
| `recommendation_engine` | Matching: similarity, scene matching, preference, ranking |

## Design Principles

1. **Pure functions** — Engine takes audio input, returns analysis output. No side effects.
2. **No product logic** — Engine doesn't know about QA, Master, Rating, or Supply.
3. **Versioned outputs** — All results are versioned and reproducible.
4. **Uncertainty-aware** — Every score carries uncertainty bounds.
5. **Evidence-backed** — Every judgment produces evidence artifacts.

## Migration Status

This is a new directory structure. Modules will be progressively migrated from `moodify-core-package/src/moodify/`. See `docs/MOODIFY_ARCHITECTURE_V1.md` for the migration plan.

### Migration Map

| Engine Module | Source (moodify-core-package) |
|---------------|------------------------------|
| `acoustic_analysis` | `auditory/`, `fingerprint.py`, `icc.py` |
| `audio_features` | `v01_analyzer.py`, `audio_io.py` |
| `music_understanding` | `diagnosis/`, `knowledge/` |
| `scoring_engine` | `mrs/`, `evaluation/`, `reality_metrics.py` |
| `recommendation_engine` | `knowledge/emotion_targets.py` |

## Usage

```python
# Future API (after migration)
from engine.acoustic_analysis import analyze_loudness, analyze_spectrum
from engine.scoring_engine import compute_mrs
from engine.audio_features import extract_features
```
