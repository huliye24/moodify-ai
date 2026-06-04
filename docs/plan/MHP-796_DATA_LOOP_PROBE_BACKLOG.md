# MHP-796: Data Loop Probe Backlog

**Status**: ready
**Direction**: ECHAIN-MOODIFY-DATA-LOOP-014 / NEM-MOODIFY-DATA-LOOP-PROBE-042 / Probe Plan-6A: Loop Boundary / P6 (Next Entry)
**Depends on**: MHP-795
**Protocol**: E-Chain 54 = Probe NEM-18 + Build NEM-18 + System NEM-18

## Goal

Define the next metric probes after the first data-loop extraction.

## Backlog

1. MHP-797 Runtime Reliability Scorecard
   - Count fatal errors, missing logs, task failures, retries, and phase failures.
2. MHP-798 MRS Disagreement Matrix
   - Compare pseudo delta sign vs MRS Open delta sign by sample and preset.
3. MHP-799 Preset Outcome Table
   - Rank presets by MRS Open delta and penalty flags per sample class.
4. MHP-800 Penalty Flag Review Queue
   - Create review queue for `over_dark` and future penalty flags.
5. MHP-801 Metric Probe Report
   - Convert metric tables into recommended software actions.
6. MHP-802 Metric Probe Gate Decision
   - Decide ADOPT/HOLD/DROP for build investment.

## Acceptance Criteria

- Backlog names the next executable MHP.
- Each backlog item names a metric, source artifact, and expected decision.
