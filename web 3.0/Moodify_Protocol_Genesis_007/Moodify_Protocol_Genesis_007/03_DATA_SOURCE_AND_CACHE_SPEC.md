# Data Source and Cache Specification

### Source priority

#### Token facts
1. Package 001 config
2. on-chain token reads for verification

#### Treasury balances
1. on-chain RPC

#### Genesis registration/review
1. D1/Drizzle

#### Genesis distribution
1. approved Package 004 snapshot
2. Package 005 deployment record
3. on-chain distributor state/events

#### Contribution rewards
1. Package 006 reward ledger

#### Liquidity
1. verified PancakeSwap/BSC contract reads
2. configured verified addresses

### Cache

Use existing application caching conventions.

Suggested freshness:
- token total supply: 5–30 min
- treasury balances: 1–5 min
- Genesis DB aggregates: normal app cache or live DB
- contribution aggregates: normal app cache
- liquidity: 1–5 min where RPC cost permits

Do not introduce a new Redis/service only for this package.

### Failure behavior

If RPC fails:
- keep last-known value only if UI clearly labels it stale;
- otherwise show unavailable;
- do not substitute fake zero.

If DB query fails:
- show section unavailable;
- do not imply zero participants/rewards.

### Timestamping

Expose:

```text
generatedAt
chainReadAt
databaseReadAt
snapshotId
```

where appropriate.

### Public API security

Public transparency endpoint should be read-only and rate-limit/cache friendly.

Never accept arbitrary RPC method forwarding from user input.
