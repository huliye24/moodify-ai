# Cloudflare Staging Plan

## Target

`test.crestwavecoin.com`

## Do Not Touch

`crestwavecoin.com`

unless separately approved.

---

## Preferred Deployment Model

```text
Git branch
codex/mood-mainnet-integration-009
        ↓
build
        ↓
Cloudflare Worker
moodify-web3-staging
        ↓
Custom Domain
test.crestwavecoin.com
```

If the repository has an established Cloudflare deployment naming convention, follow it instead of forcing the preferred name.

---

## Required Cloudflare Checks

1. Confirm the zone for `crestwavecoin.com` is active.
2. Confirm no existing Worker owns `test.crestwavecoin.com`.
3. Confirm DNS/custom-domain binding will not replace an unrelated record.
4. Confirm required Worker compatibility flags.
5. Confirm D1 binding requirements.
6. Confirm R2 binding requirements.
7. Confirm environment variable/secret strategy.
8. Confirm build artifact and entrypoint.
9. Confirm rollback procedure before first deployment.

---

## First Public Verification

After deployment:

```text
https://test.crestwavecoin.com
```

Expected state:

```text
Network
BNB Smart Chain

Chain ID
56

MOOD Contract
0x1BB3115D43E397f7bb586F090831B02cA639e73E

Total Supply
LIVE

Wallet
CONNECTABLE

MOOD Balance
LIVE AFTER WALLET CONNECT

Airdrop Claim
DISABLED
```

---

## Rollback

Rollback must be possible without touching the MOOD token.

Preferred rollback:

1. restore previous Worker deployment version;
2. or remove only the staging custom-domain mapping;
3. leave root domain untouched;
4. leave BSC and token state untouched;
5. leave Distributor undeployed.

Document the exact rollback command/process actually used.
