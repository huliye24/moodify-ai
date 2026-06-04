# MHP-741: Write Tonight Runbook

**Status**: ready
**Direction**: ECHAIN-MOODIFY-NIGHT-RESULT-013 / NEM-MOODIFY-NIGHT-RESULT-PROBE-039 / Probe Plan-6A: Night Result Boundary / P5 (Systemization)
**Depends on**: MHP-740
**Protocol**: E-Chain 54 = Probe NEM-18 + Build NEM-18 + System NEM-18

## Goal

Provide a copy-pasteable command sequence for tonight's evidence run.

## Runbook

```bash
cd /home/ubuntu/moodify-mainline
RUN_ID=night_result_013_$(date -u +%Y%m%d_%H%M%S)
OUT=reports/echain_moodify_night_result_013/$RUN_ID
mkdir -p "$OUT"

printf '# Night Result Question\n\nCan Moodify produce a coherent one-night evidence bundle from runtime health, tidal state, intelligence, operations, and tests?\n' > "$OUT/night_result_question.md"

git status --short --branch > "$OUT/git_status.txt"
git rev-parse HEAD > "$OUT/git_head.txt"
python3 -m moodify_runtime.cli runtime-health --json > "$OUT/runtime_health.json"
python3 -m moodify_runtime.cli tidal-state > "$OUT/tidal_state.txt"
python3 -m moodify_runtime.cli tidal-intel --run-id "$RUN_ID" > "$OUT/tidal_intel.txt"
python3 -m moodify_runtime.cli tidal-intel-brief --run-id "$RUN_ID" > "$OUT/morning_brief.md"
python3 -m moodify_runtime.cli tidal-ops --run-id "$RUN_ID" > "$OUT/tidal_ops.txt"
python3 -m pytest moodify_runtime/tests/ -q > "$OUT/runtime_tests.txt"
python3 -m pytest moodify-core-package/tests -q > "$OUT/core_tests.txt"

find "$OUT" -maxdepth 1 -type f -printf '%f\n' | sort > "$OUT/artifact_index.txt"
```

## Expected Output

`reports/echain_moodify_night_result_013/{RUN_ID}/artifact_index.txt`

## Acceptance Criteria

- The runbook creates a unique evidence directory.
- The artifact index lists all expected outputs.
- Failures are preserved in their output files and become HOLD evidence.
