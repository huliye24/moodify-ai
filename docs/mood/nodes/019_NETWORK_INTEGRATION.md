# MOOD NODES 019 — Network Integration

**Authority:** MOOD-NODES-019 TASK.md Phase O

## 017 /network reads

`NetworkObservatory` now exposes:

- `nodes()` → total registered
- `nodesActive()` → active status
- `nodesDegraded()` → degraded status
- `nodesByRole()` → per-role breakdown

## Activity events

`NetworkObservatory.activity()` includes:

- `NodeRegistered` (on node.createdAt)

## 020 should add

- `mips` metric
- Events: `MIPPublished`, `MIPReviewStarted`, `MIPAccepted`, `MIPImplemented`