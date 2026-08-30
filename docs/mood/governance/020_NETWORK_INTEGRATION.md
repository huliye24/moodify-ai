# 020 — Network Integration

How MIP Governance integrates with the `/network` Observatory and the
public Activity Feed.

## Metrics

The Network Observatory exposes the following MIP metrics. All read from
`mipRegistry.counts()` (real source, not fabricated).

| Metric | Source | Definition |
| --- | --- | --- |
| `mips` | `mip-registry:020` | Total MIPs (any status, including MIP-000). |
| `mipsInDiscussion` | `mip-registry:020` | MIPs currently in Discussion. |
| `mipsInReview` | `mip-registry:020` | MIPs currently in Review. |
| `mipsAccepted` | `mip-registry:020` | MIPs accepted but not yet Implemented. |
| `mipsImplemented` | `mip-registry:020` | MIPs Implemented. |
| `mips.byCategory.*` | `mip-registry:020` | Per-category breakdown. |

These metrics are surfaced in the existing `NetworkOverview.metrics` object
and the existing `/api/network/overview` route.

## Activity Feed

The Network Observatory activity feed includes the following event types
sourced from the MIP registry:

| Event | When |
| --- | --- |
| `MIPPublished` | A new MIP is created (any status from draft). |
| `MIPAccepted` | A MIP's status transitions to `accepted`. |
| `MIPImplemented` | A MIP's status transitions to `implemented`. |
| `MIPReviewStarted` | A MIP transitions to `review` (planned, not yet emitted). |

`taskSlug` is set to the lowercased MIP id (e.g. `mip-001`). This is
cosmetic; the network feed does not link to canonical task records.

## INV-020-11 Satisfied

`Network Observatory.mips()` (and the related `mipsInDiscussion` etc.)
read from `mipRegistry.counts()`. The metric value is the real total /
breakdown. No fabrication.

## INV-020-12 Satisfied

The MIP registry and its metrics do not depend on Token / chain / RPC
configuration. The registry is in-memory. The public surface is JSON. No
private key material or chain config is loaded.

## What 020 Does NOT Add to `/network`

- Token-vote turnout.
- Quorum math.
- On-chain governance activity.
- DAO delegation metrics.

These belong to 025 (Token Activation) and beyond.
