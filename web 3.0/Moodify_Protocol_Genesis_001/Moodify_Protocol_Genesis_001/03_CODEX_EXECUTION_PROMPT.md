# Codex Execution Prompt

You are executing **Moodify Protocol Genesis 001 — MOOD Protocol Foundation** inside the existing Moodify repository.

Work directly in the repository. Do not create a separate demo project.

## Mission

Turn the existing MOOD BEP-20 token into a first-class, official, verifiable asset inside the Moodify web product by creating a single token configuration authority, an official `/token` page, protocol documentation and tests.

## Hard facts

- Network: BNB Smart Chain
- Chain ID: 56
- Token name: Moodify
- Symbol: Mood
- Contract:
  `0x1BB3115D43E397f7bb586F090831B02cA639e73E`
- Decimals: 18
- Total supply: 33,000,000 MOOD
- Primary DEX: PancakeSwap V3
- Primary pair: MOOD / WBNB
- Fee tier: 1%

## Hard constraints

- CANON_CHANGE = NO
- audit first, edit second;
- preserve existing Moodify UI;
- web-first;
- do not touch Android or Electron;
- do not redeploy or modify the MOOD contract;
- do not create or modify liquidity;
- do not sign wallet transactions;
- do not request or store private keys;
- do not introduce staking, yield, APY, ROI or price promises;
- do not invent allocation percentages;
- do not fabricate pair addresses, token prices, market cap, holder count or volume;
- if a chain fact is not verified, present it as unknown or omit it.

## Required workflow

### Phase A — Audit

1. Read repository instructions and canon.
2. Find the active web app and its routing structure.
3. Find design-system primitives and existing config patterns.
4. Find existing Web3/RPC code.
5. Find tests/build commands.
6. Record baseline git status.
7. If the working tree has unrelated user changes, preserve them.

### Phase B — Implement

1. Create a single MOOD token config source.
2. Add `/token`.
3. Add contract-copy UX.
4. Add BscScan + PancakeSwap official links.
5. Add protocol purpose and risk notice.
6. Add `docs/protocol/MOOD_TOKEN.md`.
7. Add/update navigation only where consistent with current IA.
8. Add tests.

### Phase C — Verify

Run the repository's real:
- lint;
- typecheck;
- tests;
- production build.

Fix only task-related failures.

### Phase D — Report

Return:
1. audit findings;
2. changed files;
3. implementation summary;
4. verification output;
5. screenshots/render evidence if tooling allows;
6. remaining risks;
7. git diff summary;
8. statement:
   `No token contract, liquidity position, wallet signature, or production asset transfer was modified by this task.`

## Stop conditions

Stop and ask for human confirmation if:
- canon requires a conflicting product identity;
- the official token contract differs from the supplied address;
- deployment/signature/payment is required;
- the repository state is unsafe to modify;
- a migration would destroy existing data;
- an external service requires credentials not already available.

Do not work around these stop conditions.
