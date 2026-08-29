# Protocol Read Model

## Purpose

Build query-optimized projections from authoritative modules.

## Network summary

Suggested minimum:

```text
protocol status
contributors count
contributions total
contributions verified/finalized
node count
active node count
node type distribution
public region distribution
reputation profile count
snapshot count
generated timestamp
```

## Excluded from core summary

Do not include by default:

```text
token price
market cap
trading volume
wallet wealth ranking
node earnings
contributor token balance
```

Those are economic/market read models and are not part of MPF-005.

## Provenance

Where practical, expose source version references:

```json
{
  "sources": {
    "mainnet": "mpf-001-lock-fingerprint",
    "contributionPolicy": "002-...",
    "reputationPolicy": "003-...",
    "nodeRegistryPolicy": "004-..."
  }
}
```

This makes the public Transparency layer auditable.
