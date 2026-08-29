# Test Plan

## T1 — Schema validation

Valid fixture passes.
Malformed contributor fails.
Missing required evidence fails when policy requires evidence.

## T2 — Canonical normalization

Equivalent JSON with different key order yields the same canonical normalized representation.

## T3 — Fingerprint determinism

Same immutable input yields same fingerprint over repeated runs.

## T4 — Fingerprint sensitivity

Changing material contribution content changes fingerprint.

## T5 — Duplicate prevention

Same contributor + same category + same fingerprint is rejected unless superseding is explicitly valid.

## T6 — Cross-contributor duplicate flag

Identical content under a different contributor is flagged for review.

## T7 — State transition

Allowed transitions pass.
Skipped or illegal transitions fail.

## T8 — Score guard

Attempting to score `draft`, `submitted` or `under_review` fails.

## T9 — Evidence guard

A record with no valid evidence cannot become verified.

## T10 — Policy pinning

A score created under policy version A cannot silently be recomputed under policy version B without creating a new result/version.

## T11 — Finalization immutability

Any in-place edit of finalized immutable content fails.

## T12 — Reputation evidence determinism

Same inputs and policy produce the same artifact content except fields explicitly excluded from artifact fingerprinting.

## T13 — Economic-field prohibition

Core output rejects or excludes fields such as:
- tokenAmount
- payout
- claimAmount
- vesting
- price

## T14 — No chain writes

Static scan and/or mocks demonstrate there is no signing or transaction-send path in the MPF-002 implementation.

## T15 — Offline operation

Core unit tests pass without Cloudflare, RPC, D1 or internet access.

## T16 — Fixtures

At least ten fixtures described in `CODEX_TASK.md` are covered.
