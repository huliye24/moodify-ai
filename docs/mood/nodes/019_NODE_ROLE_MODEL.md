# MOOD NODES 019 — Role Model

**Authority:** MOOD-NODES-019 TASK.md Phase E

## Roles (v1)

| Role | Purpose |
|---|---|
| `compute` | General compute: batch jobs, audio processing, task execution. |
| `ai` | Model inference, agent runtime, audio intelligence, classification. |
| `storage` | Artifact / dataset / evidence / archive storage. |
| `verification` | Proof validation, artifact hash verification, contribution verification, protocol checks. |

## Multi-role

A node MAY have multiple capabilities (e.g. compute + ai) but MUST declare one
primary role. The `byRole` breakdown in `/network` counts primary role.