# Moodify Protocol Genesis 007
## Transparency & Treasury

**Package ID:** `MOOD-GENESIS-007`  
**Depends on:** `MOOD-GENESIS-001` → `006`  
**Execution target:** Existing Moodify repository  
**Mode:** Public transparency / treasury classification / chain-read only  
**CANON_CHANGE:** `NO`

This package turns Moodify's token operations into a public, verifiable protocol ledger.

Target public route:

`/transparency`

The page should explain and verify:

- MOOD total supply;
- official token contract;
- Genesis registration/distribution state;
- contribution reward state;
- treasury wallets;
- liquidity wallets/positions where safely discoverable;
- ecosystem reserves;
- contributor/team allocations where publicly approved;
- on-chain balances;
- links to BscScan/PancakeSwap;
- the distinction between **balance**, **allocation**, **circulating supply**, and **treasury reserve**.

## Core principle

Transparency must be factual.

Do not fabricate:
- circulating supply;
- market cap;
- holder count;
- token price;
- treasury ownership;
- liquidity depth;
- wallet labels;
- lock periods;
- vesting schedules.

If a fact is not yet approved or verifiable, show it as:
`Not yet published`
or omit it.

## Safety boundary

Package 007 is **read-only on-chain**.

Codex may:
- query RPC/explorer;
- aggregate public balances;
- build dashboards;
- define treasury configuration;
- generate docs;
- build reconciliation tests.

Codex must not:
- transfer MOOD;
- move treasury assets;
- add/remove liquidity;
- sign transactions;
- create a multisig;
- change token contract state;
- publish invented tokenomics.

Read `01_TASK_SPEC.md` and execute `05_CODEX_EXECUTION_PROMPT.md`.
