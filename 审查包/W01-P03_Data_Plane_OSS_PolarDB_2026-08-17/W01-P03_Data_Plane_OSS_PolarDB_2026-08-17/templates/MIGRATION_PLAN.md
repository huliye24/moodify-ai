# Migration Plan

## Database

- selected engine:
- selected instance:
- target database/schema:
- existing tables:
- migration tool:
- transaction behavior:
- destructive operations:
- backup prerequisite:
- rollback:
- dry-run result:
- production authorization:
- execution status:

Allowed execution status:

- DESIGN_ONLY
- MIGRATION_READY
- SCHEMA_WRITE_BLOCKED
- EXECUTED_DEV
- EXECUTED_STAGING
- EXECUTED_PRODUCTION

## OSS

- provider:
- region:
- bucket:
- bucket exists:
- versioning:
- lifecycle:
- public access:
- test prefix:
- credential source:
- write authorization:
- status:

Allowed status:

- DESIGN_ONLY
- OSS_WRITE_BLOCKED
- TEST_PREFIX_READY
- CONNECTED_DEV
- CONNECTED_STAGING
- CONNECTED_PRODUCTION
