# Moodify Protocol Genesis 002
## Genesis Registration

**Package ID:** `MOOD-GENESIS-002`  
**Depends on:** `MOOD-GENESIS-001`  
**Execution target:** Existing Moodify web project  
**Mode:** Web-first / wallet-signature only / no token distribution  
**CANON_CHANGE:** `NO`

This package creates the first real participation gateway for Moodify Protocol.

The target flow is:

`/genesis`
→ Connect Wallet
→ Detect BNB Smart Chain
→ Request server nonce
→ Sign a human-readable Genesis message
→ Verify signature server-side
→ Create one Genesis Participant record
→ Return immutable participant number

No MOOD token is transferred in this package.

## Product outcome

A person with a supported EVM wallet can become a registered **Moodify Genesis Participant** without:
- depositing assets;
- approving token spending;
- sending a transaction;
- exposing a private key;
- paying gas.

The only wallet action is a message signature.

## Read order

1. `01_TASK_SPEC.md`
2. `02_SECURITY_MODEL.md`
3. `03_DATABASE_SCHEMA.md`
4. `04_ACCEPTANCE_CRITERIA.md`
5. `05_CODEX_EXECUTION_PROMPT.md`
6. `06_TEST_MATRIX.md`
7. `07_ROLLBACK_AND_OPERATIONS.md`
8. `08_FINAL_REPORT_TEMPLATE.md`
