# W01-P05 Handoff

P04 freezes control-plane semantics.

P05 must not redefine:

- Job lifecycle states
- transition authority
- lease semantics
- retry budget ownership
- attempt identity
- fencing
- idempotency
- failure top-level taxonomy

unless a P04 defect is demonstrated.

## Worker Receives

- job_id
- track_id
- attempt_id
- lease_id / fencing token
- input object refs
- pipeline version request
- safe config refs
- stage reporting contract

## Worker Must Return

- output object refs
- evidence refs
- resource summary
- completion command

or:

- structured failure class/code
- safe details/evidence

## P05 Question

> How does one legally claimed RUNNING job execute the audio compute pipeline and produce a verified READY candidate?
