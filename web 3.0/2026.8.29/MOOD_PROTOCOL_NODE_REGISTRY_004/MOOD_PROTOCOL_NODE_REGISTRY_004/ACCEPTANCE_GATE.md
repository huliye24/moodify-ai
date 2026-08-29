# MPF-004 Acceptance Gate

## Gate A — Authority

- [ ] AGENTS / Canon inspected
- [ ] MPF-001/002/003 inspected
- [ ] existing node/cloud code inspected
- [ ] no duplicate node authority
- [ ] CANON_CHANGE declared

## Gate B — Identity

- [ ] stable node ID
- [ ] operator protocol ID support
- [ ] node ID does not depend on mutable IP
- [ ] no private key required
- [ ] duplicate identity protection

## Gate C — Model

- [ ] node schema
- [ ] capability schema
- [ ] heartbeat schema
- [ ] registry snapshot schema
- [ ] required node types supported

## Gate D — Capabilities

- [ ] declaration != verification
- [ ] capability-level verification state
- [ ] sensitive infrastructure details not required
- [ ] data provenance/licensing metadata representable

## Gate E — Verification

- [ ] public challenge supported
- [ ] verification evidence stored
- [ ] node verification does not imply capability verification
- [ ] failed challenge fails safely

## Gate F — Lifecycle

- [ ] single lifecycle authority
- [ ] illegal transitions fail
- [ ] suspension cannot be bypassed by heartbeat
- [ ] lifecycle history retained

## Gate G — Health

- [ ] heartbeats timestamped
- [ ] health policy versioned
- [ ] stale state tested
- [ ] recovery tested
- [ ] health != reputation

## Gate H — Discovery

- [ ] node list
- [ ] node detail
- [ ] capability read
- [ ] health read
- [ ] filters
- [ ] no remote-control endpoint

## Gate I — Privacy / Security

- [ ] exact location not required
- [ ] no private IP required
- [ ] no credentials
- [ ] endpoint treated as untrusted input
- [ ] SSRF guard
- [ ] no SSH
- [ ] no shell
- [ ] no RCE

## Gate J — Economic isolation

- [ ] no token reward
- [ ] no stake
- [ ] no payout
- [ ] no treasury
- [ ] no node income model

## Gate K — Chain isolation

- [ ] no private wallet key
- [ ] no signing
- [ ] no transaction send
- [ ] no chain write

## Gate L — Tests / Evidence

- [ ] offline core tests
- [ ] deterministic registry snapshot
- [ ] regression tests
- [ ] sample nodes
- [ ] sample heartbeat transitions
- [ ] execution report
- [ ] rollback

Any mandatory failure means:

`STATUS = PARTIAL` or `STATUS = BLOCKED`

not PASS.
