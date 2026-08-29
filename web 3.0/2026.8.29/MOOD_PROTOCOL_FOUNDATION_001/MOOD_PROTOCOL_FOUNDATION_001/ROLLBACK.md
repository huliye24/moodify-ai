# MPF-001 Rollback Plan

MPF-001 should be easy to revert because it performs no chain writes.

## Rollback trigger

Rollback or hold merge if:

- canonical config points to the wrong chain;
- canonical token identifier conflicts with verified deployed state;
- a testnet value leaks into production authority;
- an existing claim/read flow breaks;
- environment override semantics become unsafe;
- secrets appear in the diff;
- unrelated product/audio behavior changes;
- a lock artifact was produced from unresolved facts.

## Rollback procedure

1. Stop release/merge.
2. Do not perform any compensating chain transaction.
3. Revert MPF-001 code/config commit(s) only.
4. Restore prior runtime configuration from version control/deployment config.
5. Delete invalid `protocol/mainnet.lock.json` if it was created.
6. Preserve the evidence report explaining the conflict.
7. Set mainnet state back to draft.
8. Re-run pre-task tests/build.
9. Open a `HUMAN_DECISION_REQUIRED` item for the disputed fact.

## What rollback does not require

Because MPF-001 forbids chain writes, rollback should not require:

- token recovery;
- treasury transfer;
- contract redeploy;
- liquidity removal;
- ownership changes.

If any of those become necessary, task scope was violated.
