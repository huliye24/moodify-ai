# Pipeline Version Contract

## Pipeline Version Binds

- stage order
- enabled/optional stages
- adapter versions
- tool/model versions
- analysis schema
- judgment policy
- intervention logic
- profile version
- render policy
- verification policy

## Version Format

Decision:
- format:
- authority:
- change rule:
- deprecation rule:

## Production Fingerprint

Inputs:

- canonical source content hash
- pipeline version
- stage config
- profile version
- tool/model versions
- render policy version

Algorithm:

`SHA-256(stable canonical serialization)`

## Important

- fingerprint != Job ID
- fingerprint != ownership
- same fingerprint is a reproducibility hint, not a legal equivalence claim
