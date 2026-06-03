# MT-002 MRS Baseline Evidence

Generated: 2026-06-03 UTC

## Result

- Task: MT-002 MRS scoring baseline from MT-001 Gate 3 real AI batch
- Run ID: `mt002_mrs_baseline_gate3_20260603`
- Source manifest: `outputs/mt001_gate3_real_ai/mt001_gate3_real_ai_20260603/manifest.csv`
- MRS version: `mrs_open_v031`
- Records: `90/90` completed
- Failed: `0`
- Unique samples: `30`
- Score min / median / mean / max: `986.7` / `1041.75` / `1047.43` / `1146.7`
- Delta median / mean: `6.45` / `18.64`
- Decision: `PASS`

## Per Preset

| Preset | Count | Median MRS | Mean MRS | Median Delta | Mean Delta |
|---|---:|---:|---:|---:|---:|
| clean_master | 30 | 1038.40 | 1038.87 | 5.20 | 10.08 |
| warm_vocal | 30 | 1043.40 | 1052.87 | 10.65 | 24.08 |
| wide_space | 30 | 1043.60 | 1050.55 | 10.65 | 21.75 |

## Evidence Paths

- Score JSONL: `reports/mt002_mrs_baseline/mt002_mrs_baseline_gate3_20260603/mrs_score_records.jsonl`
- Score CSV: `reports/mt002_mrs_baseline/mt002_mrs_baseline_gate3_20260603/mrs_score_records.csv`
- Summary JSON: `reports/mt002_mrs_baseline/mt002_mrs_baseline_gate3_20260603/summary.json`
- Summary Markdown: `reports/mt002_mrs_baseline/mt002_mrs_baseline_gate3_20260603/summary.md`

The report directory is intentionally ignored by git as runtime evidence. This Markdown file is the tracked evidence summary.

## Command

```bash
cd /home/ubuntu/moodify-mainline
.venv/bin/python scripts/mt002_mrs_score_manifest.py \
  --manifest outputs/mt001_gate3_real_ai/mt001_gate3_real_ai_20260603/manifest.csv \
  --run-id mt002_mrs_baseline_gate3_20260603 \
  --output-dir reports/mt002_mrs_baseline \
  --expected-records 90 \
  --require-complete
```

## Gate Meaning

This verifies MT-002 Gate 3 and Gate 4 on the existing MT-001 real AI batch: MRS is optional post-run scoring, produces schema-shaped records, and can score 30 uploaded AI music samples across 90 Runtime outputs.

## Follow-Up Gate

- Gate 2 hardening: expand the validation matrix beyond this real-batch smoke baseline.
- Gate 5 adoption: decide whether `mrs_open_v031` becomes the current default MRS scoring version after MT-001 Gate 4 24h evidence is complete.
