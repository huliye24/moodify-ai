# MHP-799: Generate Scoring Calibration Task JSONL

**Status**: planned
**Direction**: ECHAIN-MOODIFY-DATA-LOOP-014 / NEM-MOODIFY-DATA-LOOP-PROBE-042 / Probe Plan-6B: DeepSeek Micro Tasks / P3 (Validation)
**Depends on**: MHP-797
**Protocol**: E-Chain 54 = Probe NEM-18 + Build NEM-18 + System NEM-18

## Goal

Create one DeepSeek task for each scoring direction disagreement.

## Input

`last_night_metric_snapshot.json`

Task fields:

- `task_id`
- `sample_id`
- `preset`
- `pseudo_delta_mrs`
- `delta_mrs_open_v031`
- `score_direction_disagreement`

## Output

Append one JSONL line per task where `score_direction_disagreement` is `true`.

## Acceptance Criteria

- Each line describes one task only.
- The model is asked for one calibration action only.
- No genre-wide or project-wide inference is required.
