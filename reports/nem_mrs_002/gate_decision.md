# Gate Decision — NEM-MOODIFY-MRS-002 Validate-6

**Date**: 2026-06-04
**Protocol**: NEM-18 / Validate-6 / N1
**Decision**: **HOLD** ⚠️

---

## Decision Rationale

Validate-6 tested the MRS scoring system on 61 real audio samples with 33 human labels. The system is not production-ready.

### Evidence

| Criterion | Target | Actual | Pass? |
|-----------|--------|--------|-------|
| Gate accuracy overall | ≥85% | 9.1% | ❌ |
| Per-genre accuracy | ≥70% | 0-20% | ❌ |
| MRS correlation with human labels | r ≥ 0.7 | r = 0.19 | ❌ |
| Over-dark discrimination | 3 distinct levels | 100% "severe" | ❌ |
| Pseudo-MRS delta sign | ≥50% positive | 0% positive | ❌ |

### What Went Wrong

Two Build-6 components failed validation:

1. **`over_dark.py:_band_energy()`** uses a time-domain moving average that measures total energy, not band-specific energy. This makes the detector flag ALL audio as "severe" regardless of actual spectral changes.

2. **`metrics.py:pseudo_mrs()`** uses reference values (rms=0.12, crest=8.0, peak=0.98) calibrated for a narrow audio profile. MP3-sourced tracks have different characteristics, causing all deltas to be negative.

### What Worked

3. **MRS Open v0.3.1**: 60.6% agreement with human labels — not production-ready, but significantly better than pseudo_mrs (9.1%) and better than random (33%).
4. **Pipeline infrastructure**: The calibration pipeline, dataset builder, analysis scripts all work correctly.
5. **Genre threshold YAML**: Configuration system is solid; just can't be validated until the scoring functions are fixed.
6. **Test framework**: 135 tests pass, including 16 gate threshold tests.

### Why Not REBUILD?

The infrastructure and architecture are correct:
- `configs/mrs_thresholds.yaml` — genre dispatch works
- `scripts/calibrate_pseudo_mrs.py` — grid search engine works
- `scripts/run_calibration_pipeline.py` — pipeline runs end-to-end
- `test_mrs_gate.py` — 16 tests cover all gate paths

The problems are in two specific signal-processing functions (`pseudo_mrs` reference values and `over_dark` band isolation). These are fixable without architectural changes.

---

## Re-evaluation Conditions

| Condition | Current | Target |
|-----------|---------|--------|
| over_dark produces ≥2 distinct levels on real data | 1 (only "severe") | ≥2 (none + mild or mild + severe) |
| pseudo_mrs delta sign matches human label sign | 9% | ≥50% |
| Gate accuracy (without over_dark) | — | ≥60% |
| MRS Open per-genre agreement | 40-71% | ≥70% in ≥3 genres |

---

## Harden-6 Entry

Proceed to Harden-6 with specific fix list:
- **P0**: Fix over_dark band isolation (proper filterbank or FFT)
- **P0**: Recalibrate pseudo_mrs reference values on diverse dataset
- **P1**: Test gate accuracy with MRS Open as primary + over_dark disabled
- **P1**: Re-run 61-sample pipeline after fixes

If these fixes bring gate accuracy above 60%, proceed to ADOPT. If not, fork into separate pseudo_mrs and MRS Open tracks.

---

**Next Phase**: Harden-6 (MHP-083 → 088)
**Target Re-evaluation**: After MHP-083 (Fix Calibration Issues)

> A HOLD is not a failure. It is the gate doing its job — preventing unvalidated code from reaching production.
