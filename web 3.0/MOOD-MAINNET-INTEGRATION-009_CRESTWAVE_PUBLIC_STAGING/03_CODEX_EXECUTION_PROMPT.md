# Codex Execution Prompt
## MOOD-MAINNET-INTEGRATION-009

You are working inside the Moodify repository.

Your job is to complete the first public Web3 staging integration for MOOD.

Read these package files first:

1. `00_README.md`
2. `01_TASK_SPEC.md`
3. `02_EXECUTION_PLAN.md`
4. `04_SECURITY_GATES.md`
5. `05_ACCEPTANCE_CHECKLIST.md`
6. `06_ENVIRONMENT_TEMPLATE.md`
7. `07_CLOUDFLARE_STAGING.md`
8. `08_FINAL_REPORT_TEMPLATE.md`

---

## Known Inputs

Repository:

`huliye24/moodify-ai`

Cloudflare staging domain:

`test.crestwavecoin.com`

Official chain:

BNB Smart Chain Mainnet

Chain ID:

`56`

Official MOOD contract:

`0x1BB3115D43E397f7bb586F090831B02cA639e73E`

---

## Core Mission

Convert the existing local Packages 001–008 Web3 implementation into a public staging deployment with real BSC read-only integration.

The public staging site must read real MOOD chain state.

It must not move assets.

---

## Mandatory Execution Order

### Step 1 — Audit local state

Before any code edits:

- inspect Git;
- locate Packages 001–008 implementation;
- locate Web3 routes;
- locate MOOD contract config;
- locate `mood-chain.ts` or equivalent;
- locate wallet implementation;
- locate Cloudflare worker/build config;
- locate D1/R2 usage;
- locate localhost and local RPC dependencies;
- scan for secrets.

Write a short preflight note before editing.

### Step 2 — Create integration branch

Use:

`codex/mood-mainnet-integration-009`

unless an equivalent branch already exists.

Do not modify `main` directly.

### Step 3 — Make local Web3 reproducible

Ensure the relevant 001–008 implementation is represented on the integration branch.

Do not blindly add generated files or local caches.

### Step 4 — Implement real read-only BSC integration

Replace placeholder chain reads with a real typed RPC client.

Preferred library: `viem`, if compatible.

Required live reads:

- chain ID;
- MOOD decimals;
- MOOD total supply;
- connected wallet MOOD balance.

Do not implement asset-moving write methods.

### Step 5 — Wallet UX

Ensure:

- wallet connection;
- BSC detection;
- wrong-network state;
- disconnect;
- account and chain changes;
- safe failure.

### Step 6 — Disable dangerous write surface

Airdrop claim must not be executable in this package.

If `/airdrop` is public, it must clearly indicate staging/read-only status.

### Step 7 — Build and test

Run repository-native build/tests.

Do not weaken tests merely to make them pass.

### Step 8 — Cloudflare staging

Deploy only the staging target.

Bind:

`test.crestwavecoin.com`

Do not repoint:

`crestwavecoin.com`

### Step 9 — Public verification

Verify live chain reads from the public deployment.

### Step 10 — Report

Produce a final report using `08_FINAL_REPORT_TEMPLATE.md`.

---

## Absolute Restrictions

Do not:

- ask for a private key;
- ask for a seed phrase;
- store wallet credentials;
- deploy MoodGenesisDistributor;
- transfer MOOD;
- fund any contract;
- call claim;
- change liquidity;
- change token ownership;
- rename or redeploy MOOD;
- merge to `main` without human approval;
- change `crestwavecoin.com` root domain;
- silently fall back to config values when RPC is unavailable.

---

## Stop Conditions

Stop and report immediately if:

1. official MOOD contract differs across active production code;
2. secret material is tracked;
3. staging deployment would require real private-key custody;
4. Cloudflare deployment would overwrite an unrelated production Worker;
5. D1 migration would mutate an existing production database;
6. current local Web3 state cannot be reconstructed safely;
7. airdrop claim cannot be disabled without risking a real transaction.

---

## Final Chat Response

Return only:

1. branch name;
2. commit SHA;
3. staging URL;
4. live chain read status;
5. wallet status;
6. Cloudflare deployment status;
7. P0 blockers;
8. P1 blockers;
9. files changed;
10. final report path.

Do not begin Package 010.
