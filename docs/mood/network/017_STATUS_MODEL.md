# MOOD NETWORK 017 — Status Model

**Authority:** MOOD-NETWORK-017 TASK.md Phase E

## Network status

```ts
type NetworkStatus =
  | "operational"
  | "degraded"
  | "partial"
  | "maintenance"
  | "unknown";
```

## Semantics (v1)

- `operational`: registries reachable, no subsystem flagged.
- `partial`: a non-critical subsystem is unavailable but core flow works.
- `degraded`: core flow (contribution, review) impaired.
- `maintenance`: operator-declared.
- `unknown`: cannot verify health.

## Implementation

`NetworkObservatory.status()` reads:

- size of contribution submissions registry,
- size of contribution tasks registry.

If both are populated and reachable, returns `operational`. Otherwise `unknown`
/ `partial`. **It does NOT read any RPC or chain state** (INV-017-11).