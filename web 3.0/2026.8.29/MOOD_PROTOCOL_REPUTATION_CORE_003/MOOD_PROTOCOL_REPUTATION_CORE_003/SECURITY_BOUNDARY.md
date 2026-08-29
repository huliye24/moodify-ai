# Security Boundary

## Allowed

- read MPF-002 contribution records
- read public contributor identities
- hash canonical records
- build local profiles
- create reputation snapshots
- create local/repository attestations
- run offline tests

## Forbidden

- private key storage
- seed phrase access
- wallet custody
- transaction signing
- token transfer
- claim
- staking
- governance assignment
- treasury movement
- liquidity operations
- contract deployment
- chain writes

## Sensitive data

Protocol reputation should be based on public contribution evidence where possible.

Do not import:
- private emails
- private chat history
- private billing details
- private audio
- legal identity documents

without explicit future authorization.

## Integrity

Every snapshot should expose:
- input IDs
- input fingerprints
- policy version
- snapshot fingerprint

so unauthorized mutation can be detected.
