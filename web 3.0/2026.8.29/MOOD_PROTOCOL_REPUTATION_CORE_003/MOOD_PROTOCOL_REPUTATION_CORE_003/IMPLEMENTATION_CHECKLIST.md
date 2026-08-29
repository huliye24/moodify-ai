# Implementation Checklist

## Phase 0 — Inspect

- [ ] repository authority
- [ ] MPF-001 outputs
- [ ] MPF-002 schemas/code/tests
- [ ] Genesis/010 scoring policy
- [ ] existing profile/identity systems

## Phase 1 — Model

- [ ] contributor profile schema
- [ ] reputation snapshot schema
- [ ] attestation schema
- [ ] reputation policy
- [ ] epoch policy
- [ ] immutable fields

## Phase 2 — Identity

- [ ] identity normalizer
- [ ] protocol ID generator
- [ ] linked identity evidence
- [ ] no auto-merge by display name

## Phase 3 — Reputation

- [ ] eligible input filter
- [ ] duplicate guard
- [ ] dimension aggregator
- [ ] persistence evaluator
- [ ] early evaluator
- [ ] confidence/completeness
- [ ] snapshot builder
- [ ] snapshot fingerprinter

## Phase 4 — History

- [ ] immutable snapshot storage
- [ ] supersede support
- [ ] profile currentSnapshotId

## Phase 5 — Fixtures

- [ ] single contribution
- [ ] multi-category
- [ ] multi-epoch
- [ ] rejected input
- [ ] duplicate input
- [ ] policy mismatch
- [ ] valid identity link
- [ ] inconclusive identity link
- [ ] superseded snapshot
- [ ] insufficient persistence
- [ ] missing weights

## Phase 6 — Tests

- [ ] all MPF-003 tests
- [ ] MPF-002 regression
- [ ] offline run
- [ ] no chain write
- [ ] no economic output

## Phase 7 — Report

- [ ] execution evidence
- [ ] sample profile
- [ ] sample snapshot
- [ ] human decisions
- [ ] rollback
