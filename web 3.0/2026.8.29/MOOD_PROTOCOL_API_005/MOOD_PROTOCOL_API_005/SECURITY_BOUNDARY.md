# Security Boundary

## Allowed

- read public protocol facts
- read public contribution records
- read public reputation records
- read public node registry
- aggregate public network summary
- safe domain writes if explicitly authorized
- local/offline tests

## Forbidden

- private keys
- seed phrases
- transaction signing
- transaction sending
- token transfers
- treasury operations
- staking
- claim
- liquidity
- contract deployment
- SSH
- shell
- arbitrary remote execution

## Input security

Validate:

- path IDs
- query filters
- pagination
- sort fields
- JSON bodies
- URLs if any

Avoid:
- raw SQL composition
- path traversal
- SSRF
- unsafe deserialization
- unbounded payloads

## Output security

Default-deny private fields.

Use explicit DTO/serializer definitions for public responses.
