# Acceptance Checklist

## A. Git

- [ ] Integration branch exists.
- [ ] 001–008 relevant Web3 files are committed.
- [ ] No secrets committed.
- [ ] Fresh checkout builds.
- [ ] Exact commit SHA recorded.

## B. Canonical Asset

- [ ] Chain = BNB Smart Chain Mainnet.
- [ ] Chain ID = 56.
- [ ] MOOD contract =
  `0x1BB3115D43E397f7bb586F090831B02cA639e73E`.
- [ ] No conflicting active contract address.
- [ ] BscScan link matches the official contract.

## C. Live RPC

- [ ] Real production-grade BSC RPC configured for staging.
- [ ] No localhost RPC in runtime staging config.
- [ ] RPC errors surface explicitly.
- [ ] No silent config fallback masquerading as live data.

## D. Token Reads

- [ ] `decimals()` succeeds.
- [ ] `totalSupply()` succeeds.
- [ ] result formatting respects token decimals.
- [ ] `balanceOf(address)` succeeds.

## E. Wallet

- [ ] Connect works.
- [ ] Disconnect works.
- [ ] Account changes handled.
- [ ] Chain changes handled.
- [ ] Wrong network detected.
- [ ] BSC mainnet recognized.
- [ ] No hidden signing.

## F. Airdrop Safety

- [ ] Distributor is NOT deployed by this package.
- [ ] No MOOD transferred.
- [ ] Claim disabled.
- [ ] No Merkle root write.
- [ ] No distributor funding.
- [ ] No project private key required.

## G. Cloudflare

- [ ] Staging Worker deployed.
- [ ] `test.crestwavecoin.com` resolves.
- [ ] HTTPS works.
- [ ] root `crestwavecoin.com` remains unchanged.
- [ ] staging bindings documented.
- [ ] D1 staging binding isolated if used.
- [ ] R2 staging binding isolated if used.

## H. Public Validation

- [ ] `/token` loads.
- [ ] wallet connect works on public URL.
- [ ] live total supply visible.
- [ ] live wallet MOOD balance visible.
- [ ] network status visible.
- [ ] BscScan link works.
- [ ] no localhost references in browser network calls.
- [ ] no secret visible in browser source/network logs.

## I. Final Decision

Package 009 is complete only when:

```text
PUBLIC URL
+ REAL BSC READ
+ REAL WALLET
+ ZERO ASSET MOVEMENT
```

is proven.
