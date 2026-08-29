# Genesis v1 Public Launch Checklist

## Phase 1 — Code Freeze

- [ ] Packages 001–007 complete
- [ ] Package 008 audit complete
- [ ] release branch/tag candidate created
- [ ] unrelated experimental features excluded
- [ ] production build passes

## Phase 2 — Data

- [ ] Genesis DB backup/export
- [ ] approved participants finalized
- [ ] allocation totals approved
- [ ] Package 004 snapshot generated
- [ ] snapshot SHA256 approved
- [ ] Merkle root approved
- [ ] checksums archived

## Phase 3 — Contract

- [ ] contract tests pass
- [ ] fuzz pass
- [ ] invariants pass
- [ ] static analysis reviewed
- [ ] constructor values reviewed
- [ ] owner/deadline/recovery policy approved
- [ ] deployment address not yet assumed

## Phase 4 — Mainnet Deployment

- [ ] operator wallet confirmed
- [ ] chain = BNB Smart Chain
- [ ] gas balance sufficient

[HUMAN SIGNATURE REQUIRED]

- [ ] deploy distributor
- [ ] record tx/address/block
- [ ] verify on BscScan
- [ ] compare bytecode/source

## Phase 5 — Funding

- [ ] exact approved MOOD amount calculated
- [ ] distributor address rechecked
- [ ] token address rechecked

[HUMAN SIGNATURE REQUIRED]

- [ ] transfer approved MOOD to distributor
- [ ] verify distributor balance
- [ ] archive funding tx

## Phase 6 — Website

- [ ] production distributor config added
- [ ] `/token` correct
- [ ] `/genesis` correct
- [ ] `/airdrop` correct
- [ ] `/contribute` correct
- [ ] `/transparency` correct
- [ ] no mock/test data
- [ ] mobile smoke test
- [ ] desktop smoke test

## Phase 7 — Claim Smoke Test

- [ ] approved eligible wallet
- [ ] proof correct
- [ ] wallet has BNB gas
- [ ] claim receipt success
- [ ] Claimed event verified
- [ ] frontend shows claimed
- [ ] transparency aggregate updates

## Phase 8 — Public Release

- [ ] security report reviewed
- [ ] known limitations published internally
- [ ] incident contacts ready
- [ ] monitoring enabled
- [ ] human GO decision recorded
