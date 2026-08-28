# Execution Plan

## Gate 0 — Preflight

Before changing code:

1. Run `git status`.
2. Record current branch and HEAD.
3. Identify local 001–008 Web3 files.
4. Identify files absent from GitHub `main`.
5. Check `.gitignore`.
6. Scan tracked and untracked files for accidental secrets.
7. Identify build command and test command.
8. Identify Cloudflare configuration and bindings.
9. Identify all references to the MOOD contract.
10. Identify all localhost / local RPC dependencies.

If any private key, seed phrase, or real signing secret is found:

**STOP — P0 SECRET EXPOSURE**

Do not continue deployment.

---

## Gate A — Git Convergence

Goal:

> The local Web3 state must be reproducible from Git.

Actions:

- create/switch to:
  `codex/mood-mainnet-integration-009`
- preserve all unrelated work;
- commit only the required Web3 integration changes;
- do not force-push;
- do not rewrite `main`;
- record commit SHA.

Pass condition:

A fresh checkout of the staging branch can reproduce the Web3 app build.

---

## Gate B — Chain Integration

Goal:

> Read real MOOD state from BSC mainnet.

Implement a typed read-only chain layer.

Preferred approach:

- use `viem` if compatible with the repository;
- avoid mixing multiple EVM libraries unless necessary;
- centralize MOOD ABI and contract address;
- centralize chain config.

Minimum contract ABI required:

```solidity
function totalSupply() view returns (uint256)
function decimals() view returns (uint8)
function balanceOf(address account) view returns (uint256)
```

Do not add write functions merely for convenience.

Pass conditions:

- chain ID 56 detected;
- `decimals()` read succeeds;
- `totalSupply()` read succeeds;
- `balanceOf()` works for a valid wallet address;
- network/RPC errors are explicit.

---

## Gate C — Wallet Integration

Goal:

> Public browser wallet connectivity without asset movement.

Required:

- connect;
- disconnect;
- reconnect behavior if already supported;
- account change handling;
- chain change handling;
- BSC mainnet detection;
- explicit wrong-network state;
- explicit user action for wallet network switch.

Forbidden:

- auto-sign;
- auto-send;
- hidden signature;
- hidden transaction;
- claim write.

---

## Gate D — Cloudflare Staging

Goal:

> Public deployment at `test.crestwavecoin.com`.

Codex must:

1. verify build works;
2. verify Cloudflare worker compatibility;
3. define required non-secret env values;
4. define required secret env names without exposing values;
5. deploy staging Worker;
6. bind staging custom domain;
7. leave `crestwavecoin.com` root untouched;
8. record Worker name and deployment version.

Preferred worker name:

`moodify-web3-staging`

If existing repository naming conventions conflict, follow the repository.

---

## Gate E — Public Validation

Test from the public URL.

Required checks:

```text
GET /
GET /token
GET /genesis
GET /contribute
GET /transparency
```

Where relevant.

Then validate:

- TLS works;
- no localhost dependency;
- no mixed content;
- BSC RPC reachable;
- contract address correct;
- totalSupply live;
- wallet connect works;
- wrong-network UX works;
- MOOD balance live;
- BscScan link correct;
- no claim transaction available;
- no secrets in browser bundle.

---

## Gate F — Freeze

After validation:

- record exact commit SHA;
- record Cloudflare deployment version;
- record staging URL;
- write validation report;
- do not merge to `main` unless explicitly approved;
- do not proceed to Distributor deployment.
