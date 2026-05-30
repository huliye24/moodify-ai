# PROJECT SNAPSHOT — Moodify v0.1.0-alpha.2

> First local experience-loop baseline.  
> Target audience: Claude / ChatGPT / future agents needing rapid context recovery.

## 1. Current Identity

Moodify is an AI music post-processing and emotional wave engineering system.

## 2. Version

- **Version**: v0.1.0-alpha.2
- **Previous**: v0.1.0-alpha.1
- **Meaning**: first version with complete local experience loop

## 3. What alpha.2 Adds vs alpha.1

| alpha.1 | alpha.2 |
|---------|---------|
| v01 pipeline + CLI + API | same, plus toolchain |
| 20 v01 tests | same |
| no calibration tool | `v01_calibrate_presets.py` |
| no inspector | `v01_inspector.py` + RMS matching |
| no treatment records | `v01_create_treatment_record.py` |
| no feedback | `v01_update_treatment_feedback.py` |
| no aggregation | `v01_aggregate_treatment_records.py` |

## 4. Core v01 Mainline (unchanged)

```
v01_types.py          — AudioMetrics / DiagnosisReport / ProcessResult
v01_presets.py        — 3 presets × 15 DSP params (MHP-006-A tuned)
v01_analyzer.py       — FFT spectrum → AudioMetrics + PNG
v01_diagnostics.py    — rule-based DiagnosisReport
v01_exporter.py       — 16-bit WAV + peak clamp
v01_pipeline.py       — import → analyze → diagnose → process → export
```

pedalboard_chain.py Limiter ceiling: -1.0 dBFS (MHP-006-C).

## 5. Local Toolchain

```text
v01_pipeline                      = hand        (process audio)
v01_inspector                     = eye         (observe before/after)
v01_calibrate_presets             = ruler       (measure preset quality)
v01_create_treatment_record       = memory      (archive one run)
v01_aggregate_treatment_records   = ledger      (summarize all runs)
v01_update_treatment_feedback     = experience  (write human judgement)
```

## 6. Data Assets (local, gitignored)

```
calibration_reports/     — before/after preset quality data
inspector_reports/       — per-case visualizations + metrics
listening_test/          — A/B comparison WAVs
treatment_records/       — structured processing memory
```

## 7. Test Status

```
pytest -m v01  → 20 passed
pytest         → 104 passed
```

## 8. Architecture Rules

- Do not delete legacy system
- Do not reconnect WorkflowOrchestrator to v0.1.0 /process
- Do not add new presets before more treatment records and feedback exist
- Do not start cloud / database / model training in v0.1.x
- Do not build Adaptive Preset on only 3 records

## 9. Current Feedback State

```
warm_vocal:    completed=1, better_yes=1
clean_master:  pending
wide_space:    pending
```

## 10. Known Issues

- `tests/baseline/run_baseline.py` references nonexistent `moodify.llm.offline_fallback`
- `v01_analyzer.py:166` emits tight_layout UserWarning (cosmetic)
- CLI/API smoke tests are manual, not in pytest

## 11. Next Steps

```
MHP-019  Feedback-aware Aggregator Enhancement
MHP-020  More Treatment Records (wider audio variety)
MHP-021  Rule-based Adaptive Preset Prototype
```

Adaptive Preset should not be built until at least 10+ records with feedback exist.
