# MOOD NODES 019 — Privacy / Security

**Authority:** MOOD-NODES-019 TASK.md Phase R

## What is NEVER exposed

- Private IP (10.x, 192.168.x, 172.16.x, etc.)
- SSH endpoints / keys / ports
- Cloud account IDs
- Database credentials
- Service tokens / internal RPC URLs
- Internal hostname
- Operator raw IDs (only operator label)

The public serializer (`publicBySlug`, `publicList`) strips:
- `operatorResidentId` (raw)
- `operatorOrganizationId` (raw)
- `healthSummary`

INV-019-05 is enforced by serialization.

## Credentials

**Hard rule: registry must never store raw infrastructure credentials.**
SSH private keys, API secrets, cloud access keys, DB passwords are NEVER
written into `NodeRecord`. Use secret manager / env / existing secure store.

## Node jobs

Any job execution API must be:

- bounded
- authenticated
- allowlisted
- auditable

019 does not provide a generic remote shell. Job execution is reserved for
future packages.