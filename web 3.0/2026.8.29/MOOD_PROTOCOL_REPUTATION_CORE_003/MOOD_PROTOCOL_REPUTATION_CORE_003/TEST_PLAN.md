# MPF-003 Test Plan

## T1 — Stable protocol ID

Same normalized public identity → same protocol ID.

## T2 — Identity normalization

Equivalent normalized wallet/public identity forms do not create duplicate profiles.

## T3 — Eligible contribution filter

Only approved MPF-002 scored/finalized inputs count.

## T4 — Rejected input exclusion

Rejected or unverified contribution does not increase reputation.

## T5 — Duplicate input

Same contribution/fingerprint cannot be counted twice.

## T6 — Dimension aggregation

Dimension values aggregate deterministically under the active policy.

## T7 — Missing weights

If weights are not approved:
- dimensions exist
- aggregate = null
- no invented aggregate

## T8 — Policy pinning

Historical snapshot remains tied to original policy version.

## T9 — Epoch determinism

Same timestamp always resolves to the same epoch under the same epoch policy.

## T10 — Persistence insufficient history

One contribution cannot produce unjustified persistence.

## T11 — Multi-epoch persistence

Multiple valid separated epochs produce deterministic persistence evidence if policy supports it.

## T12 — Identity link verified

Valid public evidence can create a verified identity link.

## T13 — Identity link inconclusive

Weak similarity does not merge identities.

## T14 — Snapshot determinism

Same inputs + same policies → same snapshot fingerprint.

## T15 — Snapshot mutation

In-place mutation after finalization fails.

## T16 — Supersede

New snapshot can supersede old snapshot without deleting history.

## T17 — Economic isolation

No output contains:
- tokenAmount
- claimAmount
- votingPower
- stakingWeight
- payout
- vesting

## T18 — Chain isolation

No transaction signing/sending path exists.

## T19 — Offline

Tests run without:
- internet
- D1
- RPC
- wallet

## T20 — Regression

Relevant MPF-002 tests still pass.
