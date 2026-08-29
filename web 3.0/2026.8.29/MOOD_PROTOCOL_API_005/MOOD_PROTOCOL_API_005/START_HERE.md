# MPF-005 — MOOD Protocol API

## Mission

Build the first unified, versioned **Protocol API** for MOOD Protocol.

MPF-001 establishes mainnet facts.
MPF-002 establishes contribution records.
MPF-003 establishes protocol identity/reputation.
MPF-004 establishes the node registry.

MPF-005 exposes those authorities through one stable application boundary.

## Core flow

```text
MPF-001 Mainnet Facts ───────┐
MPF-002 Contributions ───────┤
MPF-003 Reputation ──────────┤
MPF-004 Node Registry ───────┤
                             ▼
                       Protocol API
                             │
                 ┌───────────┼───────────┐
                 ▼           ▼           ▼
            Protocol Web  Transparency  Genesis
```

## Primary purpose

The API must answer protocol questions without duplicating protocol logic.

Examples:

- What is the official protocol/mainnet configuration?
- What contributions exist?
- What reputation snapshot belongs to a contributor?
- Which nodes are active?
- What is the current network summary?
- What data is public vs restricted?

## Non-negotiable principle

**The API exposes protocol authority. It does not become a second authority.**

Business rules remain in MPF-001/002/003/004 domain modules.

## Read order

1. `START_HERE.md`
2. `CODEX_TASK.md`
3. `ARCHITECTURE.md`
4. `API_CONTRACT.md`
5. `READ_MODEL.md`
6. `WRITE_BOUNDARY.md`
7. `AUTH_AND_RATE_LIMIT.md`
8. `VERSIONING.md`
9. `ERROR_MODEL.md`
10. `OBSERVABILITY.md`
11. `SECURITY_BOUNDARY.md`
12. `TEST_PLAN.md`
13. `ACCEPTANCE_GATE.md`
14. `IMPLEMENTATION_CHECKLIST.md`
15. `ROLLBACK.md`

Then inspect repository authority and MPF-001–004 implementation.

## Expected completion output

Codex must return:

- branch
- base commit
- final commit
- changed files
- endpoint inventory
- schema/openapi location
- test results
- sample responses
- unresolved human decisions
- `NO_CHAIN_WRITE_PERFORMED`
- `NO_TOKEN_TRANSFER_PATH_ADDED`
- `NO_REMOTE_EXECUTION_PATH_ADDED`
