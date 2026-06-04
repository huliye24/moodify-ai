# Runtime Operator Runbook — MHP-135

**E-Chain**: ECHAIN-MOODIFY-RUNTIME-001 | **Date**: 2026-06-04

## Quick Start

```bash
# Check if runtime is alive
curl http://localhost:8700/runtime/heartbeat

# Full status
curl http://localhost:8700/runtime/status

# Start supervised run
python3 -m moodify_runtime.cli runtime-supervisor-start --limit 50

# Force-release stale lock
python3 -m moodify_runtime.cli runtime-cleanup --release-lock
```

## Incident Response

| Symptom | Check | Fix |
|---------|-------|-----|
| Runner dead | `runtime/heartbeat` age > 120s | Restart: `runtime-supervisor-start` |
| Tasks stuck | `runtime/status` active_jobs not changing | Resume: force-release stale lock, restart |
| Disk low | `runtime/status` storage healthy=false | Clean outputs: `runtime-cleanup --prune 7d` |
| High failure rate | `gate_decisions.jsonl` reject > 20% | Check presets, audio quality, MRS thresholds |

## Health Metrics

| Metric | Good | Warning | Critical |
|--------|------|---------|----------|
| Heartbeat age | < 30s | 30-120s | > 120s |
| Task success rate | > 95% | 80-95% | < 80% |
| Free disk | > 10GB | 3-10GB | < 3GB |
| P99 latency | < 60s | 60-120s | > 120s |
