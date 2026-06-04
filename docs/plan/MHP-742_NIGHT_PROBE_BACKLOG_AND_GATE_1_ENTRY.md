# MHP-742: Night Probe Backlog and Gate 1 Entry

**Status**: ready
**Direction**: ECHAIN-MOODIFY-NIGHT-RESULT-013 / NEM-MOODIFY-NIGHT-RESULT-PROBE-039 / Probe Plan-6A: Night Result Boundary / P6 (Next Entry)
**Depends on**: MHP-741
**Protocol**: E-Chain 54 = Probe NEM-18 + Build NEM-18 + System NEM-18

## Goal

Convert tonight's run into a Gate 1 entry decision and backlog.

## Expected Output

`reports/echain_moodify_night_result_013/{RUN_ID}/gate1_entry.md`

## Gate 1 Decision Rules

- **ADOPT**: runtime/core tests pass, runtime health passes, tidal intelligence and ops produce outputs, X-CLP score >= 7.
- **HOLD**: any test command fails, health fails, or X-CLP score is 4-6.
- **DROP**: the runbook cannot be executed without reconstructing missing context.

## Next Backlog

If Gate 1 is ADOPT, start:

- MHP-743 Run Health and Test Snapshot
- MHP-744 Run Tidal Intelligence Snapshot
- MHP-745 Run Tidal Operations Snapshot

If Gate 1 is HOLD, write the blocking command and one concrete fix task before rerunning.

## Acceptance Criteria

- `gate1_entry.md` exists.
- The decision is one of ADOPT, HOLD, or DROP.
- The next MHP is named explicitly.
