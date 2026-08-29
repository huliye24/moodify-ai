# MPF-002 Acceptance Gate

MPF-002 is PASS only if every mandatory gate passes.

## Gate A — Authority

- [ ] Repository authority files inspected
- [ ] Existing Genesis/010 policy inspected if present
- [ ] No silent policy conflict
- [ ] `CANON_CHANGE` explicitly declared

## Gate B — Model

- [ ] Versioned contribution schema exists
- [ ] Versioned evidence schema exists
- [ ] Versioned reputation-evidence schema exists
- [ ] Controlled category policy exists
- [ ] Contributor identity requires no custody

## Gate C — Evidence

- [ ] Contributions cannot verify without required evidence
- [ ] Evidence verification state is explicit
- [ ] Evidence hashes/identifiers are retained
- [ ] Sensitive secrets are prohibited

## Gate D — State machine

- [ ] One authoritative state machine
- [ ] Illegal transitions fail
- [ ] Score-before-verify fails
- [ ] Finalized mutation fails
- [ ] Superseding history preserved

## Gate E — Determinism

- [ ] Canonical normalization tested
- [ ] Fingerprints deterministic
- [ ] Duplicate protection tested
- [ ] Policy version pinned
- [ ] Machine-scored outputs reproducible

## Gate F — Scoring

- [ ] Five dimensions represented
- [ ] Evidence references attached to scores
- [ ] No invented weights if no approved policy exists
- [ ] Aggregate is null when policy weights are not approved
- [ ] Persistence is not guessed from a single record

## Gate G — Economic isolation

- [ ] No score → MOOD conversion
- [ ] No payout field
- [ ] No claim field
- [ ] No vesting field
- [ ] No treasury instruction

## Gate H — Chain isolation

- [ ] No private key
- [ ] No seed phrase
- [ ] No signing
- [ ] No transaction send
- [ ] No token transfer
- [ ] No deployment
- [ ] Completion report says `NO_CHAIN_WRITE_PERFORMED`

## Gate I — Offline tests

- [ ] Unit tests run without internet
- [ ] Unit tests run without D1
- [ ] Unit tests run without RPC
- [ ] Mandatory fixtures covered

## Gate J — Evidence report

- [ ] Base/final commits recorded
- [ ] Files changed recorded
- [ ] Test command and output recorded
- [ ] Sample contribution IDs recorded
- [ ] Human decisions recorded
- [ ] Rollback described

Any failed mandatory gate means:

`STATUS = BLOCKED` or `STATUS = PARTIAL`

not PASS.
