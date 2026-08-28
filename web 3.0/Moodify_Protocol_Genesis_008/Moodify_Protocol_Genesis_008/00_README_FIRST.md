# Moodify Protocol Genesis 008
## Security & Public Launch

**Package ID:** `MOOD-GENESIS-008`  
**Depends on:** `MOOD-GENESIS-001` → `007`  
**Execution target:** Existing Moodify repository  
**Mode:** Full-system audit / hardening / release candidate / no unattended mainnet actions  
**CANON_CHANGE:** `NO`

This is the final package in the Moodify Protocol Genesis v1 sequence.

Its goal is not to add more product surface. Its goal is to make the entire Genesis system safe, coherent, testable, reviewable and ready for controlled public launch.

The system under review includes:

- `/token`
- `/genesis`
- `/admin/genesis`
- Distribution Engine
- Merkle Airdrop
- `/airdrop`
- `/contribute`
- `/admin/contributions`
- `/transparency`
- treasury/accounting reads
- D1/Drizzle schema
- wallet message signatures
- Merkle artifacts
- claim contract
- admin authorization
- privacy boundaries
- deployment/funding runbooks

## Primary outcome

Produce a **Genesis Release Candidate** with:

1. full security review;
2. regression suite;
3. contract review;
4. database integrity review;
5. frontend/wallet abuse review;
6. privacy review;
7. operational runbook;
8. release checklist;
9. incident response guide;
10. production readiness report.

## Hard boundary

Codex may:
- audit;
- refactor;
- test;
- harden;
- simulate;
- deploy locally/testnet if already configured and safe;
- generate mainnet commands;
- generate human approval checklists.

Codex must not:
- access private keys;
- auto-sign production transactions;
- auto-deploy to BNB mainnet;
- auto-fund the distributor;
- transfer treasury MOOD;
- add/remove liquidity;
- change token economics;
- invent production wallet labels;
- silently change protocol canon.

The principle remains:

**AI writes. AI verifies. Human signs. Human approves canon.**

Read all files before execution.
