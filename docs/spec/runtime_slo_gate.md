# Runtime SLO and Gate Spec — MHP-128

**E-Chain**: ECHAIN-MOODIFY-RUNTIME-001

## SLO Targets

| SLO | Target | Window | Measurement |
|-----|--------|--------|-------------|
| Uptime | ≥99% | Rolling 24h | Heartbeat gap ≤60s |
| Task success rate | ≥95% | Per run | done / (done + failed) |
| Task P99 latency | ≤120s | Per run | claimed_at → done_at |
| Recovery time | ≤30s | Per incident | Crash detection → first task restart |
| Event loss | ≤0.1% | Per run | event_id sequence gaps |
| Disk headroom | ≥5GB | Continuous | Free space check |

## Error Budget

| SLO | Monthly Budget (720h) |
|-----|----------------------|
| 99% uptime | 7.2h downtime |
| 95% success rate | 5% of tasks may fail |
| P99 ≤120s | 1% of tasks may exceed |

## Gate Criteria

| Gate | When | Decision Options |
|------|------|-----------------|
| Gate 1 | After Probe NEM | ADOPT / HOLD / DROP |
| Gate 2 | After Build NEM | ADOPT / HOLD / ROLLBACK |
| Gate 3 | After System NEM | SEALED / EXTEND / REWORK |
