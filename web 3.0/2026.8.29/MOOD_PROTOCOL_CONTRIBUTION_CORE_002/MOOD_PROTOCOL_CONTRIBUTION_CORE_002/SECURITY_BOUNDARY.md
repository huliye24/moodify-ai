# Security Boundary

## Allowed

- parse public wallet addresses
- read public transaction hashes as evidence
- read public repository evidence
- hash files/content
- validate schemas
- run local tests
- create local fixture records
- produce reputation-evidence artifacts

## Forbidden

- private keys
- seed phrases
- wallet custody
- signing
- approvals
- token transfers
- token minting
- token burning
- liquidity operations
- treasury movement
- contract deployment
- claim execution
- airdrop execution
- RPC write methods

## RPC rule

If chain data is consulted, use read-only calls.

A test should make it difficult for a write-capable path to appear accidentally.

## Secrets

No real secret may be committed.

Use placeholders in fixtures.

## URLs

External evidence retrieval should be treated as untrusted input.

Avoid shell interpolation and unsafe command construction.

## File hashes

Hash bytes, not filenames.

Normalize structured JSON before hashing when the protocol definition requires semantic equivalence.
