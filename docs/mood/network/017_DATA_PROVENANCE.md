# MOOD NETWORK 017 — Data Provenance

**Authority:** MOOD-NETWORK-017 TASK.md Phase B

## Source order

1. **In-memory registries** from earlier packages:
   - `ContributionRegistry` (016)
   - `ReputationRegistry` (016)
   - `PendingRewardRegistry` (016)
   - `AuditLog` (016)
2. **Constants** for declared identity (Moodify as Genesis Application).
3. **Future package sources** (`agents`, `nodes`, `mips`) report `coming-soon`.

## What we never read |
- Wallet balances or holdings.
- Chain RPC state.
- DEX volume, liquidity, or token price.
- Holder reward distributions.

## Provenance guarantees

Every `MetricValue.source` field carries one of:
- `contribution-registry:016`
- `reputation-registry:016`
- `pending-reward-registry:016`
- `constant:<name>`
- `package-XXX:pending`

If a metric has no real source, it is reported as `unavailable` or
`coming-soon`, never as a fake number.