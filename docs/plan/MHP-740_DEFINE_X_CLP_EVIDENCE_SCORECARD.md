# MHP-740: Define X-CLP Evidence Scorecard

**Status**: ready
**Direction**: ECHAIN-MOODIFY-NIGHT-RESULT-013 / NEM-MOODIFY-NIGHT-RESULT-PROBE-039 / Probe Plan-6A: Night Result Boundary / P4 (Validation)
**Depends on**: MHP-739
**Protocol**: E-Chain 54 = Probe NEM-18 + Build NEM-18 + System NEM-18

## Goal

Define a simple X-CLP scorecard for tonight's result.

## Scorecard

| Dimension | 0 | 1 | 2 |
|-----------|---|---|---|
| Executability | command missing | command runs with manual fixes | command runs from runbook |
| Continuity | no run id | run id exists | run id links all artifacts |
| Loop Closure | no decision | partial decision | PASS/HOLD/REWORK plus next MHP |
| Product Evidence | raw logs only | logs plus summary | morning review brief |
| Risk Control | artifacts uncontrolled | risks listed | cleanup/staging rule documented |

Maximum score: 10.

## Expected Output

`reports/echain_moodify_night_result_013/{RUN_ID}/x_clp_scorecard.md`

## Acceptance Criteria

- The scorecard is filled after tonight's run.
- A score below 7 forces HOLD.
- A score of 7 or higher allows Gate 1 ADOPT if tests also pass.
