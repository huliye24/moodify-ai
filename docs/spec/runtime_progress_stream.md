# Progress Streaming Contract — MHP-132

**E-Chain**: ECHAIN-MOODIFY-RUNTIME-001

## Protocol

The Console polls `/runtime/status` for progress. No WebSocket or SSE yet (future E-Chain).

## Status Response Shape

```json
{
  "heartbeat_alive": true,
  "heartbeat_age_s": 3.2,
  "active_jobs": 5,
  "total_jobs": 90,
  "slo": {
    "uptime_target": 0.99,
    "success_rate_target": 0.95,
    "p99_latency_target_s": 120
  }
}
```

## Client Polling Contract

- Poll interval: 5-30s (configurable in Console JS)
- Staleness threshold: heartbeat_age_s > 60 → show "Runner Dead" warning
- Progress %: (total_jobs - active_jobs) / total_jobs × 100
- Active jobs: jobs with status not in (delivered, failed)
