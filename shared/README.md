# Moodify Shared Infrastructure

> Cross-cutting infrastructure serving all layers: Engine, Products, and Applications.

## Modules

| Module | Responsibility |
|--------|---------------|
| `contracts` | Evidence artifacts, provenance, rules, serialization, IDs |
| `authority` | Decision authority, escalation, scope contracts, review store |
| `safety` | Bounds, projection, guardrails |
| `node` | Worker queue, DB, runner adapter, resource management |
| `api` | FastAPI application, routing, middleware, shared API gateway |

## Migration Source

All modules migrate from `moodify-core-package/src/moodify/`:

| Shared Module | Source |
|---------------|--------|
| `contracts/` | `contracts/` (base, evidence_artifact, hashing, ids, machine_finding, measurement_record, production_case, provenance, rule, serialization) |
| `authority/` | `authority/` (escalation, pipeline, review_store, scope_contract) |
| `safety/` | `safety/` (bounds, projection) |
| `node/` | `node/` (cli, config, db, models, queue, resources, runner_adapter, worker) |
| `api/` | `api/` (main, routes, schemas, services) |
