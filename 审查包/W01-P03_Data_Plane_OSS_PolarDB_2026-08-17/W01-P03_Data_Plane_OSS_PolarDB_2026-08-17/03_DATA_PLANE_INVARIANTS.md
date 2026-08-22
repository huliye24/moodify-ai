# Data Plane Invariants

## INV-01 — Immutable Source
Canonical source bytes are never overwritten in place.

## INV-02 — Object Key Is Not Business Identity
Object key is a locator, not the sole logical identity.

## INV-03 — No Large Audio Blobs in Relational DB
Audio/render/stem binary data belongs in object storage.

## INV-04 — Job State Does Not Live in OSS
Object storage does not become authoritative orchestration state.

## INV-05 — READY Is Traceable
Every READY render must trace to canonical source and producer job.

## INV-06 — Production Is Versioned
Every final render records pipeline/tool/profile version identity.

## INV-07 — Evidence Has a Claim
Evidence must state what it is evidence for.

## INV-08 — Orphans Are Detectable
Objects without DB registration must be detectable.

## INV-09 — Missing Objects Are Detectable
DB references to missing object storage objects must be detectable.

## INV-10 — Referential Deletion Is Explicit
Neither DB rows nor objects are silently deleted in a way that destroys provenance.

## INV-11 — Writes Are Idempotent
Retried registration must not create logical duplicates.

## INV-12 — Ownership != Hash
Identical bytes do not imply identical user ownership.

## INV-13 — No Long-lived Client Cloud Secret
Mobile clients never receive long-term OSS/database credentials.

## INV-14 — Reality Beats Schema
Migration must accommodate real existing data discovered in P00.
