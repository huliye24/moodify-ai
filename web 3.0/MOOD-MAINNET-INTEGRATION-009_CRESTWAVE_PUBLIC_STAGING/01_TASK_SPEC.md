# Task Specification
## MOOD-MAINNET-INTEGRATION-009

## 1. Background

The Moodify Web3 Completion Audit classified the current system as:

**Stage B — WEB3 INTEGRATION**

Current known state:

- MOOD token is already deployed on BNB Smart Chain mainnet.
- Official MOOD contract:
  `0x1BB3115D43E397f7bb586F090831B02cA639e73E`
- Token foundation is implemented.
- Genesis registration exists.
- Contribution network exists.
- Merkle distribution engine exists.
- Distributor contract code exists but is not deployed.
- Live chain reads remain incomplete.
- Production RPC is not yet properly configured.
- Public staging does not yet exist.

This package must not expand product scope.

It must convert the existing local Web3 implementation into a public, verifiable, read-only BSC staging deployment.

---

## 2. Primary Outcomes

### Outcome A — Repository Convergence

The local Web3 implementation from Packages 001–008 must become reproducible from Git.

Codex must determine:

- current branch;
- local modified files;
- untracked files;
- Web3 files not present in GitHub `main`;
- whether the 001–008 implementation is committed;
- whether any secrets exist in local `.env*`.

The implementation must be placed on a dedicated staging/integration branch.

Preferred branch:

`codex/mood-mainnet-integration-009`

Do not directly overwrite `main`.

---

### Outcome B — Real BSC Read Layer

Replace placeholder or config-only chain reads with a real BSC mainnet read client.

Required live reads:

- chain ID;
- MOOD `totalSupply()`;
- MOOD `decimals()`;
- connected wallet MOOD `balanceOf(address)`.

If additional safe read-only fields already exist in the app, Codex may preserve them.

Do not add speculative protocol features.

---

### Outcome C — Public Cloudflare Staging

Deploy the Web app to Cloudflare staging and bind:

`test.crestwavecoin.com`

The root domain:

`crestwavecoin.com`

must not be repointed unless separately approved by the human owner.

---

### Outcome D — Wallet Readiness

A public user must be able to:

- connect a compatible EVM wallet;
- detect BSC mainnet;
- receive a wrong-network message if not on chain ID 56;
- switch network only through an explicit wallet/user action;
- read their MOOD balance.

No automatic signing.
No automatic transactions.
No asset movement.

---

## 3. Explicit Non-Goals

This package must not:

- deploy `MoodGenesisDistributor`;
- set a Merkle root on-chain;
- transfer MOOD;
- fund a distributor;
- move treasury assets;
- request a private key;
- store a seed phrase;
- run claim transactions;
- enable production airdrop claims;
- modify the MOOD token contract;
- alter token ownership;
- change liquidity;
- create staking;
- create token sale functionality;
- change `crestwavecoin.com` root domain unless separately approved;
- delete existing Web2 / music product functionality merely to simplify deployment.

---

## 4. Architecture Rule

The chain source of truth must become:

```text
Web UI
  ↓
typed chain client
  ↓
BSC RPC
  ↓
MOOD contract
```

Configuration may define:

- chain ID;
- contract address;
- explorer base URL;
- RPC endpoint configuration.

Configuration must not impersonate live chain state for:

- balances;
- total supply;
- claim state;
- distributor state.

If RPC is unavailable, the UI must show:

`UNAVAILABLE`

or an equivalent explicit state.

It must not silently show cached/config fallback data as if it were live.

---

## 5. Canonical MOOD Asset

For this package, use:

```text
Chain: BNB Smart Chain Mainnet
Chain ID: 56
Contract: 0x1BB3115D43E397f7bb586F090831B02cA639e73E
```

Codex must scan the repository for conflicting MOOD contract addresses or conflicting chain definitions.

Any conflict must be reported before deployment.

Do not silently replace historic references if their purpose is archival.

---

## 6. Public Staging Boundary

The first staging release is:

**PUBLIC INTERNET + REAL BSC READS + ZERO ASSET MOVEMENT**

The following routes may remain public if already implemented:

- `/token`
- `/genesis`
- `/contribute`
- `/transparency`

The `/airdrop` route may be visible only if it cannot execute a real claim.

If there is any ambiguity, disable or gate the write path and clearly label:

`Claims are not enabled in this staging release.`

---

## 7. Cloudflare Deployment

Current repository already contains Cloudflare-oriented Web infrastructure under `apps/web`.

Codex must preserve repository conventions.

Expected checks include:

- `apps/web/package.json`
- Cloudflare Vite plugin
- Wrangler
- worker entrypoint
- D1 bindings
- R2 bindings
- build scripts
- current GitHub Actions behavior

Do not assume the existing workflow actually deploys merely because its filename is `deploy.yml`.

Verify its behavior.

---

## 8. Database

If Genesis registration or contribution features require D1, create or bind a staging database only if required for the public staging build.

Do not point staging to a production database without explicit human approval.

Preferred naming:

`moodify-web3-staging`

or repository-native equivalent.

Schema migrations must be reversible and recorded.

---

## 9. Required Final Artifacts

Codex must produce or update:

1. staging environment documentation;
2. chain integration documentation;
3. Cloudflare deployment procedure;
4. validation report;
5. list of environment variable names;
6. rollback instructions;
7. exact Git branch and commit used for staging.

Do not put secrets in these files.
