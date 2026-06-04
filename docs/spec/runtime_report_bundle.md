# Runtime Report Bundle Standard — MHP-129

**E-Chain**: ECHAIN-MOODIFY-RUNTIME-001

## Bundle Structure

```
outputs/{run_id}/
├── manifest.csv              # per-task results (existing)
├── summary.json              # aggregate stats (existing)
├── daily_run.log             # text log (existing)
├── runtime_events.jsonl      # structured events (NEW)
├── gate_decisions.jsonl      # gate decisions per task
├── heartbeat.jsonl           # heartbeat records
└── failure_log.jsonl         # classified failures
```

## Required Fields per File

### runtime_events.jsonl
`event_id, event_type, run_id, timestamp, task_id, sample_id, preset, extra`

### gate_decisions.jsonl
`candidate_id, job_id, decision, reasons, required_mrs_delta`

### failure_log.jsonl
`failure_id, task_id, sample_id, exit_code, severity, retryable, attempt, classified_at`
