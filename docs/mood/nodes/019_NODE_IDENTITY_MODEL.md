# MOOD NODES 019 — Identity Model

**Authority:** MOOD-NODES-019 TASK.md Phase D

## Stable identity

```text
node_N           (sequential auto-incremented)
node_<slug>      (operator-provided, unique)
```

## Decoupling invariants

- Node ID is stable across IP changes.
- Node ID is decoupled from cloud vendor / instance type.
- Node ID does not change when the machine migrates.
- Node ID survives hardware replacement (operator may re-bind the ID to a new deployment).

## Distinction

| Layer | Carries |
|---|---|
| Node Identity | slug, name, role |
| Node Deployment | capacity, publicRegion, version |
| Node Endpoint | publicEndpoint (safe service URL only) |
| Node Operator | operatorResidentId or operatorOrganizationId |
| Node Service Proof | proof id (per-job) |

The identity layer is never changed by infrastructure migrations.