# MHP-800: Generate Craft/Preset Task JSONL

**Status**: done
**Direction**: ECHAIN-MOODIFY-DATA-LOOP-014 / NEM-MOODIFY-DATA-LOOP-PROBE-042 / Probe Plan-6B: DeepSeek Micro Tasks / P4 (Validation)
**Depends on**: MHP-797
**Protocol**: E-Chain 54 = Probe NEM-18 + Build NEM-18 + System NEM-18

## Goal

Create one DeepSeek task for each preset result that needs review.

## Input

`last_night_metric_snapshot.json`

Task fields:

- `task_id`
- `sample_id`
- `preset`
- `delta_mrs_open_v031`
- `mrs_open_flags`

## Output

Append one JSONL line when `mrs_open_flags` is not empty.

## Acceptance Criteria

- Each line contains one sample and one preset.
- The model is asked for one craft/preset action only.
- The output does not update craft memory directly.
