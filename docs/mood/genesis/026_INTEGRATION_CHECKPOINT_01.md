# Genesis Integration 026 - Checkpoint 01

**Date:** 2026-08-30
**Branch:** `codex/mood-genesis-integration-026`
**Scope:** Whitepaper baseline plus packages 011-020

## Outcome

The previously separate package chain now compiles and builds as one web application. This checkpoint does not claim that a persistent or public Genesis network is running.

## Integrated package sequence

011 Foundation, 012 Protocol Extraction, 013 Portal, 014 Library, 015 Passport, 016 Contribution, 017 Network, 018 Agents, 019 Nodes, and 020 Governance were absorbed from their recorded commits. Packages 021-025 were not admitted as continued feature development.

## Integration defects corrected

- Reconciled application imports through the project alias instead of package-specific relative paths.
- Enabled TypeScript's source-extension imports for the existing bundler/no-emit model.
- Added the shared `ResidentId` type required by Contribution.
- Added `AgentTaskCompleted` to the Network activity contract.
- Removed the invalid Node `paused` state branch; maintenance remains the defined operator pause state.
- Corrected Library policy access to the canonical exported registry functions.
- Corrected API identity-helper resolution.
- Added explicit JSON response typing at client boundaries.
- Restored the public MOOD Library path expected by the player surface contract.
- Refreshed the integrated Decision Log hash in both the Library registry and verifier.

## Verification evidence

| Check | Result |
|---|---|
| TypeScript `--noEmit` | PASS |
| vinext production build | PASS |
| Sites artifact validation | PASS |
| Existing web tests | 48/48 PASS |
| 014-020 root invariants | 91/91 PASS |
| Library document hashes | 10/10 PASS |
| Canon guard | PASS |

The repository's default `npm test` launcher attempts WSL on this Windows host. The same verified build script was executed successfully through Git for Windows Bash.

## Runtime truth audit

The build is not yet a deployable Genesis network because the current authoritative registries are process memory:

- Passport residents, wallets, sessions, nonces, profiles, privacy, and reputation: in-memory.
- Contribution tasks, submissions, evidence, reputation events, and pending rewards: in-memory.
- Agents, heartbeats, task runs, and proofs: in-memory.
- Nodes, heartbeats, capacity, and service proofs: in-memory.
- Governance proposals, decisions, implementations, and audit events: in-memory.

Consequences:

1. State can disappear on worker restart or move between isolates.
2. Multiple instances can expose inconsistent network counts.
3. A real participant cannot yet rely on durable identity or contribution history.
4. Public staging and real Genesis participant onboarding remain blocked.

Network metrics are sourced from these registries and avoid invented global-scale numbers, but they are not durable network facts until persistence and snapshot evidence are established.

## Next critical integration slice

The next work is not Treasury, Security, Staging, or Token as separate feature packages. It is a 026 persistence and evidence slice:

```text
canonical persistent store
  -> Passport adapter
  -> Contribution / Proof transaction
  -> Agent / Node heartbeat and proof store
  -> Governance history
  -> Observatory read model
  -> restart / concurrency / idempotency tests
  -> runtime snapshot evidence
```

Storage selection and migration must preserve one data authority. Existing database bindings and schemas must be audited before adding any new store.

## Current release state

```text
CODE_INTEGRATION = PASS
BUILD = PASS
PACKAGE_INVARIANTS = PASS
PERSISTENT_NETWORK = NOT_IMPLEMENTED
PUBLIC_STAGING = NOT_DEPLOYED
REAL_GENESIS_PARTICIPANTS = NOT_ONBOARDED
TOKEN_LAUNCH = NOT_AUTHORIZED
```

