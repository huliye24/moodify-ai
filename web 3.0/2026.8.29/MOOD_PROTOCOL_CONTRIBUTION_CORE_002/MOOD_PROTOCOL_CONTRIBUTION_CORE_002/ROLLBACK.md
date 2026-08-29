# Rollback

## Goal

MPF-002 must be reversible without touching MOOD balances, contracts, liquidity, or treasury.

Because this package forbids chain writes, rollback should be a normal Git/application rollback.

## Recommended rollback

1. identify MPF-002 final commit;
2. revert the MPF-002 commit(s), or delete the isolated feature branch;
3. remove only MPF-002-generated local fixture/output data;
4. rerun pre-002 regression tests;
5. confirm MPF-001 mainnet facts remain unchanged.

## Never rollback by

- transferring tokens
- changing treasury balances
- redeploying contracts
- deleting historical chain data
- mutating finalized production contribution records in place

## If production records were created later

Use a migration/superseding strategy.

Do not erase audit history.
