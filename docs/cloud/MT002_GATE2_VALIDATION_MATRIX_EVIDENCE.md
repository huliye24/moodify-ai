# MT-002 Gate 2 Validation Matrix Evidence

Generated: 2026-06-03 UTC

## Result

- Gate: MT-002 Gate 2, executable validation matrix
- Run ID: `mt002_validation_matrix_gate2_20260603`
- Source records: `reports/mt002_mrs_baseline/mt002_mrs_baseline_gate3_20260603/mrs_score_records.jsonl`
- Source manifest: `outputs/mt001_gate3_real_ai/mt001_gate3_real_ai_20260603/manifest.csv`
- MRS version: `mrs_open_v031`
- Runnable tests: `9`
- PASS / HOLD / FAIL: `7` / `2` / `0`
- Validation decision: `EXPERIMENTAL`
- Gate 2 execution status: `PASS` for runnable matrix, `EXPERIMENTAL` for version adoption

## Matrix

| Test | Status | Notes |
|---|---|---|
| monotonicity | `PASS` | MRS ordering follows D_real ordering within rounding tolerance |
| scale_validation | `PASS` | baseline median remains near the 1000 reference band |
| no_ceiling | `PASS` | open scale produces scores above the 1000 baseline and has no 0-100 cap |
| v02_v031_correlation | `HOLD` | v0.2/pseudo scores do not yet validate MRS Open ranking |
| bad_sample_suppression | `PASS` | bottom-decile records remain below median and include penalty signal |
| improvement_reward | `PASS` | processed outputs receive positive median reward when D_real improves |
| loudness_cheat_resistance | `HOLD` | current batch has no loudness-cheat positive controls |
| stability | `PASS` | same input sample keeps stable before-score across presets |
| hq_damage_sensitivity | `PASS` | high-quality samples can receive negative deltas after processing |

## HOLD Items

- `v02_v031_correlation`: v0.2/pseudo scores do not yet validate MRS Open ranking
- `loudness_cheat_resistance`: current batch has no loudness-cheat positive controls

These HOLD items block Gate 5 adoption, but they do not block Gate 2's requirement that at least 8 validation tests are runnable and report PASS/HOLD/FAIL.

## Evidence Paths

- Validation JSON: `reports/mt002_mrs_validation/mt002_validation_matrix_gate2_20260603/validation_result.json`
- Validation Markdown: `reports/mt002_mrs_validation/mt002_validation_matrix_gate2_20260603/validation_result.md`
- Baseline evidence: `docs/cloud/MT002_MRS_BASELINE_EVIDENCE.md`

The validation report directory is intentionally ignored by git as runtime evidence. This Markdown file is the tracked evidence summary.

## Command

```bash
cd /home/ubuntu/moodify-mainline
.venv/bin/python scripts/mt002_validate_mrs_matrix.py \
  --records reports/mt002_mrs_baseline/mt002_mrs_baseline_gate3_20260603/mrs_score_records.jsonl \
  --manifest outputs/mt001_gate3_real_ai/mt001_gate3_real_ai_20260603/manifest.csv \
  --run-id mt002_validation_matrix_gate2_20260603 \
  --output-dir reports/mt002_mrs_validation \
  --min-runnable-tests 8
```

## Gate Meaning

This verifies that MT-002 has an executable validation matrix with at least 8 runnable checks. The current MRS version remains `EXPERIMENTAL` because two validation dimensions need dedicated controls before adoption.
