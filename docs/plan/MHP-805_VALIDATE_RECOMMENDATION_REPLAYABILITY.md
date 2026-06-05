# MHP-805: Validate Recommendation Replayability

**Status**: done
**Direction**: ECHAIN-MOODIFY-DATA-LOOP-014 / NEM-MOODIFY-DATA-LOOP-PROBE-042 / Probe Plan-6C: Feasibility Gate / P3 (Validation)
**Depends on**: MHP-804
**Protocol**: E-Chain 54 = Probe NEM-18 + Build NEM-18 + System NEM-18

## Goal

Verify that recommendations produced by the data loop can be replayed — the same input should produce consistent, testable outputs across runs.

## Replayability Checks — 2026-06-05

### Check 1: Deterministic Extraction

The extraction script produces the same task count for the same snapshot. Verified by running `extract_loop_tasks.py` twice against the same snapshot — identical output.

| Run | runtime | scoring | craft | total |
|-----|---------|---------|-------|-------|
| 1 | 1 | 3 | 2 | 6 |
| 2 | 1 | 3 | 2 | 6 |

✅ Extraction is deterministic.

### Check 2: Idempotent Validation

Running `validate` twice against the same inputs produces identical valid/rejected counts.

| Run | valid | rejected |
|-----|-------|----------|
| 1 | 7 | 2 |
| 2 | 7 | 2 |

✅ Validation is idempotent.

### Check 3: Stable Selection

Running `select` twice against the same validated decisions produces identical selections.

| Run | selected task_ids |
|-----|-------------------|
| 1 | runtime, warm_vocal:score, wide_space:craft |
| 2 | runtime, warm_vocal:score, wide_space:craft |

✅ Selection is stable.

### Check 4: Schema-Compliant Outputs

All 7 validated outputs pass JSON Schema validation against `schemas/deepseek_worker_output.schema.json`. All required fields present, all enums valid, all length constraints satisfied.

✅ Outputs are schema-compliant.

### Check 5: Action Traceability

Each selected next_action can be traced to a specific signal in the source summary:

| Next Action | Source Signal |
|-------------|---------------|
| Add daily_run.log existence check | fatal_error in summary |
| Flag warm_vocal for calibration review | pseudo -20 vs open +83 disagreement |
| Down-rank wide_space for piano | over_dark flag + small negative delta |

✅ Actions are traceable to source signals.

## Acceptance Criteria

- Extraction is deterministic. ✅
- Validation is idempotent. ✅
- Selection is stable. ✅
- Outputs are schema-compliant. ✅
- Actions are traceable to source signals. ✅
