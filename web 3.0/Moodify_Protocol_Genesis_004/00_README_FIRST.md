# Moodify Protocol Genesis 004
## Distribution Engine

**Package ID:** `MOOD-GENESIS-004`  
**Depends on:** `MOOD-GENESIS-001`, `MOOD-GENESIS-002`, `MOOD-GENESIS-003`  
**Execution target:** Existing Moodify repository  
**Mode:** Deterministic snapshot / export / Merkle preparation / no token transfer  
**CANON_CHANGE:** `NO`

This package turns the reviewed Genesis participant database into a reproducible distribution artifact set.

Target pipeline:

`Genesis Admin`
→ select eligible/allocated participants
→ freeze deterministic snapshot
→ validate wallet/allocation integrity
→ export CSV/JSON
→ generate Merkle tree + root
→ create human-readable distribution report
→ generate checksums
→ STOP before any token transfer or claim deployment

This package is the bridge between **off-chain allocation decisions** and the later on-chain airdrop package.

## Primary outcome

Create a deterministic command such as:

`npm run genesis:snapshot`

that produces:

```text
artifacts/genesis/<snapshot-id>/
├── snapshot.json
├── distribution.csv
├── merkle.json
├── distribution-report.md
├── checksums.txt
└── manifest.json
```

The same database state + same config + same source revision must produce the same participant ordering, allocation totals, Merkle root and canonical artifacts.

## Safety boundary

Codex must not:
- transfer MOOD;
- approve MOOD;
- sign a wallet transaction;
- deploy an airdrop contract;
- fund a distributor;
- publish a production Merkle root without human approval;
- access a private key.

Read `01_TASK_SPEC.md` first, then execute `05_CODEX_EXECUTION_PROMPT.md`.
