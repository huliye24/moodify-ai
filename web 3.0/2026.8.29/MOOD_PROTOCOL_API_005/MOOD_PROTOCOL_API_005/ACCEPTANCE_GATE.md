# MPF-005 Acceptance Gate

## Gate A — Authority

- [ ] AGENTS / Canon inspected
- [ ] MPF-001–004 inspected
- [ ] existing API framework reused
- [ ] no second protocol authority created
- [ ] CANON_CHANGE declared

## Gate B — Versioning

- [ ] explicit API v1
- [ ] consistent response envelope
- [ ] policy versions separate from API version
- [ ] breaking-change rules documented

## Gate C — Protocol reads

- [ ] mainnet facts
- [ ] contributions
- [ ] contributor profile
- [ ] reputation
- [ ] nodes
- [ ] capabilities
- [ ] health
- [ ] network summary
- [ ] network snapshot

## Gate D — Domain delegation

- [ ] route handlers thin
- [ ] no reputation logic in routes
- [ ] no node state logic in routes
- [ ] no hard-coded official contract facts
- [ ] no direct critical DB mutations

## Gate E — Public data

- [ ] default-deny sensitive fields
- [ ] location precision respected
- [ ] private node fields absent
- [ ] private evidence absent

## Gate F — Query safety

- [ ] bounded pagination
- [ ] validated filters
- [ ] sort allowlist
- [ ] payload limits
- [ ] standard errors

## Gate G — Observability

- [ ] request IDs
- [ ] health endpoint
- [ ] dependency state
- [ ] no secret logging

## Gate H — Security

- [ ] no private key
- [ ] no seed phrase
- [ ] no transaction signing
- [ ] no chain write
- [ ] no SSH
- [ ] no shell
- [ ] no arbitrary RCE

## Gate I — Economic isolation

- [ ] no MOOD transfer route
- [ ] no claim
- [ ] no staking
- [ ] no treasury transfer
- [ ] no reward conversion
- [ ] no market-price dependency

## Gate J — Tests

- [ ] endpoint tests
- [ ] authority-delegation tests
- [ ] private-field exclusion
- [ ] deterministic summary
- [ ] deterministic snapshot
- [ ] offline/local mode
- [ ] MPF-001–004 regression

## Gate K — Documentation

- [ ] OpenAPI/equivalent
- [ ] endpoint inventory
- [ ] auth/public status
- [ ] sample responses
- [ ] error model

Any failed mandatory gate means:

`STATUS = PARTIAL` or `STATUS = BLOCKED`

not PASS.
