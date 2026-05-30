# Treatment Record Aggregator

MHP-014: Aggregates multiple Treatment Records into summary JSON and Markdown.

## Purpose

Scans `treatment_records/` for JSON records and produces:

- `treatment_records/summary.json` — machine-readable aggregation
- `treatment_records/summary.md` — human-readable report

Answers questions like:

- How many records exist?
- Per-preset sample count and average deltas
- Which records have completed human feedback?

## Usage

```bash
# Default paths
python scripts/v01_aggregate_treatment_records.py

# Custom paths
python scripts/v01_aggregate_treatment_records.py \
  --input-dir treatment_records \
  --output-json treatment_records/summary.json \
  --output-md treatment_records/summary.md
```

## Output

### summary.json

Contains:
- `record_count` — total treatment records
- `presets` — per-preset stats (count, avg deltas, feedback counts)
- `records` — flat list of key fields per record
- `errors` — any files that failed to load

### summary.md

Tables:
- Overview (total count, feedback status)
- Preset Summary (avg deltas per preset)
- Records (all records with key deltas)
- Human Feedback Status (per-preset feedback breakdown)

## Design Rules

- Read-only: does not modify treatment records
- Standard library only: argparse, json, pathlib, statistics
- Fault-tolerant: skips broken files, reports errors without crashing
- Empty input → empty summary, not crash
