# MPF-005 Test Plan

## T1 — Health

Health endpoint returns versioned envelope and dependency states.

## T2 — Mainnet facts authority

Mainnet response is sourced from MPF-001, not route constants.

## T3 — Contributions

List and detail use MPF-002 authority.

## T4 — Reputation

Profile/reputation uses MPF-003 and preserves `aggregate = null`.

## T5 — Nodes

Node endpoints use MPF-004 authority.

## T6 — Capability verification

Declared and verified capability states remain distinguishable.

## T7 — Network summary

Counts are deterministic from fixture inputs.

## T8 — Network snapshot

Same authority inputs produce same snapshot fingerprint.

## T9 — Pagination

Invalid/oversized page request is rejected or bounded safely.

## T10 — Filter validation

Unknown unsafe filter is rejected.

## T11 — Sort allowlist

Arbitrary sort field cannot reach data layer.

## T12 — Not found

Missing resource returns standardized NOT_FOUND.

## T13 — Private field exclusion

Secrets/internal fields cannot appear in public DTOs.

## T14 — Error hygiene

No stack trace or internal exception leaks.

## T15 — Request ID

Every response contains request ID.

## T16 — API version

Every response identifies v1.

## T17 — Domain delegation

Route handler cannot bypass canonical domain service in tests/review.

## T18 — No chain writes

No transaction signing/sending path.

## T19 — No token transfer

No token payout/claim/mint/transfer route.

## T20 — No RCE

No shell/SSH/job-execution route.

## T21 — CORS/auth

Production defaults do not expose credentialed wildcard CORS.

## T22 — Offline

Core/API tests can run with local fixture adapters.

## T23 — OpenAPI/schema

Generated/documented API contract exists.

## T24 — Regression

Relevant MPF-001–004 tests remain green.
