# Verification Contract

## Technical Verification

- exists
- hash verified
- decode succeeds
- duration sane
- sample rate/channels expected
- no invalid sample values
- no catastrophic clipping/overflow
- no truncation evidence
- object registered

## Comparative Verification

Required when intervention occurred:

- before/after metrics
- target condition checked
- unsupported degradation checked
- evidence complete

## Human Verification

If policy requires:

- reviewer
- verdict
- timestamp
- comparison refs
- notes

## Result

- PASS
- FAIL
- HUMAN_REVIEW_REQUIRED

Only PASS produces an automatic CompletionCandidate eligible for READY transition.
