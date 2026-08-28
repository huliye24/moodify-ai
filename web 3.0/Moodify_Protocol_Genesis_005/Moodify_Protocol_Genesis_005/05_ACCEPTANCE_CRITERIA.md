# Acceptance Criteria
## MOOD-GENESIS-005

### Contract critical

- [ ] Contract uses official MOOD token address.
- [ ] Contract uses approved Package 004 Merkle root in deployment config.
- [ ] Root is immutable in default v1.
- [ ] Valid proof claims exact approved amount.
- [ ] Invalid proof reverts.
- [ ] Wrong wallet reverts.
- [ ] Wrong amount reverts.
- [ ] Wrong participant number reverts.
- [ ] Double claim reverts.
- [ ] Failed transfer does not permanently consume claim.
- [ ] Claimed event emitted.
- [ ] SafeERC20 used.
- [ ] No mint capability.
- [ ] No hidden admin balance mutation.
- [ ] No proxy/upgrade backdoor.
- [ ] No claimant token approval needed.
- [ ] Recovery, if present, is impossible before approved deadline.
- [ ] Ownership, if present, is minimal and documented.

### Merkle compatibility

- [ ] Package 004 fixture loads.
- [ ] Contract validates Package 004 proof.
- [ ] Mutated fixture amount fails.
- [ ] Mutated wallet fails.
- [ ] Mutated participant number fails.
- [ ] Off-chain and on-chain root/proof behavior matches.

### Tests

- [ ] Unit tests pass.
- [ ] Fuzz tests pass.
- [ ] Invariant tests added where useful.
- [ ] Slither/static analysis run or unavailable reason documented.
- [ ] Gas report generated if supported.
- [ ] Local deployment simulation succeeds.

### Frontend

- [ ] `/airdrop` exists.
- [ ] Wallet connect works.
- [ ] BNB Chain enforced.
- [ ] Not eligible state works.
- [ ] Eligible state shows correct participant and amount.
- [ ] Claim uses proof from approved artifact.
- [ ] User rejection handled.
- [ ] Insufficient gas handled.
- [ ] Pending tx state works.
- [ ] Receipt confirmation drives success state.
- [ ] Already claimed state reads chain.
- [ ] BscScan transaction link shown.
- [ ] No approval transaction requested from claimant.
- [ ] Missing production distributor config fails safely.

### Deployment safety

- [ ] No production private key exists in repo.
- [ ] Production deployment is not automatically broadcast.
- [ ] Production funding is not automatically broadcast.
- [ ] Deployment runbook exists.
- [ ] Human approval checkpoints exist.
- [ ] BscScan verification command/script exists.
- [ ] Deployment record schema exists.

### Documentation

- [ ] `GENESIS_AIRDROP.md`
- [ ] `GENESIS_AIRDROP_RUNBOOK.md`
- [ ] contract architecture documented
- [ ] owner/deadline/recovery policy documented
- [ ] Merkle root/snapshot relationship documented
