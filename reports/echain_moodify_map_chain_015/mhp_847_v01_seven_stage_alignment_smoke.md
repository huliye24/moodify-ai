# MHP-847: v01 Seven-Stage Alignment Smoke — Seal Report

**Generated**: 2026-06-05
**Status**: sealed
**E-Chain**: ECHAIN-MOODIFY-MAP-CHAIN-015 / NEM-MOODIFY-MAP-PROBE-045 / Probe Plan-6A

## Smoke Results

### Test Suite

```text
PYTHONPATH=/home/ubuntu/moodify-mainline:/home/ubuntu/moodify-mainline/moodify-core-package/src \
  python3 -m pytest -q moodify-core-package/tests/test_v01_pipeline.py moodify-core-package/tests/test_api_v01.py

12 passed, 9 warnings in 4.31s
```

- 7 v01 pipeline tests: passed
- 5 API v01 tests: passed
- All warnings are cosmetic (`tight_layout` margins).

### CLI Smoke

```text
PYTHONPATH=... python3 -m moodify.cli v01-process \
  moodify-core-package/tests/baseline/test_audio/vocal_folk.wav \
  --preset auto --output-dir /tmp/moodify_v01_check

Exit: 0
Selected: clean_master
Health: good
Quality: pass
```

### Generated Artifacts

| Artifact | Path | Exists |
|----------|------|--------|
| Processed WAV | `/tmp/moodify_v01_check/vocal_folk_clean_master.wav` | yes |
| JSON Report | `/tmp/moodify_v01_check/vocal_folk_clean_master_report.json` | yes |
| PDF Report | `/tmp/moodify_v01_check/vocal_folk_clean_master_report.pdf` | yes |
| Before Spectrum | `/tmp/moodify_v01_check/vocal_folk_before_spectrum.png` | yes |
| After Spectrum | `/tmp/moodify_v01_check/vocal_folk_clean_master_after_spectrum.png` | yes |

### MAP Stage Verification

```text
workflow == ['S_scan', 'A_analyze', 'D_diagnose', 'P_process', 'V_validate', 'R_report', 'G_generate']: True
```

### ValidationResult Field Verification

| Field | Present |
|-------|---------|
| `mrs_version` = `mrs_proxy_v01` | yes |
| `mrs_before` | yes |
| `mrs_after` | yes |
| `mrs_delta` | yes |
| `damage_loss` | yes |
| `risk_flags` | yes |
| `passed` | yes |

## Acceptance Criteria Check

- [x] `workflow` equals the seven MAP stage names.
- [x] `validation_result` includes `mrs_before`, `mrs_after`, `mrs_delta`, `damage_loss`, `risk_flags`, and `passed`.
- [x] CLI smoke produces WAV, JSON, PDF, before chart, and after chart.
- [x] Existing v01 API smoke remains green (12/12 tests pass).

## Judge Notes

MHP-847 is sealed. All four acceptance criteria are met with recorded command output. No code changes were needed — the v01 pipeline already speaks the MAP seven-stage vocabulary.
