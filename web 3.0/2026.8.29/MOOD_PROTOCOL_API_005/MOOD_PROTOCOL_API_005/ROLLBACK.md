# Rollback

## Principle

MPF-005 is an interface layer.

Rolling it back must not require changing:
- mainnet facts
- contribution history
- reputation history
- node registry state
- token balances
- chain contracts

## Standard rollback

1. revert MPF-005 commits;
2. disable/remove API v1 routing if introduced;
3. remove generated API docs only if tied to MPF-005;
4. keep MPF-001–004 domain data intact;
5. rerun MPF-001–004 tests.

## Never rollback by

- deleting protocol history
- transferring tokens
- altering treasury
- redeploying contracts
- SSHing to node machines
