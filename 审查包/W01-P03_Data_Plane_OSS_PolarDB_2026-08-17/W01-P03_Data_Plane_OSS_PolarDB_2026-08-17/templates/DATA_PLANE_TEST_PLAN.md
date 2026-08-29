# Data Plane Test Plan

## TST-01 Repeated Source
Same source bytes enter twice.

Expected:
- stable hash behavior
- no accidental overwrite
- ownership remains distinct where required

## TST-02 Immutable Source
Attempt to register different bytes at same immutable source identity.

Expected:
- reject

## TST-03 Render Provenance
Pick synthetic render object.

Expected:
- trace to track/job/source/version

## TST-04 Evidence Provenance
Evidence must identify subject and claim.

## TST-05 Idempotent Registration
Submit same object manifest twice.

Expected:
- no logical duplicate

## TST-06 Missing Object
DB refers to absent OSS object.

Expected:
- detectable

## TST-07 Orphan Object
OSS object exists without DB record.

Expected:
- detectable

## TST-08 Blob Guard
Schema contains no audio/render BLOB authority.

## TST-09 Client Credential Guard
Mobile config/build contains no long-lived OSS/DB credential.

## TST-10 Migration Replay
Migration can be applied to clean test DB reproducibly.
