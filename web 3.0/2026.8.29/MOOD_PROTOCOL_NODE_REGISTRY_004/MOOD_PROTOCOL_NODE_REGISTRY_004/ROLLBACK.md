# Rollback

## Principle

MPF-004 must be reversible without touching chain state or node machines.

## Standard rollback

1. revert MPF-004 commits;
2. remove only local/generated registry fixtures;
3. restore previous registry index if one exists;
4. rerun MPF-001/002/003 regression tests;
5. confirm node machines were not modified by the registry.

## Production registry history later

If public node records have already been published:
- do not erase audit history silently;
- mark records retired/superseded;
- preserve old snapshots.

## Never rollback by

- deleting remote servers
- SSHing into nodes
- revoking cloud credentials
- moving tokens
- redeploying contracts
- deleting contributor history
