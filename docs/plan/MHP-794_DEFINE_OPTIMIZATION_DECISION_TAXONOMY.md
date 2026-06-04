# MHP-794: Define Optimization Decision Taxonomy

**Status**: ready
**Direction**: ECHAIN-MOODIFY-DATA-LOOP-014 / NEM-MOODIFY-DATA-LOOP-PROBE-042 / Probe Plan-6A: Loop Boundary / P4 (Validation)
**Depends on**: MHP-793
**Protocol**: E-Chain 54 = Probe NEM-18 + Build NEM-18 + System NEM-18

## Goal

Convert raw metric signals into explicit software action types.

## Decision Taxonomy

| Signal | Action Type | Example |
|--------|-------------|---------|
| fatal runtime error | code fix | missing `daily_run.log` should create a reliability MHP |
| pseudo/MRS Open disagreement | scoring calibration | adjust pseudo weights or gate interpretation |
| over_dark penalty | preset/craft policy | block or down-rank preset for a sample class |
| repeated preset win | selector policy | promote preset for a sample class |
| missing report artifact | report pipeline fix | add writer or artifact manifest check |
| unclear morning review | operator workflow fix | improve brief or gate explanation |

## Expected Output

`reports/echain_moodify_data_loop_014/{RUN_ID}/optimization_decision_taxonomy.md`

## Acceptance Criteria

- Every important signal maps to exactly one primary action type.
- The taxonomy distinguishes code fixes from configuration changes and review tasks.
