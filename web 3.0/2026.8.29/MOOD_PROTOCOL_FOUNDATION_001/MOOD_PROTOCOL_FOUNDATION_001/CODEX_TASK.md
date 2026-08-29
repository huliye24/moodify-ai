# MOOD Protocol Foundation 001

**Task ID:** MPF-001  
**Stage:** Rough Build / 毛坯  
**Priority:** P0  
**Date:** 2026-08-29  
**CANON_CHANGE:** `YES — protocol authority addition only`  
**Public product identity migration:** `OUT OF SCOPE / HUMAN DECISION REQUIRED`

---

# 1. Why this task exists

The next MOOD systems — Contribution Core, Node Registry, Protocol API, Protocol Web, Transparency and Genesis — all need to agree on the same chain and token facts.

If these facts live independently in environment variables, frontend constants, scripts, docs and deployment notes, MOOD has no stable foundation. A wrong chain ID, token address, treasury address or supply value can make every later layer incorrect.

This task therefore creates the first protocol authority:

> **Mainnet Facts Layer**

It is deliberately narrow.

---

# 2. In scope

## 2.1 Discover current facts

Inspect the current repository and read-only public chain evidence to locate the best available facts for:

- chain family
- network name
- chain ID or cluster identifier
- token contract address / mint address
- token name
- symbol
- decimals
- total supply in atomic units
- treasury public address, if already defined
- genesis pool public address, if already defined
- public RPC endpoint(s), if intentionally public
- block explorer base URL
- explorer token/contract URL pattern
- deploy/source commit evidence
- contract verification/source-verification status, if applicable

Evidence priority:

1. current explicit human instruction;
2. verified deployed chain state / explorer evidence;
3. deployment artifact tied to a commit;
4. current tests and runtime behavior;
5. current Web3 config;
6. current docs;
7. legacy/historical docs.

Never promote an old doc over verified current state.

## 2.2 Create one canonical source

Create:

`protocol/mainnet.json`

using the schema in this package as the starting contract.

It becomes the only authoritative machine-readable source for public MOOD chain/token identity facts.

## 2.3 Create validation

Add a no-secret, no-network-required validation command based on `scripts/validate-mainnet-config.mjs`.

The validator must fail on:

- missing required fields;
- placeholders in a locked config;
- invalid address format for the declared chain family;
- decimals outside safe bounds;
- non-decimal atomic supply strings;
- duplicate/empty RPC entries;
- malformed explorer URL;
- missing evidence references in locked state;
- a locked config with unresolved human decisions.

## 2.4 Create deterministic lock artifact

After facts are verified and `launch.status` is explicitly `locked`, generate:

`protocol/mainnet.lock.json`

The lock must include at least:

- SHA-256 of canonical config bytes;
- source commit;
- token identifier;
- chain identity;
- locked timestamp already recorded in `mainnet.json`;
- schema version.

Do not create a misleading lock file while status is draft.

## 2.5 Reconcile existing consumers

Find all current consumers of chain/token identity facts, including but not limited to:

- frontend/provider config;
- contract client config;
- claim-related config;
- launch runbooks;
- deployment scripts;
- environment templates;
- tests.

For each, classify:

- `CANONICAL_CONSUMER` — derives facts from `protocol/mainnet.json` or a generated adapter;
- `RUNTIME_OVERRIDE` — may override transport-only values such as a public RPC endpoint, but may not redefine token identity;
- `LEGACY` — old value retained only for historical/test use and clearly labeled;
- `CONFLICT` — disagrees with higher-authority evidence.

Do not perform a mass rewrite. Use the smallest compatibility layer that removes ambiguity.

## 2.6 Produce evidence docs

Create:

- `docs/protocol/MAINNET.md`
- `docs/protocol/ADDRESSES.md`
- `docs/protocol/MAINNET_EVIDENCE.md`

These docs must be generated from or manually checked against `protocol/mainnet.json`. They are explanatory surfaces, not independent authority.

---

# 3. Out of scope

Do not implement any of the following in MPF-001:

- Contribution Core;
- Reputation scoring;
- Node Registry;
- Protocol API;
- Genesis claim;
- airdrop distribution;
- token transfers;
- liquidity pool creation or changes;
- market-making;
- price logic;
- DAO/governance;
- staking;
- cross-chain bridge;
- token migration;
- contract upgrade;
- contract redeployment;
- mint/burn;
- new wallet custody;
- UI redesign;
- public launch announcement.

If resolving a fact would require an on-chain write, stop and report it.

---

# 4. Required implementation sequence

## Gate A — Repository authority scan

Read repository authority files before editing.

Produce an internal fact inventory table:

```text
Fact | Candidate Value | Source | Authority | Conflict? | Resolution
```

Search for all references to likely identity inputs such as:

```text
MOOD
CHAIN_ID
RPC
CONTRACT
TOKEN_ADDRESS
MINT
TREASURY
GENESIS
EXPLORER
DECIMALS
TOTAL_SUPPLY
NEXT_PUBLIC_CHAIN_ID
NEXT_PUBLIC_RPC_URL
```

Do not assume filenames from this task package exist in the repository.

## Gate B — Fact conflict resolution

For each required fact:

- if one high-authority value is verified, use it;
- if multiple equal-authority values conflict, mark `HUMAN_DECISION_REQUIRED`;
- if a required fact is absent, mark `HUMAN_DECISION_REQUIRED`;
- never choose a value because it is more convenient for current code.

A draft config is an acceptable result. A guessed locked config is not.

## Gate C — Canonical config implementation

Create `protocol/mainnet.json` and `protocol/mainnet.schema.json`.

Required top-level sections:

```text
schemaVersion
protocol
chain
token
addresses
endpoints
evidence
launch
```

Use string representations for atomic token quantities to avoid integer precision loss.

## Gate D — Consumer reconciliation

Map all duplicated values.

Preferred pattern:

```text
protocol/mainnet.json
        ↓
small adapter / generated constants
        ↓
existing frontend + scripts + docs
```

Do not create another manual constants file that can drift independently.

Runtime environment variables may override connectivity endpoints only when explicitly documented. They must not silently redefine the official token contract/mint, symbol, decimals or chain identity in production.

## Gate E — Validation and lock

Run validation in draft mode.

Only if all required facts are verified and human-decision flags are empty:

1. set `launch.status = "locked"`;
2. record `lockedAt` and `sourceCommit`;
3. run validation again;
4. generate `protocol/mainnet.lock.json`;
5. rerun validation and repository tests/build.

If any required fact remains unresolved:

```text
MAINNET_LOCKED = FALSE
```

and do not manufacture a lock artifact.

## Gate F — Evidence report

Write `docs/protocol/MAINNET_EVIDENCE.md` containing:

- each canonical fact;
- exact repository or public-chain evidence source;
- evidence date;
- confidence/status;
- unresolved conflicts;
- commands used for read-only verification.

No secret material belongs in this document.

---

# 5. Canonical authority rules

After MPF-001:

`protocol/mainnet.json` is authoritative for:

- official MOOD token identity;
- official chain identity;
- public protocol addresses;
- official explorer identity;
- mainnet launch state.

It is **not** authoritative for:

- private RPC credentials;
- private keys;
- deployer secrets;
- database credentials;
- signing infrastructure;
- contributor records;
- node records;
- reputation;
- market price.

---

# 6. Existing repository compatibility

This repository has existing authority rules in root `AGENTS.md`. Current explicit human direction adds a MOOD Protocol foundation, but MPF-001 must not silently rewrite unrelated Moodify Music / Player Canon.

Therefore:

- document the protocol authority addition;
- add a minimal Canon changelog entry if required by repository policy;
- do not mass-edit product wording;
- do not change listening/product state machines;
- do not change audio processing behavior;
- do not delete historical Web3 experiments merely because they differ;
- clearly label superseded config as legacy or remove duplication only when tests prove it is safe.

If the repository requires a broader public-identity decision, emit:

```text
HUMAN_DECISION_REQUIRED: PUBLIC_PROTOCOL_IDENTITY_MIGRATION
```

That decision belongs to a separate task.

---

# 7. Definition of done

MPF-001 is complete when all applicable acceptance gates in `ACCEPTANCE_GATE.md` pass and Codex can truthfully report one of two states:

```text
MAINNET_LOCKED = TRUE
```

or

```text
MAINNET_LOCKED = FALSE
Reason: <specific unresolved evidence/conflict>
```

Both are valid engineering outcomes. False certainty is not.
