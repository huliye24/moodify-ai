# Package Manifest

Package: `MOOD_PROTOCOL_API_005`

Purpose:

> Build the single stable application interface over MPF-001–004.

## Files

- START_HERE.md
- CODEX_TASK.md
- ARCHITECTURE.md
- API_CONTRACT.md
- READ_MODEL.md
- WRITE_BOUNDARY.md
- AUTH_AND_RATE_LIMIT.md
- VERSIONING.md
- ERROR_MODEL.md
- OBSERVABILITY.md
- SECURITY_BOUNDARY.md
- TEST_PLAN.md
- ACCEPTANCE_GATE.md
- IMPLEMENTATION_CHECKLIST.md
- ROLLBACK.md
- EVIDENCE_TEMPLATE.md
- OPENAPI_REQUIREMENTS.md
- schema/api-envelope.schema.json
- schema/api-error.schema.json
- schema/network-summary.schema.json
- schema/network-snapshot.schema.json
- config/api-policy.draft.json
- fixtures/network-summary.example.json
- SHA256SUMS.txt

## Explicit exclusions

- token transfer
- claim
- staking
- node rewards
- treasury
- governance voting
- liquidity
- contract deployment
- job execution
- SSH / shell
- cloud provisioning
- marketplace

## Success condition

A client should be able to ask one API:

```text
What is MOOD?
Who has contributed?
What reputation exists?
Which nodes exist?
What is the current network state?
```

without knowing the internal storage or implementation of MPF-001–004.
