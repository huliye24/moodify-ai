# Moodify Protocol Genesis 005
## Merkle Airdrop

**Package ID:** `MOOD-GENESIS-005`  
**Depends on:** `MOOD-GENESIS-001` → `004`  
**Execution target:** Existing Moodify repository  
**Mode:** Smart-contract + claim UI + deployment preparation  
**CANON_CHANGE:** `NO`

This package is the first stage that can produce a real on-chain distribution mechanism.

Target flow:

`approved Package 004 snapshot`
→ human approves Merkle root
→ deploy MoodGenesisDistributor
→ fund distributor with approved MOOD amount
→ publish `/airdrop`
→ eligible participant connects wallet
→ frontend loads proof
→ participant submits `claim`
→ contract verifies proof
→ MOOD is transferred
→ claim event is indexed/displayed

## Critical execution boundary

Codex may:
- write Solidity;
- write Foundry tests;
- generate deployment scripts;
- generate BscScan verification commands;
- build `/airdrop`;
- consume Package 004 artifacts;
- simulate deployment and claims;
- prepare transaction calldata;
- produce a deployment runbook.

Codex must **not**:
- access private keys;
- sign production deployment;
- transfer production MOOD;
- fund the distributor automatically;
- publish a production Merkle root without explicit human approval;
- change the MOOD token contract;
- alter PancakeSwap liquidity.

The execution principle is:

**AI writes. AI verifies. Human signs.**

Read all package files before implementation.
