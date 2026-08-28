# Codex Execution Prompt

Execute **Moodify Protocol Genesis 007 — Transparency & Treasury** inside the existing Moodify repository.

## Dependencies

Confirm Packages 001–006 or equivalent foundations.

Official MOOD:

- Network: BNB Smart Chain
- chainId: 56
- Token: Moodify / Mood
- Contract: `0x1BB3115D43E397f7bb586F090831B02cA639e73E`
- Decimals: 18
- Total supply expected: 33,000,000 MOOD

Verify chain-readable values where appropriate.

## Mission

Build a factual, public, read-only transparency layer for protocol assets.

Create:

`/transparency`

Optionally:

`/admin/treasury`

read-only only.

## Mandatory audit before editing

1. Read repository instructions/canon.
2. Inspect git status and preserve unrelated work.
3. Reuse Package 001 MOOD config authority.
4. Inspect Genesis DB schemas.
5. Inspect Package 004 snapshot artifacts/schema.
6. Inspect Package 005 deployment record/config.
7. Inspect Package 006 reward ledger.
8. Inspect existing RPC/Web3 read stack.
9. Inspect caching/fetch conventions.
10. Inspect current public UI/design system.
11. Identify any already-approved treasury wallet labels.
12. Identify any approved token allocation/circulating methodology.

Never infer a treasury label from wallet size alone.

## Build

### 1. Treasury config authority

Create repository-consistent equivalent of:

`mood-treasury.ts`

Support approved public accounts only.

Safe empty-state required.

### 2. Read-only chain service

Implement typed reads for:
- totalSupply;
- configured account balanceOf;
- distributor balance where configured;
- relevant liquidity facts only if safely verifiable.

No signer.

No write client.

### 3. Public transparency aggregation

Build a server-side aggregation layer and optional API:

`GET /api/protocol/transparency`

Return safe data only.

Every metric must carry enough metadata to distinguish:
- on-chain;
- DB;
- snapshot;
- configured;
- derived.

### 4. `/transparency`

Sections:
- protocol asset;
- supply/accounting;
- treasury accounts;
- Genesis;
- contribution network;
- liquidity;
- methodology.

Use calm Moodify design language.

### 5. Circulating supply

If no approved methodology exists:
- do not show a number;
- show methodology status as not yet published/approved.

Do not invent one.

### 6. Allocation visualization

Only show approved/current factual balances or approved allocation policy.

Do not use brainstormed percentages from previous discussions unless found in repository canon with explicit approval.

### 7. Reconciliation

Implement warnings for:
- config mismatch;
- duplicate addresses;
- stale/unavailable reads;
- snapshot/distributor mismatch;
- DB/chain distribution mismatch where detectable.

Do not silently rewrite values.

### 8. Docs

Create:
- `docs/protocol/TREASURY.md`
- `docs/protocol/TRANSPARENCY.md`

## Hard prohibitions

Do not:
- send MOOD;
- construct transfer UI;
- add/remove liquidity;
- create a Safe;
- propose Safe transactions;
- sign anything;
- request private keys;
- publish market cap/FDV from guessed price;
- publish circulating supply without approved methodology;
- label a wallet "team/founder/treasury" without approved config;
- fabricate lock/vesting status.

## Tests

At minimum:

- official contract config consistency;
- totalSupply exactness;
- treasury address validation;
- duplicate treasury address guard;
- empty treasury config;
- RPC failure state;
- stale cache state;
- Genesis aggregate;
- contribution aggregate;
- pending != distributed;
- public API privacy;
- circulating supply disabled when methodology draft;
- exact percentage arithmetic;
- no signer/write client imported in transparency module;
- no transfer action in admin view.

Run:
- lint;
- typecheck;
- tests;
- production build.

## Completion output

Return:

1. audit findings;
2. approved treasury labels discovered;
3. unapproved/missing treasury decisions;
4. data-source architecture;
5. public API schema;
6. `/transparency` screenshots;
7. reconciliation output;
8. tests/build;
9. files changed;
10. git diff summary;
11. exact safety statement:

`No MOOD token transfer, wallet signature, treasury transaction, liquidity mutation, smart-contract state write, or private-key handling was performed by this task.`

## Stop conditions

Stop for human confirmation if:
- a wallet must be publicly labeled but no approved classification exists;
- circulating supply methodology must be published but is not approved;
- token allocation percentages are requested but not canon-approved;
- write/signing credentials are requested;
- a destructive migration is required;
- canon conflict exists.
