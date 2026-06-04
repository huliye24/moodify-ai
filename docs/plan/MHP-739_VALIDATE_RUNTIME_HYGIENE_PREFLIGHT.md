# MHP-739: Validate Runtime Hygiene Preflight

**Status**: ready
**Direction**: ECHAIN-MOODIFY-NIGHT-RESULT-013 / NEM-MOODIFY-NIGHT-RESULT-PROBE-039 / Probe Plan-6A: Night Result Boundary / P3 (Validation)
**Depends on**: MHP-738
**Protocol**: E-Chain 54 = Probe NEM-18 + Build NEM-18 + System NEM-18

## Goal

Validate that tonight's run starts from a known state and does not accidentally commit generated runtime assets.

## Commands

```bash
git status --short --branch
git rev-parse HEAD
python3 -m moodify_runtime.cli runtime-health --json
python3 -m moodify_runtime.cli tidal-state
```

## Expected Output

```text
reports/echain_moodify_night_result_013/{RUN_ID}/git_status.txt
reports/echain_moodify_night_result_013/{RUN_ID}/git_head.txt
reports/echain_moodify_night_result_013/{RUN_ID}/runtime_health.json
reports/echain_moodify_night_result_013/{RUN_ID}/tidal_state.txt
```

## Acceptance Criteria

- Any dirty working tree files are listed explicitly.
- Runtime health exits successfully or a HOLD reason is documented.
- Tidal state exits successfully or a HOLD reason is documented.
- Generated outputs remain in reports/outputs/data paths and are not staged by default.
