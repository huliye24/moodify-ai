# MHP-793: Extract Last-Night Metrics Snapshot

**Status**: ready
**Direction**: ECHAIN-MOODIFY-DATA-LOOP-014 / NEM-MOODIFY-DATA-LOOP-PROBE-042 / Probe Plan-6A: Loop Boundary / P3 (Validation)
**Depends on**: MHP-792
**Protocol**: E-Chain 54 = Probe NEM-18 + Build NEM-18 + System NEM-18

## Goal

Extract a compact metric snapshot from the latest useful run.

## Current Source

```text
outputs/20260605_000141/summary.json
```

## Key Metrics

- selected tasks;
- success / failed count;
- fatal error;
- pseudo MRS delta;
- MRS Open delta;
- penalty flags;
- preset and sample identity.

## Expected Output

`reports/echain_moodify_data_loop_014/{RUN_ID}/last_night_metric_snapshot.json`

## Acceptance Criteria

- Snapshot contains one row per task.
- Snapshot preserves both pseudo and MRS Open deltas.
- Snapshot marks score-disagreement and penalty-flag cases for later review.
