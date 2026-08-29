# W01-P05 Input Contract

## Required from P04

- Job lifecycle semantics
- Attempt model
- Lease/fencing
- Retry policy
- Failure taxonomy
- Stage reporting command
- Completion command
- P05 handoff

## Required from P03

- Track / Job / Object identity
- Object storage adapter
- Object manifest
- Data provenance
- Object key convention
- Evidence model
- Output registration

## Required from P02

- Compute node
- External audio service roles
- capacity contract
- network matrix
- secret ownership

## Required from P01

- Ear is internal
- product external surface is not the compute pipeline
- evidence/human authority boundaries

## Hard Stop

If any of these are unknown:

- how worker validates lease
- how output object is registered
- how failure is reported
- how completion is submitted

then:

`STOP — PIPELINE_RUNTIME_CONTRACT_INCOMPLETE`
