# Write Boundary

## Default mode

Prefer:

`READ_ONLY`

for MPF-005 unless safe domain commands already exist.

## Allowed safe writes

Only when existing domain modules authorize them:

- submit a contribution draft
- register a node draft
- post a heartbeat observation

Even these must pass domain validation.

## Forbidden writes

- finalize contribution without domain authority
- directly edit reputation snapshot
- manually set arbitrary reputation
- directly mutate node lifecycle
- transfer MOOD
- mint/burn MOOD
- claim
- stake
- vote
- treasury transfer
- liquidity
- contract deploy
- remote job execution
- SSH
- shell

## Why

The API is a boundary, not protocol governance.
