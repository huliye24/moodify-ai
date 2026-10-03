# ACCEPTANCE CRITERIA

## Dependency
- [ ] 017 accepted
- [ ] Network Agent extension point found

## Registry
- [ ] stable Agent ID
- [ ] unique slug
- [ ] operator linkage
- [ ] capability list
- [ ] version
- [ ] public/private serialization

## Status
- [ ] draft
- [ ] active
- [ ] paused
- [ ] degraded
- [ ] offline
- [ ] retired
- [ ] status based on real signals

## Proof
- [ ] task/activity linkage
- [ ] proof record
- [ ] public-safe proof
- [ ] no secret leakage

## Contribution
- [ ] Agent can assist
- [ ] Agent cannot self-approve
- [ ] Agent cannot write Reputation directly
- [ ] Agent cannot settle reward

## Network
- [ ] `/agents`
- [ ] `/agents/[slug]`
- [ ] real agent metrics on `/network`
- [ ] public activity integration

## Security
- [ ] prompt/tool threat model
- [ ] no private keys
- [ ] no funds movement
- [ ] no secret endpoint exposure

## Token independence
- [ ] registry works without MOOD Token
- [ ] no token gating
- [ ] no token rewards automation

## Verification
- [ ] `git diff --check`
- [ ] tests
- [ ] 019 handoff
