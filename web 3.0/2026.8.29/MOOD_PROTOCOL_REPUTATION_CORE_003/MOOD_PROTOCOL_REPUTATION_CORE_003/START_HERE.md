# MPF-003 — MOOD Protocol Reputation Core

## Mission

Build the first auditable **Protocol Reputation** layer for MOOD Protocol.

MPF-002 records and verifies individual contributions.

MPF-003 answers a different question:

> What has this contributor repeatedly and verifiably contributed to the protocol over time?

The output is a versioned, reproducible, non-economic **Protocol Identity + Reputation Snapshot**.

## Core flow

```text
Finalized Contributions
        ↓
Reputation Evidence
        ↓
Contributor Profile
        ↓
Epoch Aggregation
        ↓
Reputation Snapshot
        ↓
Protocol Identity
```

MPF-003 MUST NOT convert reputation into:
- MOOD
- token rewards
- claim amounts
- staking weight
- governance voting power
- treasury allocation
- market privileges

Those belong to later packages.

## Read order

1. `START_HERE.md`
2. `CODEX_TASK.md`
3. `ARCHITECTURE.md`
4. `REPUTATION_MODEL.md`
5. `IDENTITY_MODEL.md`
6. `EPOCH_POLICY.md`
7. `ATTESTATION_POLICY.md`
8. `DECAY_AND_PERSISTENCE.md`
9. `ANTI_GAMING.md`
10. `SECURITY_BOUNDARY.md`
11. `TEST_PLAN.md`
12. `ACCEPTANCE_GATE.md`
13. `IMPLEMENTATION_CHECKLIST.md`
14. `ROLLBACK.md`

Then inspect repository authority, MPF-001, MPF-002 implementation, Genesis/010 policy, and existing reputation-related code.

## Non-negotiable principle

**Reputation is earned protocol history. It is not a financial balance.**

## Expected completion report

Codex must return:

- branch
- base commit
- final commit
- changed files
- tests
- sample contributor profile
- sample reputation snapshot
- active policy version
- unresolved human decisions
- `NO_CHAIN_WRITE_PERFORMED`
- `NO_TOKEN_DISTRIBUTION_PERFORMED`
- `NO_PROTOCOL_RIGHTS_ASSIGNED`
