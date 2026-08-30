# MOOD AGENTS 018 — Agent Identity Model

**Authority:** MOOD-AGENTS-018 TASK.md Phase D

## Stable identity

```text
agent_N   (auto-incremented sequential ID)
agent_<slug>  (operator-provided, unique)
```

## Decoupling invariants

- Agent ID is **stable** across model provider changes.
- Agent ID is **decoupled** from any specific API key.
- Agent ID **does not change** when the underlying model is upgraded.
- Agent ID **survives** runtime endpoint migration.

## Distinction

| Layer | Carries |
|---|---|
| Agent Identity | slug, name, description |
| Agent Runtime | runtimeType, modelProvider, modelName, version (mutable) |
| Agent Operator | operatorResidentId or operatorOrganizationId |
| Agent Task Run | run id (per-task) |
| Agent Proof | proof id (per-task) |

The identity layer is **never** changed by runtime migrations.