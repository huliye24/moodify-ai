# Architecture — Contribution Core

## Position in the protocol

```text
                     MOOD PROTOCOL

 Developers      Compute       Data       Community
     │              │            │            │
     └──────────────┴────────────┴────────────┘
                            │
                    Contribution Core
                            │
                  Proof / Evidence Bundle
                            │
                    Validation + Review
                            │
                    Dimension Scoring
                            │
                  Reputation Evidence
                            │
                 [future package boundary]
                            │
                    Protocol Reputation
                            │
                     Protocol Rights
                            │
                   MOOD Settlement
```

MPF-002 ends at **Reputation Evidence**.

## Design goals

### 1. Evidence first

A score with no evidence is not a protocol fact.

### 2. Deterministic core

Same immutable inputs + same policy version → same machine-derived output.

### 3. Human judgment is explicit

When impact or quality requires human evaluation, the reviewer identity, timestamp, evidence, and policy rule must be recorded.

### 4. Storage agnostic

The domain layer must not depend on D1, Postgres, an RPC endpoint, or a hosted service.

### 5. No economic side effects

Contribution data cannot trigger funds.

### 6. Version pinning

Every scored record pins the exact policy version used.

## Recommended module boundaries

```text
domain/
  Contribution
  Evidence
  Review
  ScoreDimension
  ReputationEvidence

services/
  Normalizer
  Validator
  Fingerprinter
  StateMachine
  DuplicateGuard
  Scorer

ports/
  ContributionRepository
  PolicyRepository

adapters/
  FilesystemContributionRepository
```

## Authority model

There must be one state-machine authority and one policy-version authority.

Do not duplicate rules across:
- frontend
- API
- worker
- contract code

UI/API layers should call the same domain rules.
