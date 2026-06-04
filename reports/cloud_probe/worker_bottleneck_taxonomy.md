# Worker Bottleneck Taxonomy — MHP-253 | **Date**: 2026-06-04

## Scaling Bottlenecks

| # | Bottleneck | Severity | Impact |
|---|-----------|----------|--------|
| 1 | Queue is single JSONL — can't partition | P0 | Only 1 worker can process |
| 2 | No worker identity — can't assign tasks to specific workers | P0 | Multi-worker coordination impossible |
| 3 | Output files local-only — no shared storage | P1 | Workers on different machines can't see each other's results |
| 4 | Lock file is local — no distributed lease | P1 | Multi-machine collision protection missing |
| 5 | Scheduler models exist but not wired | P1 | /scheduler/* API works but doesn't drive actual workers |
| 6 | No cost tracking | P2 | CostRecord schema exists, never populated |
| 7 | No auto-scaling trigger | P2 | Manual intervention needed |

## Worker Failure Modes

| Mode | Detection | Recovery |
|------|-----------|----------|
| Worker crash | Heartbeat age > 60s | Reassign worker's claimed tasks to another worker |
| Worker hang | Heartbeat age > 120s | Force-kill worker, reassign tasks |
| Queue corruption | Parse error on read | Restore from backup, compact |
| Disk full on worker | Storage health check | Pause task assignment, alert |
| Network partition | Lease expiry | Worker loses lease, tasks reassigned |
