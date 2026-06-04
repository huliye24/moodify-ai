# Runtime Event Schema Spec — MHP-125

**Date**: 2026-06-04 | **E-Chain**: ECHAIN-MOODIFY-RUNTIME-001

## Event Types

| Type | Trigger | Fields |
|------|---------|--------|
| task_started | Task subprocess launched | task_id, sample_id, preset, input_path |
| task_completed | Task subprocess exit 0 | task_id, sample_id, preset, elapsed_s, exit_code, mrs_delta |
| task_failed | Task subprocess exit != 0 or timeout | task_id, sample_id, preset, error, exit_code, attempt |
| heartbeat | Periodic (default 15s) | active_tasks, completed, failed, uptime_s, free_disk_gb |
| run_summary | End of run | total_tasks, success, failed, elapsed_s, exit_reason |

## Event ID Format

```
{prefix}_{run_id}_{task_id}
ts_R20260604_TASK_001    (task_started)
tc_R20260604_TASK_001    (task_completed)
tf_R20260604_TASK_001    (task_failed)
hb_R20260604_3600        (heartbeat at 3600s uptime)
rs_R20260604             (run_summary)
```

## Query Examples

```bash
# Tasks that failed in a specific run
jq 'select(.event_type=="task_failed")' runtime_events.jsonl

# Success rate from run_summary
jq 'select(.event_type=="run_summary") | .extra' runtime_events.jsonl

# Latency distribution
jq 'select(.event_type=="task_completed") | .extra.elapsed_s' runtime_events.jsonl | sort -n

# Heartbeat gaps (detect dead runner)
jq 'select(.event_type=="heartbeat") | {ts: .timestamp, uptime: .extra.uptime_s}' runtime_events.jsonl
```
