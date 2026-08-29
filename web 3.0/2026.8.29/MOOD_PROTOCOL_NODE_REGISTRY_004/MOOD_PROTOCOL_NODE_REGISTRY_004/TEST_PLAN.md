# MPF-004 Test Plan

## T1 — Stable node ID

Same stable identity inputs produce same node ID.

## T2 — Infrastructure migration

Changing IP/endpoint does not silently change stable node ID if policy says endpoint is mutable.

## T3 — Schema validation

Valid node passes.
Malformed node fails.

## T4 — Node types

All required node types can be represented.

## T5 — Endpoint optionality

Developer/data nodes can omit endpoint where policy allows.

## T6 — Capability declaration

Declared capability remains visibly unverified.

## T7 — Capability verification

Verified evidence can move capability state without modifying unrelated capabilities.

## T8 — Node verification

Valid challenge verifies.
Invalid challenge fails.

## T9 — Verification separation

Verified node endpoint does not automatically verify GPU/storage/data claims.

## T10 — State transitions

Allowed transitions pass.
Illegal skip fails.

## T11 — Heartbeat

Fresh successful heartbeat → healthy.

## T12 — Stale heartbeat

Stale observation results in degraded/inactive according to policy.

## T13 — Recovery

New valid heartbeat can recover degraded/inactive node where lifecycle policy allows.

## T14 — Suspension guard

Heartbeat cannot bypass suspension.

## T15 — Duplicate node

Duplicate stable node identity rejected/merged according to deterministic policy.

## T16 — Location privacy

Public record does not require exact location.

## T17 — Secret rejection

Schemas/output do not accept known secret fields.

## T18 — SSRF safety

Verifier rejects localhost/private-network targets where appropriate for public verification.

## T19 — No remote execution

No SSH/shell/command-execution path exists.

## T20 — No economics

No reward, stake, price, payout or token fields.

## T21 — No chain write

No transaction signing/sending.

## T22 — Offline

Domain tests pass with no internet/RPC/cloud DB.

## T23 — Snapshot determinism

Same node records + same policy → same registry snapshot fingerprint.

## T24 — Regression

Relevant MPF-001/002/003 tests remain green.
