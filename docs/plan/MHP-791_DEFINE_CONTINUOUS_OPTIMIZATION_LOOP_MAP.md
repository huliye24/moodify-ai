# MHP-791: Define Continuous Optimization Loop Map

**Status**: ready
**Direction**: ECHAIN-MOODIFY-DATA-LOOP-014 / NEM-MOODIFY-DATA-LOOP-PROBE-042 / Probe Plan-6A: Loop Boundary / P1 (Execution)
**Protocol**: E-Chain 54 = Probe NEM-18 + Build NEM-18 + System NEM-18

## Goal

Define the software-improvement loops that use nightly data as input.

## Required Loops

1. Runtime Reliability Loop: summary + events + queue -> failure task -> runtime fix -> rerun.
2. Scoring Calibration Loop: pseudo MRS + MRS Open + human review -> calibration proposal -> rerun.
3. Craft/Preset Selection Loop: sample + preset + score deltas + penalty flags -> selector policy -> rerun.
4. Operator Report Loop: evidence bundle + morning brief -> PASS/HOLD/REWORK -> next MHP -> rerun.

## Expected Output

`reports/echain_moodify_data_loop_014/{RUN_ID}/optimization_loop_map.md`

## Acceptance Criteria

- Each loop has inputs, decision rule, software action, and verification metric.
- Each loop can run from artifacts already produced by Moodify.
