# MHP-803: Define Data Loop SLO

**Status**: done
**Direction**: ECHAIN-MOODIFY-DATA-LOOP-014 / NEM-MOODIFY-DATA-LOOP-PROBE-042 / Probe Plan-6C: Feasibility Gate / P1 (Execution)
**Depends on**: MHP-802
**Protocol**: E-Chain 54 = Probe NEM-18 + Build NEM-18 + System NEM-18

## Goal

Define Service Level Objectives for each of the four data loops so the Probe phase has a measurable acceptance threshold.

## SLO Definitions

### Loop A: Runtime Reliability

| Metric | Target | Measurement |
|--------|--------|-------------|
| Task success rate | ≥ 95% | success / (success + failed) |
| Fatal error rate | ≤ 1 per run | count of fatal_error in summary |
| Missing artifact rate | ≤ 1 per 10 tasks | count of missing artifacts |
| Recovery coverage | ≥ 80% of fatal errors have recovery path | manual classification |

### Loop B: Scoring Calibration

| Metric | Target | Measurement |
|--------|--------|-------------|
| Score direction agreement | ≥ 85% | 1 - disagreement_count / task_count |
| Calibration severity false-positive rate | ≤ 20% | human review of high-severity flags |
| Per-loop action specificity | 100% of actions are executable | regex check of next_action |

### Loop C: Craft/Preset Selection

| Metric | Target | Measurement |
|--------|--------|-------------|
| Penalty precision | ≥ 80% of flags indicate real quality issue | human review |
| Preset verdict specificity | 100% of verdicts name one preset + one action | regex check |
| Action coverage | ≥ 1 action per flagged preset | count |

### Loop D: Operator Report

| Metric | Target | Measurement |
|--------|--------|-------------|
| Morning decision accuracy | ≥ 90% agreement with human operator | comparison over 5 nights |
| Next-MHP clarity | 100% of next_mhp fields are valid MHP IDs | schema validation |
| Artifact completeness | all required artifacts present | checklist |

## Gate Thresholds

A loop passes feasibility if it meets ≥ 2 of its 3 SLOs. The Probe as a whole passes if ≥ 3 of 4 loops pass.

## Acceptance Criteria

- Each loop has at least 2 measurable SLOs.
- Each SLO has a numeric target.
- Gate thresholds are explicit.
