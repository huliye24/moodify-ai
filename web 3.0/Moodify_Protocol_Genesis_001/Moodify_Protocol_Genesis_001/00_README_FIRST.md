# Moodify Protocol Genesis 001
## MOOD Protocol Foundation

**Package ID:** `MOOD-GENESIS-001`  
**Execution target:** Moodify main repository  
**Mode:** Web-first / audit-first / minimal-change  
**CANON_CHANGE:** `NO`

This package is the first engineering package for turning MOOD from a deployed BEP-20 token into an official, verifiable protocol asset inside the Moodify web product.

### Primary outcome

Ship one public source of truth for MOOD:

`/token`

The page must clearly answer:

1. What is MOOD?
2. What chain is it on?
3. What is the official contract?
4. What is the total supply?
5. Where can the contract be verified?
6. Where can the token be traded?
7. What is the relationship between MOOD and Moodify?
8. What risks should a user understand?

### Non-goals

This task does **not**:
- create a new token;
- modify the MOOD contract;
- modify liquidity positions;
- deploy a new smart contract;
- build airdrop claiming;
- add wallet registration;
- introduce token staking;
- add price promises or investment language;
- modify Android / Electron products.

### Execution rule

Codex must audit the repository before editing. Existing architecture, routing, styles, database conventions and configuration patterns take priority over guessed paths in this package.

Read `01_TASK_SPEC.md` first, then follow `03_CODEX_EXECUTION_PROMPT.md`.
