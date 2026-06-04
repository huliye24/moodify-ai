# MHP-061: 6-Hour Unattended Run — Production Metrics Collection

**Status**: completed
**Direction**: NEM-MOODIFY-STUDIO-OS-001 / Validate-6 / V (Validation)
**Depends on**: MHP-060 (validation dataset ready)
**Protocol**: NEM-18 = Build-6 + Validate-6 + Harden-6

## Context

Studio OS Alpha processes audio through `run_daily` and collects MRS metrics, gate decisions, and timing data. But we have zero production runtime metrics. We don't know:

- What is the average processing time per audio sample?
- What percentage of runs fail and why?
- What is the MRS score distribution across presets?
- How often does over_dark trigger in real data?
- What is the memory/CPU profile over 6 hours?

## Goal

Run a 6-hour unattended processing session with the validation dataset. Collect:

1. **Timing**: per-sample elapsed time, queue wait time, total run duration
2. **Success rate**: % of tasks with status=done
3. **MRS metrics**: distribution of MRS scores per preset, delta distributions
4. **Gate decisions**: approve/reprocess/reject counts per preset
5. **Failure analysis**: error types and frequencies
6. **Resource**: peak memory, CPU utilization samples

## Non-Goals

- Don't interrupt the run to fix bugs mid-flight (document, don't fix)
- Don't run for exactly 6 hours if 30 samples × 3 presets finishes sooner
- Don't optimize performance yet (that's Harden-6)

## Requirements

### Run configuration
```yaml
samples: 30 (minimum)
presets: [warm_vocal, clean_master, wide_space]
total_tasks: 90 (30 × 3)
expected_duration: 2-6 hours (depends on per-sample processing time)
dry_run: false
```

### Metrics collected
```text
outputs/nem_validate_001/
├── manifest.csv           — per-task results
├── summary.json            — aggregate stats
├── timing.jsonl            — per-task elapsed times
├── mrs_distribution.json   — MRS score histogram per preset
├── failure_log.jsonl       — error messages and stack traces
├── resource_log.jsonl      — memory/CPU samples (every 5 min)
└── daily_run.log           — full runtime log
```

## Acceptance Criteria
- At least 90 tasks processed (30 samples × 3 presets)
- Success rate documented
- MRS distribution computed per preset
- Gate decision counts per preset
- All failures classified by type
- Run log preserved for analysis

## Test Plan
```bash
python3 scripts/run_validation_6h.sh  # launches the run
python3 scripts/collect_validation_metrics.py  # post-run analysis
```
