# Acceptance Criteria
## MOOD-GENESIS-007

### Public page

- [ ] `/transparency` exists.
- [ ] Official MOOD contract shown.
- [ ] BNB Smart Chain shown.
- [ ] Total supply shown and verified/read consistently.
- [ ] BscScan link works.
- [ ] PancakeSwap link works.
- [ ] Treasury/accounts section exists.
- [ ] Genesis section exists.
- [ ] Contribution section exists.
- [ ] Liquidity section exists or explicitly states unavailable.
- [ ] Methodology section exists.
- [ ] Last-updated/source labels exist.

### Accuracy

- [ ] No fabricated market cap.
- [ ] No fabricated price.
- [ ] No fabricated holder count.
- [ ] No fabricated circulating supply.
- [ ] No fabricated treasury address.
- [ ] No fabricated liquidity value.
- [ ] No brainstormed tokenomics percentages published as fact.
- [ ] On-chain values distinguish from DB/snapshot values.
- [ ] Missing data displays unavailable/not published, not zero.

### Treasury config

- [ ] Single treasury config authority exists.
- [ ] Duplicate addresses rejected.
- [ ] Chain ID validated.
- [ ] Invalid addresses rejected.
- [ ] Public/private classification respected.
- [ ] Unapproved account labels not invented.
- [ ] Read-only admin view has no transfer controls.

### Genesis integration

- [ ] Registration aggregate accurate.
- [ ] Allocation aggregate accurate.
- [ ] Snapshot metadata displayed only if approved/public.
- [ ] Claim data prefers on-chain source if deployed.
- [ ] Internal notes/signatures/nonces are not exposed.

### Contribution integration

- [ ] Pending rewards accurate.
- [ ] Included-in-snapshot rewards distinguishable.
- [ ] Distributed rewards distinguishable.
- [ ] Pending rewards are not counted as distributed tokens.

### Accounting

- [ ] Exact token arithmetic.
- [ ] Treasury percentage formatting safe.
- [ ] Balance != allocation explicitly represented.
- [ ] Circulating supply numeric metric disabled unless methodology approved.
- [ ] Reconciliation warnings exist.

### Reliability

- [ ] RPC failure does not become fake zero.
- [ ] DB failure does not become fake zero.
- [ ] stale data labeled if cache fallback used.
- [ ] public endpoint contains no admin/private fields.

### Safety

- [ ] No signer required.
- [ ] No private key required.
- [ ] No token transfer code.
- [ ] No liquidity mutation code.
- [ ] No Safe transaction execution.
- [ ] No contract state write.

### Build

- [ ] Lint.
- [ ] Typecheck.
- [ ] Tests.
- [ ] Production build.
- [ ] `TREASURY.md`.
- [ ] `TRANSPARENCY.md`.
