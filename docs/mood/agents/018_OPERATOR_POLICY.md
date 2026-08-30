# MOOD AGENTS 018 — Operator Policy

**Authority:** MOOD-AGENTS-018 TASK.md Phase E

## Required operator

Every active agent MUST have an operator:

- `operatorResidentId` — bound to a 015 Resident ID.
- OR `operatorOrganizationId` — bound to a registered organization.

## Operator authority

Only the operator (matching `operatorResidentId`) may:

- `activate(agentId, actorResidentId)` → requires match.
- `pause(agentId, actorResidentId)` → requires match.
- `retire(agentId, actorResidentId)` → requires match.

Other actors receive `not-operator` error.

## Display

Public serializer shows `operatorLabel`:
- `"Resident M7Q4K2"`
- `"Org <id>"`

Never shows the raw `operatorResidentId` or `operatorOrganizationId` values.