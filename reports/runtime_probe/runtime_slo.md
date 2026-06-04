# Runtime SLO Definition — MHP-101

**Date**: 2026-06-04

## Service Level Objectives

| SLO | Target | Measurement | Window |
|-----|--------|-------------|--------|
| Uptime | ≥99% | Heartbeat gap ≤60s | Rolling 24h |
| Task success rate | ≥95% | done / (done + failed) | Per run |
| Task P99 latency | ≤120s | Elapsed from claimed→done | Per run |
| Recovery time | ≤30s | Time from crash detection to first task restart | Per incident |
| Event loss | ≤0.1% | Missing event_id gaps in sequence | Per run |
| Disk headroom | ≥5GB | Free space at output_root | Continuous |

## Error Budget

| SLO | Monthly Budget (720h) |
|-----|----------------------|
| 99% uptime | 7.2h downtime |
| 95% success rate | 5% of tasks may fail |
| P99 ≤120s | 1% of tasks may exceed |

## Alerting Thresholds

| Alert | Condition | Severity |
|-------|-----------|----------|
| Runner dead | Heartbeat age > 120s | CRITICAL |
| Success rate < 80% | Per-run threshold | HIGH |
| Disk < 3GB | Free space check | HIGH |
| Stale lock > 30min | Lock file age check | MEDIUM |
| Event loss detected | Gap in event_id sequence | MEDIUM |
