# Implementation Checklist

## Phase 0 — Inspect

- [ ] Read AGENTS.md
- [ ] Read Canon authority
- [ ] Locate MPF-001 outputs
- [ ] Locate Web3 / Genesis / 010 policy files
- [ ] Locate existing schemas and domain patterns
- [ ] Locate test framework
- [ ] Record conflicts

## Phase 1 — Define

- [ ] Choose canonical contribution module location
- [ ] Define schemas
- [ ] Define policy file
- [ ] Define categories
- [ ] Define evidence types
- [ ] Define state transitions
- [ ] Define immutable fields

## Phase 2 — Core

- [ ] Normalizer
- [ ] Fingerprinter
- [ ] Validator
- [ ] State machine
- [ ] Duplicate guard
- [ ] Scoring engine
- [ ] Reputation-evidence builder

## Phase 3 — Adapter

- [ ] Filesystem/test adapter
- [ ] No cloud hard dependency

## Phase 4 — Fixtures

- [ ] valid code
- [ ] valid docs
- [ ] valid compute
- [ ] missing evidence
- [ ] malformed contributor
- [ ] duplicate
- [ ] illegal transition
- [ ] score-before-verify
- [ ] finalized mutation
- [ ] policy mismatch

## Phase 5 — Tests

- [ ] Run all MPF-002 tests
- [ ] Run relevant repository regression tests
- [ ] Verify offline
- [ ] Verify no chain write path
- [ ] Verify no economic fields

## Phase 6 — Evidence

- [ ] Produce execution report
- [ ] Record sample IDs/fingerprints
- [ ] Record unresolved decisions
- [ ] Confirm no chain write/token distribution
