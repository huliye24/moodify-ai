# API CONTRACT — REFERENCE

## Public

```text
GET /api/agents
GET /api/agents/[slug]
GET /api/agents/[slug]/activity
GET /api/agents/[slug]/proofs
```

## Operator/Admin

```text
POST  /api/agents
PATCH /api/agents/[id]
POST  /api/agents/[id]/activate
POST  /api/agents/[id]/pause
POST  /api/agents/[id]/retire
POST  /api/agents/[id]/heartbeat
POST  /api/agents/[id]/proofs
```

## Requirements

- operator/admin auth
- server-side validation
- idempotent heartbeat
- bounded proof payload
- no secret fields in public serializer
