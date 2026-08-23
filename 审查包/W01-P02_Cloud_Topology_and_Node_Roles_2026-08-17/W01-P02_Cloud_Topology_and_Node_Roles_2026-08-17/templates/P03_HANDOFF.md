# W01-P03 Handoff

P02 has decided **where responsibilities live**.

P03 must not reopen topology unless P02 contains `HUMAN_DECISION_REQUIRED`.

## Required P03 Inputs

- Node Role Assignment
- Network Matrix
- Secret Ownership Matrix
- Deployment Boundary
- Failure Domain Matrix
- Capacity Contract
- Target One Song Topology
- Architecture Decision Register

## P03 Question

> How should OSS and PolarDB form the unique, traceable and recoverable data plane?

P03 scope:

- track identity
- job identity
- object key convention
- source/stem/render/evidence prefixes
- metadata schema
- hashes
- versions
- provenance
- retention/lifecycle
- idempotent object/data writes
