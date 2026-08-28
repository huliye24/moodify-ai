# Moodify Protocol Genesis 003
## Genesis Admin

**Package ID:** `MOOD-GENESIS-003`  
**Depends on:** `MOOD-GENESIS-001`, `MOOD-GENESIS-002`  
**Execution target:** Existing Moodify web project  
**Mode:** Admin-only / allocation management / no token transfer  
**CANON_CHANGE:** `NO`

This package creates the internal control plane for the first Moodify Genesis participants.

The target workflow is:

Participant registers on `/genesis`
→ Admin reviews participant
→ Admin records notes / contribution score
→ Admin marks eligibility
→ Admin assigns a provisional MOOD allocation
→ Every change is auditable
→ Export approved allocation data for the future Distribution Engine

This package must **not** send MOOD.

## Primary outcome

Create a secure admin area, preferably:

`/admin/genesis`

where authorized operators can:

- view Genesis participants;
- search/filter participants;
- inspect one participant;
- review status;
- edit contribution score;
- assign provisional MOOD allocation;
- add internal notes;
- export CSV/JSON;
- see allocation totals;
- inspect immutable audit history.

## Human authority boundary

Codex may build all management logic.

Codex must not:
- hold a private key;
- sign token transfers;
- auto-send MOOD;
- deploy an airdrop contract;
- approve token spending;
- mutate on-chain balances.

The admin system only manages **off-chain eligibility and allocation records**.

Read `01_TASK_SPEC.md` and then execute `05_CODEX_EXECUTION_PROMPT.md`.
