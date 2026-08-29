# MOOD Protocol Foundation 001 — START HERE

**Package:** `MOOD_PROTOCOL_FOUNDATION_001`  
**Purpose:** Build the rough foundation of the MOOD Protocol mainnet facts layer.  
**Target repository:** `huliye24/moodify-ai`  
**Recommended base branch:** `codex/mood-mainnet-integration-009`  
**Recommended work branch:** `codex/mood-protocol-foundation-001`

## One-line mission

Create **one canonical, machine-readable, auditable source of truth** for MOOD mainnet facts, then make existing Web3 consumers read from or reconcile against it.

This package does **not** deploy contracts, move tokens, add liquidity, distribute MOOD, build Contribution Core, build Node Registry, or redesign the website.

---

## Paste this to Codex

```text
Execute MOOD Protocol Foundation 001.

Repository: huliye24/moodify-ai
Base branch: codex/mood-mainnet-integration-009
Create/use work branch: codex/mood-protocol-foundation-001

First read, in order:
1. AGENTS.md
2. docs/canon/CURRENT_CANON.md
3. docs/canon/PRODUCT_BOUNDARY.md
4. docs/canon/AUTHORITY_ORDER.md
5. docs/REPOSITORY_STATUS.md
6. this package: START_HERE.md
7. this package: CODEX_TASK.md
8. this package: ACCEPTANCE_GATE.md
9. this package: SECURITY_BOUNDARY.md

Goal: create a single canonical mainnet facts layer for MOOD, with evidence, schema validation, a deterministic lock artifact, and compatibility with existing Web3 consumers.

Critical constraints:
- READ-ONLY chain inspection only.
- NO deploy.
- NO contract write.
- NO mint/burn/transfer.
- NO liquidity operation.
- NO wallet signing.
- NO private keys or seed phrases.
- Do not guess chain, token address/mint, decimals, supply, treasury, genesis pool, RPC, explorer, or ownership facts.
- If authoritative evidence conflicts or is incomplete, emit HUMAN_DECISION_REQUIRED and leave launch.status=draft.
- Do not silently rewrite Moodify product Canon. This task adds protocol infrastructure authority only; any broader public-identity migration must be separately documented and approved.

Implement the task completely, run the acceptance gates, and end with a concise execution report containing:
- files added/modified
- discovered canonical facts + evidence source
- conflicts/unresolved facts
- validation output
- tests/build output
- whether MAINNET_LOCKED is TRUE or FALSE
- exact reason if FALSE
- next safe task
```

---

## Expected outcome

At the end of this package, the repository should have a stable foundation resembling:

```text
protocol/
├── mainnet.json              # single canonical fact source
├── mainnet.schema.json       # machine-readable contract for that source
└── mainnet.lock.json         # only created after lock gate passes

scripts/
├── validate-mainnet-config.mjs
└── generate-mainnet-lock.mjs

docs/protocol/
├── MAINNET.md
├── ADDRESSES.md
└── MAINNET_EVIDENCE.md
```

Existing public runtime consumers should either consume this canonical source directly or use a thin generated/compatibility adapter. There must not be a second independent set of chain/token identity constants.

---

## Success sentence

When this package is done, we should be able to say:

> **MOOD has one mainnet truth, and every later protocol module can build on it.**
