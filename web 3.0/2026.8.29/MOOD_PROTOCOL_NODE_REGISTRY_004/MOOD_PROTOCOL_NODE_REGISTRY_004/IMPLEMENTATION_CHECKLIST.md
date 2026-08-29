# Implementation Checklist

## Phase 0 — Inspect

- [ ] authority files
- [ ] MPF-001
- [ ] MPF-002
- [ ] MPF-003
- [ ] node/cloud/worker code
- [ ] tests
- [ ] storage abstractions

## Phase 1 — Schemas

- [ ] node
- [ ] capability manifest
- [ ] verification evidence
- [ ] heartbeat
- [ ] registry snapshot

## Phase 2 — Identity

- [ ] node ID factory
- [ ] operator link
- [ ] duplicate guard
- [ ] public node key support if appropriate

## Phase 3 — Lifecycle

- [ ] state machine
- [ ] transition history
- [ ] reason codes
- [ ] suspension guard

## Phase 4 — Capability

- [ ] namespace
- [ ] declaration
- [ ] verification state
- [ ] manifest fingerprint

## Phase 5 — Verification

- [ ] safe challenge
- [ ] evidence record
- [ ] failure state
- [ ] SSRF safety

## Phase 6 — Health

- [ ] heartbeat record
- [ ] draft/approved policy
- [ ] freshness evaluator
- [ ] stale transition
- [ ] recovery

## Phase 7 — Discovery

- [ ] list
- [ ] detail
- [ ] filters
- [ ] registry snapshot

## Phase 8 — Fixtures

- [ ] compute
- [ ] storage
- [ ] data
- [ ] validation
- [ ] developer
- [ ] gateway
- [ ] challenge pass/fail
- [ ] heartbeat fresh/stale
- [ ] illegal transition
- [ ] duplicate
- [ ] privacy
- [ ] snapshot

## Phase 9 — Tests

- [ ] MPF-004
- [ ] offline
- [ ] no RCE
- [ ] no chain write
- [ ] no economics
- [ ] MPF regressions

## Phase 10 — Report

- [ ] execution evidence
- [ ] sample node IDs
- [ ] sample snapshot
- [ ] human decisions
- [ ] rollback
