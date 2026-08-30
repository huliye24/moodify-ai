# MOOD AGENTS 018 — Status Model

**Authority:** MOOD-AGENTS-018 TASK.md Phase G

## Status values

```text
draft       — registered, not yet activated
active      — operator-declared active; runtime healthy
paused      — operator-declared paused
degraded    — heartbeat reports error
offline     — heartbeat stale beyond threshold (>30 min)
retired     — permanent
```

## Heartbeat freshness

`lastSeenAt` updated on OK heartbeat.
`lastErrorAt` updated on error heartbeat.
`lastSuccessAt` updated on successful task completion.

`effectiveStatus()`:
- `retired` / `draft` / `paused` → returned directly.
- Otherwise: if `lastSeenAt` missing or > 30 min → `offline`.
- Otherwise: if `lastErrorAt > lastSuccessAt` → `degraded`.
- Otherwise → `active`.

## Display rule

INV-018-03: **never display "Online" without a heartbeat.**
Without heartbeat, status reads `Registered — runtime status unavailable`.