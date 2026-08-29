# W01-P04 Handoff

P03 freezes the data identity backbone.

P04 must not redefine:

- Track ID
- Job ID
- Object ID
- source hash semantics
- provenance semantics
- object storage vs DB responsibility

unless a P03 defect is proven.

## P04 receives

- selected metadata DB adapter
- selected object storage adapter
- data model
- object key convention
- invariants
- migration state
- provenance contract
- tests

## P04 question

> How does a Job move through one authoritative state machine with lease, retry, recovery, idempotency and evidence?
