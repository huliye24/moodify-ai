# Anti-Sybil and Abuse Boundary

## Scope

MPF-002 does not attempt to solve global proof-of-personhood.

It must, however, avoid obvious ways a contribution ledger can be gamed.

## Minimum protections

### Duplicate fingerprint guard

The same contributor cannot submit the same canonical contribution twice as two independent contributions.

### Cross-contributor duplicate flag

If identical content fingerprints appear under different contributor IDs, flag for review.

Do not automatically accuse users of fraud.

### Evidence reuse flag

Track evidence IDs / digests reused across multiple contribution records.

### Self-review guard

If policy requires independent review, contributor and reviewer cannot be the same identity.

### Finalization immutability

A finalized high-scoring contribution cannot be edited after review.

### Rate / batch observability

Store enough metadata to identify suspicious bursts later.

Do not introduce invasive personal tracking.

## Do not use

- device fingerprinting
- hidden browser tracking
- biometric identity
- private KYC data

unless a future governance policy explicitly authorizes it.

## Outcome states

Suspicious records should enter:
- `under_review`
- `needs_more_evidence`
- `rejected`

rather than causing automatic punishment outside policy.
