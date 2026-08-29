# MPF-002 — MOOD Protocol Contribution Core

## Mission

Build the first auditable **Proof of Contribution** layer for MOOD Protocol.

This package starts after **MPF-001 Protocol Foundation** has established or drafted the canonical network facts.

The output of 002 is NOT an airdrop system and NOT a token-distribution system.

It is the protocol's evidence layer for answering:

> Who contributed what, when, with which evidence, under which policy version, and what deterministic reputation evidence did that contribution produce?

## Core flow

```text
Contributor
   ↓
Contribution Submission
   ↓
Evidence Bundle
   ↓
Validation
   ↓
Review / Verification
   ↓
Dimension Scores
   ↓
Contribution Record
   ↓
Reputation Evidence
```

Later packages may connect reputation evidence to protocol rights or MOOD settlement.

**002 MUST NOT do that.**

## Read order

1. `START_HERE.md`
2. `CODEX_TASK.md`
3. `ARCHITECTURE.md`
4. `CONTRIBUTION_SPEC.md`
5. `EVIDENCE_POLICY.md`
6. `SCORING_POLICY.md`
7. `ANTI_SYBIL.md`
8. `SECURITY_BOUNDARY.md`
9. `TEST_PLAN.md`
10. `ACCEPTANCE_GATE.md`
11. `IMPLEMENTATION_CHECKLIST.md`
12. `ROLLBACK.md`

Then inspect the repository's current authority files, especially `AGENTS.md`, current Canon files, MPF-001 output, and any existing Genesis/010 contribution or allocation policy.

## Non-negotiable principle

**Contribution is evidence. It is not money.**

No token transfer, mint, claim, vesting, treasury movement, wallet signing, or reward conversion is permitted in MPF-002.

## Expected completion output

Codex should return:

- branch name
- base commit
- final commit
- changed files
- test results
- sample contribution IDs
- policy status
- unresolved human decisions
- explicit statement: `NO_CHAIN_WRITE_PERFORMED`
- explicit statement: `NO_TOKEN_DISTRIBUTION_PERFORMED`
