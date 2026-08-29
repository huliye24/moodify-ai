# MPF-003 Acceptance Gate

PASS requires every mandatory gate below.

## Gate A — Authority

- [ ] AGENTS / Canon inspected
- [ ] MPF-001 inspected
- [ ] MPF-002 implementation inspected
- [ ] Genesis/010 reputation/scoring policy inspected if present
- [ ] no duplicate reputation authority created
- [ ] CANON_CHANGE declared

## Gate B — Identity

- [ ] stable protocol ID exists
- [ ] public identity normalization tested
- [ ] no private key needed
- [ ] identity links require evidence
- [ ] similarity alone cannot merge identities

## Gate C — Input integrity

- [ ] only eligible MPF-002 inputs count
- [ ] rejected/unverified inputs excluded
- [ ] duplicate input guard exists
- [ ] input fingerprints retained

## Gate D — Reputation

- [ ] five dimensions preserved
- [ ] policy version pinned
- [ ] weights not invented
- [ ] aggregate null allowed
- [ ] persistence uses longitudinal evidence
- [ ] early score uses objective epoch rule

## Gate E — Epochs

- [ ] epoch policy versioned
- [ ] UTC boundaries
- [ ] deterministic resolution
- [ ] locked historical epoch not silently edited

## Gate F — Snapshots

- [ ] snapshot schema exists
- [ ] snapshot fingerprint deterministic
- [ ] snapshot immutable
- [ ] superseding preserves history
- [ ] current profile points to current snapshot safely

## Gate G — Attestation

- [ ] attestation is evidence, not automatic reputation
- [ ] attestor provenance retained
- [ ] no chain attestation required

## Gate H — Economic isolation

- [ ] no score→MOOD conversion
- [ ] no claim amount
- [ ] no payout
- [ ] no governance power
- [ ] no staking weight
- [ ] no treasury allocation

## Gate I — Chain isolation

- [ ] no private key
- [ ] no seed phrase
- [ ] no signing
- [ ] no transaction send
- [ ] no token transfer
- [ ] no chain write

## Gate J — Tests

- [ ] deterministic IDs
- [ ] deterministic snapshots
- [ ] rejected inputs excluded
- [ ] duplicates rejected
- [ ] persistence guard
- [ ] policy pinning
- [ ] offline tests
- [ ] MPF-002 regression

## Gate K — Evidence report

- [ ] branch/base/final commits
- [ ] files changed
- [ ] test commands/results
- [ ] sample protocol ID
- [ ] sample snapshot ID/fingerprint
- [ ] unresolved human decisions
- [ ] rollback

Failed mandatory gate means:

`STATUS = BLOCKED` or `STATUS = PARTIAL`

not PASS.
