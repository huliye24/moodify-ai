# Rollback

## Principle

MPF-003 creates reputation records only.

It must not modify token balances, treasury, liquidity, contracts, or governance.

## Standard rollback

1. revert MPF-003 code commits;
2. remove local/generated MPF-003 fixture outputs;
3. restore previous profile index if needed;
4. rerun MPF-002 regression;
5. confirm MPF-001 mainnet facts unchanged.

## Historical snapshots

If production snapshots already exist later:

Do not delete or rewrite them.

Create a new corrective/superseding snapshot under a new policy version.

## Forbidden rollback strategies

- changing token balances
- revoking funds
- redeploying token contracts
- deleting contribution history
- editing finalized historical snapshots in place
