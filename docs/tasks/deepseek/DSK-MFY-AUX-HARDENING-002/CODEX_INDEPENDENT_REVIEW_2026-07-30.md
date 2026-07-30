# DSK-MFY-AUX-HARDENING-002 — Codex Independent Review

**Date:** 2026-07-30  
**Reviewer:** Codex  
**Decision:** REWORK  
**Worker state preserved:** yes, pending local recovery checkpoint

## Verified Evidence

Codex independently executed:

```text
python -m pytest moodify_runtime/tests/test_craft_proposals.py moodify_runtime/tests/test_atomic_pair_writer.py moodify_runtime/tests/test_historical_compatibility.py -q
```

Result: exit 0; 96 passed in 9.41 seconds.

This proves the submitted focused tests pass in the current environment. It does not prove the declared interruption, deterministic-retry, or idempotent-promotion invariants.

## P0 — Craft Promotion Is Not Crash-Idempotent

### Reproduction

Inject an I/O failure after `craft_records.jsonl` is appended but before the proposal file is updated to `promoted`, then retry the same promotion.

### Observed result

`promotion_records_after_retry 2`

### Cause

`promote_proposal_to_craft()` appends the approved record before persistently recording proposal promotion. A failure between those writes leaves the proposal eligible for a second append. The replay guard only works after the proposal update succeeds.

### Required correction

Use a durable idempotency identity derived from the proposal and enforce it against the authoritative Craft store before append, with crash/retry tests at every write boundary. The evidence payload must also be structurally validated rather than accepted solely for being non-empty.

## P0 — AtomicPairWriter Can Expose an Incomplete Current Pair

### Reproduction

Start with a complete old pair. Inject `OSError` on the second staged-to-current move.

### Observed result

```text
files ['summary.json', 'summary.json.prev', 'summary.md.prev']
json: new generation
md: MISSING
recover: None
```

### Cause

The exception path deletes the transaction marker and staging directory even after partial promotion. Recovery then has no durable transaction state from which to complete or roll back. Two independent pathname replacements are not an atomic pair for direct readers.

### Required correction

Use generation directories plus one atomically replaced current-pointer/manifest, or an equivalent reader-mediated commit protocol. Preserve the transaction marker until commit or rollback completes. Add real fault injection inside `write()` before first promotion, between promotions, and after promotion before cleanup. Assert the public reader always resolves a complete generation.

## P1 — Historical Migration Is Not Deterministically Repeatable

### Reproduction

Migrate the identical source twice into separate target directories.

### Observed result

```text
migration_repeatable False
```

### Cause

The target embeds a random UUID treatment ID and current migration timestamp. Therefore identical source, version, and tool inputs produce different target bytes and hashes.

### Required correction

Define the intended repeatability contract. Prefer a deterministic treatment identity derived from stable source identity and an idempotent migration policy. If event timestamps are required, separate the migration event envelope from the canonical migrated payload and test both contracts explicitly.

## Gate Decision

- Batch A: REWORK — namespace isolation exists, but promotion retry can duplicate approved knowledge.
- Batch B: REWORK — focused tests pass, but the declared core interruption guarantee is false.
- Batch C: REWORK — load and preservation coverage exists, but deterministic retry is not satisfied.

No Mainline, `VERIFIED`, `PRODUCTION-PROVEN`, or Annual Stable claim is authorized. Preserve the current implementation as a recovery checkpoint, then fix in P0/P1 order and rerun independent acceptance.
