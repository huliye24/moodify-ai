# MOOD NODES 019 — Health Model

**Authority:** MOOD-NODES-019 TASK.md Phases I/J

## Status values

```text
draft       — registered, not yet activated
active      — operator-declared active + healthy
degraded    — heartbeat reports error
offline     — heartbeat stale beyond threshold (>30 min)
maintenance — operator-declared
retired     — permanent
```

## Heartbeat freshness

`lastSeenAt` updated on every OK heartbeat. If the last heartbeat is older
than 30 minutes, status moves to `offline`.

## Health checks per role

| Role | Health signal |
|---|---|
| `compute` | process alive, queue capacity, disk scratch availability |
| `ai` | runtime loaded, provider reachable, inference smoke test |
| `storage` | read/write OK, integrity check OK, capacity > 0 |
| `verification` | proof endpoint, deterministic test, hash verification |

## Display rule

INV-019-03: **never display "Online" without a heartbeat.**