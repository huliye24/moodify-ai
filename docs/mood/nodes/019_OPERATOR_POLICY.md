# MOOD NODES 019 — Operator Policy

**Authority:** MOOD-NODES-019 TASK.md Phase Q

## Required operator

Every active node MUST have an operator:

- `operatorResidentId` — bound to a 015 Resident ID.
- OR `operatorOrganizationId` — bound to a registered organization.

## Operator authority

Only the operator (matching `operatorResidentId`) may:

- `activate(nodeId, actorResidentId)` → requires match.
- `setMaintenance(nodeId, actorResidentId)` → requires match.
- `retire(nodeId, actorResidentId)` → requires match.

Other actors receive `not-operator` error.

## Display

Public serializer shows `operatorLabel`:
- `"Resident M7Q4K2"`
- `"Org <id>"`

Never shows the raw `operatorResidentId` or `operatorOrganizationId` values.