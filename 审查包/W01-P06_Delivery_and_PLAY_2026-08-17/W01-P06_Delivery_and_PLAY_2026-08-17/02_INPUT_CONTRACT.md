# W01-P06 Input Contract

## From P05

- render format
- ready candidate/final object identity
- playback metadata
- verification result
- pipeline/profile version
- P06 handoff

## From P04

- READY semantics
- Track/Job query path
- control API authority
- no mutation of production state from playback errors

## From P03

- object locator
- object access class
- object existence verification
- object storage adapter
- Track ID

## From P02

- delivery node
- network boundary
- secret ownership
- public/private edge policy

## Hard Stop

If Android requires a permanent cloud credential to play:

`STOP — DELIVERY_SECURITY_INVALID`

If READY object cannot be retrieved through an authorized stable contract:

`STOP — READY_DELIVERY_CONTRACT_INCOMPLETE`
