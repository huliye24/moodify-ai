# Acceptance Criteria
## MOOD-GENESIS-004

### Critical

- [ ] Package 003 allocation records are read, not rewritten.
- [ ] Snapshot CLI exists.
- [ ] Dry-run exists.
- [ ] Inclusion rules are explicit.
- [ ] Only valid allocated recipients are included.
- [ ] Wallet addresses are validated.
- [ ] Duplicate wallets fail generation.
- [ ] Duplicate participant numbers fail generation.
- [ ] Token arithmetic uses exact integers.
- [ ] MOOD decimals = 18.
- [ ] Chain ID = 56.
- [ ] Contract matches official MOOD authority.
- [ ] Total allocation cannot exceed configured Genesis pool ceiling.
- [ ] Deterministic participant ordering exists.
- [ ] `snapshot.json` generated.
- [ ] `distribution.csv` generated.
- [ ] `merkle.json` generated.
- [ ] `distribution-report.md` generated.
- [ ] `manifest.json` generated.
- [ ] `checksums.txt` generated.
- [ ] Merkle root is reproducible from same canonical input.
- [ ] Every proof verifies locally.
- [ ] No token transfer occurs.
- [ ] No token approval occurs.
- [ ] No wallet transaction occurs.
- [ ] No smart contract is deployed.
- [ ] No private key handling exists.

### Reproducibility

- [ ] Same canonical input gives same participant ordering.
- [ ] Same canonical input gives same leaves.
- [ ] Same canonical input gives same Merkle root.
- [ ] Same canonical input gives same snapshot data hash.
- [ ] Non-deterministic timestamps do not alter canonical Merkle calculation.

### Integrity

- [ ] Rejected participants excluded.
- [ ] Zero allocations excluded/rejected according to spec.
- [ ] Negative allocation fails.
- [ ] >18 decimal precision fails.
- [ ] Malformed address fails.
- [ ] Scientific notation ambiguity fails or normalizes explicitly.
- [ ] Excluded rows reported.
- [ ] Snapshot ID overwrite protection exists.

### Reporting

- [ ] Participant count correct.
- [ ] Total MOOD correct.
- [ ] Min/max correct.
- [ ] Median correct.
- [ ] Merkle root displayed.
- [ ] Source commit recorded.
- [ ] Safety statement present.

### Documentation

- [ ] `docs/protocol/GENESIS_DISTRIBUTION.md` exists.
- [ ] Merkle encoding documented.
- [ ] Snapshot schema documented.
- [ ] Human approval boundary documented.
