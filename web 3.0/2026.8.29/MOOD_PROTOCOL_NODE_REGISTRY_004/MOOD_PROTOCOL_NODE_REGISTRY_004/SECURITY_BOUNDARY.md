# Security Boundary

## Allowed

- public registration data
- public node IDs
- public operator protocol IDs
- public HTTPS endpoint verification
- public verification keys
- capability declarations
- read-only health probes
- local fixtures
- deterministic snapshots

## Forbidden

- SSH private keys
- SSH commands
- remote shell
- arbitrary command execution
- cloud account credentials
- API secrets
- seed phrases
- wallet private keys
- wallet signing
- token transfers
- staking
- treasury movement
- contract deployment
- firewall mutation
- cloud resource creation/deletion

## Endpoint safety

Registry must treat node endpoints as untrusted external input.

Mitigate where applicable:
- SSRF
- localhost/internal-network probing
- unexpected URI schemes
- redirect abuse
- oversized responses
- slow responses
- malformed certificates
- DNS rebinding

Verification implementation should only allow explicitly approved schemes and paths.

## Public keys

Node public verification keys are acceptable.

Node private verification keys must remain node-side.

## Registry compromise

Compromise of the registry must not grant shell access to nodes.

This is a critical architectural invariant.
