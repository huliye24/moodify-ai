# MHP-738: Inventory Runnable Surfaces

**Status**: ready
**Direction**: ECHAIN-MOODIFY-NIGHT-RESULT-013 / NEM-MOODIFY-NIGHT-RESULT-PROBE-039 / Probe Plan-6A: Night Result Boundary / P2 (Execution)
**Depends on**: MHP-737
**Protocol**: E-Chain 54 = Probe NEM-18 + Build NEM-18 + System NEM-18

## Goal

Inventory the surfaces that can be run tonight without adding new feature code.

## Runnable Surface Set

```bash
python3 -m moodify_runtime.cli runtime-health --json
python3 -m moodify_runtime.cli tidal-state
python3 -m moodify_runtime.cli tidal-intel --run-id "$RUN_ID"
python3 -m moodify_runtime.cli tidal-intel-brief --run-id "$RUN_ID"
python3 -m moodify_runtime.cli tidal-ops --run-id "$RUN_ID"
python3 -m pytest moodify_runtime/tests/ -q
python3 -m pytest moodify-core-package/tests -q
```

## Expected Output

`reports/echain_moodify_night_result_013/{RUN_ID}/runnable_surfaces.md`

## Acceptance Criteria

- Each command is classified as health, intelligence, operations, or regression.
- Each command has an expected output file.
- Known long-running or generated-asset risks are noted.
