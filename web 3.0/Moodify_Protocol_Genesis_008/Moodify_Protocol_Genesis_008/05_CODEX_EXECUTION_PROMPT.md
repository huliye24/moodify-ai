# Codex Execution Prompt

Execute **Moodify Protocol Genesis 008 — Security & Public Launch** inside the existing Moodify repository.

This is the final Genesis v1 hardening package.

## Mission

Audit Packages 001–007 end-to-end and produce a release candidate.

Do not add major new features.

Focus on:
- security;
- correctness;
- consistency;
- privacy;
- deployment safety;
- operational readiness;
- production launch clarity.

## Mandatory audit first

1. Read repository instructions/canon.
2. Inspect git status and preserve unrelated changes.
3. Locate all Package 001–007 implementations.
4. Map routes, APIs, DB tables, configs, contracts and scripts.
5. Identify production/test environment boundaries.
6. Identify existing security tooling.
7. Record baseline test/build status.
8. Locate any real secrets safely without printing them.

## Audit order

### A. Token identity
Check all official MOOD values against one config authority.

### B. Registration
Threat-model and test nonce/signature/replay/duplicate/concurrency.

### C. Admin
Test authorization, IDOR, mutation audit, notes privacy, allocation integrity.

### D. Distribution
Reproduce snapshot/root/proofs and validate exact arithmetic.

### E. Smart contract
Run:
- Foundry unit tests;
- fuzz;
- invariants;
- coverage if useful;
- gas report;
- Slither if available.

Verify Package 004 fixture compatibility.

### F. Airdrop UI
Test wallet states, proof lookup, wrong chain, receipt confirmation, claimed state, errors.

### G. Contribution Network
Test task/submission/review/reputation/reward integrity and anti-abuse.

### H. Transparency
Test data source correctness, stale behavior, privacy and read-only guarantees.

### I. Secrets/environment
Scan for leaked secrets and production/test config confusion.

### J. Public UX
Review `/token`, `/genesis`, `/airdrop`, `/contribute`, `/transparency`.

## Security findings

Create:

`docs/security/GENESIS_SECURITY_REVIEW.md`

Use severity:
- CRITICAL
- HIGH
- MEDIUM
- LOW
- INFO

Do not mark release GO with unresolved CRITICAL/HIGH unless HIGH has explicit human risk acceptance.

## Threat model

Create:

`docs/security/GENESIS_THREAT_MODEL.md`

## Privacy review

Create:

`docs/security/GENESIS_PRIVACY_REVIEW.md`

## Incident response

Create:

`docs/security/GENESIS_INCIDENT_RESPONSE.md`

Use the package template, adapted to real architecture.

## Launch runbook

Create:

`docs/protocol/GENESIS_LAUNCH_RUNBOOK.md`

Include:
- backup;
- snapshot approval;
- root approval;
- contract deployment;
- BscScan verification;
- distributor funding;
- frontend config;
- smoke claim;
- monitoring;
- rollback/containment.

Mark all production wallet actions:

`[HUMAN SIGNATURE REQUIRED]`

## Release candidate

Create:

`docs/releases/GENESIS_V1_RC.md`

Include:
- package completion map;
- security summary;
- known issues;
- tests;
- deployment readiness;
- environment readiness;
- human decisions outstanding;
- GO / CONDITIONAL GO / NO-GO.

## Refactoring rule

Fix security/correctness issues with minimal targeted changes.

Do not perform broad architecture rewrites unless a critical flaw cannot otherwise be fixed.

## Secret handling

If a real secret/private key is found:

1. do not print it;
2. redact it in report;
3. identify file/path safely;
4. stop using it;
5. mark release NO-GO until human rotates it;
6. remove from tracked source if appropriate;
7. note git-history exposure separately.

Do not attempt to rotate external credentials without human authorization.

## Production prohibitions

Do not:
- deploy BNB mainnet contract;
- sign production transaction;
- fund distributor;
- transfer treasury MOOD;
- add/remove liquidity;
- create Safe;
- publish unapproved tokenomics;
- expose private keys;
- automate MetaMask.

## Required tests

At minimum:

### Registration
- replay
- expiry
- wrong signer
- wrong chain
- duplicate/concurrent

### Admin
- unauthorized read/write
- IDOR
- audit integrity
- allocation exactness

### Distribution
- deterministic root
- proof verification
- duplicate wallet
- pool ceiling
- artifact privacy

### Contract
- valid claim
- wrong wallet/amount/proof
- double claim
- insufficient balance
- fuzz/invariants
- Package 004 compatibility

### Contribution
- unauthorized submission/review
- self-review
- exact reward
- duplicate reward
- export privacy

### Transparency
- source correctness
- stale/unavailable handling
- circulating methodology guard
- read-only enforcement
- API privacy

### Environment
- no production secret in client
- no mock config in production
- mainnet/testnet mismatch fail closed

## Completion output

Return:

1. system map;
2. security findings by severity;
3. fixes applied;
4. unresolved findings;
5. contract audit result;
6. privacy result;
7. migration/data integrity result;
8. public UX result;
9. environment/secret result;
10. full test/build matrix;
11. deployment readiness;
12. human-only production steps;
13. final GO / CONDITIONAL GO / NO-GO;
14. files changed;
15. git diff summary;
16. exact safety statement:

`No production MOOD transfer, production wallet signature, production smart-contract deployment, treasury transaction, liquidity mutation, Safe transaction, or private-key handling was performed by this task.`

## Stop conditions

Stop immediately and report if:

- real private key/seed phrase is found;
- CRITICAL fund-loss vulnerability is discovered;
- production database migration would be destructive;
- canon conflict affects token identity;
- mainnet broadcast/signing is requested;
- unapproved treasury/tokenomics publication is required.
