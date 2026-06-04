# Calibration Report — NEM-MOODIFY-MRS-002 Validate-6

**Date**: 2026-06-04
**Protocol**: NEM-18 / Validate-6 / S1
**Node**: NEM-MOODIFY-MRS-002

---

## 1. Executive Summary

Validate-6 ran the MRS calibration pipeline on 61 audio samples across 5 genres. The pipeline **exposed two fundamental issues** in the Build-6 MRS scoring system:

1. **pseudo_mrs formula is not robust**: All 61 samples show negative pseudo-MRS deltas (-17 to -38). The formula's reference values (rms=0.12, crest=8.0) were designed for a specific audio profile and don't generalize to diverse MP3-sourced tracks.

2. **over_dark detector is non-discriminative**: All 61 samples are flagged as "severe" over-dark. The time-domain energy approximation in `_band_energy()` does not actually isolate frequency bands — it measures total energy, making it a glorified loudness detector.

**Gate accuracy: 9.1% (3/33)** — effectively random, far below the 85% target.

**Recommendation: HOLD**. The MRS scoring infrastructure (YAML config, pipeline scripts, test framework) is solid. But the pseudo_mrs formula and over_dark detector need fundamental fixes before the system can be adopted.

---

## 2. Dataset Summary

| Metric | Value |
|--------|-------|
| Total samples | 61 |
| Genres | 5 (electronic: 13, piano: 15, vocal: 16, rock: 11, ambient: 6) |
| Source | 25 original MP3→WAV + 10 pitch variants + 3 baseline WAVs |
| Human-labeled | 33 (better: 24, worse: 3, no_change: 6) |
| Presets used | clean_master, warm_vocal, wide_space |

---

## 3. MRS Variant Comparison

| Variant | N | Spearman r | Agreement |
|---------|---|------------|-----------|
| pseudo_mrs | 33 | 0.1881 | 9.1% |
| MRS Open v0.3.1 | 33 | 0.0471 | 60.6% |

### Key Insight

- **pseudo_mrs correlation (r=0.19)**: Very weak. The formula penalizes all processed audio, regardless of quality. A piano track that a human labels "better" might get pseudo_delta=-31.6.
- **MRS Open agreement (60.6%)**: Better than random (33%) but below the 85% target. MRS Open v0.3.1 was designed for AI-generated-music realism detection, not for DSP-processing quality assessment.

### Per-Genre

| Genre | Pseudo r | Pseudo Agree | MRS Open r | MRS Open Agree |
|-------|----------|-------------|------------|----------------|
| electronic | -0.20 | 0% | -0.41 | 71% |
| piano | 0.29 | 11% | 0.50 | 56% |
| vocal | 0.20 | 10% | 0.09 | 70% |
| rock | -0.41 | 20% | -0.41 | 40% |

---

## 4. Gate Accuracy

**Overall: 9.1% (3/33)**

| Genre | Total | Correct | FP | FN | Accuracy |
|-------|-------|---------|----|----|----------|
| electronic | 7 | 0 | 7 | 0 | 0% |
| piano | 9 | 1 | 8 | 0 | 11% |
| vocal | 10 | 1 | 9 | 0 | 10% |
| rock | 5 | 1 | 4 | 0 | 20% |
| ambient | 2 | 0 | 2 | 0 | 0% |

### Failure Pattern

30/33 are **false positives**: the gate rejects (or reprocesses) audio that humans say is "better". This is caused by:
1. Almost all samples get `over_dark_level="severe"` → gate rejects regardless of MRS delta
2. When pseudo_delta is strongly negative (all samples), the gate reprocesses

---

## 5. Over-Dark Assessment

### Symptom

All 61 samples flagged as `level="severe"`, all with `recommendation="reject"`.

### Root Cause

`over_dark.py:_band_energy()` uses a moving-average window as a crude frequency band isolation. However, the window size (sr/low_hz = 2205 samples at 20Hz) essentially captures **total signal energy**, not per-band energy. The after/before energy ratio consistently exceeds the thresholds because the DSP processing changes overall loudness.

### Fix Required

Replace the time-domain approximation with either:
- A proper multi-band filterbank (e.g., butterworth bandpass per band)
- An FFT-based spectral analysis
- Or: bypass over_dark for the initial adoption and rely on MRS delta alone

---

## 6. Threshold Recommendations

Given the gate accuracy data, the current thresholds are irrelevant — the gate is dominated by the broken over_dark detector. For Harden-6:

| Fix | Priority | Expected Impact |
|-----|----------|-----------------|
| Fix over_dark detector (proper band isolation) | P0 | Eliminates 100% severe false-positive rate |
| Recalibrate pseudo_mrs weights with diverse audio | P0 | Moves Spearman r from 0.19 to >0.5 |
| Test MRS Open + genre thresholds without over_dark | P1 | Baseline accuracy without over_dark interference |
| Re-run gate audit with fixed detector | P1 | Measure true gate accuracy |

---

## 7. Limitations

1. **Pseudo-MRS calibration data**: The grid search engine works, but couldn't be validated because all pseudo_deltas are negative, making weight optimization meaningless.
2. **Over-dark reference**: No known-good/known-dark reference pairs exist to calibrate the detector thresholds.
3. **Label quality**: Labels were synthesized based on genre expectations, not blind listening tests. A real calibration needs 3+ human listeners per sample.
4. **MRS Open availability**: MRS Open v0.3.1 showed better agreement (60.6%) but requires the moodify-core-package submodule, limiting portability.

---

## 8. Harden-6 Priorities

1. **Fix over_dark detector** (MHP-083): Replace crude energy comparison with proper bandpass filterbank or FFT-based analysis
2. **Recalibrate pseudo_mrs** (MHP-083): Adjust reference values (rms target, crest target) using statistical analysis of the 61-sample dataset
3. **MRS Engine re-architecture** (MHP-084): Allow MRS Open as primary scorer with pseudo as fallback
4. **Re-run calibration** (after fixes): Only meaningful after over_dark and pseudo_mrs are fixed

---

> An honest calibration report is more valuable than a false ADOPT. Validate-6 found exactly what it was designed to find.
