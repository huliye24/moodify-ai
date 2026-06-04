# MHP-792: Inventory Existing Night Data Artifacts

**Status**: ready
**Direction**: ECHAIN-MOODIFY-DATA-LOOP-014 / NEM-MOODIFY-DATA-LOOP-PROBE-042 / Probe Plan-6A: Loop Boundary / P2 (Execution)
**Depends on**: MHP-791
**Protocol**: E-Chain 54 = Probe NEM-18 + Build NEM-18 + System NEM-18

## Goal

Inventory the existing data artifacts that can feed optimization loops.

## Artifact Classes

```text
outputs/*/summary.json
outputs/*/manifest.csv
outputs/tidal/tidal_events.jsonl
outputs/tidal/tidal_records.jsonl
outputs/tidal/tidal_heartbeat.json
data/tidal_queue.jsonl
reports/daily_report_*.json
reports/daily_report_*.md
reports/mt002_mrs_baseline/*/summary.json
reports/mt002_mrs_validation/*
```

## Expected Output

`reports/echain_moodify_data_loop_014/{RUN_ID}/artifact_inventory.md`

## Acceptance Criteria

- Each artifact class has producer, consumer, retention policy, and optimization use.
- Generated heavy assets remain excluded from git.
